import streamlit as st
import pandas as pd
import os
import base64
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

/* Desain Kotak Info (st.info) - Latar Putih Tipis & Teks Putih */
div[data-testid="stNotification"] {{
    background-color: rgba(255, 255, 255, 0.2) !important; /* Latar putih transparan */
    border: 1px solid rgba(255, 255, 255, 0.5) !important; /* Garis tepi putih */
    border-radius: 10px;
}}

/* Mengubah semua teks di dalam kotak info menjadi putih */
div[data-testid="stNotification"] div, 
div[data-testid="stNotification"] p, 
div[data-testid="stNotification"] span {{
    color: #ffffff !important; /* Warna teks putih bersih */
    font-weight: 600 !important;
}}

/* Memastikan ikon di dalam kotak info juga berwarna putih */
div[data-testid="stNotification"] svg {{
    fill: #ffffff !important;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- SETUP DATABASE ---
FILE_DATA = 'data_keuangan.csv'

@st.cache_data
def muat_data():
    if not os.path.exists(FILE_DATA):
        return pd.DataFrame(columns=['Tanggal', 'Jenis', 'Kategori', 'Nominal', 'Keterangan'])
    return pd.read_csv(FILE_DATA)

def simpan_transaksi(tanggal, jenis, kategori, nominal, keterangan):
    data_baru = pd.DataFrame({
        'Tanggal': [str(tanggal)],
        'Jenis': [jenis],
        'Kategori': [kategori],
        'Nominal': [float(nominal)],
        'Keterangan': [keterangan]
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
    "Jajan",      
    "Lainnya"
])
        nominal_input = st.number_input("Nominal (Rp)", min_value=0, step=1000, format="%d")
        keterangan_input = st.text_input("Keterangan Singkat")
        
        submit_tombol = st.form_submit_button("Simpan Transaksi")

    if submit_tombol:
        if nominal_input > 0:
            simpan_transaksi(tanggal_input, jenis_input, kategori_input, nominal_input, keterangan_input)
            st.success("✅ Transaksi berhasil dicatat!")
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
    st.dataframe(df.sort_values(by='Tanggal', ascending=False), use_container_width=True, hide_index=True)
else:
    st.markdown("""
        <div style="background-color: rgba(255, 255, 255, 0.25); border: 1px solid rgba(255, 255, 255, 0.6); padding: 15px; border-radius: 10px; text-align: center; backdrop-filter: blur(5px);">
            <p style="color: #ffffff !important; font-weight: 600; font-size: 16px; margin: 0;">ℹ️ Belum ada data transaksi yang tercatat. Silakan tambah melalui menu di sidebar.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Aplikasi Manajemen Keuangan Pribadi Syariah v1.0")