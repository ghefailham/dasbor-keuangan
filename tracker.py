import streamlit as st
import pandas as pd
import os
import base64
import time
from datetime import date
from sqlalchemy import text

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Money Tracker", page_icon="favicon.png", layout="wide")

def get_base64_image(png_file):
    if os.path.exists(png_file):
        with open(png_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

css = f"""
<style>
.stApp {{ background-image: url("data:image/png;base64,{get_base64_image('background.png')}"); background-size: cover; background-attachment: fixed; }}
[data-testid="stSidebar"] {{ background-image: url("data:image/png;base64,{get_base64_image('sidebar-bg.png')}"); background-size: cover; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- KONEKSI DATABASE ---
try:
    conn = st.connection("postgresql", type="sql")
except Exception as e:
    st.error("Gagal terhubung ke Database.")
    st.stop()

def muat_data():
    try:
        df = conn.query("SELECT * FROM transaksi", ttl=0)
        return df
    except:
        return pd.DataFrame(columns=['Tanggal', 'Jenis', 'Kategori', 'Nominal', 'Keterangan', 'Bukti'])

def simpan_ke_database(df_bersih):
    # Gunakan koneksi langsung untuk menjalankan SQL mentah agar benar-benar terhapus
    with conn.engine.connect() as connection:
        connection.execute(text("DELETE FROM transaksi"))
        connection.commit()
        if not df_bersih.empty:
            df_bersih.to_sql("transaksi", con=connection, if_exists="append", index=False)
            connection.commit()

# --- INPUT DATA ---
with st.sidebar:
    st.subheader("➕ Tambah Transaksi")
    with st.form("form_transaksi", clear_on_submit=True):
        tanggal = st.date_input("Tanggal", date.today())
        jenis = st.radio("Jenis", ["Pengeluaran", "Pemasukan"], horizontal=True)
        kategori = st.selectbox("Kategori", ["Makanan", "Transportasi", "Tagihan", "Gaji", "Zakat/Sedekah", "Investasi", "Kesehatan", "Pendidikan", "Lainnya"])
        nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
        keterangan = st.text_input("Keterangan")
        file_bukti = st.file_uploader("Upload Bukti", type=["png", "jpg", "jpeg"])
        if st.form_submit_button("Simpan"):
            bukti_base64 = base64.b64encode(file_bukti.getvalue()).decode('utf-8') if file_bukti else ""
            df = muat_data()
            new_row = pd.DataFrame({'Tanggal': [str(tanggal)], 'Jenis': [jenis], 'Kategori': [kategori], 'Nominal': [nominal], 'Keterangan': [keterangan], 'Bukti': [bukti_base64]})
            simpan_ke_database(pd.concat([df, new_row], ignore_index=True))
            st.rerun()

# --- RIWAYAT ---
st.title("📊 Ringkasan Keuangan")
df = muat_data()

if not df.empty:
    # Persiapan Tampilan
    df_tampil = df.copy()
    df_tampil.insert(0, 'No', range(1, len(df_tampil) + 1))
    df_tampil.insert(0, '📸 Lihat', False)

    df_edited = st.data_editor(df_tampil, use_container_width=True, hide_index=True, num_rows="dynamic")

    if st.button("💾 Simpan Perubahan Riwayat"):
        # Hapus kolom UI agar data yang masuk ke database murni
        df_final = df_edited.drop(columns=['No', '📸 Lihat'])
        simpan_ke_database(df_final)
        st.success("✅ Tersimpan!")
        st.rerun()

    # Logika Lihat Bukti
    baris_terpilih = df_edited[df_edited['📸 Lihat'] == True]
    if not baris_terpilih.empty:
        bukti = baris_terpilih.iloc[0]['Bukti']
        if bukti:
            st.image(base64.b64decode(bukti), caption="Bukti Transaksi", width=400)
        else:
            st.info("Tidak ada bukti untuk transaksi ini.")
else:
    st.write("Belum ada data.")