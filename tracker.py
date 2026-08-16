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
    if 'Bukti' not in df.columns:
        df['Bukti'] = ''
    return df

def simpan_data_ke_csv(df):
    df.to_csv(FILE_DATA, index=False)
    st.cache_data.clear()

def simpan_transaksi(tanggal, jenis, kategori, nominal, keterangan, file_bukti):
    nama_file_unik = ""
    if file_bukti is not None:
        nama_file_unik = f"{int(time.time())}_{file_bukti.name}"
        path_file = os.path.join(FOLDER_UPLOAD, nama_file_unik)
        with open(path_file, "wb") as f:
            f.write(file_bukti.getbuffer())

    df = muat_data()
    data_baru = pd.DataFrame({
        'Tanggal': [str(tanggal)],
        'Jenis': [jenis],
        'Kategori': [kategori],
        'Nominal': [float(nominal)],
        'Keterangan': [keterangan],
        'Bukti': [nama_file_unik]
    })
    df = pd.concat([df, data_baru], ignore_index=True)
    simpan_data_ke_csv(df)

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
            "Makanan", "Transportasi", "Tagihan", "Gaji", 
            "Zakat/Sedekah", "Investasi", "Kesehatan", "Pendidikan", "Lainnya"
        ])
        nominal_input = st.number_input("Nominal (Rp)", min_value=0, step=1000, format="%d")
        keterangan_input = st.text_input("Keterangan Singkat")
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

st.subheader("📋 Riwayat & Kelola Transaksi")

if not df.empty:
    # Tampilkan tabel data
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("⚙️ Edit atau Hapus Transaksi")
    
    # Pilih baris transaksi yang ingin diedit/dihapus berdasarkan index
    pilihan_index = st.selectbox("Pilih nomor baris transaksi yang ingin diubah/dihapus:", df.index.tolist())
    
    if pilihan_index is not None:
        row_pilih = df.loc[pilihan_index]
        
        with st.form("form_edit"):
            st.write(f"**Mengubah Transaksi Baris ke-{pilihan_index}**")
            edit_tanggal = st.date_input("Tanggal", value=pd.to_datetime(row_pilih['Tanggal']).date())
            edit_jenis = st.selectbox("Jenis", ["Pengeluaran", "Pemasukan"], index=0 if row_pilih['Jenis']=='Pengeluaran' else 1)
            edit_kategori = st.text_input("Kategori", value=row_pilih['Kategori'])
            edit_nominal = st.number_input("Nominal (Rp)", min_value=0.0, value=float(row_pilih['Nominal']), step=1000.0)
            edit_keterangan = st.text_input("Keterangan", value=row_pilih['Keterangan'])
            
            col_btn1, col_btn2 = st.columns(2)
            simpan_edit = col_btn1.form_submit_button("💾 Simpan Perubahan")
            hapus_data = col_btn2.form_submit_button("🗑️ Hapus Transaksi Ini")
            
            if simpan_edit:
                df.at[pilihan_index, 'Tanggal'] = str(edit_tanggal)
                df.at[pilihan_index, 'Jenis'] = edit_jenis
                df.at[pilihan_index, 'Kategori'] = edit_kategori
                df.at[pilihan_index, 'Nominal'] = edit_nominal
                df.at[pilihan_index, 'Keterangan'] = edit_keterangan
                simpan_data_ke_csv(df)
                st.success("✅ Transaksi berhasil diperbarui!")
                st.rerun()
                
            if hapus_data:
                # Hapus file bukti jika ada
                if pd.notna(row_pilih['Bukti']) and row_pilih['Bukti'] != '':
                    path_file_lama = os.path.join(FOLDER_UPLOAD, str(row_pilih['Bukti']))
                    if os.path.exists(path_file_lama):
                        os.remove(path_file_lama)
                
                df = df.drop(pilihan_index).reset_index(drop=True)
                simpan_data_ke_csv(df)
                st.success("🗑️ Transaksi berhasil dihapus!")
                st.rerun()

    # Fitur melihat foto bukti transaksi
    st.markdown("---")
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
        # Kotak info kustom dengan latar putih tipis & teks putih bersih
        st.markdown("""
            <div style="background-color: rgba(255, 255, 255, 0.2); border: 1px solid rgba(255, 255, 255, 0.5); padding: 12px; border-radius: 10px; text-align: center; backdrop-filter: blur(5px);">
                <p style="color: #ffffff !important; font-weight: 600; font-size: 15px; margin: 0;">Belum ada transaksi yang menyertakan foto bukti.</p>
            </div>
        """, unsafe_allow_html=True)
else:
    # Kotak info kustom dengan latar putih tipis & teks putih bersih
    st.markdown("""
        <div style="background-color: rgba(255, 255, 255, 0.2); border: 1px solid rgba(255, 255, 255, 0.5); padding: 15px; border-radius: 10px; text-align: center; backdrop-filter: blur(5px);">
            <p style="color: #ffffff !important; font-weight: 600; font-size: 16px; margin: 0;">ℹ️ Belum ada data transaksi yang tercatat. Silakan tambah melalui menu di sidebar.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Aplikasi Manajemen Keuangan Pribadi Syariah v1.0")