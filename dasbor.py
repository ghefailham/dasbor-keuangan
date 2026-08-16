import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dasbor Keuangan", page_icon="📊", layout="wide")

# Judul Utama Aplikasi
st.title("📊 Dasbor Analisis Kinerja Keuangan")
st.markdown("Prototipe portofolio untuk memantau tren pendapatan dan profitabilitas perusahaan.")

# --- MEMBUAT DATA TIRUAN (DUMMY DATA) ---
# Di masa depan, data ini bisa diganti dengan file Excel atau CSV betulan
data = {
    'Bulan': ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'],
    'Pendapatan': [150, 200, 180, 220, 250, 230, 280, 310, 290, 340, 360, 400],
    'Pengeluaran': [100, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 250]
}
df = pd.DataFrame(data)

# Menghitung Keuntungan (Profit) secara otomatis menggunakan Pandas
df['Keuntungan'] = df['Pendapatan'] - df['Pengeluaran']
df['Margin_Profit_%'] = round((df['Keuntungan'] / df['Pendapatan']) * 100, 1)

# --- MENAMPILKAN INDIKATOR UTAMA (KPI) ---
st.subheader("Ringkasan Kinerja Tahunan")

# Membuat 3 kolom agar rapi menyamping
kolom1, kolom2, kolom3 = st.columns(3)

with kolom1:
    st.metric(label="Total Pendapatan", value=f"Rp {df['Pendapatan'].sum()} Juta", delta="Target Tercapai")
with kolom2:
    st.metric(label="Total Pengeluaran", value=f"Rp {df['Pengeluaran'].sum()} Juta", delta="-Efisiensi Biaya", delta_color="inverse")
with kolom3:
    st.metric(label="Total Keuntungan Bersih", value=f"Rp {df['Keuntungan'].sum()} Juta")

st.divider() # Garis pembatas

# --- MEMBUAT GRAFIK INTERAKTIF DENGAN PLOTLY ---
st.subheader("Tren Pendapatan vs Pengeluaran Bulanan")

# Membuat grafik garis (Line Chart)
grafik = px.line(
    df, 
    x='Bulan', 
    y=['Pendapatan', 'Pengeluaran', 'Keuntungan'],
    markers=True,
    labels={'value': 'Nominal (Juta Rupiah)', 'variable': 'Keterangan'}
)

# Menampilkan grafik ke dalam web
st.plotly_chart(grafik, use_container_width=True)

# --- MENAMPILKAN TABEL DATA ---
st.subheader("Detail Data Historis")
st.dataframe(df, use_container_width=True)