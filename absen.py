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

st.set_page_config(page_title="Absensi Galva Manado", layout="wide") # Layout wide agar grafik luas
st.title("Sistem Absensi Galva Manado")

# Konfigurasi Folder & File
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

for folder in [folder_foto, folder_penebusan]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Inisialisasi DataFrame
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%Y-%m-%d')
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

# Menu Navigasi
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
            if (waktu_sekarang.hour > 8 or (waktu_sekarang.hour == 8 and waktu_sekarang.minute > 5)):
                st.warning("⚠️ Status Anda: **TERLAMBAT**")
            else:
                st.success("✅ Status Anda: **TEPAT WAKTU**")

    alasan = ""
    if opsi_absen == "Tugas Luar Kota":
        alasan = st.text_input("📍 Masukkan Lokasi/Tujuan Tugas:")
    elif opsi_absen != "Hadir di Kantor":
        alasan = st.text_area("📝 Masukkan Alasan / Catatan (Sakit/Cuti/Izin):")
    
    img_file = None
    if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota"]:
        img_file = st.camera_input("Ambil foto untuk langsung absen")
    else:
        img_file = st.file_uploader("Upload Bukti (Opsional)", type=['jpg', 'jpeg', 'png', 'pdf'])

    if nama != "Pilih Nama":
        ready_to_save = (opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota"] and img_file is not None) or \
                        (opsi_absen in ["Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit"])

        if ready_to_save:
            if st.button("🚀 KLIK DISINI UNTUK KIRIM ABSENSI", key="btn_absen"):
                with st.spinner('Mencatat...'):
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

                    data_baru = pd.DataFrame([[tgl_absen, jam_absen, nama, status, alasan, denda, status_denda]], columns=columns)
                    df_total = pd.concat([df_total, data_baru], ignore_index=True)
                    df_total.to_excel(excel_file, index=False)

                    if img_file:
                        ext = "jpg" if not hasattr(img_file, 'name') else img_file.name.split('.')[-1]
                        nama_file = f"{tgl_absen}_{nama}_{status}_{waktu_klik.strftime('%H%M%S')}.{ext}".replace(" ", "_")
                        with open(os.path.join(folder_foto, nama_file), "wb") as f:
                            f.write(img_file.getbuffer())

                    st.balloons()
                    st.success(f"✅ BERHASIL! Absensi {nama} tersimpan.")
                    time.sleep(2)
                    st.rerun()

# --- HALAMAN TEBUS DENDA (Logika Sama Seperti Sebelumnya) ---
elif menu == "Tebus Denda":
    st.subheader("Penebusan Denda Keterlambatan")
    nama_tebus = st.selectbox("Siapa yang ingin menebus?", Karyawan_List)
    if nama_tebus != "Pilih Nama":
        idx_hutang = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_hutang = df_total.loc[idx_hutang, 'Denda'].sum()
        if total_hutang > 0:
            st.error(f"Total Akumulasi Denda Anda: Rp {total_hutang:,}")
            mode_tebus = st.radio("Pilih Jumlah:", ["Tebus Semua", "Tebus Sebagian (Cicil)"])
            jumlah_dibayar = total_hutang if mode_tebus == "Tebus Semua" else st.number_input("Nominal:", min_value=10000, step=10000)
            metode = st.radio("Metode:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            
            # Tombol Konfirmasi (Logika simpan bukti tetap ada)
            if st.button("Konfirmasi Penebusan"):
                jumlah_terpenuhi = 0
                for idx in idx_hutang:
                    if jumlah_terpenuhi < jumlah_dibayar:
                        df_total.at[idx, 'Status Denda'] = f"Lunas ({metode})"
                        jumlah_terpenuhi += df_total.at[idx, 'Denda']
                df_total.to_excel(excel_file, index=False)
                st.success("Berhasil ditebus!")
                st.rerun()
        else:
            st.success("Tidak ada tunggakan.")

# --- HALAMAN ADMIN (UPDATE BESAR) ---
elif menu == "Login Admin":
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard & Grafik", "📑 Laporan Bulanan", "📸 Galeri Foto", "⚙️ Pengaturan"])
        
        # LOGIKA FILTER BULAN
        df_total['Tanggal_DT'] = pd.to_datetime(df_total['Tanggal'])
        df_total['Bulan_Tahun'] = df_total['Tanggal_DT'].dt.strftime('%B %Y')
        list_bulan = df_total['Bulan_Tahun'].unique()

        with tab1:
            st.subheader("Ringkasan Performa Karyawan")
            if not df_total.empty:
                col_a, col_b = st.columns(2)
                
                # Hitung Statistik
                stats_terlambat = df_total[df_total['Status'] == 'TERLAMBAT'].groupby('Nama').size()
                stats_luar_kota = df_total[df_total['Status'] == 'TUGAS LUAR KOTA'].groupby('Nama').size()
                
                with col_a:
                    st.write("**Top Terlambat**")
                    st.bar_chart(stats_terlambat)
                with col_b:
                    st.write("**Top Tugas Luar Kota**")
                    st.bar_chart(stats_luar_kota)

                # Total Dana
                total_cash = df_total[df_total['Status Denda'] == 'Lunas (Bayar Tunai / Transfer)']['Denda'].sum()
                total_kerja = df_total[df_total['Status Denda'] == 'Lunas (Membersihkan Kantor)']['Denda'].sum()
                
                st.divider()
                c1, c2 = st.columns(2)
                c1.metric("Total Dana Terkumpul (Tunai)", f"Rp {total_cash:,}")
                c2.metric("Total Denda Dibayar (Kerja Bakti)", f"Rp {total_kerja:,}")
            else:
                st.info("Belum ada data untuk dianalisa.")

        with tab2:
            st.subheader("Laporan Per Bulan")
            bulan_pilih = st.selectbox("Pilih Bulan Laporan:", list_bulan if len(list_bulan)>0 else ["Belum Ada Data"])
            
            df_filter = df_total[df_total['Bulan_Tahun'] == bulan_pilih].copy()
            st.dataframe(df_filter[columns])

            # Export Excel dengan Grafik/Summary
            if not df_filter.empty:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_filter[columns].to_excel(writer, sheet_name='Data Absensi', index=False)
                    # Sheet Summary
                    summary = df_filter.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                    summary.to_excel(writer, sheet_name='Ringkasan Statistik')
                
                st.download_button(
                    label="📥 Download Excel Laporan " + bulan_pilih,
                    data=output.getvalue(),
                    file_name=f"Laporan_Galva_{bulan_pilih.replace(' ','_')}.xlsx",
                    mime="application/vnd.ms-excel"
                )

        with tab3:
            st.subheader("Galeri Kehadiran")
            daftar_foto = sorted(os.listdir(folder_foto), reverse=True)
            if daftar_foto:
                cols = st.columns(4)
                for i, f in enumerate(daftar_foto):
                    with cols[i % 4]: st.image(os.path.join(folder_foto, f), caption=f)

        with tab4:
            if st.button("⚠️ RESET SEMUA DATA (PERMANEN)"):
                if os.path.exists(excel_file): os.remove(excel_file)
                shutil.rmtree(folder_foto); os.makedirs(folder_foto)
                shutil.rmtree(folder_penebusan); os.makedirs(folder_penebusan)
                st.rerun()