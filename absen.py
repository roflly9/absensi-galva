import streamlit as st
from datetime import datetime
import os
import pandas as pd

st.title("Sistem Absensi Galva Manado")

# Membuat folder penyimpanan jika belum ada
if not os.path.exists("hasil_absen"):
    os.makedirs("hasil_absen")

excel_file = "hasil_absen/report_absensi.xlsx"

Karyawan = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
nama = st.selectbox("Pilih Nama Anda:", Karyawan)

opsi_absen = st.radio("Tipe Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Izin Tidak Masuk / Cuti"])

alasan = ""
if opsi_absen != "Hadir di Kantor":
    alasan = st.text_area("Masukkan Alasan / Catatan:")

img_file = None
if opsi_absen == "Hadir di Kantor":
    img_file = st.camera_input("Silahkan ambil foto untuk absen")
else:
    img_file = st.file_uploader("Upload Bukti (Foto/PDF jika ada)", type=['jpg', 'jpeg', 'png', 'pdf'])

# Tombol submit muncul otomatis untuk foto, atau manual untuk izin/cuti
submit = st.button("Simpan Data") if opsi_absen != "Hadir di Kantor" else (img_file is not None)

if submit and nama != "Pilih Nama":
    waktu_klik = datetime.now()
    jam_absen = waktu_klik.strftime("%H:%M:%S")
    tgl_absen = waktu_klik.strftime("%Y-%m-%d")

    # Penentuan Status
    status = ""
    if opsi_absen == "Hadir di Kantor":
        if waktu_klik.hour > 8 or (waktu_klik.hour == 8 and waktu_klik.minute > 5):
            status = "TERLAMBAT"
        else:
            status = "TEPAT WAKTU"
    else:
        status = opsi_absen.upper()

    # --- SIMPAN KE EXCEL ---
    data_baru = {
        "Tanggal": [tgl_absen],
        "Jam": [jam_absen],
        "Nama": [nama],
        "Status": [status],
        "Alasan": [alasan]
    }
    df_baru = pd.DataFrame(data_baru)

    if os.path.exists(excel_file):
        df_lama = pd.read_excel(excel_file)
        df_final = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df_final = df_baru

    df_final.to_excel(excel_file, index=False)

    # --- SIMPAN FILE MEDIA ---
    ext = "jpg" if opsi_absen == "Hadir di Kantor" else "file"
    nama_file = f"{status}_{nama}_{waktu_klik.strftime('%Y%m%d_%H%M%S')}.{ext}"
    path_simpan = os.path.join("hasil_absen", nama_file)
    
    if img_file:
        with open(path_simpan, "wb") as f:
            f.write(img_file.getbuffer())
    
    st.success(f"Berhasil! Data {nama} tersimpan.")
    st.dataframe(df_baru)

# --- TOMBOL DOWNLOAD (Di Luar IF agar selalu muncul) ---
st.markdown("---")
st.subheader("Admin Area")
if os.path.exists(excel_file):
    with open(excel_file, "rb") as f:
        st.download_button(
            label="📊 Download Laporan Excel",
            data=f,
            file_name=f"Rekap_Absen_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Belum ada data absen masuk untuk diunduh.")