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

for folder in [folder_foto, folder_penebusan]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- INISIALISASI DATAFRAME ---
# Kolom ditambah 'ID_Tebus' untuk mencocokkan foto dengan transaksi denda
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
    
    img_file = st.camera_input("Ambil foto absen") if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] else st.file_uploader("Upload Bukti", type=['jpg','png','jpeg','pdf'])

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
                        with open(os.path.join(folder_foto, f"{waktu_klik.strftime('%Y%m%d_%H%M%S')}_{nama}.jpg"), "wb") as f:
                            f.write(img_file.getbuffer())
                    st.success("✅ Absensi berhasil dicatat.")
                    time.sleep(1); st.rerun()

# --- HALAMAN TEBUS DENDA ---
elif menu == "Tebus Denda":
    st.subheader("Penebusan Denda")
    nama_tebus = st.selectbox("Siapa yang menebus?", Karyawan_List)
    if nama_tebus != "Pilih Nama":
        # Ambil denda yang benar-benar Belum Lunas (bukan yang sedang menunggu approval)
        idx_hutang = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_hutang = df_total.loc[idx_hutang, 'Denda'].sum()
        
        if total_hutang > 0:
            st.error(f"Total Denda: Rp {total_hutang:,}")
            metode = st.radio("Metode:", ["Bayar Tunai / Transfer", "Membersihkan Kantor"])
            
            file_bukti = []
            if metode == "Bayar Tunai / Transfer":
                bt = st.file_uploader("Upload Bukti Bayar", type=['jpg','png','jpeg'])
                if bt: file_bukti.append(bt)
            else:
                f_seb = st.camera_input("Foto Sebelum")
                f_ses = st.camera_input("Foto Sesudah")
                if f_seb and f_ses: file_bukti.extend([f_seb, f_ses])
            
            if st.button("Ajukan Penebusan"):
                if not file_bukti:
                    st.warning("⚠️ Lampirkan bukti foto!")
                else:
                    id_unik = f"{nama_tebus}_{datetime.now(timezone).strftime('%H%M%S')}"
                    for i, f in enumerate(file_bukti):
                        with open(os.path.join(folder_penebusan, f"{id_unik}_{i}.jpg"), "wb") as f_save:
                            f_save.write(f.getbuffer())
                    
                    # Set status ke 'Menunggu Persetujuan'
                    df_total.loc[idx_hutang, 'Status Denda'] = f"Menunggu Persetujuan ({metode})"
                    df_total.loc[idx_hutang, 'ID_Tebus'] = id_unik
                    df_total.to_excel(excel_file, index=False)
                    st.info("✅ Pengajuan dikirim! Menunggu konfirmasi Admin.")
                    time.sleep(2); st.rerun()
        else:
            st.success("Tidak ada denda.")

# --- HALAMAN ADMIN ---
elif menu == "Login Admin":
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🔔 Persetujuan Denda", "📑 Laporan", "📸 Galeri", "⚙️ Pengaturan"])
        
        with tab1: # DASHBOARD
            if not df_total.empty:
                c1, c2 = st.columns(2)
                c1.metric("Total Denda Belum Lunas", f"Rp {df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum():,}")
                c2.metric("Menunggu Approval", len(df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)]))
                st.bar_chart(df_total[df_total['Status'] == 'TERLAMBAT'].groupby('Nama').size())

        with tab2: # PERSETUJUAN DENDA
            st.subheader("Verifikasi Penebusan Denda")
            pending = df_total[df_total['Status Denda'].str.contains("Menunggu", na=False)].groupby('ID_Tebus').first()
            
            if pending.empty:
                st.write("Tidak ada pengajuan penebusan.")
            else:
                for id_t, row in pending.iterrows():
                    with st.expander(f"Penebusan: {row['Nama']} - {row['Status Denda']}"):
                        st.write(f"Tanggal Pengajuan: {row['Tanggal']}")
                        # Tampilkan Foto Bukti
                        bukti_files = [f for f in os.listdir(folder_penebusan) if f.startswith(id_t)]
                        cols = st.columns(len(bukti_files) if bukti_files else 1)
                        for i, b_file in enumerate(bukti_files):
                            cols[i].image(os.path.join(folder_penebusan, b_file), width=300)
                        
                        ca, cb = st.columns(2)
                        if ca.button("✅ SETUJUI", key=f"acc_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Lunas (Approved)"
                            df_total.to_excel(excel_file, index=False)
                            st.rerun()
                        if cb.button("❌ TOLAK", key=f"rej_{id_t}"):
                            df_total.loc[df_total['ID_Tebus'] == id_t, 'Status Denda'] = "Belum Lunas"
                            df_total.to_excel(excel_file, index=False)
                            st.rerun()

        with tab3: # LAPORAN EXCEL
            df_total['Bulan'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%B %Y')
            bulan = st.selectbox("Pilih Bulan", df_total['Bulan'].unique())
            df_f = df_total[df_total['Bulan'] == bulan].copy()
            st.dataframe(df_f[columns[:-1]])
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_f[columns[:-1]].to_excel(writer, sheet_name='Data', index=False)
                summary = df_f.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                summary.to_excel(writer, sheet_name='Grafik')
                chart = writer.book.add_chart({'type': 'column'})
                for i in range(len(summary.columns)):
                    chart.add_series({'name':['Grafik',0,i+1],'categories':['Grafik',1,0,len(summary),0],'values':['Grafik',1,i+1,len(summary),i+1]})
                writer.sheets['Grafik'].insert_chart('E2', chart)
            st.download_button("📥 Download Excel", output.getvalue(), f"Laporan_{bulan}.xlsx")

        with tab4: # GALERI FOTO ABSENSI
            st.subheader("Foto Absensi Terbaru")
            files = sorted(os.listdir(folder_foto), reverse=True)
            if files:
                c = st.columns(4)
                for i, f in enumerate(files[:12]):
                    with c[i%4]: st.image(os.path.join(folder_foto, f), caption=f)

        with tab5: # RESET
            if st.button("🚨 RESET TOTAL"):
                if os.path.exists(excel_file): os.remove(excel_file)
                shutil.rmtree(folder_foto); os.makedirs(folder_foto)
                shutil.rmtree(folder_penebusan); os.makedirs(folder_penebusan)
                st.rerun()