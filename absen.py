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

# Styling CSS untuk tampilan Mobile-Friendly
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #f8f9fa; }
    .app-header {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        padding: 20px; color: white; text-align: center; font-weight: 800;
        border-radius: 0 0 20px 20px; margin-bottom: 15px;
    }
    .status-card {
        background: white; padding: 15px; border-radius: 12px;
        border-left: 8px solid #0d47a1; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .status-card.terlambat { border-left: 8px solid #d32f2f; }
    div.stButton > button {
        height: 60px !important; width: 100% !important; border-radius: 12px !important;
        font-weight: 700 !important; background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%) !important;
        color: white !important; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE DATA (PENGAMAN OTOMATIS) ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "Foto_Absen", "Bukti_Bayar"]
karyawan_list = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]

def muat_data():
    if os.path.exists(excel_file):
        try:
            df = pd.read_excel(excel_file)
            # Proteksi: Jika ada kolom baru yang belum ada di file lama, tambahkan otomatis
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
            return df
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

df_total = muat_data()

# --- 3. SISTEM NAVIGASI ---
if 'page' not in st.session_state: st.session_state.page = 'Dashboard'
def navigasi(nama_hal):
    st.session_state.page = nama_hal
    st.rerun()

# --- 4. LOGIKA HALAMAN ---

# --- DASHBOARD ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header"><h1>🏢 GALVA MANADO</h1><p>Sistem Presensi & Denda</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 MULAI ABSENSI"): navigasi('Absensi')
    with col2:
        if st.button("💰 TEBUS DENDA"): navigasi('Tebus')
    
    st.markdown("---")
    if st.button("🔐 ADMIN PANEL"): navigasi('Admin')

    # Ringkasan Cepat
    if not df_total.empty:
        tgl_skrg = datetime.now(timezone).date()
        df_hari_ini = df_total[df_total['Tanggal'] == tgl_skrg]
        c1, c2 = st.columns(2)
        c1.metric("Telat Hari Ini", f"{len(df_hari_ini[df_hari_ini['Status'] == 'TERLAMBAT'])}x")
        c2.metric("Total Kas Denda", f"Rp {df_total[df_total['Status Denda'] == 'Lunas']['Denda'].sum():,}")

# --- FORM ABSENSI ---
elif st.session_state.page == 'Absensi':
    st.subheader("📝 Form Kehadiran")
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    
    nama = st.selectbox("Pilih Nama:", karyawan_list)
    opsi = st.radio("Status:", ["Hadir di kantor", "Izin terlambat", "Tugas Luar kota", "Cuti/Sakit"], index=0)
    
    waktu_skrg = datetime.now(timezone)
    batas = datetime.strptime("08:05:00", "%H:%M:%S").time()
    is_telat = (opsi == "Hadir di kantor" and waktu_skrg.time() > batas)
    
    st_text = "TERLAMBAT" if is_telat else opsi.upper()
    denda_val = 10000 if is_telat else 0
    
    st.markdown(f"""<div class="status-card {'terlambat' if is_telat else ''}">
        <h4>{waktu_skrg.strftime('%H:%M:%S')} WITA</h4>
        Status: <b>{st_text}</b> | Denda: <b>Rp {denda_val:,}</b>
    </div>""", unsafe_allow_html=True)
    
    img_selfie = st.camera_input("Ambil Foto Selfie")
    
    if st.button("🚀 KIRIM DATA"):
        if nama == "Pilih Nama" or img_selfie is None:
            st.error("Nama dan Foto Selfie wajib diisi!")
        else:
            baru = pd.DataFrame([[waktu_skrg.date(), waktu_skrg.strftime("%H:%M:%S"), nama, st_text, opsi, denda_val, "Belum Lunas" if denda_val > 0 else "Lunas", img_selfie.getvalue(), None]], columns=columns)
            df_total = pd.concat([df_total, baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False)
            st.success("Data berhasil dikirim!"); time.sleep(1); navigasi('Dashboard')

# --- MENU TEBUS ---
elif st.session_state.page == 'Tebus':
    st.subheader("💰 Penebusan Denda")
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    
    user = st.selectbox("Nama Karyawan:", karyawan_list)
    if user != "Pilih Nama":
        unpaid = df_total[(df_total['Nama'] == user) & (df_total['Status Denda'] == 'Belum Lunas')]
        total_hutang = unpaid['Denda'].sum()
        
        if total_hutang > 0:
            st.error(f"Total Tunggakan: Rp {total_hutang:,}")
            bukti = st.file_uploader("Upload Foto Bukti Bayar", type=['jpg','png','jpeg'])
            if st.button("✅ KIRIM BUKTI"):
                if bukti:
                    mask = (df_total['Nama'] == user) & (df_total['Status Denda'] == 'Belum Lunas')
                    df_total.loc[mask, 'Status Denda'] = 'Menunggu Persetujuan'
                    df_total.loc[mask, 'Bukti_Bayar'] = bukti.getvalue()
                    df_total.to_excel(excel_file, index=False)
                    st.success("Terkirim! Admin akan segera memverifikasi."); time.sleep(1); navigasi('Dashboard')
                else: st.warning("Mohon lampirkan foto bukti.")
        else: st.success("Anda tidak memiliki tunggakan denda.")

# --- ADMIN PANEL ---
elif st.session_state.page == 'Admin':
    if st.button("⬅️ Keluar Admin"): navigasi('Dashboard')
    pwd = st.text_input("Masukkan Password Admin:", type="password")
    
    if pwd == "galva123":
        t1, t2, t3, t4, t5 = st.tabs(["📈 TREN", "📊 DATA", "✅ VERIFIKASI", "📸 FOTO", "⚙️ RESET"])
        
        with t1:
            if HAS_PLOTLY and not df_total.empty:
                telat_df = df_total[df_total['Status'] == 'TERLAMBAT']
                if not telat_df.empty:
                    grafik = px.bar(telat_df.groupby('Tanggal').size().reset_index(name='Jumlah'), x='Tanggal', y='Jumlah', title="Keterlambatan Harian")
                    st.plotly_chart(grafik, use_container_width=True)
                else: st.info("Tidak ada data telat.")
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
            # Galeri Foto Selfie
            rows = [df_total.iloc[i:i+4] for i in range(0, len(df_total), 4)]
            for r in rows:
                cols = st.columns(4)
                for i, (idx, item) in enumerate(r.iterrows()):
                    if item.get('Foto_Absen') is not None:
                        try: cols[i].image(item['Foto_Absen'], caption=f"{item['Nama']} - {item['Tanggal']}", use_container_width=True)
                        except: pass

        with t5:
            st.error("Hapus Permanen Seluruh Data")
            if st.button("🔥 RESET SEMUA DATA SEKARANG"):
                if os.path.exists(excel_file): os.remove(excel_file)
                st.rerun()