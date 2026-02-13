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
    
    .logo-container { display: flex; justify-content: center; margin-bottom: 5px; }

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

    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA ---
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

# --- 3. DASHBOARD UTAMA ---
if st.session_state.page == 'Dashboard':
    top_col1, top_col2, top_col3 = st.columns([1, 2, 1])
    with top_col2:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        try: st.image("images.png", width=140)
        except: st.subheader("🏢 Galva Manado")
        st.markdown('</div>', unsafe_allow_html=True)
    with top_col3:
        st.markdown('<div class="btn-admin">', unsafe_allow_html=True)
        if st.button("🔐 Admin"): navigasi('Admin')
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="btn-main">', unsafe_allow_html=True)
    if st.button("📝 ABSENSI KARYAWAN"): navigasi('Absensi')
    if st.button("💰 PENEBUSAN DENDA"): navigasi('Tebus')
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 Statistik Kehadiran (Real-time)")
    if not df_total.empty:
        total_terlambat = len(df_total[df_total['Status'] == 'TERLAMBAT'])
        hutang = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        cash = df_total[df_total['Status Denda'].str.contains("Verified", na=False)]['Denda'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Terlambat", f"{total_terlambat} Kali")
        m2.metric("Hutang Belum Bayar", f"Rp {hutang:,}")
        m3.metric("Total Denda Masuk", f"Rp {cash:,}")
        
        rekap = df_total[df_total['Status'] == 'TERLAMBAT'].groupby('Nama').size().reset_index(name='Jumlah')
        st.bar_chart(rekap.set_index('Nama'))
    else: st.info("Belum ada data.")

# --- 4. HALAMAN ABSENSI ---
elif st.session_state.page == 'Absensi':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.header("📝 Absensi Karyawan")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Pilih Nama:", Karyawan_List)
    
    # KEMBALI: Pilihan absen lengkap
    opsi = st.radio("Tipe Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit", "Tugas Luar Kota", "Langsung ke Customer"])
    
    waktu_skrg = datetime.now(timezone)
    if nama != "Pilih Nama":
        # KEMBALI: Info Jam & Denda real-time
        st.info(f"Jam Sekarang: **{waktu_skrg.strftime('%H:%M:%S')}**")
        if opsi == "Hadir di Kantor":
            if (waktu_skrg.hour > 8 or (waktu_skrg.hour == 8 and waktu_skrg.minute > 5)):
                st.warning("⚠️ Status: TERLAMBAT (Denda Rp 10.000)")
            else: st.success("✅ Status: TEPAT WAKTU")

        alasan = st.text_area("Lokasi / Alasan:") if opsi != "Hadir di Kantor" else ""
        img = st.camera_input("Ambil Foto Selfie") if opsi in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] else st.file_uploader("Upload Bukti", type=['jpg','png','jpeg'])

        if st.button("🚀 KIRIM ABSENSI"):
            if (img is not None) or (opsi == "Tidak Masuk Kantor Cuti/Sakit") or (opsi == "Izin Terlambat"):
                is_late = (waktu_skrg.hour > 8 or (waktu_skrg.hour == 8 and waktu_skrg.minute > 5))
                denda = 10000 if (opsi == "Hadir di Kantor" and is_late) else 0
                
                data_baru = pd.DataFrame([[waktu_skrg.strftime("%Y-%m-%d"), waktu_skrg.strftime("%H:%M:%S"), 
                                          nama, "TERLAMBAT" if denda > 0 else opsi.upper(), alasan, denda, 
                                          "Belum Lunas" if denda > 0 else "Lunas", ""]], columns=columns)
                df_total = pd.concat([df_total, data_baru], ignore_index=True)
                df_total.to_excel(excel_file, index=False)
                
                if img:
                    with open(os.path.join(folder_foto, f"{waktu_skrg.strftime('%Y%m%d_%H%M%S')}_{nama}.jpg"), "wb") as f:
                        f.write(img.getbuffer())
                st.success("✅ Berhasil!")
                time.sleep(1); navigasi('Dashboard')

# --- 5. HALAMAN TEBUS ---
elif st.session_state.page == 'Tebus':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.header("💰 Penebusan Denda")
    nama_tebus = st.selectbox("Pilih Nama:", ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"])
    if nama_tebus != "Pilih Nama":
        idx_h = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_h = df_total.loc[idx_h, 'Denda'].sum()
        if total_h > 0:
            st.error(f"Tunggakan: Rp {total_h:,}")
            metode = st.radio("Metode:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            f_bukti = st.file_uploader("Upload Bukti", type=['jpg','png','jpeg'])
            if st.button("Ajukan Penebusan") and f_bukti:
                id_u = f"{nama_tebus}_{datetime.now(timezone).strftime('%y%m%d%H%M%S')}"
                df_total.loc[idx_h, 'Status Denda'] = f"Menunggu ({metode})"
                df_total.loc[idx_h, 'ID_Tebus'] = id_u
                df_total.to_excel(excel_file, index=False)
                st.success("✅ Pengajuan Terkirim!")
                time.sleep(1); navigasi('Dashboard')
        else: st.success("Status: BEBAS DENDA")

# --- 6. HALAMAN ADMIN ---
elif st.session_state.page == 'Admin':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        # KEMBALI: Tab lengkap (Statistik, Verifikasi, Laporan, Galeri, Reset)
        t1, t2, t3, t4, t5 = st.tabs(["📊 Statistik", "🔔 Verifikasi", "📑 Laporan Perbulan", "📸 Galeri Foto", "⚙️ Reset Data"])
        
        with t1: # Dashboard Admin
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Terlambat", len(df_total[df_total['Status'] == 'TERLAMBAT']))
            c2.metric("Hutang Denda", f"Rp {df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum():,}")
            c3.metric("Uang Masuk", f"Rp {df_total[df_total['Status Denda'].str.contains('Verified', na=False)]['Denda'].sum():,}")
            st.bar_chart(df_total.groupby('Status').size())

        with t2: # Verifikasi
            pending = df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)].groupby('ID_Tebus').first()
            if not pending.empty:
                for id_t, row in pending.iterrows():
                    with st.expander(f"Penebusan: {row['Nama']}"):
                        if st.button("Setujui", key=f"y_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Lunas (Verified)"
                            df_total.to_excel(excel_file, index=False); st.rerun()
            else: st.info("Tidak ada antrean.")

        with t3: # KEMBALI: Rekapan perbulan & Download
            if not df_total.empty:
                df_total['Bulan'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%B %Y')
                pilih_bulan = st.selectbox("Pilih Bulan:", df_total['Bulan'].unique())
                df_filt = df_total[df_total['Bulan'] == pilih_bulan]
                st.dataframe(df_filt)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_filt.to_excel(writer, index=False)
                st.download_button("📥 Download Excel", output.getvalue(), f"Laporan_{pilih_bulan}.xlsx")

        with t4: # Galeri Foto
            files = sorted([f for f in os.listdir(folder_foto) if f.endswith('.jpg')], reverse=True)
            cols = st.columns(4)
            for i, f in enumerate(files):
                cols[i % 4].image(os.path.join(folder_foto, f), caption=f, use_container_width=True)

        with t5: # KEMBALI: Tombol Reset
            st.warning("⚠️ Perhatian: Tindakan ini menghapus SEMUA data permanen.")
            if st.button("HAPUS SEMUA DATA & FOTO"):
                if os.path.exists(excel_file): os.remove(excel_file)
                for d in [folder_foto, folder_penebusan]:
                    if os.path.exists(d): shutil.rmtree(d)
                inisialisasi_folder(); st.rerun()