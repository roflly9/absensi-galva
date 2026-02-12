import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 

# Tentukan zona waktu Manado (WITA)
timezone = pytz.timezone('Asia/Makassar')

st.title("Sistem Absensi Galva Manado")

# File Excel untuk menyimpan semua data
excel_file = "report_absensi.xlsx"

# Inisialisasi DataFrame di awal agar tidak error
if os.path.exists(excel_file):
    df_total = pd.read_excel(excel_file)
else:
    df_total = pd.DataFrame(columns=["Tanggal", "Jam", "Nama", "Status", "Alasan"])

# Menu Navigasi
menu = st.sidebar.selectbox("Menu", ["Absensi Karyawan", "Login Admin"])

# --- HALAMAN ABSENSI ---
if menu == "Absensi Karyawan":
    Karyawan = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Pilih Nama Anda:", Karyawan)
    opsi_absen = st.radio("Tipe Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Izin Tidak Masuk / Cuti"])

    alasan = st.text_area("Masukkan Alasan / Catatan:") if opsi_absen != "Hadir di Kantor" else ""
    
    img_file = None
    if opsi_absen == "Hadir di Kantor":
        img_file = st.camera_input("Ambil foto untuk absen")
    else:
        img_file = st.file_uploader("Upload Bukti", type=['jpg', 'jpeg', 'png', 'pdf'])

    # Logika penentuan tombol submit
    if opsi_absen == "Hadir di Kantor":
        submit = img_file is not None
    else:
        submit = st.button("Simpan Data")

    # PERBAIKAN INDENTASI DI SINI
    if submit and nama != "Pilih Nama":
        waktu_klik = datetime.now(timezone) 
        jam_absen = waktu_klik.strftime("%H:%M:%S")
        tgl_absen = waktu_klik.strftime("%Y-%m-%d")

        # Logika Status
        if opsi_absen == "Hadir di Kantor":
            if (waktu_klik.hour > 8 or (waktu_klik.hour == 8 and waktu_klik.minute > 5)):
                status = "TERLAMBAT"
            else:
                status = "TEPAT WAKTU"
        else:
            status = opsi_absen.upper()

        # Update Data ke DataFrame Total
        data_baru = pd.DataFrame([[tgl_absen, jam_absen, nama, status, alasan]], columns=df_total.columns)
        
        # Simpan permanen ke Excel
        df_total = pd.concat([df_total, data_baru], ignore_index=True)
        df_total.to_excel(excel_file, index=False)

        st.success(f"Berhasil! Absen {nama} telah tercatat.")
        st.table(data_baru)

# --- HALAMAN ADMIN ---
elif menu == "Login Admin":
    st.subheader("Halaman Khusus Admin")
    password = st.text_input("Masukkan Password Admin:", type="password")
    
    if password == "galva123":
        st.success("Login Berhasil! Berikut Rekap Seluruh Karyawan:")
        
        # Reload data terbaru dari Excel
        if os.path.exists(excel_file):
            df_admin = pd.read_excel(excel_file)
            st.dataframe(df_admin)
            
            with open(excel_file, "rb") as f:
                st.download_button(
                    label="📊 Download Semua Data (Excel)",
                    data=f,
                    file_name=f"Rekap_Total_{datetime.now(timezone).strftime('%d%m%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("Belum ada data absen.")
    elif password != "":
        st.error("Password Salah!")