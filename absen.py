import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import zipfile 
import shutil

# Tentukan zona waktu Manado (WITA)
timezone = pytz.timezone('Asia/Makassar')

st.set_page_config(page_title="Absensi Galva Manado", layout="centered")
st.title("Sistem Absensi Galva Manado")

# Konfigurasi Folder & File
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

# Pastikan folder tersedia
for folder in [folder_foto, folder_penebusan]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Inisialisasi DataFrame
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        for col in columns:
            if col not in df_total.columns:
                df_total[col] = "Lunas" if col == "Status Denda" else 0
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
    # Penambahan Opsi Tugas Luar Kota
    opsi_absen = st.radio("Tipe Kehadiran:", ["Hadir di Kantor", "Tugas Luar Kota", "Izin Terlambat", "Izin Tidak Masuk / Cuti"])

    # Logika Input Keterangan
    alasan = ""
    if opsi_absen == "Tugas Luar Kota":
        alasan = st.text_input("Masukkan Lokasi/Tujuan Tugas:")
    elif opsi_absen != "Hadir di Kantor":
        alasan = st.text_area("Masukkan Alasan / Catatan:")
    
    img_file = None
    if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota"]:
        img_file = st.camera_input("Ambil foto bukti kehadiran/lokasi")
    else:
        img_file = st.file_uploader("Upload Bukti", type=['jpg', 'jpeg', 'png', 'pdf'])

    # Tombol Simpan
    submit = False
    if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota"]:
        submit = img_file is not None
    else:
        submit = st.button("Simpan Data Absensi")

    if submit and nama != "Pilih Nama":
        waktu_klik = datetime.now(timezone) 
        jam_absen = waktu_klik.strftime("%H:%M:%S")
        tgl_absen = waktu_klik.strftime("%Y-%m-%d")

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

        # Simpan ke Excel
        data_baru = pd.DataFrame([[tgl_absen, jam_absen, nama, status, alasan, denda, status_denda]], columns=columns)
        df_total = pd.concat([df_total, data_baru], ignore_index=True)
        df_total.to_excel(excel_file, index=False)

        # Simpan File Foto
        ext = "jpg" if img_file.name is None else img_file.name.split('.')[-1]
        nama_file = f"{tgl_absen}_{nama}_{status}.{ext}".replace(" ", "_")
        with open(os.path.join(folder_foto, nama_file), "wb") as f:
            f.write(img_file.getbuffer())

        st.success(f"Absen {nama} ({status}) berhasil disimpan!")
        if denda > 0:
            st.warning(f"⚠️ Terlambat! Denda Rp 10.000 tercatat.")
        st.rerun()

# --- HALAMAN TEBUS DENDA ---
elif menu == "Tebus Denda":
    st.subheader("Penebusan Denda Keterlambatan")
    nama_tebus = st.selectbox("Siapa yang ingin menebus?", Karyawan_List)
    
    if nama_tebus != "Pilih Nama":
        hutang_user = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')]
        total_hutang = hutang_user['Denda'].sum()
        
        if total_hutang > 0:
            st.error(f"Total Akumulasi Denda Anda: Rp {total_hutang:,}")
            metode = st.radio("Pilih Metode Penebusan:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            
            if metode == "Bayar Tunai / Transfer":
                bukti = st.file_uploader("Upload Bukti Bayar", type=['jpg','png','jpeg'])
                if bukti and st.button("Konfirmasi Bayar"):
                    tgl = datetime.now(timezone).strftime("%Y%m%d_%H%M")
                    with open(os.path.join(folder_penebusan, f"BAYAR_{nama_tebus}_{tgl}.jpg"), "wb") as f:
                        f.write(bukti.getbuffer())
                    df_total.loc[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas'), 'Status Denda'] = 'Lunas (Bayar)'
                    df_total.to_excel(excel_file, index=False)
                    st.success("Denda Lunas!")
                    st.rerun()
            else:
                f_seb = st.camera_input("Foto Sebelum")
                f_ses = st.camera_input("Foto Sesudah")
                if f_seb and f_ses and st.button("Kirim Laporan"):
                    tgl = datetime.now(timezone).strftime("%Y%m%d_%H%M")
                    with open(os.path.join(folder_penebusan, f"SEBELUM_{nama_tebus}_{tgl}.jpg"), "wb") as f:
                        f.write(f_seb.getbuffer())
                    with open(os.path.join(folder_penebusan, f"SESUDAH_{nama_tebus}_{tgl}.jpg"), "wb") as f:
                        f.write(f_ses.getbuffer())
                    df_total.loc[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas'), 'Status Denda'] = 'Lunas (Bersih)'
                    df_total.to_excel(excel_file, index=False)
                    st.success("Denda Lunas!")
                    st.rerun()
        else:
            st.success("Tidak ada tunggakan denda.")

# --- HALAMAN ADMIN ---
elif menu == "Login Admin":
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        tab1, tab2 = st.tabs(["📊 Laporan", "⚙️ Pengaturan"])
        with tab1:
            st.dataframe(df_total)
            if os.path.exists(excel_file):
                with open(excel_file, "rb") as f:
                    st.download_button("Download Excel", f, "Laporan_Absen.xlsx")
        with tab2:
            if st.button("RESET SEMUA DATA"):
                if os.path.exists(excel_file): os.remove(excel_file)
                shutil.rmtree(folder_foto); os.makedirs(folder_foto)
                shutil.rmtree(folder_penebusan); os.makedirs(folder_penebusan)
                st.rerun()