import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Money Tracker", page_icon="💰", layout="wide")

# --- MENAMPIKAN LOGO ---
# Pastikan file gambar bernama 'logo.png' berada di folder yang sama
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
    try:
        st.image("logo.png", width=200)
    except:
        st.title("💰 Money Tracker Pribadi")

st.markdown("<h3 style='text-align: center; color: gray;'>Aplikasi Manajemen Keuangan Pribadi</h3>", unsafe_allow_html=True)
st.divider()

# --- 1. SETUP DATABASE ---
FILE_DATA = 'data_keuangan.csv'
if not os.path.exists(FILE_DATA):
    df_awal = pd.DataFrame(columns=['Tanggal', 'Jenis', 'Kategori', 'Nominal', 'Keterangan'])
    df_awal.to_csv(FILE_DATA, index=False)

# --- 2. FUNGSI LOGIKA PERHITUNGAN ---
df = pd.read_csv(FILE_DATA)

pemasukan = df[df['Jenis'] == 'Pemasukan']['Nominal'].sum() if not df.empty else 0
pengeluaran = df[df['Jenis'] == 'Pengeluaran']['Nominal'].sum() if not df.empty else 0
saldo = pemasukan - pengeluaran

# --- 3. TAMPILAN RINGKASAN SALDO ---
st.subheader("📊 Ringkasan Keuangan")
col1, col2, col3 = st.columns(3)
col1.metric("Total Pemasukan", f"Rp {pemasukan:,.0f}")
col2.metric("Total Pengeluaran", f"Rp {pengeluaran:,.0f}")
col3.metric("Saldo Tersisa", f"Rp {saldo:,.0f}")

st.divider()

# --- 4. FORMULIR INPUT DATA ---
with st.expander("➕ Tambah Transaksi Baru"):
    with st.form("form_transaksi", clear_on_submit=True):
        tanggal = st.date_input("Tanggal")
        jenis = st.radio("Jenis", ["Pengeluaran", "Pemasukan"], horizontal=True)
        kategori = st.selectbox("Kategori", ["Makanan", "Transportasi", "Tagihan", "Gaji", "Zakat/Sedekah", "Lainnya"])
        nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
        keterangan = st.text_input("Keterangan")
        
        tombol_simpan = st.form_submit_button("Simpan Transaksi")

    if tombol_simpan:
        if nominal > 0:
            data_baru = pd.DataFrame([[tanggal, jenis, kategori, nominal, keterangan]], 
                                     columns=['Tanggal', 'Jenis', 'Kategori', 'Nominal', 'Keterangan'])
            data_baru.to_csv(FILE_DATA, mode='a', header=False, index=False)
            st.success("✅ Transaksi berhasil dicatat!")
            st.rerun()
        else:
            st.error("Nominal harus lebih dari 0!")

# --- 5. TABEL RIWAYAT ---
st.subheader("📋 Riwayat Transaksi")
if not df.empty:
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
else:
    st.info("Belum ada data transaksi. Silakan tambahkan transaksi baru melalui menu di atas.")