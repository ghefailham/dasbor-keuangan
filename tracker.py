import streamlit as st
import pandas as pd
import os
from datetime import date

# Konfigurasi Halaman (Menggunakan emoji untuk tab agar stabil & tidak error)
st.set_page_config(
    page_title="Money Tracker",
    page_icon="favicon.png",  # Menggunakan file gambar untuk tab browser
    layout="wide"
)
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
        st.image("favicon.png", use_column_width=True) # Memanggil file yang sama
    except:
        st.subheader("💰 Money Tracker")        
    st.markdown("---")
    st.subheader("➕ Tambah Transaksi Baru")
    
    with st.form("form_transaksi", clear_on_submit=True):
        tanggal_input = st.date_input("Tanggal", value=date.today())
        jenis_input = st.radio("Jenis", ["Pengeluaran", "Pemasukan"], horizontal=True)
        kategori_input = st.selectbox("Kategori", ["Makanan", "Transportasi", "Tagihan", "Gaji", "Zakat/Sedekah", "Investasi", "Lainnya"])
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
    st.info("Belum ada data transaksi yang tercatat. Silakan tambah melalui menu di sidebar.")

st.markdown("---")
st.caption("Aplikasi Manajemen Keuangan Pribadi Syariah v1.0")