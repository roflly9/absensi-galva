import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import shutil
import time
import io
from PIL import Image

# --- 1. KONFIGURASI HALAMAN & UI ANDROID ---
st.set_page_config(page_title="Absensi Galva Manado", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Container Logo */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }

    /* Style Tombol Utama Ala Android */
    div.stButton > button {
        width: 100%;
        border-radius: 15px;
        height: 4.5em;
        font-size: 18px;
        font-weight: bold;
        background-color: #0046ad !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }

    /* Tombol Kembali */
    .btn-kembali div button {
        background-color: #ff4b4b !important;
        height: 3em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP FOLDER & DATA (FIXED) ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

def inisialisasi_folder():
    for folder in [folder_foto, folder_penebusan]:
        if not os.path.exists(folder):
            os.makedirs(folder)

inisialisasi_folder()

columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "ID_Tebus"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%Y-%m-%d')
        if "ID_Tebus" not in df_total.columns:
            df_total["ID_Tebus"] = ""
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

# State Navigasi
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

def navigasi(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 3. DASHBOARD UTAMA (LOGI & TOMBOL) ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        # Gunakan nama file logo yang Anda upload
        st.image("images.png", width=200) 
    except:
        st.title("🏢 Galva Manado")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>Sistem Absensi Digital</h3>", unsafe_allow_html=True)
    st.write("---")
    
    if st.button("📝 ABSENSI KARYAWAN"): navigasi('Absensi')
    if st.button("💰 PENEBUSAN DENDA"): navigasi('Tebus')
    st.write("---")
    if st.button("🔐 PANEL ADMIN"): navigasi('Admin')

# --- 4. HALAMAN ABSENSI (FIXED) ---
elif st.session_state.page == 'Absensi':
    st.markdown('<div class="btn-kembali">', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Dashboard"): navigasi('Dashboard')
    st.markdown('</div>', unsafe_allow_html=True)

    st.header("📝 Absensi Karyawan")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Pilih Nama Anda:", Karyawan_List)
    opsi_absen = st.radio("Tipe Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit", "Tugas Luar Kota", "Langsung ke Customer"])

    waktu_sekarang = datetime.now(timezone)
    if nama != "Pilih Nama":
        st.info(f"Jam Sekarang: **{waktu_sekarang.strftime('%H:%M:%S')}**")
        if opsi_absen == "Hadir di Kantor":
            if (waktu_sekarang.hour > 8 or (waktu_sekarang.hour == 8 and waktu_sekarang.minute > 5)):
                st.warning("⚠️ Status: TERLAMBAT (Denda Rp 10.000)")
            else: st.success("✅ Status: TEPAT WAKTU")

        alasan = st.text_input("📍 Lokasi/Alasan:") if opsi_absen != "Hadir di Kantor" else ""
        img_file = st.camera_input("Ambil foto") if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] else st.file_uploader("Upload Bukti", type=['jpg','png','jpeg'])

        if img_file or opsi_absen in ["Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit"]:
            if st.button("🚀 KIRIM ABSENSI"):
                waktu_klik = datetime.now(timezone)
                denda = 10000 if (opsi_absen == "Hadir di Kantor" and (waktu_klik.hour > 8 or (waktu_klik.hour == 8 and waktu_klik.minute > 5))) else 0
                data_baru = pd.DataFrame([[waktu_klik.strftime("%Y-%m-%d"), waktu_klik.strftime("%H:%M:%S"), nama, opsi_absen.upper() if denda == 0 else "TERLAMBAT", alasan, denda, "Belum Lunas" if denda > 0 else "Lunas", ""]], columns=columns)
                df_total = pd.concat([df_total, data_baru], ignore_index=True)
                df_total.to_excel(excel_file, index=False)
                if img_file:
                    with open(os.path.join(folder_foto, f"{waktu_klik.strftime('%Y%m%d_%H%M%S')}_{nama}.jpg"), "wb") as f:
                        f.write(img_file.getbuffer())
                st.success("✅ Absensi Berhasil!")
                time.sleep(2)
                navigasi('Dashboard')

# --- 5. HALAMAN TEBUS DENDA (FIXED) ---
elif st.session_state.page == 'Tebus':
    st.markdown('<div class="btn-kembali">', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Dashboard"): navigasi('Dashboard')
    st.markdown('</div>', unsafe_allow_html=True)

    st.header("💰 Penebusan Denda")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama_tebus = st.selectbox("Pilih Nama:", Karyawan_List)
    if nama_tebus != "Pilih Nama":
        idx_hutang = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_hutang = df_total.loc[idx_hutang, 'Denda'].sum()
        if total_hutang > 0:
            st.error(f"Total Tunggakan: Rp {total_hutang:,}")
            metode = st.radio("Metode:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            f_seb = st.file_uploader("Foto Bukti/Sebelum", type=['jpg','png','jpeg'], key="f1")
            f_ses = st.file_uploader("Foto Sesudah (Jika Bersih Kantor)", type=['jpg','png','jpeg'], key="f2") if metode == "Membersihkan Kantor" else None
            
            if st.button("Ajukan Penebusan"):
                id_unik = f"{nama_tebus}_{datetime.now(timezone).strftime('%y%m%d%H%M%S')}"
                df_total.loc[idx_hutang, 'Status Denda'] = f"Menunggu ({metode})"
                df_total.loc[idx_hutang, 'ID_Tebus'] = id_unik
                df_total.to_excel(excel_file, index=False)
                st.success("✅ Terkirim ke Admin!")
                time.sleep(2)
                navigasi('Dashboard')
        else: st.success("Bebas Denda.")

# --- 6. HALAMAN ADMIN (FIXED & LENGKAP) ---
elif st.session_state.page == 'Admin':
    st.markdown('<div class="btn-kembali">', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Dashboard"): navigasi('Dashboard')
    st.markdown('</div>', unsafe_allow_html=True)

    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        t1, t2, t3, t4, t5 = st.tabs(["📊 Statistik", "🔔 Verifikasi", "📑 Laporan", "📸 Galeri Foto", "⚙️ Reset"])
        
        with t1: # Statistik
            c1, c2, c3 = st.columns(3)
            c1.metric("Terlambat", len(df_total[df_total['Status'] == 'TERLAMBAT']))
            c2.metric("Belum Lunas", f"Rp {df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum():,}")
            c3.metric("Menunggu", len(df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)]))
            st.bar_chart(df_total.groupby('Nama')['Denda'].sum())

        with t2: # Verifikasi
            pending = df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)].groupby('ID_Tebus').first()
            for id_t, row in pending.iterrows():
                with st.expander(f"Verifikasi: {row['Nama']}"):
                    if st.button("Setujui", key=f"s_{id_t}"):
                        df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Lunas (Verified)"
                        df_total.to_excel(excel_file, index=False)
                        st.rerun()

        with t3: # Laporan Excel
            st.dataframe(df_total)
            output = io.BytesIO()
            df_total.to_excel(output, index=False)
            st.download_button("📥 Download Excel", output.getvalue(), "Laporan_Galva.xlsx")

        with t4: # Galeri Foto
            files = sorted([f for f in os.listdir(folder_foto) if f.endswith('.jpg')], reverse=True)
            cols = st.columns(4)
            for i, f in enumerate(files):
                cols[i % 4].image(os.path.join(folder_foto, f), caption=f, use_container_width=True)

        with t5: # Reset
            if st.button("🚨 RESET TOTAL SEMUA DATA"):
                if os.path.exists(excel_file): os.remove(excel_file)
                for d in [folder_foto, folder_penebusan]:
                    if os.path.exists(d): shutil.rmtree(d)
                inisialisasi_folder()
                st.rerun()