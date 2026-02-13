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

    /* Kotak Status Terpadu */
    .status-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #0d47a1;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin: 15px 0;
    }
    .status-card.terlambat { border-left: 10px solid #d32f2f; }
    .status-card.izin { border-left: 10px solid #ffa000; }
    .status-card.dinas { border-left: 10px solid #1976d2; }

    /* --- STYLING INPUT WAJIB --- */
    /* Merah untuk Izin/Cuti */
    .wajib-isi textarea {
        border: 2px solid #d32f2f !important;
        border-radius: 10px !important;
    }
    /* Biru untuk Dinas */
    .dinas-isi textarea {
        border: 2px solid #1976d2 !important;
        border-radius: 10px !important;
    }

    div[data-testid="stFileUploader"] {
        border: 2px dashed #d32f2f !important;
        padding: 10px !important;
        border-radius: 10px !important;
        background-color: #fff5f5 !important;
    }

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

# --- A. DASHBOARD ---
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

# --- B. FORM ABSENSI ---
elif st.session_state.page == 'Absensi':
    st.markdown('<div class="app-header">📝 FORM ABSENSI</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Menu"): navigasi('Dashboard')
    
    karyawan = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Nama Karyawan:", karyawan)
    
    opsi = st.radio("Opsi Kehadiran:", [
        "Hadir di kantor", 
        "Izin terlambat", 
        "Tidak masuk kantor Cuti/Sakit", 
        "Tugas Luar kota", 
        "Langsung ke customer"
    ], index=0)
    
    waktu_skrg = datetime.now(timezone)
    jam_skrg = waktu_skrg.time()
    batas_absen = datetime.strptime("08:05:00", "%H:%M:%S").time()
    
    is_telat = (opsi == "Hadir di kantor" and jam_skrg > batas_absen)
    is_izin_terlambat = (opsi == "Izin terlambat")
    is_cuti_sakit = (opsi == "Tidak masuk kantor Cuti/Sakit")
    is_tugas_luar = (opsi == "Tugas Luar kota")
    
    # LOGIKA STATUS UNTUK DISPLAY
    if is_telat:
        card_class, st_text, dn_text, icon = "status-card terlambat", "TERLAMBAT", "Rp 10.000", "⚠️"
    elif is_izin_terlambat:
        card_class, st_text, dn_text, icon = "status-card izin", "IJIN TERLAMBAT", "Rp 0", "ℹ️"
    elif is_cuti_sakit:
        card_class, st_text, dn_text, icon = "status-card izin", "CUTI / SAKIT", "Rp 0", "ℹ️"
    elif is_tugas_luar:
        card_class, st_text, dn_text, icon = "status-card dinas", "DINAS LUAR KOTA", "Rp 0", "✈️"
    else:
        card_class, st_text, dn_text, icon = "status-card", "HADIR TEPAT WAKTU", "Rp 0", "✅"

    st.markdown(f"""
        <div class="{card_class}">
            <p style="margin:0; font-size:11px; color:#666; font-weight:bold;">SISTEM ABSENSI OTOMATIS</p>
            <h2 style="margin:5px 0; color:#0d47a1;">{waktu_skrg.strftime('%H:%M:%S')} <span style="font-size:14px;">WITA</span></h2>
            <div style="display:flex; justify-content:space-between; margin-top:10px; padding-top:10px; border-top:1px solid #eee;">
                <span>Status: <b>{icon} {st_text}</b></span>
                <span style="font-weight:bold;">Denda: {dn_text}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    alasan_val = ""
    foto_bukti = None
    img_selfie = None
    lokasi_dinas = ""

    # KONDISI INPUT BERDASARKAN OPSI
    if is_izin_terlambat or is_cuti_sakit:
        st.markdown('<div class="wajib-isi">', unsafe_allow_html=True)
        st.error("WAJIB: Isi alasan dan upload foto bukti (Kotak Merah).")
        alasan_val = st.text_area("Alasan Ijin/Cuti:")
        foto_bukti = st.file_uploader("Upload Foto Bukti:", type=['jpg', 'jpeg', 'png', 'pdf'])
        st.markdown('</div>', unsafe_allow_html=True)
        
    elif is_tugas_luar:
        st.markdown('<div class="dinas-isi">', unsafe_allow_html=True)
        st.info("KETERANGAN: Sebutkan lokasi penugasan Anda (Kotak Biru).")
        lokasi_dinas = st.text_area("Sedang dinas di mana?", placeholder="Contoh: Dinas di Jakarta Utara...")
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Hadir di kantor atau Langsung ke customer
        img_selfie = st.camera_input("Ambil Foto Selfie Kehadiran")

    if st.button("🚀 KIRIM ABSENSI"):
        if nama == "Pilih Nama":
            st.error("Gagal! Pilih Nama terlebih dahulu.")
        elif (is_izin_terlambat or is_cuti_sakit) and (not alasan_val or not foto_bukti):
            st.error("Gagal! Alasan dan Foto Bukti tidak boleh kosong.")
        elif is_tugas_luar and not lokasi_dinas:
            st.error("Gagal! Keterangan lokasi dinas wajib diisi.")
        elif (not is_izin_terlambat and not is_cuti_sakit and not is_tugas_luar) and not img_selfie:
            st.error("Gagal! Foto selfie wajib diambil.")
        else:
            denda_final = 10000 if is_telat else 0
            status_final = st_text
            
            # Formating alasan untuk database
            if is_tugas_luar:
                alasan_simpan = f"Lokasi: {lokasi_dinas}"
            elif is_izin_terlambat or is_cuti_sakit:
                alasan_simpan = alasan_val
            else:
                alasan_simpan = opsi
            
            data_baru = pd.DataFrame([[
                waktu_skrg.date(), 
                waktu_skrg.strftime("%H:%M:%S"),
                nama, 
                status_final, 
                alasan_simpan, 
                denda_final, 
                "Belum Lunas" if denda_final > 0 else "Lunas"
            ]], columns=columns)
            
            df_total = pd.concat([df_total, data_baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False)
            
            st.balloons()
            st.success(f"✅ Berhasil! Absensi {nama} sebagai {status_final} telah terkirim.")
            time.sleep(2)
            navigasi('Dashboard')

# --- C. TEBUS DENDA ---
elif st.session_state.page == 'Tebus':
    st.markdown('<div class="app-header">💰 TEBUS DENDA</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Dashboard"): navigasi('Dashboard')
    if not df_total.empty:
        df_tunggak = df_total[df_total['Status Denda'] == 'Belum Lunas']
        if not df_tunggak.empty:
            st.warning(f"Total tunggakan belum dibayar: Rp {df_tunggak['Denda'].sum():,}")
            st.dataframe(df_tunggak[['Tanggal', 'Nama', 'Status', 'Denda']], use_container_width=True)
        else:
            st.success("Semua denda sudah lunas!")
    else:
        st.info("Belum ada data.")

# --- D. ADMIN PANEL ---
elif st.session_state.page == 'Admin':
    st.markdown('<div class="app-header">🔐 ADMIN PANEL</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Dashboard"): navigasi('Dashboard')
    pswd = st.text_input("Password Admin:", type="password")
    if pswd == "galva123":
        st.write("### Rekap Seluruh Data")
        st.dataframe(df_total, use_container_width=True)
        st.divider()
        if os.path.exists(excel_file):
            st.download_button("📊 Download Laporan Excel", data=open(excel_file, "rb"), file_name="rekap_absensi_galva.xlsx")