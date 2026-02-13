import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import shutil
import time
import io

# Tentukan zona waktu Manado (WITA)
timezone = pytz.timezone('Asia/Makassar')

st.set_page_config(page_title="Absensi Galva Manado", layout="wide")
st.title("Sistem Absensi Galva Manado")

# --- KONFIGURASI FOLDER & FILE ---
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

for folder in [folder_foto, folder_penebusan]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- INISIALISASI DATAFRAME ---
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        # Pastikan kolom tanggal terbaca sebagai string untuk filter
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%Y-%m-%d')
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

# --- MENU NAVIGASI ---
menu = st.sidebar.selectbox("Menu", ["Absensi Karyawan", "Tebus Denda", "Login Admin"])
Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]

# --- HALAMAN ABSENSI ---
if menu == "Absensi Karyawan":
    nama = st.selectbox("Pilih Nama Anda:", Karyawan_List)
    opsi_absen = st.radio("Tipe Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit", "Tugas Luar Kota"])

    waktu_sekarang = datetime.now(timezone)
    jam_skrg = waktu_sekarang.strftime("%H:%M:%S")
    
    if nama != "Pilih Nama":
        st.info(f"Jam Sekarang: **{jam_skrg}**")
        if opsi_absen == "Hadir di Kantor":
            # Toleransi 5 menit (08:05)
            if (waktu_sekarang.hour > 8 or (waktu_sekarang.hour == 8 and waktu_sekarang.minute > 5)):
                st.warning("⚠️ Status Anda: **TERLAMBAT** (Denda Rp 10.000)")
            else:
                st.success("✅ Status Anda: **TEPAT WAKTU**")

    alasan = ""
    if opsi_absen == "Tugas Luar Kota":
        alasan = st.text_input("📍 Masukkan Lokasi/Tujuan Tugas:")
    elif opsi_absen != "Hadir di Kantor":
        alasan = st.text_area("📝 Masukkan Alasan / Catatan (Sakit/Cuti/Izin):")
    
    img_file = None
    if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota"]:
        img_file = st.camera_input("Ambil foto untuk absen")
    else:
        img_file = st.file_uploader("Upload Bukti (Opsional)", type=['jpg', 'jpeg', 'png', 'pdf'])

    if nama != "Pilih Nama":
        # Syarat tombol muncul
        ready_to_save = (opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota"] and img_file is not None) or \
                        (opsi_absen in ["Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit"])

        if ready_to_save:
            if st.button("🚀 KIRIM ABSENSI SEKARANG", key="btn_absen"):
                with st.spinner('Menyimpan data...'):
                    waktu_klik = datetime.now(timezone)
                    tgl_absen = waktu_klik.strftime("%Y-%m-%d")
                    jam_absen = waktu_klik.strftime("%H:%M:%S")
                    denda = 0
                    status_denda = "Lunas"
                    
                    if opsi_absen == "Hadir di Kantor":
                        if (waktu_klik.hour > 8 or (waktu_klik.hour == 8 and waktu_klik.minute > 5)):
                            status = "TERLAMBAT"
                            denda = 10000
                            status_denda = "Belum Lunas"
                        else:
                            status = "TEPAT WAKTU"
                    else:
                        status = opsi_absen.upper()

                    # Simpan ke DataFrame
                    data_baru = pd.DataFrame([[tgl_absen, jam_absen, nama, status, alasan, denda, status_denda]], columns=columns)
                    df_total = pd.concat([df_total, data_baru], ignore_index=True)
                    df_total.to_excel(excel_file, index=False)

                    # Simpan Foto
                    if img_file:
                        ext = "jpg" if not hasattr(img_file, 'name') else img_file.name.split('.')[-1]
                        nama_file = f"{tgl_absen}_{nama}_{status}_{waktu_klik.strftime('%H%M%S')}.{ext}".replace(" ", "_")
                        with open(os.path.join(folder_foto, nama_file), "wb") as f:
                            f.write(img_file.getbuffer())

                    st.balloons()
                    st.success(f"✅ BERHASIL! Absensi {nama} berhasil dicatat pada {jam_absen}.")
                    time.sleep(2)
                    st.rerun()

# --- HALAMAN TEBUS DENDA ---
elif menu == "Tebus Denda":
    st.subheader("Penebusan Denda Keterlambatan")
    nama_tebus = st.selectbox("Siapa yang ingin menebus?", Karyawan_List)
    if nama_tebus != "Pilih Nama":
        idx_hutang = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_hutang = df_total.loc[idx_hutang, 'Denda'].sum()
        
        if total_hutang > 0:
            st.error(f"Total Akumulasi Denda Anda: Rp {total_hutang:,}")
            mode_tebus = st.radio("Pilih Jumlah:", ["Tebus Semua", "Tebus Sebagian (Cicil)"])
            jumlah_dibayar = total_hutang if mode_tebus == "Tebus Semua" else st.number_input("Nominal Kelipatan 10rb:", min_value=10000, step=10000)
            metode = st.radio("Metode Penebusan:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            
            if st.button("Konfirmasi Penebusan"):
                jumlah_terpenuhi = 0
                for idx in idx_hutang:
                    if jumlah_terpenuhi < jumlah_dibayar:
                        df_total.at[idx, 'Status Denda'] = f"Lunas ({metode})"
                        jumlah_terpenuhi += df_total.at[idx, 'Denda']
                
                df_total.to_excel(excel_file, index=False)
                st.success(f"Berhasil! Denda Rp {jumlah_dibayar:,} telah lunas.")
                time.sleep(2)
                st.rerun()
        else:
            st.success("Anda tidak memiliki tunggakan denda.")

# --- HALAMAN ADMIN ---
elif menu == "Login Admin":
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📑 Laporan & Grafik Excel", "📸 Galeri Foto", "⚙️ Pengaturan"])
        
        # Setup Data untuk Filter
        df_total['Tanggal_DT'] = pd.to_datetime(df_total['Tanggal'])
        df_total['Bulan_Tahun'] = df_total['Tanggal_DT'].dt.strftime('%B %Y')
        list_bulan = df_total['Bulan_Tahun'].unique()

        with tab1:
            st.subheader("Statistik Kehadiran (Aplikasi)")
            if not df_total.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**Grafik Terlambat**")
                    st.bar_chart(df_total[df_total['Status'] == 'TERLAMBAT'].groupby('Nama').size())
                with c2:
                    st.write("**Grafik Tugas Luar Kota**")
                    st.bar_chart(df_total[df_total['Status'] == 'TUGAS LUAR KOTA'].groupby('Nama').size())
                
                st.divider()
                # Ringkasan Dana
                t_tunai = df_total[df_total['Status Denda'] == 'Lunas (Bayar Tunai / Transfer)']['Denda'].sum()
                t_bersih = df_total[df_total['Status Denda'] == 'Lunas (Membersihkan Kantor)']['Denda'].sum()
                st.metric("Total Dana Masuk (Tunai)", f"Rp {t_tunai:,}")
                st.metric("Total Denda Dibayar (Bersih Kantor)", f"Rp {t_bersih:,}")
            else:
                st.info("Belum ada data.")

        with tab2:
            st.subheader("Ekspor Laporan Bulanan")
            bulan_pilih = st.selectbox("Pilih Bulan:", list_bulan if len(list_bulan)>0 else ["Data Kosong"])
            
            df_filter = df_total[df_total['Bulan_Tahun'] == bulan_pilih].copy()
            st.dataframe(df_filter[columns])

            if not df_filter.empty:
                # --- PROSES EXCEL + CHART ---
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # Sheet 1: Data Detail
                    df_filter[columns].to_excel(writer, sheet_name='Data Absensi', index=False)
                    
                    # Sheet 2: Ringkasan & Grafik
                    summary = df_filter.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                    summary.to_excel(writer, sheet_name='Ringkasan Statistik')
                    
                    workbook  = writer.book
                    worksheet = writer.sheets['Ringkasan Statistik']
                    
                    # Buat Grafik Batang
                    chart = workbook.add_chart({'type': 'column'})
                    max_row = len(summary) + 1
                    status_cols = summary.columns.tolist()
                    
                    for i, col_name in enumerate(status_cols):
                        chart.add_series({
                            'name':       ['Ringkasan Statistik', 0, i + 1],
                            'categories': ['Ringkasan Statistik', 1, 0, max_row - 1, 0],
                            'values':     ['Ringkasan Statistik', 1, i + 1, max_row - 1, i + 1],
                        })
                    
                    chart.set_title({'name': f'Laporan Kehadiran {bulan_pilih}'})
                    chart.set_style(11)
                    # Simpan Grafik di samping tabel (Kolom E baris 2)
                    worksheet.insert_chart('E2', chart, {'x_scale': 1.5, 'y_scale': 1.5})
                
                st.download_button(
                    label=f"📥 Download Excel + Grafik ({bulan_pilih})",
                    data=output.getvalue(),
                    file_name=f"Laporan_Galva_{bulan_pilih.replace(' ','_')}.xlsx",
                    mime="application/vnd.ms-excel"
                )

        with tab3:
            st.subheader("Foto Kehadiran Terbaru")
            daftar_foto = sorted(os.listdir(folder_foto), reverse=True)
            if daftar_foto:
                cols = st.columns(4)
                for i, f in enumerate(daftar_foto[:20]): # Tampilkan 20 foto terbaru
                    with cols[i % 4]: st.image(os.path.join(folder_foto, f), caption=f)

        with tab4:
            st.warning("Tombol di bawah ini akan menghapus seluruh database.")
            if st.button("🚨 RESET SEMUA DATA SEKARANG"):
                if os.path.exists(excel_file): os.remove(excel_file)
                shutil.rmtree(folder_foto); os.makedirs(folder_foto)
                shutil.rmtree(folder_penebusan); os.makedirs(folder_penebusan)
                st.success("Data berhasil direset!")
                st.rerun()