import streamlit as st
import pandas as pd
import os
import base64
import time
from datetime import date

# Konfigurasi Halaman menggunakan favicon.png
st.set_page_config(
    page_title="Money Tracker",
    page_icon="favicon.png", 
    layout="wide"
)

# --- FUNGSI UNTUK MEMASANG BACKGROUND (HALAMAN & SIDEBAR) ---
def get_base64_image(png_file):
    if os.path.exists(png_file):
        with open(png_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

bg_main = get_base64_image("background.png")
bg_sidebar = get_base64_image("sidebar-bg.png")

# --- KUSTOMISASI CSS ---
css = f"""
<style>
/* Background Halaman Utama */
.stApp {{
    background-image: url("data:image/png;base64,{bg_main}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

/* Background Sidebar */
[data-testid="stSidebar"] {{
    background-image: url("data:image/png;base64,{bg_sidebar}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- SETUP DATABASE & FOLDER UPLOAD ---
FILE_DATA = 'data_keuangan.csv'
FOLDER_UPLOAD = 'uploads'

if not os.path.exists(FOLDER_UPLOAD):
    os.makedirs(FOLDER_UPLOAD)

@st.cache_data
def muat_data():
    if not os.path.exists(FILE_DATA):
        return pd.DataFrame(columns=['Tanggal', 'Jenis', 'Kategori', 'Nominal', 'Keterangan', 'Bukti'])
    df = pd.read_csv(FILE_DATA)
    # Pastikan kolom 'Bukti' ada jika file lama belum ada kolomnya
    if 'Bukti' not in df.columns:
        df['Bukti'] = ''
    return df

def simpan_transaksi(tanggal, jenis, kategori, nominal, keterangan, file_bukti):
    nama_file_unik = ""
    
    if file_bukti is not None:
        # Buat nama file unik berdasarkan waktu agar tidak bentrok
        nama_file_unik = f"{int(time.time())}_{file_bukti.name}"
        path_file = os.path.join(FOLDER_UPLOAD, nama_file_unik)
        with open(path_file, "wb") as f:
            f.write(file_bukti.getbuffer())

    data_baru = pd.DataFrame({
        'Tanggal': [str(tanggal)],
        'Jenis': [jenis],
        'Kategori': [kategori],
        'Nominal': [float(nominal)],
        'Keterangan': [keterangan],
        'Bukti': [nama_file_unik]
    })
    data_baru.to_csv(FILE_DATA, mode='a', header=not os.path.exists(FILE_DATA), index=False)
    st.cache_data.clear()

# --- SIDEBAR: LOGO & INPUT ---
with st.sidebar:
    try:
        st.image("favicon.png", use_container_width=True)
    except:
        st.subheader("💰 Money Tracker")
        
    st.markdown("---")
    st.subheader("➕ Tambah Transaksi Baru")
    
    with st.form("form_transaksi", clear_on_submit=True):
        tanggal_input = st.date_input("Tanggal", value=date.today())
        jenis_input = st.radio("Jenis", ["Pengeluaran", "Pemasukan"], horizontal=True)
        kategori_input = st.selectbox("Kategori", [
            "Makanan", 
            "Transportasi", 
            "Tagihan", 
            "Gaji", 
            "Zakat/Sedekah", 
            "Investasi", 
            "Kesehatan", 
            "Pendidikan",
            "Ngopi",
            "Lainnya"
        ])
        nominal_input = st.number_input("Nominal (Rp)", min_value=0, step=1000, format="%d")
        keterangan_input = st.text_input("Keterangan Singkat")
        
        # --- INPUT FILE BUKTI TRANSAKSI ---
        file_bukti_input = st.file_uploader("Upload Bukti (Opsional)", type=["png", "jpg", "jpeg"])
        
        submit_tombol = st.form_submit_button("Simpan Transaksi")

    if submit_tombol:
        if nominal_input > 0:
            simpan_transaksi(tanggal_input, jenis_input, kategori_input, nominal_input, keterangan_input, file_bukti_input)
            st.success("✅ Transaksi & Bukti berhasil dicatat!")
            st.rerun()
        else:
            st.error("Nominal harus lebih dari 0!")

# --- HALAMAN UTAMA ---
st.title("📊 Ringkasan Keuangan Anda")

df = muat_data()

# Hitung Keuangan
if not df.empty:
    total_pemasukan = df[df['Jenis'] == 'Pemasukan']['Nominal'].sum()
    total_pengeluaran = df[df['Jenis'] == 'Pengeluaran']['Nominal'].sum()
    saldo_akhir = total_pemasukan - total_pengeluaran
else:
    total_pemasukan = 0
    total_pengeluaran = 0
    saldo_akhir = 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.0f}".replace(",", "."))
col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.0f}".replace(",", "."))
col3.metric("Saldo Tersisa", f"Rp {saldo_akhir:,.0f}".replace(",", "."))

st.divider()

st.subheader("📋 Riwayat Transaksi")
if not df.empty:
    # Tampilkan tabel data
    st.dataframe(df.sort_values(by='Tanggal', ascending=False), use_container_width=True, hide_index=True)
    
    # Fitur melihat foto bukti transaksi yang diunggah
    st.markdown("### 🖼️ Lihat Bukti Transaksi")
    daftar_bukti = df[df['Bukti'].notna() & (df['Bukti'] != '')]['Bukti'].tolist()
    
    if daftar_bukti:
        pilih_bukti = st.selectbox("Pilih file bukti transaksi yang ingin dilihat:", daftar_bukti)
        if pilih_bukti:
            path_tampil = os.path.join(FOLDER_UPLOAD, pilih_bukti)
            if os.path.exists(path_tampil):
                st.image(path_tampil, caption=f"Bukti: {pilih_bukti}", width=300)
            else:
                st.warning("File gambar bukti tidak ditemukan di server.")
    else:
        st.info("Belum ada transaksi yang menyertakan foto bukti.")
else:
    st.markdown("""
        <div style="background-color: rgba(255, 255, 255, 0.25); border: 1px solid rgba(255, 255, 255, 0.6); padding: 15px; border-radius: 10px; text-align: center; backdrop-filter: blur(5px);">
            <p style="color: #ffffff !important; font-weight: 600; font-size: 16px; margin: 0;">ℹ️ Belum ada data transaksi yang tercatat. Silakan tambah melalui menu di sidebar.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Aplikasi Manajemen Keuangan Pribadi Syariah v1.0")