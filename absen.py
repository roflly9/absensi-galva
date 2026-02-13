import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import shutil
import time

# Tentukan zona waktu Manado (WITA)
timezone = pytz.timezone('Asia/Makassar')

st.set_page_config(page_title="Absensi Galva Manado", layout="centered")
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
        alasan = st.text_area("📝 Masukkan Alasan / Catatan:")
    
    img_file = None
    if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota"]:
        img_file = st.camera_input("Ambil foto untuk langsung absen")
    else:
        img_file = st.file_uploader("Upload Bukti (Opsional)", type=['jpg', 'jpeg', 'png', 'pdf'])

    # Logika Simpan
    if nama != "Pilih Nama":
        # Tombol hanya muncul jika syarat terpenuhi
        ready_to_save = False
        if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota"] and img_file is not None:
            ready_to_save = True
        elif opsi_absen in ["Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit"]:
            ready_to_save = True

        if ready_to_save:
            # Gunakan key unik agar tidak tertukar
            if st.button("🚀 KLIK DISINI UNTUK KIRIM ABSENSI", key="btn_absen"):
                with st.spinner('Sedang mencatat absensi... Mohon tunggu...'):
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

                    # Cek double absen (nama yang sama di jam yang hampir sama)
                    # Jika data terakhir adalah orang yang sama di hari yang sama, beri konfirmasi
                    
                    data_baru = pd.DataFrame([[tgl_absen, jam_absen, nama, status, alasan, denda, status_denda]], columns=columns)
                    df_total = pd.concat([df_total, data_baru], ignore_index=True)
                    df_total.to_excel(excel_file, index=False)

                    if img_file:
                        ext = "jpg" if not hasattr(img_file, 'name') else img_file.name.split('.')[-1]
                        nama_file = f"{tgl_absen}_{nama}_{status}_{waktu_klik.strftime('%H%M%S')}.{ext}".replace(" ", "_")
                        with open(os.path.join(folder_foto, nama_file), "wb") as f:
                            f.write(img_file.getbuffer())

                    st.balloons()
                    st.success(f"✅ BERHASIL! Absensi {nama} jam {jam_absen} sudah tersimpan di server.")
                    time.sleep(2) # Beri waktu user membaca konfirmasi
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
            mode_tebus = st.radio("Pilih Jumlah Tebusan:", ["Tebus Semua", "Tebus Sebagian (Cicil)"])
            
            jumlah_dibayar = total_hutang
            if mode_tebus == "Tebus Sebagian (Cicil)":
                jumlah_dibayar = st.number_input("Masukkan Nominal (Kelipatan 10.000):", min_value=10000, max_value=int(total_hutang), step=10000)
            
            metode = st.radio("Pilih Metode Penebusan:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            
            file_bukti = []
            if metode == "Bayar Tunai / Transfer":
                bt = st.file_uploader("Upload Bukti Bayar", type=['jpg','png','jpeg'])
                if bt: file_bukti.append(bt)
            else:
                f_seb = st.camera_input("Foto Sebelum")
                f_ses = st.camera_input("Foto Sesudah")
                if f_seb and f_ses:
                    file_bukti.extend([f_seb, f_ses])
            
            if st.button("Konfirmasi Penebusan"):
                if not file_bukti:
                    st.warning("Mohon lampirkan bukti foto!")
                else:
                    tgl_skrg = datetime.now(timezone).strftime("%Y%m%d_%H%M")
                    for i, f in enumerate(file_bukti):
                        with open(os.path.join(folder_penebusan, f"TEBUS_{nama_tebus}_{tgl_skrg}_{i}.jpg"), "wb") as file_simpan:
                            file_simpan.write(f.getbuffer())
                    
                    jumlah_terpenuhi = 0
                    for idx in idx_hutang:
                        if jumlah_terpenuhi < jumlah_dibayar:
                            df_total.at[idx, 'Status Denda'] = f"Lunas ({metode})"
                            jumlah_terpenuhi += df_total.at[idx, 'Denda']
                    
                    df_total.to_excel(excel_file, index=False)
                    st.success(f"Denda Rp {jumlah_dibayar:,} Berhasil Ditebus!")
                    time.sleep(2)
                    st.rerun()
        else:
            st.success("Tidak ada tunggakan denda.")

# --- HALAMAN ADMIN ---
elif menu == "Login Admin":
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        tab1, tab2, tab3 = st.tabs(["📊 Data Absensi", "📸 Galeri Foto", "⚙️ Pengaturan"])
        with tab1:
            st.dataframe(df_total)
            if os.path.exists(excel_file):
                with open(excel_file, "rb") as f:
                    st.download_button("📥 Download Excel", f, "Laporan_Absen.xlsx")
        with tab2:
            st.subheader("Foto Absensi Hari Ini")
            daftar_foto = sorted(os.listdir(folder_foto), reverse=True)
            if daftar_foto:
                cols = st.columns(3)
                for i, file_foto in enumerate(daftar_foto):
                    with cols[i % 3]: st.image(os.path.join(folder_foto, file_foto), caption=file_foto)
        with tab3:
            if st.button("⚠️ RESET SEMUA DATA"):
                if os.path.exists(excel_file): os.remove(excel_file)
                shutil.rmtree(folder_foto); os.makedirs(folder_foto)
                shutil.rmtree(folder_penebusan); os.makedirs(folder_penebusan)
                st.rerun()