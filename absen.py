import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import shutil
import time
import io
from PIL import Image

# --- 1. KONFIGURASI HALAMAN & UI ---
st.set_page_config(page_title="Galva Manado", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Container Logo */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 5px;
    }

    /* Tombol Utama (Absen & Tebus) - Full Width */
    .btn-main div button {
        width: 100% !important;
        border-radius: 15px !important;
        height: 5em !important;
        font-size: 20px !important;
        font-weight: bold !important;
        background-color: #0046ad !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,70,173,0.3);
        margin-bottom: 15px;
    }

    /* Tombol Admin - Pojok Kanan Atas */
    .btn-admin div button {
        background-color: #f0f2f6 !important;
        color: #495057 !important;
        border: 1px solid #ced4da !important;
        height: 3em !important;
        border-radius: 10px !important;
    }

    /* Statistik Card */
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA (FIXED) ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

def inisialisasi_folder():
    for folder in [folder_foto, folder_penebusan]:
        if not os.path.exists(folder): os.makedirs(folder)

inisialisasi_folder()

columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "ID_Tebus"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%Y-%m-%d')
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

# --- 3. DASHBOARD UTAMA ---
if st.session_state.page == 'Dashboard':
    # Baris Atas: Logo (Kiri/Tengah) & Admin (Kanan)
    top_col1, top_col2, top_col3 = st.columns([1, 2, 1])
    with top_col2:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        try:
            st.image("images.png", width=140)
        except:
            st.subheader("🏢 Galva Manado")
        st.markdown('</div>', unsafe_allow_html=True)
    with top_col3:
        st.markdown('<div class="btn-admin">', unsafe_allow_html=True)
        if st.button("🔐 Admin"): navigasi('Admin')
        st.markdown('</div>', unsafe_allow_html=True)

    # Menu Utama (Full Width)
    st.markdown('<div class="btn-main">', unsafe_allow_html=True)
    if st.button("📝 ABSENSI KARYAWAN"): navigasi('Absensi')
    if st.button("💰 PENEBUSAN DENDA"): navigasi('Tebus')
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # --- INFORMASI REAL-TIME (DASHBOARD) ---
    st.subheader("📊 Ringkasan Kehadiran & Denda")
    if not df_total.empty:
        # Perhitungan Data
        total_terlambat = len(df_total[df_total['Status'] == 'TERLAMBAT'])
        hutang_denda = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        pemasukan_cash = df_total[df_total['Status Denda'].str.contains("Verified", na=False) & 
                                  df_total['Status Denda'].str.contains("Tunai|Transfer", na=False)]['Denda'].sum()

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Terlambat", f"{total_terlambat} Kali")
        m2.metric("Hutang Belum Bayar", f"Rp {hutang_denda:,}")
        m3.metric("Total Pemasukan Cash", f"Rp {pemasukan_cash:,}")

        # Grafik Terlambat
        df_terlambat = df_total[df_total['Status'] == 'TERLAMBAT']
        if not df_terlambat.empty:
            rekap_graph = df_terlambat.groupby('Nama').size().reset_index(name='Jumlah')
            st.bar_chart(rekap_graph.set_index('Nama'))
    else:
        st.info("Belum ada data untuk ditampilkan.")

# --- 4. HALAMAN ABSENSI (FUNGSI TETAP) ---
elif st.session_state.page == 'Absensi':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.header("📝 Absensi Karyawan")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Nama:", Karyawan_List)
    opsi = st.radio("Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Tugas Luar Kota", "Langsung ke Customer"])
    img = st.camera_input("Foto") if opsi != "Izin Terlambat" else None
    
    if st.button("KIRIM ABSEN"):
        if nama != "Pilih Nama":
            waktu_klik = datetime.now(timezone)
            is_late = (waktu_klik.hour > 8 or (waktu_klik.hour == 8 and waktu_klik.minute > 5))
            denda = 10000 if (opsi == "Hadir di Kantor" and is_late) else 0
            
            data_baru = pd.DataFrame([[waktu_klik.strftime("%Y-%m-%d"), waktu_klik.strftime("%H:%M:%S"), 
                                      nama, "TERLAMBAT" if denda > 0 else opsi.upper(), "", denda, 
                                      "Belum Lunas" if denda > 0 else "Lunas", ""]], columns=columns)
            df_total = pd.concat([df_total, data_baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False)
            
            if img:
                with open(os.path.join(folder_foto, f"{waktu_klik.strftime('%Y%m%d_%H%M%S')}_{nama}.jpg"), "wb") as f:
                    f.write(img.getbuffer())
            st.success("Absensi Terkirim!")
            time.sleep(1)
            navigasi('Dashboard')

# --- 5. HALAMAN TEBUS (FUNGSI TETAP) ---
elif st.session_state.page == 'Tebus':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.header("💰 Tebus Denda")
    # Logika Tebus Denda Anda yang sudah fix tetap sama di sini...

# --- 6. HALAMAN ADMIN (FUNGSI TETAP) ---
elif st.session_state.page == 'Admin':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        tab1, tab2, tab3, tab4 = st.tabs(["📑 Laporan", "📸 Galeri", "🔔 Verifikasi", "⚙️ Reset"])
        with tab1: st.dataframe(df_total)
        with tab2:
            files = os.listdir(folder_foto)
            cols = st.columns(4)
            for i, f in enumerate(files): cols[i%4].image(os.path.join(folder_foto, f), use_container_width=True)
        # Logika Tab 3 & 4 tetap sama sesuai kode asli Anda...