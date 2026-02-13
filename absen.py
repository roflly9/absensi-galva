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
st.set_page_config(page_title="Absensi Galva Manado", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Latar Belakang Putih Bersih */
    .stApp {
        background-color: #ffffff;
    }

    /* Header Banner Melengkung Biru */
    .header-banner {
        background: linear-gradient(135deg, #0046ad 0%, #00d4ff 100%);
        padding: 30px 20px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 8px 15px rgba(0,70,173,0.1);
    }
    .header-banner h1 {
        margin: 5px 0;
        font-size: 26px;
        font-weight: 800;
        color: white !important;
    }
    .header-banner p {
        font-size: 13px;
        opacity: 0.9;
        margin-bottom: 0;
    }

    /* Judul Seksi */
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #333;
        margin-bottom: 15px;
        padding-left: 10px;
        border-left: 5px solid #0046ad;
    }

    /* FORCE MOBILE GRID (Penting agar tidak menumpuk di HP) */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 calc(50% - 10px) !important;
        min-width: 45% !important;
    }

    /* Styling Tombol Menu Kotak Putih */
    div.stButton > button {
        background-color: #f8f9fa !important;
        color: #333 !important;
        border: 1px solid #eee !important;
        border-radius: 20px !important;
        height: 140px !important;
        width: 100% !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    div.stButton > button:hover {
        border: 1px solid #0046ad !important;
        color: #0046ad !important;
        background-color: #ffffff !important;
        transform: translateY(-2px);
    }

    /* Metric Box */
    [data-testid="stMetric"] {
        background-color: #fdfdfd !important;
        padding: 15px !important;
        border-radius: 15px !important;
        border: 1px solid #f0f0f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA (FIX) ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

def inisialisasi_folder():
    for f in [folder_foto, folder_penebusan]:
        if not os.path.exists(f): os.makedirs(f)

inisialisasi_folder()

columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "ID_Tebus"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%Y-%m-%d')
        if "ID_Tebus" not in df_total.columns: df_total["ID_Tebus"] = ""
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

if 'page' not in st.session_state: st.session_state.page = 'Dashboard'
def navigasi(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 3. DASHBOARD UTAMA (MOBILE OPTIMIZED) ---
if st.session_state.page == 'Dashboard':
    # Header Banner
    st.markdown(f"""
        <div class="header-banner">
            <p>Selamat Datang,</p>
            <h1>🏢 MANADO</h1>
            <p>Silahkan pilih menu di bawah untuk absensi atau penebusan denda.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-title">Menu Utama Karyawan</p>', unsafe_allow_html=True)

    # Baris 1: Absensi & Tebus (Bersebelahan)
    col_absen, col_tebus = st.columns(2)
    with col_absen:
        if st.button("📝\n\nMULAI\nABSENSI"): navigasi('Absensi')
    with col_tebus:
        if st.button("💰\n\nTEBUS\nDENDA"): navigasi('Tebus')

    # Baris 2: Admin Panel (Tengah Bawah)
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    # Spacer digunakan agar tombol Admin berada di tengah baris kedua
    _, col_admin, _ = st.columns([0.5, 2, 0.5])
    with col_admin:
        if st.button("🔐\n\nADMIN\nPANEL"): navigasi('Admin')

    # Ringkasan Statistik
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">📊 Statistik Saya</p>', unsafe_allow_html=True)
    
    if not df_total.empty:
        total_terlambat = len(df_total[df_total['Status'] == 'TERLAMBAT'])
        hutang = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("Terlambat", f"{total_terlambat}x")
        m_col2.metric("Denda", f"Rp {hutang:,}")
    else: 
        st.info("Belum ada data tercatat.")

# --- 4. HALAMAN ABSENSI (FIX) ---
elif st.session_state.page == 'Absensi':
    if st.button("⬅️ Kembali ke Beranda"): navigasi('Dashboard')
    st.subheader("📝 Form Absensi")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Pilih Nama:", Karyawan_List)
    opsi = st.radio("Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Tugas Luar", "Cuti/Sakit"])
    
    waktu_skrg = datetime.now(timezone)
    if nama != "Pilih Nama":
        st.info(f"Jam: **{waktu_skrg.strftime('%H:%M:%S')} WITA**")
        img = st.camera_input("Ambil Selfie")
        if st.button("🚀 KIRIM DATA"):
            if img:
                is_late = (waktu_skrg.hour > 8 or (waktu_skrg.hour == 8 and waktu_skrg.minute > 5))
                denda = 10000 if (opsi == "Hadir di Kantor" and is_late) else 0
                data_baru = pd.DataFrame([[waktu_skrg.strftime("%Y-%m-%d"), waktu_skrg.strftime("%H:%M:%S"), nama, "TERLAMBAT" if denda > 0 else opsi.upper(), "", denda, "Belum Lunas" if denda > 0 else "Lunas", ""]], columns=columns)
                df_total = pd.concat([df_total, data_baru], ignore_index=True)
                df_total.to_excel(excel_file, index=False)
                st.success("Absensi Berhasil!"); time.sleep(1); navigasi('Dashboard')
            else:
                st.error("Foto Selfie Wajib!")

# --- 5. HALAMAN TEBUS (FIX) ---
elif st.session_state.page == 'Tebus':
    if st.button("⬅️ Kembali ke Beranda"): navigasi('Dashboard')
    st.subheader("💰 Tebus Denda")
    nama_tebus = st.selectbox("Pilih Nama:", ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"])
    if nama_tebus != "Pilih Nama":
        idx_h = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_h = df_total.loc[idx_h, 'Denda'].sum()
        if total_h > 0:
            st.error(f"Total Tunggakan: Rp {total_h:,}")
            metode = st.radio("Metode:", ["Bayar Tunai", "Membersihkan Kantor"])
            bukti = st.file_uploader("Upload Bukti", type=['jpg','png','jpeg'])
            if st.button("🚀 AJUKAN"):
                if bukti:
                    id_u = f"{nama_tebus}_{datetime.now(timezone).strftime('%y%m%d%H%M%S')}"
                    df_total.loc[idx_h, 'Status Denda'] = "Menunggu Approval"
                    df_total.loc[idx_h, 'ID_Tebus'] = id_u
                    df_total.to_excel(excel_file, index=False)
                    st.success("Pengajuan Terkirim!"); time.sleep(1); navigasi('Dashboard')
                else: st.warning("Lampirkan bukti!")
        else: st.success("Anda tidak memiliki denda.")

# --- 6. HALAMAN ADMIN (FIX) ---
elif st.session_state.page == 'Admin':
    if st.button("⬅️ Kembali ke Beranda"): navigasi('Dashboard')
    pw = st.text_input("Sandi Admin:", type="password")
    if pw == "galva123":
        t1, t2, t3 = st.tabs(["📊 Laporan", "🔔 Verifikasi", "⚙️ Reset"])
        with t1:
            st.dataframe(df_total)
        with t2:
            st.info("Fitur verifikasi denda.")
        with t3:
            if st.button("Hapus Semua Data"):
                if os.path.exists(excel_file): os.remove(excel_file)
                st.rerun()