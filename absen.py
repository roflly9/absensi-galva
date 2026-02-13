import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import time

# --- PENGAMAN LIBRARY GRAFIK ---
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Absensi Galva Manado", page_icon="🏢", layout="wide")

# Styling CSS
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
    .section-title { 
        font-size: 14px; font-weight: 800; color: #0d47a1; margin: 25px 0 10px 10px; 
        display: flex; align-items: center; text-transform: uppercase; 
    }
    .section-title::before { content: ""; width: 5px; height: 18px; background: #d32f2f; margin-right: 10px; border-radius: 3px; }
    .status-card { 
        background: white; padding: 20px; border-radius: 15px; border-left: 10px solid #0d47a1; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin: 15px 0; 
    }
    .status-card.terlambat { border-left: 10px solid #d32f2f; }
    div[data-testid="stMetric"] { 
        background: white !important; padding: 15px !important; border-radius: 18px !important; 
        border: 1px solid #e3f2fd !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE DATA ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "Foto_Absen", "Bukti_Bayar"]
karyawan_list = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]

def muat_data():
    if os.path.exists(excel_file):
        try:
            df = pd.read_excel(excel_file)
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
            return df
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

df_total = muat_data()

if 'page' not in st.session_state: st.session_state.page = 'Dashboard'
def navigasi(nama_hal):
    st.session_state.page = nama_hal
    st.rerun()

# --- 3. LOGIKA HALAMAN ---

# --- DASHBOARD ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">PRESENSI & DENDA</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="section-title">Aktivitas Karyawan</p>', unsafe_allow_html=True)
    if st.button("📝 &nbsp; MULAI ABSENSI"): navigasi('Absensi')
    if st.button("💰 &nbsp; TEBUS DENDA"): navigasi('Tebus')
    
    st.markdown('<p class="section-title">Menu Pengelola</p>', unsafe_allow_html=True)
    if st.button("🔐 &nbsp; ADMIN PANEL"): navigasi('Admin')

    st.markdown('<p class="section-title">Status & Ringkasan</p>', unsafe_allow_html=True)
    if not df_total.empty:
        # Menghitung Total Dana Lunas
        total_setoran = df_total[df_total['Status Denda'] == 'Lunas']['Denda'].sum()
        st.metric("Total Dana Pembayaran Denda", f"Rp {total_setoran:,}")

        # Menampilkan Grafik Terlambat per User (Sama seperti di Admin)
        if HAS_PLOTLY:
            telat_df = df_total[df_total['Status'] == 'TERLAMBAT']
            if not telat_df.empty:
                st.markdown('<p style="font-size:13px; font-weight:bold; color:#0d47a1; margin-left:10px;">GRAFIK KETERLAMBATAN PER USER</p>', unsafe_allow_html=True)
                # Group by Nama untuk melihat siapa yang paling sering telat
                grafik_user = telat_df.groupby('Nama').size().reset_index(name='Total Telat')
                fig = px.bar(grafik_user, x='Nama', y='Total Telat', 
                             color='Total Telat', 
                             color_continuous_scale='Reds',
                             text_auto=True)
                fig.update_layout(margin=dict(l=20, r=20, t=10, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Belum ada data keterlambatan untuk ditampilkan di grafik.")
    else:
        st.info("Belum ada data aktivitas.")

# --- FORM ABSENSI ---
elif st.session_state.page == 'Absensi':
    st.markdown('<div class="app-header">📝 FORM ABSENSI</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Menu"): navigasi('Dashboard')
    
    nama = st.selectbox("Nama Karyawan:", karyawan_list)
    opsi = st.radio("Opsi Kehadiran:", ["Hadir di kantor", "Izin terlambat", "Tidak masuk kantor Cuti/Sakit", "Tugas Luar kota", "Langsung ke customer"], index=0)
    
    waktu_skrg = datetime.now(timezone)
    batas_absen = datetime.strptime("08:05:00", "%H:%M:%S").time()
    is_telat = (opsi == "Hadir di kantor" and waktu_skrg.time() > batas_absen)
    
    if is_telat: card_class, st_text, dn_text, icon = "status-card terlambat", "TERLAMBAT", "Rp 10.000", "⚠️"
    else: card_class, st_text, dn_text, icon = "status-card", opsi.upper(), "Rp 0", "✅"
    
    st.markdown(f"""<div class="{card_class}"><h2 style="margin:5px 0;">{waktu_skrg.strftime('%H:%M:%S')} WITA</h2><span>Status: <b>{icon} {st_text}</b></span> | <b>Denda: {dn_text}</b></div>""", unsafe_allow_html=True)
    
    img_selfie = st.camera_input("Ambil Foto Selfie Kehadiran")
    
    if st.button("🚀 KIRIM ABSENSI"):
        if nama == "Pilih Nama" or img_selfie is None:
            st.error("Gagal! Pilih Nama dan Ambil Foto Selfie.")
        else:
            denda_final = 10000 if is_telat else 0
            baru = pd.DataFrame([[waktu_skrg.date(), waktu_skrg.strftime("%H:%M:%S"), nama, st_text, opsi, denda_final, "Belum Lunas" if denda_final > 0 else "Lunas", img_selfie.getvalue(), None]], columns=columns)
            df_total = pd.concat([df_total, baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False)
            st.balloons(); st.success("✅ Terkirim!"); time.sleep(2); navigasi('Dashboard')

# --- MENU TEBUS ---
elif st.session_state.page == 'Tebus':
    st.markdown('<div class="app-header">💰 MENU TEBUS DENDA</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Dashboard"): navigasi('Dashboard')
    
    user_pilih = st.selectbox("Nama Karyawan:", karyawan_list)
    if user_pilih != "Pilih Nama":
        unpaid = df_total[(df_total['Nama'] == user_pilih) & (df_total['Status Denda'] == 'Belum Lunas')]
        total_hutang = unpaid['Denda'].sum()
        
        if total_hutang > 0:
            st.markdown(f'<div class="status-card terlambat">TOTAL TUNGGAKAN: <b>Rp {total_hutang:,}</b></div>', unsafe_allow_html=True)
            f_bukti = st.file_uploader("Upload Bukti Pembayaran:", type=['jpg','png','jpeg'])
            if st.button("✅ KONFIRMASI PENEBUSAN"):
                if f_bukti:
                    mask = (df_total['Nama'] == user_pilih) & (df_total['Status Denda'] == 'Belum Lunas')
                    df_total.loc[mask, 'Status Denda'] = 'Menunggu Persetujuan'
                    df_total.loc[mask, 'Bukti_Bayar'] = f_bukti.getvalue()
                    df_total.to_excel(excel_file, index=False)
                    st.success("Berhasil! Menunggu konfirmasi Admin."); time.sleep(2); navigasi('Dashboard')
                else: st.warning("Mohon lampirkan foto bukti.")
        else: st.success(f"{user_pilih} tidak memiliki tunggakan.")

# --- ADMIN PANEL ---
elif st.session_state.page == 'Admin':
    st.markdown('<div class="app-header">🔐 ADMIN PANEL</div>', unsafe_allow_html=True)
    if st.button("⬅️ Dashboard"): navigasi('Dashboard')
    
    pwd = st.text_input("Masukkan Password Admin:", type="password")
    if pwd == "galva123":
        t1, t2, t3, t4, t5 = st.tabs(["📈 TREN", "📊 DATA", "✅ VERIFIKASI", "📸 FOTO", "⚙️ RESET"])
        
        with t1:
            if HAS_PLOTLY and not df_total.empty:
                telat_df = df_total[df_total['Status'] == 'TERLAMBAT']
                if not telat_df.empty:
                    grafik = px.bar(telat_df.groupby('Tanggal').size().reset_index(name='Jumlah'), x='Tanggal', y='Jumlah', title="Keterlambatan Harian")
                    st.plotly_chart(grafik, use_container_width=True)
            elif not HAS_PLOTLY: st.warning("Library grafik belum terdeteksi.")

        with t2:
            st.dataframe(df_total.drop(columns=['Foto_Absen', 'Bukti_Bayar'], errors='ignore'))
            st.download_button("📥 Download Excel", data=open(excel_file, "rb") if os.path.exists(excel_file) else b"", file_name="rekap_galva.xlsx")

        with t3:
            pending = df_total[df_total['Status Denda'] == 'Menunggu Persetujuan']
            if not pending.empty:
                for idx, row in pending.iterrows():
                    with st.expander(f"Bukti Bayar: {row['Nama']}"):
                        if row['Bukti_Bayar']: st.image(row['Bukti_Bayar'], width=300)
                        if st.button(f"Sahkan Pembayaran {row['Nama']} (ID:{idx})"):
                            df_total.at[idx, 'Status Denda'] = 'Lunas'
                            df_total.to_excel(excel_file, index=False); st.rerun()
            else: st.info("Tidak ada permintaan verifikasi.")

        with t4:
            for i in range(0, len(df_total), 4):
                cols = st.columns(4)
                for j, (idx, item) in enumerate(df_total.iloc[i:i+4].iterrows()):
                    if item.get('Foto_Absen') is not None:
                        try: cols[j].image(item['Foto_Absen'], caption=f"{item['Nama']} ({item['Tanggal']})", use_container_width=True)
                        except: pass

        with t5:
            if st.button("🔥 RESET SEMUA DATA SEKARANG"):
                if os.path.exists(excel_file): os.remove(excel_file)
                st.rerun()