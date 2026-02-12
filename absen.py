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
        st.success("Login Berhasil!")
        
        # TAB untuk memisahkan Tabel dan Foto
        tab1, tab2 = st.tabs(["📊 Rekap Absensi", "🖼️ Lihat Lampiran Foto/File"])
        
        with tab1:
            if os.path.exists(excel_file):
                df_admin = pd.read_excel(excel_file)
                st.dataframe(df_admin)
                
                with open(excel_file, "rb") as f:
                    st.download_button(
                        label="📥 Download Excel Keseluruhan",
                        data=f,
                        file_name=f"Rekap_Total_{datetime.now(timezone).strftime('%d%m%Y')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("Belum ada data tabel.")

        with tab2:
            st.write("Daftar lampiran yang tersimpan di server:")
            folder_foto = "hasil_absen"
            
            if os.path.exists(folder_foto):
                files = os.listdir(folder_foto)
                # Filter hanya file foto atau pdf (menghindari file excel masuk daftar)
                lampiran = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.pdf'))]
                
                if lampiran:
                    selected_file = st.selectbox("Pilih file untuk dilihat:", lampiran)
                    path_file = os.path.join(folder_foto, selected_file)
                    
                    # Tampilkan jika gambar
                    if selected_file.endswith(('.jpg', '.jpeg', '.png')):
                        st.image(path_file, caption=selected_file, use_container_width=True)
                    
                    # Tombol download untuk file individu
                    with open(path_file, "rb") as f:
                        st.download_button(
                            label=f"💾 Download {selected_file}",
                            data=f,
                            file_name=selected_file
                        )
                else:
                    st.info("Belum ada lampiran foto/file.")
            else:
                st.info("Folder lampiran belum terbentuk.")
                
    elif password != "":
        st.error("Password Salah!")