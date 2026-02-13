import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import shutil
import time
import io

# --- 1. KONFIGURASI HALAMAN & UI ---
st.set_page_config(page_title="Absensi Galva Manado", page_icon="🏢", layout="wide")

# CSS Khusus untuk tombol menu dashboard agar besar dan menarik
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tombol Menu Utama di Dashboard */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 4em;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* Tombol Kembali */
    .btn-kembali > div > button {
        background-color: #ff4b4b !important;
        color: white !important;
        height: 3em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP FOLDER & DATA ---
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

# --- 3. LOGIKA NAVIGASI SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

def change_page(page_name):
    st.session_state.page = page_name

# --- 4. HALAMAN DASHBOARD UTAMA ---
if st.session_state.page == 'Dashboard':
    st.title("🏢 Galva Manado App")
    st.subheader("Silakan Pilih Menu:")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 ABSENSI KARYAWAN"):
            change_page('Absensi')
            st.rerun()
    with col2:
        if st.button("💰 TEBUS DENDA"):
            change_page('Tebus')
            st.rerun()
            
    st.write("---")
    if st.button("🔐 HALAMAN ADMIN"):
        change_page('Admin')
        st.rerun()

# --- 5. HALAMAN ABSENSI ---
elif st.session_state.page == 'Absensi':
    if st.button("⬅️ Kembali ke Dashboard", key="back_abs", help="Klik untuk kembali"):
        change_page('Dashboard')
        st.rerun()
        
    st.title("📝 Absensi Karyawan")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Pilih Nama Anda:", Karyawan_List)
    opsi_absen = st.radio("Tipe Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit", "Tugas Luar Kota", "Langsung ke Customer"])

    waktu_sekarang = datetime.now(timezone)
    jam_skrg = waktu_sekarang.strftime("%H:%M:%S")
    
    if nama != "Pilih Nama":
        st.info(f"Jam Sekarang: **{jam_skrg}**")
        if opsi_absen == "Hadir di Kantor":
            if (waktu_sekarang.hour > 8 or (waktu_sekarang.hour == 8 and waktu_sekarang.minute > 5)):
                st.warning("⚠️ Status Anda: **TERLAMBAT** (Denda Rp 10.000)")
            else:
                st.success("✅ Status Anda: **TEPAT WAKTU**")

        alasan = ""
        if opsi_absen in ["Tugas Luar Kota", "Langsung ke Customer"]:
            alasan = st.text_input("📍 Masukkan Lokasi/Tujuan:")
        elif opsi_absen != "Hadir di Kantor":
            alasan = st.text_area("📝 Masukkan Alasan / Catatan:")
        
        img_file = st.camera_input("Ambil foto absen") if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] else st.file_uploader("Upload Bukti", type=['jpg','png','jpeg'])

        ready_to_save = (opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] and img_file is not None) or \
                        (opsi_absen in ["Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit"])

        if ready_to_save:
            if st.button("🚀 KIRIM ABSENSI SEKARANG"):
                waktu_klik = datetime.now(timezone)
                denda = 10000 if (opsi_absen == "Hadir di Kantor" and (waktu_klik.hour > 8 or (waktu_klik.hour == 8 and waktu_klik.minute > 5))) else 0
                status_denda = "Belum Lunas" if denda > 0 else "Lunas"
                status = "TERLAMBAT" if denda > 0 else opsi_absen.upper()

                data_baru = pd.DataFrame([[waktu_klik.strftime("%Y-%m-%d"), waktu_klik.strftime("%H:%M:%S"), nama, status, alasan, denda, status_denda, ""]], columns=columns)
                df_total = pd.concat([df_total, data_baru], ignore_index=True)
                df_total.to_excel(excel_file, index=False)

                if img_file:
                    fname = f"{waktu_klik.strftime('%Y%m%d_%H%M%S')}_{nama}.jpg"
                    with open(os.path.join(folder_foto, fname), "wb") as f:
                        f.write(img_file.getbuffer())
                
                st.success("✅ Absensi Berhasil!")
                time.sleep(2)
                change_page('Dashboard')
                st.rerun()

# --- 6. HALAMAN TEBUS DENDA ---
elif st.session_state.page == 'Tebus':
    if st.button("⬅️ Kembali ke Dashboard"):
        change_page('Dashboard')
        st.rerun()

    st.title("💰 Penebusan Denda")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama_tebus = st.selectbox("Pilih Nama:", Karyawan_List)
    
    if nama_tebus != "Pilih Nama":
        idx_hutang = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_hutang = df_total.loc[idx_hutang, 'Denda'].sum()
        menunggu_app = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'].str.contains("Menunggu", na=False))]
        
        if not menunggu_app.empty:
            st.warning("⌛ Menunggu verifikasi Admin.")

        if total_hutang > 0:
            st.error(f"Total Tunggakan: Rp {total_hutang:,}")
            metode = st.radio("Metode:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            file_bukti = []
            
            if metode == "Bayar Tunai / Transfer":
                bt = st.file_uploader("Upload Bukti Bayar", type=['jpg','png','jpeg'])
                if bt: file_bukti.append(bt)
            else:
                f_seb = st.file_uploader("Foto Sebelum", type=['jpg','png','jpeg'], key="b")
                f_ses = st.file_uploader("Foto Sesudah", type=['jpg','png','jpeg'], key="a")
                if f_seb and f_ses: file_bukti.extend([f_seb, f_ses])
            
            if st.button("Ajukan Penebusan"):
                if not file_bukti:
                    st.warning("⚠️ Wajib lampirkan foto bukti!")
                else:
                    id_unik = f"{nama_tebus}_{datetime.now(timezone).strftime('%y%m%d%H%M%S')}"
                    for i, f in enumerate(file_bukti):
                        with open(os.path.join(folder_penebusan, f"{id_unik}_{i}.jpg"), "wb") as f_save:
                            f_save.write(f.getbuffer())
                    
                    df_total.loc[idx_hutang, 'Status Denda'] = f"Menunggu Approval ({metode})"
                    df_total.loc[idx_hutang, 'ID_Tebus'] = id_unik
                    df_total.to_excel(excel_file, index=False)
                    st.info("✅ Pengajuan dikirim.")
                    time.sleep(2)
                    change_page('Dashboard')
                    st.rerun()
        else:
            if menunggu_app.empty: st.success("Status: Bebas Denda.")

# --- 7. HALAMAN ADMIN ---
elif st.session_state.page == 'Admin':
    if st.button("⬅️ Kembali ke Dashboard"):
        change_page('Dashboard')
        st.rerun()

    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        t1, t2, t3, t4, t5 = st.tabs(["📊 Statistik", "🔔 Verifikasi", "📑 Laporan", "📸 Galeri Foto", "⚙️ Reset"])
        
        with t1:
            if not df_total.empty:
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Terlambat", len(df_total[df_total['Status'] == 'TERLAMBAT']))
                c2.metric("Hutang Denda", f"Rp {df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum():,}")
                c3.metric("Menunggu Approval", len(df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)]))
                st.bar_chart(df_total.groupby('Status').size())

        with t2:
            pending = df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)].groupby('ID_Tebus').first()
            if pending.empty:
                st.info("Tidak ada antrean.")
            else:
                for id_t, row in pending.iterrows():
                    with st.expander(f"Verifikasi: {row['Nama']}"):
                        bukti_f = [f for f in os.listdir(folder_penebusan) if f.startswith(str(id_t))]
                        for img in bukti_f:
                            st.image(os.path.join(folder_penebusan, img), width=300)
                        
                        if st.button("Setujui", key=f"y_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Lunas (Verified)"
                            df_total.to_excel(excel_file, index=False)
                            st.rerun()

        with t3:
            st.dataframe(df_total)
            output = io.BytesIO()
            df_total.to_excel(output, index=False)
            st.download_button("📥 Download Excel", output.getvalue(), "Laporan_Galva.xlsx")

        with t4:
            files = sorted([f for f in os.listdir(folder_foto) if f.endswith('.jpg')], reverse=True)
            if files:
                cols = st.columns(4)
                for i, f in enumerate(files):
                    cols[i % 4].image(os.path.join(folder_foto, f), caption=f, use_container_width=True)

        with t5:
            if st.button("🚨 RESET TOTAL DATA SEKARANG"):
                if os.path.exists(excel_file): os.remove(excel_file)
                for d in [folder_foto, folder_penebusan]:
                    if os.path.exists(d): shutil.rmtree(d)
                inisialisasi_folder()
                st.success("Sistem di-reset.")
                st.rerun()