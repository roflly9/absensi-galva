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
    # Penambahan Opsi: Langsung ke Customer
    opsi_absen = st.radio("Tipe Kehadiran:", [
        "Hadir di Kantor", 
        "Izin Terlambat", 
        "Tidak Masuk Kantor Cuti/Sakit", 
        "Tugas Luar Kota", 
        "Langsung ke Customer"
    ])

    waktu_sekarang = datetime.now(timezone)
    jam_skrg = waktu_sekarang.strftime("%H:%M:%S")
    
    if nama != "Pilih Nama":
        st.info(f"Jam Sekarang: **{jam_skrg}**")
        if opsi_absen == "Hadir di Kantor":
            if (waktu_sekarang.hour > 8 or (waktu_sekarang.hour == 8 and waktu_sekarang.minute > 5)):
                st.warning("⚠️ Status Anda: **TERLAMBAT** (Denda Rp 10.000)")
            else:
                st.success("✅ Status Anda: **TEPAT WAKTU**")

    alasan = ""
    if opsi_absen in ["Tugas Luar Kota", "Langsung ke Customer"]:
        alasan = st.text_input("📍 Masukkan Lokasi/Tujuan (Nama Toko/Instansi):")
    elif opsi_absen != "Hadir di Kantor":
        alasan = st.text_area("📝 Masukkan Alasan / Catatan (Sakit/Cuti/Izin):")
    
    img_file = None
    # Syarat Foto untuk Hadir, Luar Kota, dan Langsung ke Customer
    if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"]:
        img_file = st.camera_input("Ambil foto untuk absen")
    else:
        img_file = st.file_uploader("Upload Bukti (Opsional)", type=['jpg', 'jpeg', 'png', 'pdf'])

    if nama != "Pilih Nama":
        ready_to_save = (opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] and img_file is not None) or \
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

                    data_baru = pd.DataFrame([[tgl_absen, jam_absen, nama, status, alasan, denda, status_denda]], columns=columns)
                    df_total = pd.concat([df_total, data_baru], ignore_index=True)
                    df_total.to_excel(excel_file, index=False)

                    if img_file:
                        ext = "jpg" if not hasattr(img_file, 'name') else img_file.name.split('.')[-1]
                        nama_file = f"{tgl_absen}_{nama}_{status}_{waktu_klik.strftime('%H%M%S')}.{ext}".replace(" ", "_")
                        with open(os.path.join(folder_foto, nama_file), "wb") as f:
                            f.write(img_file.getbuffer())

                    st.balloons()
                    st.success(f"✅ BERHASIL! Absensi {nama} berhasil dicatat.")
                    time.sleep(2)
                    st.rerun()

# --- HALAMAN TEBUS DENDA (FUNGSI FOTO DIKEMBALIKAN) ---
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
            
            # Kembalikan Logika Bukti Foto
            file_bukti = []
            if metode == "Bayar Tunai / Transfer":
                bt = st.file_uploader("Upload Bukti Transfer / Foto Uang Tunai", type=['jpg','png','jpeg'])
                if bt: file_bukti.append(bt)
            else:
                st.info("Ambil foto kondisi sebelum dan sesudah membersihkan.")
                f_seb = st.camera_input("Foto Sebelum (Before)")
                f_ses = st.camera_input("Foto Sesudah (After)")
                if f_seb and f_ses:
                    file_bukti.extend([f_seb, f_ses])
            
            if st.button("Konfirmasi Penebusan"):
                if not file_bukti:
                    st.warning("⚠️ Mohon lampirkan bukti foto terlebih dahulu!")
                else:
                    # Simpan Bukti Foto Penebusan
                    tgl_skrg = datetime.now(timezone).strftime("%Y%m%d_%H%M")
                    for i, f in enumerate(file_bukti):
                        with open(os.path.join(folder_penebusan, f"TEBUS_{nama_tebus}_{tgl_skrg}_{i}.jpg"), "wb") as file_simpan:
                            file_simpan.write(f.getbuffer())

                    # Update Status di Database
                    jumlah_terpenuhi = 0
                    for idx in idx_hutang:
                        if jumlah_terpenuhi < jumlah_dibayar:
                            df_total.at[idx, 'Status Denda'] = f"Lunas ({metode})"
                            jumlah_terpenuhi += df_total.at[idx, 'Denda']
                    
                    df_total.to_excel(excel_file, index=False)
                    st.success(f"Berhasil! Denda Rp {jumlah_dibayar:,} telah lunas melalui {metode}.")
                    time.sleep(2)
                    st.rerun()
        else:
            st.success("Anda tidak memiliki tunggakan denda.")

# --- HALAMAN ADMIN ---
elif menu == "Login Admin":
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📑 Laporan & Grafik Excel", "📸 Galeri Foto", "⚙️ Pengaturan"])
        
        df_total['Tanggal_DT'] = pd.to_datetime(df_total['Tanggal'])
        df_total['Bulan_Tahun'] = df_total['Tanggal_DT'].dt.strftime('%B %Y')
        list_bulan = df_total['Bulan_Tahun'].unique()

        with tab1:
            st.subheader("Statistik Kehadiran")
            if not df_total.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**Top Terlambat**")
                    st.bar_chart(df_total[df_total['Status'] == 'TERLAMBAT'].groupby('Nama').size())
                with c2:
                    st.write("**Top Langsung Ke Customer**")
                    st.bar_chart(df_total[df_total['Status'] == 'LANGSUNG KE CUSTOMER'].groupby('Nama').size())
            else:
                st.info("Belum ada data.")

        with tab2:
            st.subheader("Ekspor Laporan Bulanan")
            bulan_pilih = st.selectbox("Pilih Bulan:", list_bulan if len(list_bulan)>0 else ["Data Kosong"])
            df_filter = df_total[df_total['Bulan_Tahun'] == bulan_pilih].copy()
            st.dataframe(df_filter[columns])

            if not df_filter.empty:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_filter[columns].to_excel(writer, sheet_name='Data Absensi', index=False)
                    
                    # Logika Grafik di Excel
                    summary = df_filter.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                    summary.to_excel(writer, sheet_name='Ringkasan Statistik')
                    
                    workbook  = writer.book
                    worksheet = writer.sheets['Ringkasan Statistik']
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
                    worksheet.insert_chart('E2', chart, {'x_scale': 1.5, 'y_scale': 1.5})
                
                st.download_button(label="📥 Download Excel + Grafik", data=output.getvalue(), file_name=f"Laporan_Galva_{bulan_pilih}.xlsx")

        with tab3:
            st.subheader("Galeri Foto Absensi")
            daftar_foto = sorted(os.listdir(folder_foto), reverse=True)
            if daftar_foto:
                cols = st.columns(4)
                for i, f in enumerate(daftar_foto[:20]):
                    with cols[i % 4]: st.image(os.path.join(folder_foto, f), caption=f)

        with tab4:
            if st.button("🚨 RESET SEMUA DATA SEKARANG"):
                if os.path.exists(excel_file): os.remove(excel_file)
                shutil.rmtree(folder_foto); os.makedirs(folder_foto)
                shutil.rmtree(folder_penebusan); os.makedirs(folder_penebusan)
                st.rerun()