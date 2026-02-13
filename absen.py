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
    
    .stApp {
        background-color: #ffffff;
    }

    /* Header Banner Ala Mobile App (Ungu/Biru) */
    .header-banner {
        background: linear-gradient(135deg, #0046ad 0%, #00d4ff 100%);
        padding: 40px;
        border-radius: 25px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(0,70,173,0.2);
    }
    .header-banner h2 {
        margin: 0;
        font-size: 20px;
        font-weight: 400;
        color: #e0e0e0;
    }
    .header-banner h1 {
        margin: 5px 0;
        font-size: 38px;
        font-weight: 800;
        color: white !important;
    }
    .header-banner p {
        font-size: 16px;
        opacity: 0.9;
    }

    /* Container untuk Menu Grid */
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #333;
        margin-bottom: 20px;
        margin-top: 10px;
        padding-left: 5px;
        border-left: 5px solid #0046ad;
    }

    /* Styling Tombol Menu (Grid Kotak Putih) */
    .stButton > button {
        background-color: #f8f9fa !important;
        color: #333 !important;
        border: 1px solid #eee !important;
        border-radius: 20px !important;
        height: 150px !important;
        width: 100% !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        white-space: pre-wrap !important; /* Agar teks \n\n terbaca */
    }

    .stButton > button:hover {
        background-color: #ffffff !important;
        border: 1px solid #0046ad !important;
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.1) !important;
        color: #0046ad !important;
    }

    /* Metric Styling agar lebih modern */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        border: 1px solid #f0f0f0 !important;
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

# --- 3. DASHBOARD UTAMA (RE-DESIGNED) ---
if st.session_state.page == 'Dashboard':
    # Banner Atas
    st.markdown(f"""
        <div class="header-banner">
            <h2>Selamat Datang,</h2>
            <h1>🏢 GALVA MANADO</h1>
            <p>Silahkan pilih menu di bawah untuk melakukan absensi atau penebusan denda.</p>
        </div>
    """, unsafe_allow_html=True)

    # Menu Kategori
    st.markdown('<p class="section-title">Kategori Menu</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝\n\nMULAI ABSENSI"): navigasi('Absensi')
            
    with col2:
        if st.button("💰\n\nTEBUS DENDA"): navigasi('Tebus')
            
    with col3:
        if st.button("🔐\n\nADMIN PANEL"): navigasi('Admin')

    # Statistik (Bawah)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">📊 Statistik Kehadiran</p>', unsafe_allow_html=True)
    
    if not df_total.empty:
        total_terlambat = len(df_total[df_total['Status'] == 'TERLAMBAT'])
        hutang = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        mask_cash = (df_total['Status Denda'].str.contains("Verified", na=False)) & (~df_total['Status Denda'].str.contains("Membersihkan Kantor", na=False))
        cash = df_total[mask_cash]['Denda'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Terlambat", f"{total_terlambat} Kali")
        m2.metric("Tunggakan Denda", f"Rp {hutang:,}")
        m3.metric("Uang Cash Masuk", f"Rp {cash:,}")
        
        rekap = df_total[df_total['Status'] == 'TERLAMBAT'].groupby('Nama').size().reset_index(name='Jumlah')
        if not rekap.empty:
            st.bar_chart(rekap.set_index('Nama'))
    else: 
        st.info("Belum ada data absensi untuk periode ini.")

# --- 4. HALAMAN ABSENSI ---
elif st.session_state.page == 'Absensi':
    if st.button("⬅️ Kembali ke Beranda"): navigasi('Dashboard')
    st.header("📝 Form Absensi")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Pilih Nama Anda:", Karyawan_List)
    opsi = st.radio("Tipe Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit", "Tugas Luar Kota", "Langsung ke Customer"])
    
    waktu_skrg = datetime.now(timezone)
    if nama != "Pilih Nama":
        st.info(f"Waktu Sekarang: **{waktu_skrg.strftime('%H:%M:%S')} WITA**")
        if opsi == "Hadir di Kantor":
            if (waktu_skrg.hour > 8 or (waktu_skrg.hour == 8 and waktu_skrg.minute > 5)):
                st.warning("⚠️ Anda TERLAMBAT (Denda Otomatis Rp 10.000)")
            else: st.success("✅ TEPAT WAKTU")

        alasan = st.text_area("Keterangan Lokasi/Alasan:") if opsi != "Hadir di Kantor" else ""
        img = st.camera_input("Ambil Foto Selfie") if opsi in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] else st.file_uploader("Upload Bukti Pendukung", type=['jpg','png','jpeg'])

        if st.button("🚀 KIRIM DATA ABSENSI"):
            if (img is not None) or (opsi in ["Tidak Masuk Kantor Cuti/Sakit", "Izin Terlambat"]):
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
                st.success("✅ Absensi berhasil direkam!")
                time.sleep(1); navigasi('Dashboard')
            else:
                st.error("⚠️ Foto selfie/bukti wajib dilampirkan!")

# --- 5. HALAMAN TEBUS ---
elif st.session_state.page == 'Tebus':
    if st.button("⬅️ Kembali ke Beranda"): navigasi('Dashboard')
    st.header("💰 Penebusan Denda")
    nama_tebus = st.selectbox("Pilih Nama:", ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"])
    
    if nama_tebus != "Pilih Nama":
        idx_h = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_h = df_total.loc[idx_h, 'Denda'].sum()
        
        if total_h > 0:
            st.error(f"Total Tunggakan Anda: Rp {total_h:,}")
            metode = st.radio("Pilih Metode Penebusan:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            tipe_pembayaran = st.selectbox("Status Pembayaran:", ["Lunas", "Cicil"])
            
            jumlah_bayar = total_h
            if tipe_pembayaran == "Cicil":
                jumlah_bayar = st.number_input(f"Nominal Pembayaran (Max Rp {total_h:,}):", min_value=1000, max_value=int(total_h), step=1000)

            bukti_1, bukti_2 = None, None
            if metode == "Membersihkan Kantor":
                st.info("💡 Wajib lampirkan foto sebelum dan sesudah membersihkan kantor.")
                col_f1, col_f2 = st.columns(2)
                with col_f1: bukti_1 = st.file_uploader("📸 Foto SEBELUM", type=['jpg','jpeg','png'], key="bef")
                with col_f2: bukti_2 = st.file_uploader("📸 Foto SESUDAH", type=['jpg','jpeg','png'], key="aft")
            else:
                bukti_1 = st.file_uploader("📸 Upload Bukti Pembayaran", type=['jpg','jpeg','png'], key="trf")

            if st.button("🚀 KIRIM PENGAJUAN"):
                ready = (metode == "Membersihkan Kantor" and bukti_1 and bukti_2) or (metode != "Membersihkan Kantor" and bukti_1)
                if ready:
                    id_u = f"{nama_tebus}_{datetime.now(timezone).strftime('%y%m%d%H%M%S')}"
                    catatan = f"Pengajuan {tipe_pembayaran} sebesar Rp {jumlah_bayar:,}"
                    df_total.loc[idx_h, 'Status Denda'] = f"Menunggu Approval ({metode})"
                    df_total.loc[idx_h, 'ID_Tebus'] = id_u
                    df_total.loc[idx_h, 'Alasan'] = catatan 
                    df_total.to_excel(excel_file, index=False)
                    
                    with open(os.path.join(folder_penebusan, f"{id_u}_1.jpg"), "wb") as f: f.write(bukti_1.getbuffer())
                    if bukti_2:
                        with open(os.path.join(folder_penebusan, f"{id_u}_2.jpg"), "wb") as f: f.write(bukti_2.getbuffer())
                    
                    st.success("✅ Pengajuan telah terkirim! Menunggu verifikasi admin."); time.sleep(2); navigasi('Dashboard')
                else: st.warning("⚠️ Harap lengkapi semua foto bukti!")
        else: st.success("✅ Anda tidak memiliki tunggakan denda.")

# --- 6. HALAMAN ADMIN ---
elif st.session_state.page == 'Admin':
    if st.button("⬅️ Kembali ke Beranda"): navigasi('Dashboard')
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        t1, t2, t3, t4, t5 = st.tabs(["📊 Statistik", "🔔 Verifikasi", "📑 Laporan", "📸 Galeri", "⚙️ Reset"])
        
        with t1:
            mask_cash_adm = (df_total['Status Denda'].str.contains("Verified", na=False)) & (~df_total['Status Denda'].str.contains("Membersihkan Kantor", na=False))
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Kasus Terlambat", len(df_total[df_total['Status'] == 'TERLAMBAT']))
            c2.metric("Total Piutang Denda", f"Rp {df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum():,}")
            c3.metric("Uang Cash di Admin", f"Rp {df_total[mask_cash_adm]['Denda'].sum():,}")
            st.bar_chart(df_total.groupby('Status').size())

        with t2:
            pending_ids = df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)]['ID_Tebus'].unique()
            if len(pending_ids) > 0:
                for id_t in pending_ids:
                    if not id_t: continue
                    row_info = df_total[df_total['ID_Tebus'] == id_t].iloc[0]
                    is_cleaning = "Membersihkan Kantor" in row_info['Status Denda']
                    with st.expander(f"Verifikasi: {row_info['Nama']} ({row_info['Alasan']})"):
                        p1, p2 = os.path.join(folder_penebusan, f"{id_t}_1.jpg"), os.path.join(folder_penebusan, f"{id_t}_2.jpg")
                        v_col1, v_col2 = st.columns(2)
                        if os.path.exists(p1): v_col1.image(p1, caption="Bukti / Foto Sebelum", use_container_width=True)
                        if os.path.exists(p2): v_col2.image(p2, caption="Foto Sesudah", use_container_width=True)
                        
                        c_acc, c_rej = st.columns(2)
                        if c_acc.button("✅ Setujui", key=f"y_{id_t}"):
                            new_status = "Lunas (Verified - Membersihkan Kantor)" if is_cleaning else "Lunas (Verified - Cash)"
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = new_status
                            df_total.to_excel(excel_file, index=False); st.rerun()
                        if c_rej.button("❌ Tolak", key=f"n_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Belum Lunas"
                            df_total.to_excel(excel_file, index=False); st.rerun()
            else: st.info("Tidak ada pengajuan penebusan yang perlu diverifikasi.")

        with t3:
            if not df_total.empty:
                df_total['Bulan'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%B %Y')
                pilih_bulan = st.selectbox("Filter Laporan Bulan:", df_total['Bulan'].unique())
                st.dataframe(df_total[df_total['Bulan'] == pilih_bulan], use_container_width=True)
        
        with t4:
            st.subheader("Galeri Absensi Selfie")
            files = sorted([f for f in os.listdir(folder_foto) if f.endswith('.jpg')], reverse=True)
            if files:
                cols = st.columns(4)
                for i, f in enumerate(files):
                    cols[i % 4].image(os.path.join(folder_foto, f), caption=f, use_container_width=True)
            else: st.info("Belum ada foto absen.")

        with t5:
            st.warning("⚠️ Perhatian: Tindakan ini akan menghapus semua file Excel dan foto permanen!")
            if st.button("HAPUS SELURUH DATABASE"):
                if os.path.exists(excel_file): os.remove(excel_file)
                for d in [folder_foto, folder_penebusan]:
                    if os.path.exists(d): shutil.rmtree(d)
                inisialisasi_folder(); st.success("Sistem telah direset!"); time.sleep(1); st.rerun()