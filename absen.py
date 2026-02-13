import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import shutil
import time
import io

# Tentukan zona waktu Manado (WITA)
timezone = pytz.timezone('Asia/Makassar')

st.set_page_config(page_title="Absensi Galva Manado", layout="wide")
st.title("Sistem Absensi Galva Manado")

# --- KONFIGURASI FOLDER & FILE ---
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

# Fungsi inisialisasi folder agar tidak error saat di-reset
def inisialisasi_folder():
    for folder in [folder_foto, folder_penebusan]:
        if not os.path.exists(folder):
            os.makedirs(folder)

inisialisasi_folder()

# --- INISIALISASI DATAFRAME ---
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

# --- MENU NAVIGASI ---
menu = st.sidebar.selectbox("Menu", ["Absensi Karyawan", "Tebus Denda", "Login Admin"])
Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]

# --- HALAMAN ABSENSI ---
if menu == "Absensi Karyawan":
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
                    st.success("✅ Absensi Berhasil!")
                    time.sleep(1); st.rerun()

# --- HALAMAN TEBUS DENDA (DENGAN LOGIKA CICILAN) ---
elif menu == "Tebus Denda":
    st.subheader("Penebusan Denda")
    nama_tebus = st.selectbox("Pilih Nama:", Karyawan_List)
    if nama_tebus != "Pilih Nama":
        idx_hutang = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_hutang = df_total.loc[idx_hutang, 'Denda'].sum()
        
        if total_hutang > 0:
            st.error(f"Total Tunggakan: Rp {total_hutang:,}")
            
            # FITUR CICIL KEMBALI
            opsi_bayar = st.radio("Opsi Pembayaran:", ["Tebus Semua", "Cicil Sebagian"])
            if opsi_bayar == "Cicil Sebagian":
                jumlah_dibayar = st.number_input("Nominal yang dibayar (Kelipatan 10.000):", min_value=10000, max_value=int(total_hutang), step=10000)
            else:
                jumlah_dibayar = total_hutang

            metode = st.radio("Metode:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            
            file_bukti = []
            if metode == "Bayar Tunai / Transfer":
                bt = st.file_uploader("Upload Bukti", type=['jpg','png','jpeg'])
                if bt: file_bukti.append(bt)
            else:
                st.info("Ambil foto Before & After.")
                f_seb = st.camera_input("Foto Sebelum")
                f_ses = st.camera_input("Foto Sesudah")
                if f_seb and f_ses: file_bukti.extend([f_seb, f_ses])
            
            if st.button("Ajukan Penebusan"):
                if not file_bukti:
                    st.warning("⚠️ Wajib lampirkan foto bukti!")
                else:
                    id_unik = f"{nama_tebus}_{datetime.now(timezone).strftime('%y%m%d%H%M%S')}"
                    for i, f in enumerate(file_bukti):
                        with open(os.path.join(folder_penebusan, f"{id_unik}_{i}.jpg"), "wb") as f_save:
                            f_save.write(f.getbuffer())
                    
                    # Logika memilih transaksi mana yang dicicil
                    terbayar = 0
                    for idx in idx_hutang:
                        if terbayar < jumlah_dibayar:
                            df_total.at[idx, 'Status Denda'] = f"Menunggu Approval ({metode})"
                            df_total.at[idx, 'ID_Tebus'] = id_unik
                            terbayar += df_total.at[idx, 'Denda']
                    
                    df_total.to_excel(excel_file, index=False)
                    st.info("✅ Pengajuan dikirim ke Admin.")
                    time.sleep(2); st.rerun()
        else:
            st.success("Status: Bebas Denda.")

# --- HALAMAN ADMIN (FIX RESET & VERIFIKASI) ---
elif menu == "Login Admin":
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        t1, t2, t3, t4, t5 = st.tabs(["📊 Dashboard", "🔔 Verifikasi", "📑 Laporan", "📸 Galeri", "⚙️ Pengaturan"])
        
        with t2: # VERIFIKASI
            pending = df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)].groupby('ID_Tebus').first()
            if pending.empty:
                st.info("Tidak ada antrean verifikasi.")
            else:
                for id_t, row in pending.iterrows():
                    with st.expander(f"Approval: {row['Nama']} (Denda Terpilih)"):
                        bukti_f = [f for f in os.listdir(folder_penebusan) if f.startswith(str(id_t))]
                        c = st.columns(len(bukti_f) if bukti_f else 1)
                        for i, img in enumerate(bukti_f):
                            c[i].image(os.path.join(folder_penebusan, img), use_container_width=True)
                        
                        if st.button("Setujui", key=f"y_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Lunas (Verified)"
                            df_total.to_excel(excel_file, index=False); st.rerun()
                        if st.button("Tolak", key=f"n_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Belum Lunas"
                            df_total.to_excel(excel_file, index=False); st.rerun()

        with t3: # LAPORAN
            if not df_total.empty:
                df_total['Bulan'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%B %Y')
                sel_bulan = st.selectbox("Filter Bulan", df_total['Bulan'].unique())
                df_f = df_total[df_total['Bulan'] == sel_bulan].copy()
                st.dataframe(df_f[columns[:-1]])
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_f[columns[:-1]].to_excel(writer, sheet_name='Data', index=False)
                    # Otomatis buat grafik di Excel
                    summary = df_f.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                    summary.to_excel(writer, sheet_name='Grafik')
                    chart = writer.book.add_chart({'type': 'column'})
                    for i in range(len(summary.columns)):
                        chart.add_series({'name':['Grafik',0,i+1],'categories':['Grafik',1,0,len(summary),0],'values':['Grafik',1,i+1,len(summary),i+1]})
                    writer.sheets['Grafik'].insert_chart('E2', chart)
                st.download_button("📥 Download Excel + Grafik", output.getvalue(), f"Galva_{sel_bulan}.xlsx")

        with t4: # GALERI (FIXED)
            st.subheader("Rekapan Foto Absensi")
            if os.path.exists(folder_foto):
                f_list = sorted([f for f in os.listdir(folder_foto) if f.endswith('.jpg')], reverse=True)
                if f_list:
                    cols = st.columns(4)
                    for i, f in enumerate(f_list[:24]):
                        with cols[i%4]: st.image(os.path.join(folder_foto, f), caption=f, use_container_width=True)
                else: st.write("Belum ada foto.")

        with t5: # RESET (FIXED)
            st.warning("Hapus semua data?")
            if st.button("🚨 YA, RESET SEMUANYA"):
                if os.path.exists(excel_file): os.remove(excel_file)
                # Hapus folder dan buat baru untuk menghindari error 'PermissionError'
                for d in [folder_foto, folder_penebusan]:
                    if os.path.exists(d):
                        shutil.rmtree(d)
                inisialisasi_folder()
                st.success("Data Bersih!")
                time.sleep(1); st.rerun()