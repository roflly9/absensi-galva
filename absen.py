import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import shutil
import time
import io
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Absensi Galva Manado", 
    page_icon="🏢", 
    layout="centered" # Menggunakan centered agar lebih pas di layar HP
)

# --- CUSTOM CSS UNTUK TAMPILAN MOBILE ---
st.markdown("""
    <style>
    /* Sembunyikan Header dan Footer bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Atur padding utama */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Mempercantik Tombol (Mobile Friendly) */
    div.stButton > button:first-child {
        width: 100%;
        height: 50px;
        border-radius: 10px;
        font-weight: bold;
        background-color: #0046ad;
        color: white;
        border: none;
    }

    /* Styling input agar lebih rapi */
    .stTextInput, .stSelectbox, .stTextArea {
        margin-bottom: 10px;
    }
    
    /* Banner Selamat Datang */
    .welcome-banner {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KONFIGURASI WAKTU & FOLDER ---
timezone = pytz.timezone('Asia/Makassar')

excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

def inisialisasi_folder():
    for folder in [folder_foto, folder_penebusan]:
        if not os.path.exists(folder):
            os.makedirs(folder)

inisialisasi_folder()

# --- INISIALISASI DATAFRAME ---
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "ID_Tebus"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        # Pastikan kolom tanggal terbaca sebagai string untuk filter
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%Y-%m-%d')
        if "ID_Tebus" not in df_total.columns:
            df_total["ID_Tebus"] = ""
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.title("📌 Menu Navigasi")
    menu = st.radio("Pilih Halaman:", ["Absensi Karyawan", "Tebus Denda", "Login Admin"])
    st.divider()
    st.caption("v1.2 - Galva Manado App")

Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]

# --- HALAMAN 1: ABSENSI ---
if menu == "Absensi Karyawan":
    st.markdown('<div class="welcome-banner"><h2>🏢 Absensi Galva</h2><p>Pastikan GPS Aktif & Foto Jelas</p></div>', unsafe_allow_html=True)
    
    nama = st.selectbox("Pilih Nama Anda:", Karyawan_List)
    opsi_absen = st.radio("Tipe Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Cuti/Sakit", "Tugas Luar Kota", "Langsung ke Customer"])

    waktu_sekarang = datetime.now(timezone)
    jam_skrg = waktu_sekarang.strftime("%H:%M:%S")
    
    if nama != "Pilih Nama":
        st.info(f"🕒 Jam Sekarang: **{jam_skrg}**")
        
        # Logika Denda Terlambat (Batas 08:05)
        is_late = (waktu_sekarang.hour > 8 or (waktu_sekarang.hour == 8 and waktu_sekarang.minute > 5))
        
        if opsi_absen == "Hadir di Kantor":
            if is_late:
                st.warning("⚠️ Status: **TERLAMBAT** (Denda Rp 10.000)")
            else:
                st.success("✅ Status: **TEPAT WAKTU**")

        alasan = ""
        if opsi_absen in ["Tugas Luar Kota", "Langsung ke Customer"]:
            alasan = st.text_input("📍 Masukkan Lokasi/Tujuan:")
        elif opsi_absen != "Hadir di Kantor":
            alasan = st.text_area("📝 Masukkan Alasan / Catatan:")
        
        # Kamera input untuk HP
        img_file = st.camera_input("Ambil Foto Absen") if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] else st.file_uploader("Upload Bukti", type=['jpg','png','jpeg'])

        if img_file:
            if st.button("🚀 KIRIM ABSENSI SEKARANG"):
                with st.spinner('Memproses Data...'):
                    waktu_klik = datetime.now(timezone)
                    denda = 10000 if (opsi_absen == "Hadir di Kantor" and is_late) else 0
                    status_denda = "Belum Lunas" if denda > 0 else "Lunas"
                    status = "TERLAMBAT" if denda > 0 else opsi_absen.upper()

                    # Simpan ke Excel
                    data_baru = pd.DataFrame([[waktu_klik.strftime("%Y-%m-%d"), waktu_klik.strftime("%H:%M:%S"), nama, status, alasan, denda, status_denda, ""]], columns=columns)
                    df_total = pd.concat([df_total, data_baru], ignore_index=True)
                    df_total.to_excel(excel_file, index=False)

                    # Simpan Foto
                    fname = f"{waktu_klik.strftime('%Y%m%d_%H%M%S')}_{nama}.jpg"
                    with open(os.path.join(folder_foto, fname), "wb") as f:
                        f.write(img_file.getbuffer())
                    
                    st.success("✅ Berhasil! Mengalihkan...")
                    time.sleep(2)
                    st.rerun()

# --- HALAMAN 2: TEBUS DENDA ---
elif menu == "Tebus Denda":
    st.subheader("💰 Penebusan Denda")
    nama_tebus = st.selectbox("Pilih Nama:", Karyawan_List)
    
    if nama_tebus != "Pilih Nama":
        idx_hutang = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_hutang = df_total.loc[idx_hutang, 'Denda'].sum()
        
        menunggu_app = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'].str.contains("Menunggu", na=False))]
        
        if not menunggu_app.empty:
            st.warning("⌛ Menunggu verifikasi Admin...")

        if total_hutang > 0:
            st.error(f"Total Tunggakan: Rp {total_hutang:,}")
            metode = st.radio("Metode Penebusan:", ["Transfer/Tunai", "Bersihkan Kantor"])
            
            file_bukti = []
            if metode == "Transfer/Tunai":
                bt = st.file_uploader("Upload Bukti Bayar", type=['jpg','png','jpeg'])
                if bt: file_bukti.append(bt)
            else:
                c1, c2 = st.columns(2)
                f_seb = c1.file_uploader("Foto Sebelum", type=['jpg','png','jpeg'], key="b4")
                f_ses = c2.file_uploader("Foto Sesudah", type=['jpg','png','jpeg'], key="af")
                if f_seb and f_ses: file_bukti.extend([f_seb, f_ses])
            
            if st.button("Ajukan Penebusan"):
                if not file_bukti:
                    st.error("Wajib melampirkan foto bukti!")
                else:
                    id_unik = f"{nama_tebus}_{datetime.now(timezone).strftime('%y%m%d%H%M%S')}"
                    for i, f in enumerate(file_bukti):
                        with open(os.path.join(folder_penebusan, f"{id_unik}_{i}.jpg"), "wb") as f_save:
                            f_save.write(f.getbuffer())
                    
                    df_total.loc[idx_hutang, 'Status Denda'] = f"Menunggu ({metode})"
                    df_total.loc[idx_hutang, 'ID_Tebus'] = id_unik
                    df_total.to_excel(excel_file, index=False)
                    st.info("✅ Pengajuan dikirim!")
                    time.sleep(2)
                    st.rerun()
        else:
            if menunggu_app.empty: st.success("🎉 Anda bebas denda!")

# --- HALAMAN 3: ADMIN ---
elif menu == "Login Admin":
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔔 Verifikasi", "📑 Laporan"])
        
        with tab1:
            if not df_total.empty:
                c1, c2 = st.columns(2)
                c1.metric("Total Terlambat", len(df_total[df_total['Status'] == 'TERLAMBAT']))
                c2.metric("Total Denda", f"Rp {df_total['Denda'].sum():,}")
                st.bar_chart(df_total.groupby('Nama')['Denda'].sum())
            else: st.info("Data kosong")

        with tab2:
            pending = df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)].groupby('ID_Tebus').first()
            if pending.empty:
                st.info("Tidak ada permintaan verifikasi.")
            else:
                for id_t, row in pending.iterrows():
                    with st.expander(f"Verifikasi: {row['Nama']}"):
                        bukti_f = [f for f in os.listdir(folder_penebusan) if f.startswith(str(id_t))]
                        for img in bukti_f:
                            st.image(os.path.join(folder_penebusan, img), width=200)
                        
                        col_a, col_b = st.columns(2)
                        if col_a.button("✅ Setujui", key=f"s_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Lunas (Verified)"
                            df_total.to_excel(excel_file, index=False)
                            st.rerun()
                        if col_b.button("❌ Tolak", key=f"t_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Belum Lunas"
                            df_total.to_excel(excel_file, index=False)
                            st.rerun()

        with tab3:
            st.dataframe(df_total)
            # Tombol Download
            output = io.BytesIO()
            df_total.to_excel(output, index=False)