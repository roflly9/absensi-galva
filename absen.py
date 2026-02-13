import streamlit as st
from datetime import datetime, timedelta
import os
import pandas as pd
import pytz 
import time

# --- 1. KONFIGURASI HALAMAN & UI ---
st.set_page_config(page_title="Absensi Galva Manado", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        max-width: 100% !important;
        padding: 0.5rem !important;
        margin: auto;
        overflow-x: hidden;
    }

    .stApp {
        background-color: #f8f9fa;
    }

    /* Header Banner */
    .app-header {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        padding: 25px 10px;
        color: white;
        text-align: center;
        font-weight: 800;
        font-size: 18px;
        border-radius: 0 0 25px 25px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .welcome-box {
        background-color: #d32f2f;
        color: white;
        padding: 5px 15px;
        font-size: 10px;
        text-align: center;
        width: fit-content;
        margin: -30px auto 15px auto;
        border-radius: 10px;
        border: 2px solid white;
        font-weight: bold;
        position: relative;
        z-index: 10;
    }

    /* Dashboard Buttons */
    div.stButton > button {
        height: 65px !important; 
        width: 100% !important;
        border-radius: 15px !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
        margin-bottom: 8px !important;
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%) !important;
    }

    /* Section Titles */
    .section-title {
        font-size: 14px;
        font-weight: 800;
        color: #0d47a1;
        margin: 25px 0 10px 10px;
        display: flex;
        align-items: center;
        text-transform: uppercase;
    }
    .section-title::before {
        content: "";
        width: 5px;
        height: 18px;
        background: #d32f2f;
        margin-right: 10px;
        border-radius: 3px;
    }

    /* Kotak Status */
    .status-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #0d47a1;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin: 15px 0;
    }
    .status-card.terlambat { border-left: 10px solid #d32f2f; }
    .status-card.tunggu { border-left: 10px solid #ffa000; }

    div[data-testid="stMetric"] {
        background: white !important;
        padding: 15px !important;
        border-radius: 18px !important;
        border: 1px solid #e3f2fd !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA & FILE ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda"]
karyawan_list = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.date
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

if 'page' not in st.session_state: st.session_state.page = 'Dashboard'

def navigasi(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 3. LOGIKA HALAMAN ---

# --- A. DASHBOARD (FIXED) ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">PRESENSI & DENDA</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-title">Aktivitas Karyawan</p>', unsafe_allow_html=True)
    if st.button("📝 &nbsp; MULAI ABSENSI"): navigasi('Absensi')
    if st.button("💰 &nbsp; TEBUS DENDA"): navigasi('Tebus')

    st.markdown('<p class="section-title">Menu Pengelola</p>', unsafe_allow_html=True)
    if st.button("🔐 &nbsp; ADMIN PANEL"): navigasi('Admin')

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
    else:
        st.info("Belum ada data aktivitas.")

# --- B. FORM ABSENSI (FIXED) ---
elif st.session_state.page == 'Absensi':
    st.markdown('<div class="app-header">📝 FORM ABSENSI</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Menu"): navigasi('Dashboard')
    
    nama = st.selectbox("Nama Karyawan:", karyawan_list)
    opsi = st.radio("Opsi Kehadiran:", ["Hadir di kantor", "Izin terlambat", "Tidak masuk kantor Cuti/Sakit", "Tugas Luar kota", "Langsung ke customer"], index=0)
    
    waktu_skrg = datetime.now(timezone)
    jam_skrg = waktu_skrg.time()
    batas_absen = datetime.strptime("08:05:00", "%H:%M:%S").time()
    
    is_telat = (opsi == "Hadir di kantor" and jam_skrg > batas_absen)
    is_izin_terlambat = (opsi == "Izin terlambat")
    is_cuti_sakit = (opsi == "Tidak masuk kantor Cuti/Sakit")
    is_tugas_luar = (opsi == "Tugas Luar kota")
    is_ke_customer = (opsi == "Langsung ke customer")
    
    if is_telat: card_class, st_text, dn_text, icon = "status-card terlambat", "TERLAMBAT", "Rp 10.000", "⚠️"
    elif is_izin_terlambat: card_class, st_text, dn_text, icon = "status-card izin", "IJIN TERLAMBAT", "Rp 0", "ℹ️"
    elif is_cuti_sakit: card_class, st_text, dn_text, icon = "status-card izin", "CUTI / SAKIT", "Rp 0", "ℹ️"
    elif is_tugas_luar: card_class, st_text, dn_text, icon = "status-card dinas", "DINAS LUAR KOTA", "Rp 0", "✈️"
    elif is_ke_customer: card_class, st_text, dn_text, icon = "status-card customer", "LANGSUNG KE CUSTOMER", "Rp 0", "🚗"
    else: card_class, st_text, dn_text, icon = "status-card", "HADIR TEPAT WAKTU", "Rp 0", "✅"

    st.markdown(f"""<div class="{card_class}"><h2 style="margin:5px 0;">{waktu_skrg.strftime('%H:%M:%S')} WITA</h2><span>Status: <b>{icon} {st_text}</b></span> | <b>Denda: {dn_text}</b></div>""", unsafe_allow_html=True)

    alasan_val, foto_bukti, img_selfie, lokasi_ket = "", None, None, ""

    if is_izin_terlambat or is_cuti_sakit:
        alasan_val = st.text_area("Masukkan Alasan:")
        foto_bukti = st.file_uploader("Upload Foto Bukti:", type=['jpg', 'jpeg', 'png', 'pdf'])
    elif is_tugas_luar:
        lokasi_ket = st.text_area("Sedang dinas di mana?", placeholder="Contoh: Dinas di Tondano...")
    elif is_ke_customer:
        lokasi_ket = st.text_area("Ke customer mana hari ini?", placeholder="Contoh: Ke Bank SulutGo...")
        img_selfie = st.camera_input("Ambil Foto Selfie di Lokasi Customer")
    else:
        img_selfie = st.camera_input("Ambil Foto Selfie Kehadiran")

    if st.button("🚀 KIRIM ABSENSI"):
        if nama == "Pilih Nama": st.error("Gagal! Pilih Nama Anda.")
        else:
            denda_final = 10000 if is_telat else 0
            alasan_simpan = f"Dinas: {lokasi_ket}" if is_tugas_luar else (f"Customer: {lokasi_ket}" if is_ke_customer else (alasan_val if (is_izin_terlambat or is_cuti_sakit) else opsi))
            data_baru = pd.DataFrame([[waktu_skrg.date(), waktu_skrg.strftime("%H:%M:%S"), nama, st_text, alasan_simpan, denda_final, "Belum Lunas" if denda_final > 0 else "Lunas"]], columns=columns)
            df_total = pd.concat([df_total, data_baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False)
            st.balloons(); st.success(f"✅ Terkirim! Status: {st_text}"); time.sleep(2); navigasi('Dashboard')

# --- C. TEBUS DENDA (UPDATE METODE BERSIH-BERSIH: CUKUP UPLOAD FOTO) ---
elif st.session_state.page == 'Tebus':
    st.markdown('<div class="app-header">💰 MENU TEBUS DENDA</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Dashboard"): navigasi('Dashboard')
    
    st.markdown('<p class="section-title">Pilih Nama untuk Cek Denda</p>', unsafe_allow_html=True)
    user_pilih = st.selectbox("Nama Karyawan:", karyawan_list)
    
    if user_pilih != "Pilih Nama":
        user_df = df_total[(df_total['Nama'] == user_pilih) & (df_total['Status Denda'] == 'Belum Lunas')]
        total_denda_user = user_df['Denda'].sum()
        
        if total_denda_user > 0:
            st.markdown(f"""
                <div class="status-card terlambat">
                    <p style="margin:0; font-weight:bold; color:gray;">TOTAL TUNGGAKAN</p>
                    <h2 style="color:#d32f2f; margin:5px 0;">Rp {total_denda_user:,}</h2>
                </div>
            """, unsafe_allow_html=True)
            
            metode = st.radio("Pilih Metode Penebusan:", ["Bayar Cash/Transfer", "Membersihkan Kantor"])
            
            nominal_tebus = st.number_input(f"Jumlah denda yang ingin ditebus (Min. 10.000)", 
                                           min_value=10000, 
                                           max_value=int(total_denda_user), 
                                           step=10000)
            
            bukti_valid = False
            if metode == "Bayar Cash/Transfer":
                st.info("Harap upload foto uang cash atau screenshot bukti transfer.")
                f_bukti = st.file_uploader("Upload Bukti Pembayaran:", type=['jpg','png','jpeg'], key="tf")
                if f_bukti: bukti_valid = True
            else:
                st.warning("Harap upload foto area kantor sebelum dan sesudah dibersihkan.")
                col1, col2 = st.columns(2)
                with col1: f_before = st.file_uploader("📸 Upload Foto SEBELUM", type=['jpg','png','jpeg'], key="bfr")
                with col2: f_after = st.file_uploader("📸 Upload Foto SESUDAH", type=['jpg','png','jpeg'], key="aft")
                if f_before and f_after: bukti_valid = True

            if st.button("✅ KONFIRMASI PENEBUSAN"):
                if not bukti_valid:
                    st.error("Gagal! Mohon lengkapi seluruh foto/bukti yang diminta.")
                else:
                    indices = df_total[(df_total['Nama'] == user_pilih) & (df_total['Status Denda'] == 'Belum Lunas')].index
                    bayar_temp = 0
                    for idx in indices:
                        if bayar_temp < nominal_tebus:
                            df_total.at[idx, 'Status Denda'] = 'Menunggu Persetujuan'
                            bayar_temp += df_total.at[idx, 'Denda']
                    
                    df_total.to_excel(excel_file, index=False)
                    st.success("Berhasil! Menunggu konfirmasi Admin untuk melunaskan status denda Anda.")
                    time.sleep(3); navigasi('Dashboard')
        else:
            st.success(f"Bebas Denda! {user_pilih} tidak memiliki tunggakan.")

# --- D. ADMIN PANEL (ACC MENU) ---
elif st.session_state.page == 'Admin':
    st.markdown('<div class="app-header">🔐 ADMIN PANEL</div>', unsafe_allow_html=True)
    if st.button("⬅️ Dashboard"): navigasi('Dashboard')
    pswd = st.text_input("Password Admin:", type="password")
    
    if pswd == "galva123":
        tab_rekap, tab_acc = st.tabs(["📊 SEMUA DATA", "✅ ACC PEMBAYARAN"])
        
        with tab_rekap:
            st.dataframe(df_total, use_container_width=True)
            st.download_button("📊 Download Excel", data=open(excel_file, "rb"), file_name="rekap_absensi.xlsx")
            
        with tab_acc:
            df_tunggu = df_total[df_total['Status Denda'] == 'Menunggu Persetujuan']
            if not df_tunggu.empty:
                st.warning(f"Terdapat {len(df_tunggu)} baris denda menunggu persetujuan.")
                st.dataframe(df_tunggu[['Tanggal', 'Nama', 'Status', 'Denda']], use_container_width=True)
                
                list_nama_tunggu = df_tunggu['Nama'].unique()
                acc_nama = st.selectbox("Pilih Nama untuk di-ACC:", list_nama_tunggu)
                
                if st.button(f"Sahkan Pembayaran {acc_nama}"):
                    df_total.loc[(df_total['Nama'] == acc_nama) & (df_total['Status Denda'] == 'Menunggu Persetujuan'), 'Status Denda'] = 'Lunas'
                    df_total.to_excel(excel_file, index=False)
                    st.success(f"Pembayaran {acc_nama} telah disahkan (Lunas).")
                    time.sleep(1); st.rerun()
            else:
                st.info("Tidak ada pengajuan penebusan denda saat ini.")