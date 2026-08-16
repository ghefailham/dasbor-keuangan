import streamlit as st
import pandas as pd
import os
from datetime import date

# Konfigurasi Halaman
st.set_page_config(page_title="Money Tracker", page_icon="logo.png.png", layout="wide")

# --- 1. SETUP DATABASE & FUNGSI ---
FILE_DATA = 'data_keuangan.csv'

# Fungsi untuk memuat data
@st.cache_data
def muat_data():
    if not os.path.exists(FILE_DATA):
        return pd.DataFrame(columns=['Tanggal', 'Jenis', 'Kategori', 'Nominal', 'Keterangan'])
    return pd.read_csv(FILE_DATA)

# Fungsi untuk menyimpan data baru
def simpan_transaksi(tanggal, jenis, kategori, nominal, keterangan):
    data_baru = pd.DataFrame({
        'Tanggal': [tanggal],
        'Jenis': [jenis],
        'Kategori': [kategori],
        'Nominal': [nominal],
        'Keterangan': [keterangan]
    })
    data_baru.to_csv(FILE_DATA, mode='a', header=False, index=False)
    st.cache_data.clear() # Hapus cache agar data di tabel langsung terupdate

# --- 2. TAMPILAN SIDEBAR (LOGO & INPUT) ---
with st.sidebar:
    # Menampilkan Logo Transparan di Sidebar
    try:
        # Pastikan file 'logo.png' berlatar belakang transparan
        # Ukurannya akan otomatis disesuaikan dengan lebar sidebar
        st.image("logo.png", use_column_width=True)
    except:
        st.title("💰 Money Tracker")
        
    st.markdown("---")
    st.subheader("➕ Tambah Transaksi Baru")
    
    with st.form("form_transaksi", clear_on_submit=True):
        tanggal_input = st.date_input("Tanggal", value=date.today())
        jenis_input = st.radio("Jenis", ["Pengeluaran", "Pemasukan"], horizontal=True)
        kategori_input = st.selectbox("Kategori", ["Makanan", "Transportasi", "Tagihan", "Gaji", "Zakat/Sedekah", "Investasi", "Lainnya"])
        nominal_input = st.number_input("Nominal (Rp)", min_value=0, step=1000, format="%d")
        keterangan_input = st.text_input("Keterangan Singkat")
        
        submit_tombol = st.form_submit_button("Simpan")

    if submit_tombol:
        if nominal_input > 0:
            simpan_transaksi(tanggal_input, jenis_input, kategori_input, nominal_input, keterangan_input)
            st.success("✅ Berhasil dicatat!")
        else:
            st.error("Nominal harus lebih dari 0!")

# --- 3. TAMPILAN HALAMAN UTAMA (RINGKASAN & TABEL) ---
st.title("📊 Ringkasan Keuangan Anda")

# Muat Data untuk Perhitungan
df = muat_data()

# Perhitungan Ringkasan
total_pemasukan = df[df['Jenis'] == 'Pemasukan']['Nominal'].sum()
total_pengeluaran = df[df['Jenis'] == 'Pengeluaran']['Nominal'].sum()
saldo_akhir = total_pemasukan - total_pengeluaran

# Menampilkan Metrik
col1, col2, col3 = st.columns(3)
col1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.0f}".replace(",", "."))
col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.0f}".replace(",", "."))
col3.metric("Saldo Tersisa", f"Rp {saldo_akhir:,.0f}".replace(",", "."))

st.divider()

st.subheader("📋 Riwayat Transaksi")
# Menampilkan tabel dengan urutan tanggal terbaru di atas
st.dataframe(df.sort_values(by='Tanggal', ascending=False), use_container_width=True, hide_index=True)

# Tambahan footer kecil
st.markdown("---")
st.caption("Aplikasi Manajemen Keuangan Pribadi Syariah v1.0")