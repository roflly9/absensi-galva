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

# Fungsi inisialisasi folder agar sistem tidak error
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
            # Toleransi 5 menit (08:05)
            if (waktu_sekarang.hour > 8 or (waktu_sekarang.hour == 8 and waktu_sekarang.minute > 5)):
                st.warning("⚠️ Status Anda: **TERLAMBAT** (Denda Rp 10.000)")
            else:
                st.success("✅ Status Anda: **TEPAT WAKTU**")

    alasan = ""
    if opsi_absen in ["Tugas Luar Kota", "Langsung ke Customer"]:
        alasan = st.text_input("📍 Masukkan Lokasi/Tujuan (Nama Toko/Instansi):")
    elif opsi_absen != "Hadir di Kantor":
        alasan = st.text_area("📝 Masukkan Alasan / Catatan (Sakit/Cuti/Izin):")
    
    img_file = st.camera_input("Ambil foto untuk absen") if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] else st.file_uploader("Upload Bukti (Opsional)", type=['jpg', 'jpeg', 'png'])

    if nama != "Pilih Nama":
        # Syarat simpan: Harus ada foto jika Hadir/Tugas Luar/Customer
        ready_to_save = (opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] and img_file is not None) or \
                        (opsi_absen in ["Izin Terlambat", "Tidak Masuk Kantor Cuti/Sakit"])

        if ready_to_save:
            if st.button("🚀 KIRIM ABSENSI SEKARANG"):
                with st.spinner('Menyimpan data...'):
                    waktu_klik = datetime.now(timezone)
                    tgl_absen = waktu_klik.strftime("%Y-%m-%d")
                    jam_absen = waktu_klik.strftime("%H:%M:%S")
                    
                    denda = 0
                    status_denda = "Lunas"
                    if opsi_absen == "Hadir di Kantor":
                        if (waktu_klik.hour > 8 or (waktu_klik.hour == 8 and waktu_klik.minute > 5)):
                            status = "TERLAMBAT"
                            denda = 10000
                            status_denda = "Belum Lunas"
                        else:
                            status = "TEPAT WAKTU"
                    else:
                        status = opsi_absen.upper()

                    data_baru = pd.DataFrame([[tgl_absen, jam_absen, nama, status, alasan, denda, status_denda, ""]], columns=columns)
                    df_total = pd.concat([df_total, data_baru], ignore_index=True)
                    df_total.to_excel(excel_file, index=False)

                    if img_file:
                        nama_file = f"{tgl_absen}_{nama}_{status}_{waktu_klik.strftime('%H%M%S')}.jpg".replace(" ", "_")
                        with open(os.path.join(folder_foto, nama_file), "wb") as f:
                            f.write(img_file.getbuffer())

                    st.balloons()
                    st.success(f"✅ BERHASIL! Absensi {nama} dicatat.")
                    time.sleep(2)
                    st.rerun()

# --- HALAMAN TEBUS DENDA ---
elif menu == "Tebus Denda":
    st.subheader("Penebusan Denda Keterlambatan")
    nama_tebus = st.selectbox("Siapa yang ingin menebus?", Karyawan_List)
    if nama_tebus != "Pilih Nama":
        idx_hutang = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_hutang = df_total.loc[idx_hutang, 'Denda'].sum()
        
        if total_hutang > 0:
            st.error(f"Total Akumulasi Denda Anda: Rp {total_hutang:,}")
            
            mode_tebus = st.radio("Pilih Jumlah:", ["Tebus Semua", "Cicil Sebagian"])
            if mode_tebus == "Cicil Sebagian":
                jumlah_dibayar = st.number_input("Nominal Pembayaran (Kelipatan 10rb):", min_value=10000, max_value=int(total_hutang), step=10000)
            else:
                jumlah_dibayar = total_hutang

            metode = st.radio("Metode Penebusan:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            
            file_bukti = []
            if metode == "Bayar Tunai / Transfer":
                bt = st.file_uploader("Upload Bukti Transfer / Foto Uang Tunai", type=['jpg','png','jpeg'])
                if bt: file_bukti.append(bt)
            else:
                st.info("Ambil foto Kondisi Sebelum dan Sesudah.")
                f_seb = st.camera_input("Foto Sebelum (Before)")
                f_ses = st.camera_input("Foto Sesudah (After)")
                if f_seb and f_ses: file_bukti.extend([f_seb, f_ses])
            
            if st.button("Konfirmasi & Ajukan Penebusan"):
                if not file_bukti:
                    st.warning("⚠️ Mohon lampirkan bukti foto!")
                else:
                    # Buat ID unik untuk grup foto ini
                    id_unik = f"{nama_tebus}_{datetime.now(timezone).strftime('%Y%m%d_%H%M%S')}"
                    for i, f in enumerate(file_bukti):
                        with open(os.path.join(folder_penebusan, f"{id_unik}_{i}.jpg"), "wb") as file_simpan:
                            file_simpan.write(f.getbuffer())

                    # Update status ke Menunggu Approval berdasarkan nominal
                    jumlah_terpenuhi = 0
                    for idx in idx_hutang:
                        if jumlah_terpenuhi < jumlah_dibayar:
                            df_total.at[idx, 'Status Denda'] = f"Menunggu Approval ({metode})"
                            df_total.at[idx, 'ID_Tebus'] = id_unik
                            jumlah_terpenuhi += df_total.at[idx, 'Denda']
                    
                    df_total.to_excel(excel_file, index=False)
                    st.success("✅ Pengajuan penebusan telah dikirim. Menunggu verifikasi Admin.")
                    time.sleep(2)
                    st.rerun()
        else:
            st.success("Anda tidak memiliki tunggakan denda.")

# --- HALAMAN ADMIN ---
elif menu == "Login Admin":
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🔔 Verifikasi Penebusan", "📑 Laporan Excel", "📸 Galeri Foto", "⚙️ Pengaturan"])
        
        with tab1: # DASHBOARD FIX
            st.subheader("Statistik Kehadiran")
            if not df_total.empty:
                c1, c2, c3 = st.columns(3)
                total_t = len(df_total[df_total['Status'] == 'TERLAMBAT'])
                denda_unpaid = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
                need_verify = len(df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)])

                c1.metric("Total Terlambat", f"{total_t} Kali")
                c2.metric("Denda Belum Bayar", f"Rp {denda_unpaid:,}")
                c3.metric("Perlu Verifikasi", f"{need_verify} Data")

                st.divider()
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Top Terlambat (Karyawan)**")
                    st.bar_chart(df_total[df_total['Status'] == 'TERLAMBAT'].groupby('Nama').size())
                with col_b:
                    st.write("**Distribusi Status Kehadiran**")
                    st.bar_chart(df_total.groupby('Status').size())
            else:
                st.info("Belum ada data absensi.")

        with tab2: # VERIFIKASI DENDA
            st.subheader("Persetujuan Penebusan Denda")
            pending_list = df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)].groupby('ID_Tebus').first()
            
            if pending_list.empty:
                st.info("Tidak ada pengajuan penebusan yang perlu diperiksa.")
            else:
                for id_t, row in pending_list.iterrows():
                    with st.expander(f"Penebusan: {row['Nama']} ({row['Status Denda']})"):
                        # Cari semua foto dengan ID tersebut
                        bukti_files = [f for f in os.listdir(folder_penebusan) if f.startswith(id_t)]
                        cols_img = st.columns(len(bukti_files) if bukti_files else 1)
                        for i, b_file in enumerate(bukti_files):
                            cols_img[i].image(os.path.join(folder_penebusan, b_file), use_container_width=True)
                        
                        btn_col1, btn_col2 = st.columns(2)
                        if btn_col1.button("✅ SETUJUI", key=f"acc_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Lunas (Approved)"
                            df_total.to_excel(excel_file, index=False)
                            st.success("Telah disetujui!")
                            st.rerun()
                        if btn_col2.button("❌ TOLAK", key=f"rej_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Belum Lunas"
                            df_total.to_excel(excel_file, index=False)
                            st.error("Penebusan ditolak.")
                            st.rerun()

        with tab3: # LAPORAN EXCEL
            if not df_total.empty:
                df_total['Bulan_Tahun'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%B %Y')
                list_bulan = df_total['Bulan_Tahun'].unique()
                bulan_pilih = st.selectbox("Pilih Bulan Laporan:", list_bulan)
                df_filter = df_total[df_total['Bulan_Tahun'] == bulan_pilih].copy()
                st.dataframe(df_filter[columns[:-1]])

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_filter[columns[:-1]].to_excel(writer, sheet_name='Data Absensi', index=False)
                    
                    # Ringkasan untuk Grafik
                    summary = df_filter.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                    summary.to_excel(writer, sheet_name='Statistik')
                    
                    workbook  = writer.book
                    worksheet = writer.sheets['Statistik']
                    chart = workbook.add_chart({'type': 'column'})
                    
                    for i in range(len(summary.columns)):
                        chart.add_series({
                            'name':       ['Statistik', 0, i + 1],
                            'categories': ['Statistik', 1, 0, len(summary), 0],
                            'values':     ['Statistik', 1, i + 1, len(summary), i + 1],
                        })
                    worksheet.insert_chart('G2', chart)
                
                st.download_button("📥 Download Laporan " + bulan_pilih, data=output.getvalue(), file_name=f"Laporan_Galva_{bulan_pilih}.xlsx")

        with tab4: # GALERI FOTO (FIXED)
            st.subheader("Galeri Foto Absensi (24 Terbaru)")
            if os.path.exists(folder_foto):
                daftar_foto = sorted([f for f in os.listdir(folder_foto) if f.endswith('.jpg')], reverse=True)
                if daftar_foto:
                    cols_galeri = st.columns(4)
                    for idx, f_name in enumerate(daftar_foto[:24]):
                        with cols_galeri[idx % 4]:
                            st.image(os.path.join(folder_foto, f_name), caption=f_name, use_container_width=True)
                else:
                    st.write("Belum ada foto absensi.")

        with tab5: # PENGATURAN RESET (FIXED)
            st.error("⚠️ TINDAKAN BERBAHAYA")
            if st.button("🚨 RESET SEMUA DATA & FOTO"):
                if os.path.exists(excel_file): os.remove(excel_file)
                for d in [folder_foto, folder_penebusan]:
                    if os.path.exists(d): shutil.rmtree(d)
                inisialisasi_folder()
                st.success("Sistem telah di-reset ke kondisi awal.")
                time.sleep(1)
                st.rerun()