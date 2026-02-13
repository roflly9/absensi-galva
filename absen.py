import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import time

# --- PENGAMAN: Cek apakah plotly terinstal ---
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# --- 1. KONFIGURASI HALAMAN & UI ---
st.set_page_config(page_title="Absensi Galva Manado", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { max-width: 100% !important; padding: 0.5rem !important; margin: auto; overflow-x: hidden; }
    .stApp { background-color: #f8f9fa; }
    .app-header {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        padding: 25px 10px; color: white; text-align: center; font-weight: 800; font-size: 18px;
        border-radius: 0 0 25px 25px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .welcome-box {
        background-color: #d32f2f; color: white; padding: 5px 15px; font-size: 10px;
        text-align: center; width: fit-content; margin: -30px auto 15px auto;
        border-radius: 10px; border: 2px solid white; font-weight: bold; position: relative; z-index: 10;
    }
    div.stButton > button {
        height: 65px !important; width: 100% !important; border-radius: 15px !important;
        border: none !important; color: white !important; font-weight: 700 !important;
        font-size: 15px !important; display: flex !important; align-items: center !important;
        justify-content: center !important; box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
        margin-bottom: 8px !important; background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%) !important;
    }
    .stTextInput > div > div > input { border: 2px solid #000000 !important; border-radius: 10px !important; }
    .section-title { font-size: 14px; font-weight: 800; color: #0d47a1; margin: 25px 0 10px 10px; display: flex; align-items: center; text-transform: uppercase; }
    .section-title::before { content: ""; width: 5px; height: 18px; background: #d32f2f; margin-right: 10px; border-radius: 3px; }
    .status-card { background: white; padding: 20px; border-radius: 15px; border-left: 10px solid #0d47a1; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin: 15px 0; }
    .status-card.terlambat { border-left: 10px solid #d32f2f; }
    div[data-testid="stMetric"] { background: white !important; padding: 15px !important; border-radius: 18px !important; border: 1px solid #e3f2fd !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA & FILE ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "Foto_Absen", "Bukti_Bayar"]
karyawan_list = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.date
        for col in columns:
            if col not in df_total.columns:
                df_total[col] = None
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

if 'page' not in st.session_state: st.session_state.page = 'Dashboard'
if 'admin_authenticated' not in st.session_state: st.session_state.admin_authenticated = False

def navigasi(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 3. LOGIKA HALAMAN ---

if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">PRESENSI & DENDA</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Aktivitas Karyawan</p>', unsafe_allow_html=True)
    if st.button("📝 &nbsp; MULAI ABSENSI"): navigasi('Absensi')
    if st.button("💰 &nbsp; TEBUS DENDA"): navigasi('Tebus')
    st.markdown('<p class="section-title">Menu Pengelola</p>', unsafe_allow_html=True)
    if st.button("🔐 &nbsp; ADMIN PANEL"): 
        st.session_state.admin_authenticated = False 
        navigasi('Admin')
    st.markdown('<p class="section-title">Status & Ringkasan Hari Ini</p>', unsafe_allow_html=True)
    if not df_total.empty:
        tgl_skrg = datetime.now(timezone).date()
        df_hari_ini = df_total[df_total['Tanggal'] == tgl_skrg]
        total_telat = len(df_hari_ini[df_hari_ini['Status'] == 'TERLAMBAT'])
        tunggakan = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        total_setoran = df_total[df_total['Status Denda'] == 'Lunas']['Denda'].sum()
        c1, c2 = st.columns(2)
        c1.metric("Telat Hari Ini", f"{total_telat}x")
        c2.metric("Total Setoran", f"Rp {total_setoran:,}")
        st.metric("Tunggakan Belum Bayar", f"Rp {tunggakan:,}", delta_color="inverse")
    else: st.info("Belum ada data aktivitas.")

elif st.session_state.page == 'Absensi':
    st.markdown('<div class="app-header">📝 FORM ABSENSI</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Menu"): navigasi('Dashboard')
    nama = st.selectbox("Nama Karyawan:", karyawan_list)
    opsi = st.radio("Opsi Kehadiran:", ["Hadir di kantor", "Izin terlambat", "Tidak masuk kantor Cuti/Sakit", "Tugas Luar kota", "Langsung ke customer"], index=0)
    waktu_skrg = datetime.now(timezone)
    batas_absen = datetime.strptime("08:05:00", "%H:%M:%S").time()
    is_telat = (opsi == "Hadir di kantor" and waktu_skrg.time() > batas_absen)
    st_text = "TERLAMBAT" if is_telat else opsi.upper()
    denda_val = 10000 if is_telat else 0
    st.markdown(f'<div class="status-card {"terlambat" if is_telat else ""}">Status: <b>{st_text}</b> | Denda: <b>Rp {denda_val:,}</b></div>', unsafe_allow_html=True)
    img_selfie = st.camera_input("Ambil Foto Selfie")
    if st.button("🚀 KIRIM ABSENSI"):
        if nama == "Pilih Nama" or img_selfie is None: st.error("Nama dan Foto wajib diisi!")
        else:
            data_baru = pd.DataFrame([[waktu_skrg.date(), waktu_skrg.strftime("%H:%M:%S"), nama, st_text, opsi, denda_val, "Belum Lunas" if denda_val > 0 else "Lunas", img_selfie.getvalue(), None]], columns=columns)
            df_total = pd.concat([df_total, data_baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False)
            st.success("Terkirim!"); time.sleep(1); navigasi('Dashboard')

elif st.session_state.page == 'Tebus':
    st.markdown('<div class="app-header">💰 MENU TEBUS DENDA</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Dashboard"): navigasi('Dashboard')
    user_pilih = st.selectbox("Nama Karyawan:", karyawan_list)
    if user_pilih != "Pilih Nama":
        user_df = df_total[(df_total['Nama'] == user_pilih) & (df_total['Status Denda'] == 'Belum Lunas')]
        total_denda = user_df['Denda'].sum()
        if total_denda > 0:
            st.warning(f"Total Denda: Rp {total_denda:,}")
            f_bukti = st.file_uploader("Upload Bukti Pembayaran", type=['jpg','png','jpeg'])
            if st.button("✅ KONFIRMASI"):
                if f_bukti:
                    mask = (df_total['Nama'] == user_pilih) & (df_total['Status Denda'] == 'Belum Lunas')
                    df_total.loc[mask, 'Status Denda'] = 'Menunggu Persetujuan'
                    df_total.loc[mask, 'Bukti_Bayar'] = f_bukti.getvalue()
                    df_total.to_excel(excel_file, index=False)
                    st.success("Menunggu konfirmasi Admin."); time.sleep(1); navigasi('Dashboard')
                else: st.error("Lampirkan foto bukti!")
        else: st.success("Bebas Denda.")

elif st.session_state.page == 'Admin':
    st.markdown('<div class="app-header">🔐 ADMIN PANEL</div>', unsafe_allow_html=True)
    if st.button("⬅️ Dashboard"): navigasi('Dashboard')
    if not st.session_state.admin_authenticated:
        pswd = st.text_input("Password:", type="password")
        if st.button("🔓 MASUK"):
            if pswd == "galva123": st.session_state.admin_authenticated = True; st.rerun()
            else: st.error("Salah!")
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 DASHBOARD", "📊 REKAPAN", "✅ ACC BAYAR", "📸 FOTO ABSEN", "⚙️ RESET"])
        
        with tab1:
            if not df_total.empty and HAS_PLOTLY:
                df_dash = df_total.copy()
                df_dash['Tanggal'] = pd.to_datetime(df_dash['Tanggal'])
                df_telat = df_dash[df_dash['Status'] == 'TERLAMBAT']
                if not df_telat.empty:
                    grafik_data = df_telat.groupby(df_telat['Tanggal'].dt.date).size().reset_index(name='Jumlah')
                    fig = px.bar(grafik_data, x='Tanggal', y='Jumlah', title='Tren Terlambat', color_discrete_sequence=['#d32f2f'])
                    st.plotly_chart(fig, use_container_width=True)
                else: st.info("Tidak ada data telat.")
            elif not HAS_PLOTLY: st.warning("Sedang menginstal library grafik... Mohon tunggu atau Reboot aplikasi.")

        with tab2:
            df_view = df_total.drop(columns=['Foto_Absen', 'Bukti_Bayar'], errors='ignore')
            st.dataframe(df_view, use_container_width=True)

        with tab3:
            df_tunggu = df_total[df_total['Status Denda'] == 'Menunggu Persetujuan']
            if not df_tunggu.empty:
                for nama_u in df_tunggu['Nama'].unique():
                    with st.expander(f"Bukti: {nama_u}"):
                        row = df_tunggu[df_tunggu['Nama'] == nama_u].iloc[0]
                        if row['Bukti_Bayar']: st.image(row['Bukti_Bayar'], width=300)
                        col1, col2 = st.columns(2)
                        if col1.button(f"Sahkan {nama_u}"):
                            df_total.loc[(df_total['Nama'] == nama_u) & (df_total['Status Denda'] == 'Menunggu Persetujuan'), 'Status Denda'] = 'Lunas'
                            df_total.to_excel(excel_file, index=False); st.rerun()
                        if col2.button(f"Tolak {nama_u}"):
                            df_total.loc[(df_total['Nama'] == nama_u) & (df_total['Status Denda'] == 'Menunggu Persetujuan'), 'Status Denda'] = 'Belum Lunas'
                            df_total.to_excel(excel_file, index=False); st.rerun()
            else: st.info("Kosong.")

        with tab4:
            if not df_total.empty:
                for i in range(0, len(df_total), 4):
                    cols = st.columns(4)
                    for j, (idx, item) in enumerate(df_total.iloc[i:i+4].iterrows()):
                        if item.get('Foto_Absen'):
                            with cols[j]: st.image(item['Foto_Absen'], caption=f"{item['Nama']}", use_container_width=True)

        with tab5:
            if st.button("🔥 RESET SEMUA DATA"):
                if os.path.exists(excel_file): os.remove(excel_file)
                st.rerun()