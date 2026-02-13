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

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #0046ad;
        color: white;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding: 10px;
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

# --- 3. NAVIGASI ---
menu = st.sidebar.selectbox("Menu Utama", ["Absensi Karyawan", "Tebus Denda", "Login Admin"])
Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]

# --- 4. HALAMAN ABSENSI ---
if menu == "Absensi Karyawan":
    st.title("Sistem Absensi Galva Manado")
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

    if nama != "Pilih Nama":
        ready_to_save = (opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] and img_file is not None) or \
                        (opsi_absen in ["Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit"])

        if ready_to_save:
            if st.button("🚀 KIRIM ABSENSI SEKARANG"):
                with st.spinner('Menyimpan...'):
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
                    
                    st.success(f"✅ Absensi Berhasil dikirim!")
                    time.sleep(2)
                    st.rerun()

# --- 5. HALAMAN TEBUS DENDA ---
elif menu == "Tebus Denda":
    st.subheader("Penebusan Denda")
    nama_tebus = st.selectbox("Pilih Nama:", Karyawan_List)
    if nama_tebus != "Pilih Nama":
        idx_hutang = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_hutang = df_total.loc[idx_hutang, 'Denda'].sum()
        
        menunggu_app = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'].str.contains("Menunggu", na=False))]
        
        if not menunggu_app.empty:
            st.warning("⌛ Anda memiliki pengajuan penebusan yang sedang menunggu verifikasi Admin.")

        if total_hutang > 0:
            st.error(f"Total Tunggakan: Rp {total_hutang:,}")
            mode_tebus = st.radio("Opsi Pembayaran:", ["Tebus Semua", "Cicil Sebagian"])
            jumlah_dibayar = st.number_input("Nominal Pembayaran:", min_value=10000, max_value=int(total_hutang), step=10000) if mode_tebus == "Cicil Sebagian" else total_hutang

            metode = st.radio("Metode:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            file_bukti = []
            
            if metode == "Bayar Tunai / Transfer":
                bt = st.file_uploader("Upload Bukti Bayar", type=['jpg','png','jpeg'])
                if bt: file_bukti.append(bt)
            else:
                st.info("Upload Foto Sebelum & Sesudah Membersihkan Kantor.")
                f_seb = st.file_uploader("Foto Sebelum", type=['jpg','png','jpeg'], key="before")
                f_ses = st.file_uploader("Foto Sesudah", type=['jpg','png','jpeg'], key="after")
                if f_seb and f_ses: file_bukti.extend([f_seb, f_ses])
            
            if st.button("Ajukan Penebusan"):
                if not file_bukti:
                    st.warning("⚠️ Wajib lampirkan bukti foto!")
                else:
                    id_unik = f"{nama_tebus}_{datetime.now(timezone).strftime('%y%m%d%H%M%S')}"
                    for i, f in enumerate(file_bukti):
                        with open(os.path.join(folder_penebusan, f"{id_unik}_{i}.jpg"), "wb") as f_save:
                            f_save.write(f.getbuffer())
                    
                    terbayar = 0
                    for idx in idx_hutang:
                        if terbayar < jumlah_dibayar:
                            df_total.at[idx, 'Status Denda'] = f"Menunggu Approval ({metode})"
                            df_total.at[idx, 'ID_Tebus'] = id_unik
                            terbayar += df_total.at[idx, 'Denda']
                    
                    df_total.to_excel(excel_file, index=False)
                    st.info("✅ Pengajuan dikirim ke Admin.")
                    time.sleep(2)
                    st.rerun()
        else:
            if menunggu_app.empty: st.success("Status: Bebas Denda.")

# --- 6. HALAMAN ADMIN ---
elif menu == "Login Admin":
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        t1, t2, t3, t4, t5 = st.tabs(["📊 Dashboard", "🔔 Verifikasi", "📑 Laporan", "📸 Galeri Foto", "⚙️ Pengaturan"])
        
        with t1:
            st.subheader("Statistik Kehadiran")
            if not df_total.empty:
                bulan_ini = datetime.now(timezone).strftime('%Y-%m')
                df_bulan_ini = df_total[df_total['Tanggal'].str.startswith(bulan_ini)].copy()
                pemasukan_bulan_ini = df_bulan_ini[df_bulan_ini['Status Denda'].str.contains("Verified", na=False) & df_bulan_ini['Status Denda'].str.contains("Tunai", na=False)]['Denda'].sum()
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Terlambat", len(df_total[df_total['Status'] == 'TERLAMBAT']))
                c2.metric("Denda Belum Lunas", f"Rp {df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum():,}")
                c3.metric("Menunggu Verifikasi", len(df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)]))
                c4.metric(f"Pemasukan Cash ({datetime.now(timezone).strftime('%B')})", f"Rp {pemasukan_bulan_ini:,}")
                
                ca, cb = st.columns(2)
                with ca:
                    st.write("**Top Terlambat**")
                    st.bar_chart(df_total[df_total['Status'] == 'TERLAMBAT'].groupby('Nama').size())
                with cb:
                    st.write("**Status Kehadiran**")
                    st.bar_chart(df_total.groupby('Status').size())
            else: st.info("Belum ada data.")

        with t2:
            pending = df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)].groupby('ID_Tebus').first()
            if pending.empty:
                st.info("Tidak ada antrean verifikasi.")
            else:
                for id_t, row in pending.iterrows():
                    with st.expander(f"Approval: {row['Nama']}"):
                        bukti_f = [f for f in os.listdir(folder_penebusan) if f.startswith(str(id_t))]
                        cols = st.columns(len(bukti_f) if bukti_f else 1)
                        for i, img in enumerate(bukti_f):
                            cols[i].image(os.path.join(folder_penebusan, img), use_container_width=True)
                        
                        metode_raw = row['Status Denda']
                        col_y, col_n = st.columns(2)
                        if col_y.button("Setujui", key=f"y_{id_t}"):
                            final_status = "Lunas (Verified) (Bayar Tunai / Transfer)" if "Bayar Tunai" in metode_raw else "Lunas (Verified) (Bersih Kantor)"
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = final_status
                            df_total.to_excel(excel_file, index=False)
                            st.rerun()
                        if col_n.button("Tolak", key=f"n_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Belum Lunas"
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'ID_Tebus'] = ""
                            df_total.to_excel(excel_file, index=False)
                            st.rerun()

        with t3:
            if not df_total.empty:
                df_total['Bulan'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%B %Y')
                sel_bulan = st.selectbox("Pilih Bulan", df_total['Bulan'].unique())
                df_f = df_total[df_total['Bulan'] == sel_bulan].copy()
                st.dataframe(df_f[columns[:-1]])
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_f[columns[:-1]].to_excel(writer, sheet_name='Data', index=False)
                    summary = df_f.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                    summary.to_excel(writer, sheet_name='Grafik')
                    rekap_denda = df_f.groupby('Nama')['Denda'].sum().reset_index()
                    rekap_denda.to_excel(writer, sheet_name='Rekap_Denda', index=False)
                st.download_button("📥 Download Excel", output.getvalue(), f"Laporan_{sel_bulan}.xlsx")

        with t4:
            st.subheader("📸 Galeri Foto Absensi")
            files = sorted([f for f in os.listdir(folder_foto) if f.endswith('.jpg')], reverse=True)
            if files:
                num_cols = 4
                cols = st.columns(num_cols)
                for i, f in enumerate(files):
                    with cols[i % num_cols]:
                        st.image(os.path.join(folder_foto, f), caption=f, use_container_width=True)
            else:
                st.info("Belum ada foto absen.")

        with t5:
            st.subheader("🚨 Bahaya: Reset Sistem")
            st.warning("Menekan tombol di bawah akan menghapus SEMUA data Excel dan SEMUA foto secara permanen!")
            if st.button("HAPUS TOTAL SEMUA DATA"):
                if os.path.exists(excel_file): os.remove(excel_file)
                for d in [folder_foto, folder_penebusan]:
                    if os.path.exists(d): shutil.rmtree(d)
                inisialisasi_folder()
                st.success("Sistem telah di-reset!")
                time.sleep(2)
                st.rerun()