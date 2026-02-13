import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import zipfile 
import shutil  

# Tentukan zona waktu Manado (WITA)
timezone = pytz.timezone('Asia/Makassar')

st.title("Sistem Absensi Galva Manado")

# Konfigurasi Folder & File
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"

if not os.path.exists(folder_foto):
    os.makedirs(folder_foto)

# Inisialisasi DataFrame (Menambahkan Kolom Denda)
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda"]
if os.path.exists(excel_file):
    df_total = pd.read_excel(excel_file)
    # Cek jika kolom denda belum ada (untuk file lama)
    if "Denda" not in df_total.columns:
        df_total["Denda"] = 0
else:
    df_total = pd.DataFrame(columns=columns)

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

    # Logika Tombol Submit
    if opsi_absen == "Hadir di Kantor":
        submit = img_file is not None
    else:
        submit = st.button("Simpan Data")

    if submit and nama != "Pilih Nama":
        waktu_klik = datetime.now(timezone) 
        jam_absen = waktu_klik.strftime("%H:%M:%S")
        tgl_absen = waktu_klik.strftime("%Y-%m-%d")

        # Logika Status & Denda
        denda = 0
        if opsi_absen == "Hadir di Kantor":
            # Terlambat jika lewat dari 08:05
            if (waktu_klik.hour > 8 or (waktu_klik.hour == 8 and waktu_klik.minute > 5)):
                status = "TERLAMBAT"
                denda = 10000
            else:
                status = "TEPAT WAKTU"
        else:
            status = opsi_absen.upper()

        # Simpan Data ke DataFrame
        data_baru = pd.DataFrame([[tgl_absen, jam_absen, nama, status, alasan, denda]], columns=columns)
        df_total = pd.concat([df_total, data_baru], ignore_index=True)
        df_total.to_excel(excel_file, index=False)

        # Simpan File Foto
        ext = "jpg" if opsi_absen == "Hadir di Kantor" else img_file.name.split('.')[-1]
        nama_file_foto = f"{tgl_absen}_{nama}_{status}.{ext}".replace(" ", "_")
        path_foto = os.path.join(folder_foto, nama_file_foto)
        
        with open(path_foto, "wb") as f:
            f.write(img_file.getbuffer())

        # Notifikasi Sukses & Info Denda
        st.success(f"Berhasil! Absen {nama} telah tercatat.")
        if denda > 0:
            st.warning(f"⚠️ Anda Terlambat! Denda: Rp {denda:,}")
        
        st.table(data_baru)

# --- HALAMAN ADMIN ---
elif menu == "Login Admin":
    st.subheader("Halaman Khusus Admin")
    password = st.text_input("Masukkan Password Admin:", type="password")
    
    if password == "galva123":
        st.success("Login Berhasil!")
        
        # --- FITUR RESET ---
        st.warning("⚠️ Area Berbahaya")
        if st.button("RESET SEMUA DATA (Hapus Excel & Foto)"):
            if os.path.exists(excel_file):
                os.remove(excel_file)
            if os.path.exists(folder_foto):
                shutil.rmtree(folder_foto)
                os.makedirs(folder_foto)
            st.error("Semua data telah direset! Halaman akan dimuat ulang...")
            st.rerun()
        
        st.markdown("---")
        tab1, tab2 = st.tabs(["📊 Rekap Absensi", "🖼️ Rekap Foto/File"])
        
        with tab1:
            if os.path.exists(excel_file):
                df_admin = pd.read_excel(excel_file)
                # Menampilkan total denda di dashboard admin
                total_denda_kumpul = df_admin["Denda"].sum()
                st.metric("Total Denda Terkumpul", f"Rp {total_denda_kumpul:,}")
                
                st.dataframe(df_admin)
                with open(excel_file, "rb") as f:
                    st.download_button("📥 Download Excel Keseluruhan", f, f"Rekap_Total_{datetime.now(timezone).strftime('%d%m%Y')}.xlsx")
            else:
                st.info("Belum ada data tabel.")

        with tab2:
            files = [f for f in os.listdir(folder_foto) if f.endswith(('.jpg', '.jpeg', '.png', '.pdf'))]
            if files:
                st.write(f"Terdapat {len(files)} file lampiran.")
                zip_path = "rekap_foto.zip"
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file in files:
                        zipf.write(os.path.join(folder_foto, file), file)
                
                with open(zip_path, "rb") as f:
                    st.download_button(label="📦 DOWNLOAD SEMUA FOTO (ZIP)", data=f, 
                                       file_name=f"Rekap_Foto_{datetime.now(timezone).strftime('%d%m%Y')}.zip",
                                       mime="application/zip")
                
                st.markdown("---")
                selected_file = st.selectbox("Lihat detail file:", files)
                path_sel = os.path.join(folder_foto, selected_file)
                if selected_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    st.image(path_sel, use_container_width=True)
            else:
                st.info("Belum ada lampiran foto.")
                
    elif password != "":
        st.error("Password Salah!")