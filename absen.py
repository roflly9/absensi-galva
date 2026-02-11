import streamlit as st
from datetime import datetime # Diperbaiki
import os

st.title("Sistem Absensi Galva Manado")

# Membuat folder penyimpanan jika belum ada
if not os.path.exists("hasil_absen"):
    os.makedirs("hasil_absen")

Karyawan = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
nama = st.selectbox("Pilih Nama Anda:", Karyawan)

img_file = st.camera_input("Silahkan ambil foto untuk absen")

if img_file is not None and nama != "Pilih Nama":
    # Mengambil waktu saat ini
    waktu_klik = datetime.now()
    jam_absen = waktu_klik.strftime("%H:%M:%S") # Ditambah tanda kutip & perbaikan variabel

    # Logika Keterlambatan (Batas 08:05)
    terlambat = False
    if waktu_klik.hour > 8 or (waktu_klik.hour == 8 and waktu_klik.minute > 5):
        terlambat = True

    # Tampilan hasil
    st.image(img_file)
    
    if terlambat:
        st.error(f"Absen Berhasil! Jam: {jam_absen} (STATUS: TERLAMBAT)")
    else:
        st.success(f"Absen Berhasil! Jam: {jam_absen} (STATUS: TEPAT WAKTU)")

    # SIMPAN FOTO
    # Nama file: Nama_Tanggal_Jam.jpg
    nama_file = f"absensi_{nama}_{waktu_klik.strftime('%Y%m%d_%H%M%S')}.jpg"
    path_simpan = os.path.join("hasil_absen", nama_file)
    
    with open(path_simpan, "wb") as f:
        f.write(img_file.getbuffer())
    
    st.info(f"Foto telah disimpan sebagai: {nama_file}")