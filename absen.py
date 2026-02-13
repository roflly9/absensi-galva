import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import time
import io

# --- PENGAMAN LIBRARY GRAFIK ---
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Absensi Galva Manado", page_icon="🏢", layout="wide")

# BUAT FOLDER FOTO JIKA BELUM ADA
if not os.path.exists("img_data"):
    os.makedirs("img_data")

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
    .stTextInput > div > div > input {
        border: 2px solid #000000 !important;
        border-radius: 10px;
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
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "Foto_Path", "Bukti_Path"]
karyawan_list = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]

def muat_data():
    if os.path.exists(excel_file):
        try:
            df = pd.read_excel(excel_file, engine='openpyxl')
            for col in columns:
                if col not in df.columns: df[col] = None
            df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
            return df
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

df_total = muat_data()

if 'page' not in st.session_state: st.session_state.page = 'Dashboard'
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False

def navigasi(nama_hal):
    st.session_state.page = nama_hal
    st.rerun()

# --- 3. LOGIKA HALAMAN ---

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
        df_total['Denda'] = pd.to_numeric(df_total['Denda'], errors='coerce').fillna(0)
        
        total_setoran = df_total[
            (df_total['Status Denda'] == 'Lunas') & 
            (df_total['Alasan'].fillna('').str.contains('Cash/Transfer'))
        ]['Denda'].sum()
        
        st.metric("Total Dana Pembayaran Denda (Tunai)", f"Rp {int(total_setoran):,}")

        if HAS_PLOTLY:
            waktu_skrg = datetime.now(timezone)
            bulan_skrg = waktu_skrg.month
            tahun_skrg = waktu_skrg.year
            nama_bulan_skrg = waktu_skrg.strftime('%B %Y')

            df_grafik = df_total.copy()
            df_grafik['Tanggal_DT'] = pd.to_datetime(df_grafik['Tanggal'])
            
            telat_df = df_grafik[
                (df_grafik['Status'] == 'TERLAMBAT') & 
                (df_grafik['Tanggal_DT'].dt.month == bulan_skrg) & 
                (df_grafik['Tanggal_DT'].dt.year == tahun_skrg)
            ]
            
            st.markdown(f'<p style="font-size:13px; font-weight:bold; color:#0d47a1; margin-left:10px;">GRAFIK KETERLAMBATAN - {nama_bulan_skrg.upper()}</p>', unsafe_allow_html=True)
            
            if not telat_df.empty:
                grafik_user = telat_df.groupby('Nama').size().reset_index(name='Total Telat')
                grafik_user = grafik_user.sort_values(by='Total Telat', ascending=False)
                
                fig = px.bar(grafik_user, x='Nama', y='Total Telat', color='Total Telat', 
                             color_continuous_scale='Reds', text_auto=True)
                fig.update_layout(margin=dict(l=20, r=20, t=10, b=20), xaxis_title=None, yaxis_title="Jumlah Telat")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"Belum ada keterlambatan di bulan {nama_bulan_skrg}.")
    else:
        st.info("Belum ada data aktivitas.")

elif st.session_state.page == 'Absensi':
    st.markdown('<div class="app-header">📝 FORM ABSENSI</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Menu"): navigasi('Dashboard')
    
    nama = st.selectbox("Nama Karyawan:", karyawan_list)
    opsi = st.radio("Opsi Kehadiran:", ["Hadir di kantor", "Izin Terlambat", "Tidak masuk kantor Cuti/Sakit", "Tugas luar kota", "Langsung ke Customer"], index=0)
    
    waktu_skrg = datetime.now(timezone)
    batas_absen = datetime.strptime("00:05:00", "%H:%M:%S").time() 
    
    alasan, img_data, denda_final, st_text = "", None, 0, ""
    
    if opsi == "Hadir di kantor":
        is_telat = waktu_skrg.time() > batas_absen
        st_text = "TERLAMBAT" if is_telat else "HADIR"
        denda_final = 10000 if is_telat else 0
        card_class = "status-card terlambat" if is_telat else "status-card"
        icon = "⚠️" if is_telat else "✅"
        st.markdown(f"""<div class="{card_class}"><h2 style="margin:5px 0;">{waktu_skrg.strftime('%H:%M:%S')} WITA</h2><span>Status: <b>{icon} {st_text}</b></span> | <b>Denda: Rp {denda_final:,}</b></div>""", unsafe_allow_html=True)
        img_capture = st.camera_input("Ambil Foto Selfie")
        if img_capture: img_data = img_capture.getvalue()
    else:
        st_text = opsi.upper()
        alasan = st.text_area(f"Keterangan {opsi}:")
        img_upload = st.file_uploader("Upload Bukti Foto:", type=['jpg','png','jpeg'])
        if img_upload: img_data = img_upload.getvalue()

    if st.button("🚀 KIRIM ABSENSI"):
        if nama == "Pilih Nama": st.error("Silahkan pilih Nama!")
        elif img_data is None: st.error("Wajib lampirkan foto!")
        else:
            file_name = f"img_data/ABS_{nama}_{waktu_skrg.strftime('%Y%m%d_%H%M%S')}.jpg"
            with open(file_name, "wb") as f: f.write(img_data)
            
            baru = pd.DataFrame([[waktu_skrg.date(), waktu_skrg.strftime("%H:%M:%S"), nama, st_text, alasan, denda_final, "Belum Lunas" if denda_final > 0 else "Lunas", file_name, None]], columns=columns)
            df_total = pd.concat([df_total, baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False, engine='openpyxl')
            st.balloons(); st.success("✅ Terkirim!"); time.sleep(1); navigasi('Dashboard')

elif st.session_state.page == 'Tebus':
    st.markdown('<div class="app-header">💰 MENU TEBUS DENDA</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Dashboard"): navigasi('Dashboard')
    
    user_pilih = st.selectbox("Nama Karyawan:", karyawan_list)
    if user_pilih != "Pilih Nama":
        df_total['Denda'] = pd.to_numeric(df_total['Denda'], errors='coerce').fillna(0)
        unpaid = df_total[(df_total['Nama'] == user_pilih) & (df_total['Status Denda'] == 'Belum Lunas')]
        total_hutang = unpaid['Denda'].sum()
        
        if total_hutang > 0:
            st.markdown(f'<div class="status-card terlambat">TOTAL TUNGGAKAN ANDA: <b>Rp {int(total_hutang):,}</b></div>', unsafe_allow_html=True)
            nominal_tebus = st.number_input("Nominal tebus:", min_value=10000, max_value=int(total_hutang), step=10000)
            metode = st.radio("Metode:", ["Cash/Transfer", "Membersihkan Kantor"])
            
            bukti_files = []
            if metode == "Cash/Transfer":
                f_bayar = st.file_uploader("Upload Bukti Pembayaran:", type=['jpg','png','jpeg'])
                if f_bayar: bukti_files = [f_bayar]
            else:
                f_before = st.file_uploader("Foto Sebelum:", type=['jpg','png','jpeg'], key="up_bfr")
                f_after = st.file_uploader("Foto Sesudah:", type=['jpg','png','jpeg'], key="up_aft")
                if f_before and f_after: bukti_files = [f_before, f_after]

            if st.button("✅ KONFIRMASI"):
                if not bukti_files: st.error("Upload bukti foto!")
                else:
                    paths = []
                    for bf in bukti_files:
                        path_bukti = f"img_data/TBS_{user_pilih}_{int(time.time())}.jpg"
                        with open(path_bukti, "wb") as f: f.write(bf.getvalue())
                        paths.append(path_bukti)
                    
                    idx_unpaid = unpaid.index.tolist()
                    terbayar = 0
                    for idx in idx_unpaid:
                        if terbayar < nominal_tebus:
                            df_total.at[idx, 'Status Denda'] = 'Menunggu Persetujuan'
                            df_total.at[idx, 'Bukti_Path'] = str(paths)
                            df_total.at[idx, 'Alasan'] = f"Metode: {metode} (Penebusan Rp {nominal_tebus:,})"
                            terbayar += df_total.at[idx, 'Denda']
                    df_total.to_excel(excel_file, index=False, engine='openpyxl')
                    st.success("Berhasil!"); time.sleep(1); navigasi('Dashboard')
        else: st.success("Tidak ada tunggakan.")

elif st.session_state.page == 'Admin':
    st.markdown('<div class="app-header">🔐 ADMIN PANEL</div>', unsafe_allow_html=True)
    if st.button("⬅️ Dashboard"): 
        st.session_state.admin_logged_in = False
        navigasi('Dashboard')
    
    if not st.session_state.admin_logged_in:
        pwd = st.text_input("Masukkan Password Admin:", type="password")
        if st.button("🔓 LOGIN ADMIN"):
            if pwd == "galva123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else: st.error("Password Salah!")
    
    if st.session_state.admin_logged_in:
        t1, t2, t3, t4, t5 = st.tabs(["📈 TREN", "📊 DATA", "✅ VERIFIKASI", "📸 FOTO", "⚙️ RESET"])
        
        with t1:
            if not df_total.empty:
                # Filter Data Bulan Berjalan
                waktu_skrg = datetime.now(timezone)
                df_tren = df_total.copy()
                df_tren['Tanggal_DT'] = pd.to_datetime(df_tren['Tanggal'])
                df_bulan_ini = df_tren[
                    (df_tren['Tanggal_DT'].dt.month == waktu_skrg.month) & 
                    (df_tren['Tanggal_DT'].dt.year == waktu_skrg.year)
                ]

                # 1. Grafik Kehadiran dalam sebulan
                st.markdown("### 📊 Ringkasan Kehadiran Bulan Ini")
                if HAS_PLOTLY and not df_bulan_ini.empty:
                    pie_data = df_bulan_ini['Status'].value_counts().reset_index()
                    pie_data.columns = ['Status', 'Jumlah']
                    fig_pie = px.pie(pie_data, values='Jumlah', names='Status', 
                                    color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Belum ada data kehadiran bulan ini.")

                st.divider()

                # 2. Total Dana Belum Lunas & Daftar Nama
                st.markdown("### 💰 Ringkasan Hutang Denda (Belum Lunas)")
                df_total['Denda'] = pd.to_numeric(df_total['Denda'], errors='coerce').fillna(0)
                df_unpaid = df_total[df_total['Status Denda'] == 'Belum Lunas']
                
                total_piutang = df_unpaid['Denda'].sum()
                st.metric("Total Denda Belum Tertagih", f"Rp {int(total_piutang):,}")

                if not df_unpaid.empty:
                    # Kelompokkan per Nama
                    list_hutang = df_unpaid.groupby('Nama')['Denda'].sum().reset_index()
                    list_hutang = list_hutang.sort_values(by='Denda', ascending=False)
                    list_hutang.columns = ['Nama Karyawan', 'Total Hutang (Rp)']
                    
                    # Tampilkan Tabel Sederhana
                    st.table(list_hutang.style.format({"Total Hutang (Rp)": "{:,.0f}"}))
                else:
                    st.success("Luar biasa! Tidak ada tunggakan denda.")
            else:
                st.info("Belum ada data untuk dianalisis.")

        with t2: # --- TAB DATA (FILTER BULAN) ---
            if not df_total.empty:
                df_temp = df_total.copy()
                df_temp['Tanggal'] = pd.to_datetime(df_temp['Tanggal'])
                df_temp['Bulan_Tahun'] = df_temp['Tanggal'].dt.strftime('%B %Y')
                list_bulan = sorted(df_temp['Bulan_Tahun'].unique().tolist(), reverse=True)
                
                c1, c2 = st.columns([2, 2])
                bulan_pilih = c1.selectbox("Pilih Bulan Rekap:", list_bulan)
                
                df_filtered = df_temp[df_temp['Bulan_Tahun'] == bulan_pilih].copy()
                df_display = df_filtered.drop(columns=['Foto_Path', 'Bukti_Path', 'Bulan_Tahun'], errors='ignore')
                
                st.write(f"### Laporan Bulan: {bulan_pilih}")
                st.dataframe(df_display, use_container_width=True)
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_display.to_excel(writer, index=False, sheet_name='Rekap_Bulanan')
                
                st.download_button(
                    label=f"📥 Download Excel - {bulan_pilih}",
                    data=buffer.getvalue(),
                    file_name=f"rekap_galva_{bulan_pilih.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("Belum ada data untuk ditampilkan.")

        with t3: # VERIFIKASI
            pending = df_total[df_total['Status Denda'] == 'Menunggu Persetujuan']
            if not pending.empty:
                for idx, row in pending.iterrows():
                    with st.expander(f"Verifikasi: {row['Nama']} | {row['Alasan']}"):
                        bpath = row.get('Bukti_Path')
                        if bpath and str(bpath) != 'nan':
                            try:
                                paths = eval(bpath) if bpath.startswith('[') else [bpath]
                                if len(paths) > 1:
                                    c1, c2 = st.columns(2)
                                    c1.image(paths[0], caption="Before")
                                    c2.image(paths[1], caption="After")
                                else:
                                    st.image(paths[0], width=300)
                            except: st.warning("File foto tidak ditemukan.")
                        
                        col_a, col_b = st.columns(2)
                        if col_a.button(f"Sahkan (ID:{idx})", key=f"y_{idx}"):
                            df_total.at[idx, 'Status Denda'] = 'Lunas'; df_total.to_excel(excel_file, index=False); st.rerun()
                        if col_b.button(f"Tolak (ID:{idx})", key=f"n_{idx}"):
                            df_total.at[idx, 'Status Denda'] = 'Belum Lunas'; df_total.to_excel(excel_file, index=False); st.rerun()
            else: st.info("Tidak ada verifikasi.")
        
        with t4: # TAB FOTO
            if os.path.exists("img_data"):
                files = sorted([os.path.join("img_data", f) for f in os.listdir("img_data") if f.startswith("ABS_")], reverse=True)
                if files:
                    for i in range(0, len(files), 4):
                        cols = st.columns(4)
                        for j, fpath in enumerate(files[i:i+4]):
                            try:
                                fname = os.path.basename(fpath).replace(".jpg","").split("_")
                                caption = f"{fname[1]} | {fname[2]}"
                                with cols[j]: st.image(fpath, caption=caption, use_container_width=True)
                            except: continue
                else: st.info("Belum ada foto di folder.")

        with t5:
            if st.button("🔥 RESET SEMUA DATA"):
                if os.path.exists(excel_file): os.remove(excel_file)
                import shutil
                if os.path.exists("img_data"): shutil.rmtree("img_data")
                st.rerun()