import streamlit as st
import pandas as pd
import os
import base64
import time
from datetime import date

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Money Tracker",
    page_icon="favicon.png", 
    layout="wide"
)

# --- FUNGSI UNTUK MEMASANG BACKGROUND ---
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
    background-attachment: fixed;
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

# Membaca data TANPA CACHE agar tidak ada lagi masalah data kembali setelah dihapus
def muat_data():
    if not os.path.exists(FILE_DATA):
        # Buat file kosong dengan header jika belum ada
        df_kosong = pd.DataFrame(columns=['Tanggal', 'Jenis', 'Kategori', 'Nominal', 'Keterangan', 'Bukti'])
        df_kosong.to_csv(FILE_DATA, index=False)
        return df_kosong
    
    df = pd.read_csv(FILE_DATA)
    if 'Bukti' not in df.columns:
        df['Bukti'] = ''
    return df

def simpan_data_ke_csv(df):
    # Buang kolom bantuan UI sebelum disimpan ke CSV permanen
    if '📸 Lihat' in df.columns:
        df = df.drop(columns=['📸 Lihat'])
    if 'No' in df.columns:
        df = df.drop(columns=['No'])
        
    df.to_csv(FILE_DATA, index=False)

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

st.subheader("📋 Riwayat & Bukti Transaksi")

if not df.empty:
    # 1. Tambahkan kolom Nomor dan Checkbox secara otomatis ke DataFrame untuk tampilan
    df.insert(0, 'No', range(1, len(df) + 1))
    df.insert(0, '📸 Lihat', False) # Kolom centang untuk melihat foto

    st.markdown("**💡 Tips:** *Centang kotak di kolom **📸 Lihat** pada tabel di bawah untuk menampilkan foto bukti transaksi. Jangan lupa klik **Simpan Perubahan** jika Anda menghapus data!*")

    # 2. Render Tabel Interaktif
    df_edited = st.data_editor(
        df, 
        use_container_width=True, 
        hide_index=True,
        num_rows="dynamic",
        key="data_editor_transaksi",
        column_config={
            "📸 Lihat": st.column_config.CheckboxColumn("📸 Lihat", default=False),
            "No": st.column_config.NumberColumn("No", disabled=True),
            "Bukti": st.column_config.TextColumn("Bukti", disabled=True)
        }
    )

    # 3. Tombol Simpan (Untuk mengunci perubahan / penghapusan)
    if st.button("💾 Simpan Perubahan Riwayat"):
        # Cari file bukti fisik yang dihapus dari tabel untuk dibersihkan dari folder
        bukti_lama = set(df['Bukti'].dropna().astype(str).unique())
        bukti_baru = set(df_edited['Bukti'].dropna().astype(str).unique())
        bukti_untuk_dihapus = bukti_lama - bukti_baru
        
        for nama_file in bukti_untuk_dihapus:
            if nama_file != "":
                path_hapus = os.path.join(FOLDER_UPLOAD, nama_file)
                if os.path.exists(path_hapus):
                    os.remove(path_hapus)
        
        simpan_data_ke_csv(df_edited)
        st.success("✅ Perubahan riwayat berhasil disimpan secara permanen!")
        st.rerun()

    # 4. Logika Menampilkan Foto (Otomatis muncul jika dicentang di tabel)
    st.markdown("---")
    
    # Saring baris yang dicentang oleh pengguna
    baris_terpilih = df_edited[df_edited['📸 Lihat'] == True]
    
    if not baris_terpilih.empty:
        # Ambil baris pertama yang dicentang
        baris_pertama = baris_terpilih.iloc[0]
        nama_bukti = baris_pertama['Bukti']
        no_tx = baris_pertama['No']
        ket_tx = baris_pertama['Keterangan']
        
        if pd.notna(nama_bukti) and str(nama_bukti).strip() != '':
            path_tampil = os.path.join(FOLDER_UPLOAD, str(nama_bukti))
            if os.path.exists(path_tampil):
                st.markdown(f"### 🖼️ Bukti Transaksi No. {no_tx} ({ket_tx})")
                st.image(path_tampil, width=400)
            else:
                st.warning("⚠️ File gambar bukti fisik tidak ditemukan di server.")
        else:
            st.markdown(f"""
                <div style="background-color: rgba(255, 255, 255, 0.2); border: 1px solid rgba(255, 255, 255, 0.5); padding: 12px; border-radius: 10px; backdrop-filter: blur(5px);">
                    <p style="color: #ffffff !important; font-weight: 500; font-size: 15px; margin: 0;">Transaksi No. {no_tx} ini tidak menyertakan foto bukti.</p>
                </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("""
        <div style="background-color: rgba(255, 255, 255, 0.2); border: 1px solid rgba(255, 255, 255, 0.5); padding: 15px; border-radius: 10px; text-align: center; backdrop-filter: blur(5px);">
            <p style="color: #ffffff !important; font-weight: 600; font-size: 16px; margin: 0;">ℹ️ Belum ada data transaksi yang tercatat. Silakan tambah melalui menu di sidebar.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Aplikasi Manajemen Keuangan Pribadi v1.0")