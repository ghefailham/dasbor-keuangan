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

css = f"""
<style>
.stApp {{
    background-image: url("data:image/png;base64,{bg_main}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
[data-testid="stSidebar"] {{
    background-image: url("data:image/png;base64,{bg_sidebar}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- KONEKSI DATABASE SUPABASE ---
# Mencoba terhubung ke Supabase melalui st.secrets
try:
    conn = st.connection("postgresql", type="sql")
except Exception as e:
    st.error("Gagal terhubung ke Database. Pastikan Anda sudah mengatur 'Secrets' di dasbor Streamlit Cloud.")
    st.stop()

# Fungsi memuat data langsung dari SQL (Tanpa Cache, selalu real-time)
def muat_data():
    try:
        df = conn.query("SELECT * FROM transaksi", ttl=0)
        if 'Bukti' not in df.columns:
            df['Bukti'] = ''
        return df
    except:
        # Jika tabel belum ada, buat struktur dasarnya
        return pd.DataFrame(columns=['Tanggal', 'Jenis', 'Kategori', 'Nominal', 'Keterangan', 'Bukti'])

# Fungsi menyimpan/menimpa data ke SQL
def simpan_data_ke_sql(df_to_save):
    # Buang kolom buatan UI (No & 📸 Lihat) sebelum dilempar ke database
    cols_to_drop = [col for col in ['📸 Lihat', 'No'] if col in df_to_save.columns]
    if cols_to_drop:
        df_to_save = df_to_save.drop(columns=cols_to_drop)
    
    # Simpan permanen ke Supabase
    df_to_save.to_sql("transaksi", con=conn.engine, if_exists="replace", index=False)

def simpan_transaksi(tanggal, jenis, kategori, nominal, keterangan, file_bukti):
    string_bukti = ""
    # Ubah foto menjadi teks sandi Base64 agar bisa disimpan langsung di Database SQL!
    if file_bukti is not None:
        string_bukti = base64.b64encode(file_bukti.getvalue()).decode('utf-8')

    df = muat_data()
    data_baru = pd.DataFrame({
        'Tanggal': [str(tanggal)],
        'Jenis': [jenis],
        'Kategori': [kategori],
        'Nominal': [float(nominal)],
        'Keterangan': [keterangan],
        'Bukti': [string_bukti]
    })
    df = pd.concat([df, data_baru], ignore_index=True)
    simpan_data_ke_sql(df)

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
            st.success("✅ Transaksi & Bukti berhasil dicatat di Database!")
            st.rerun()
        else:
            st.error("Nominal harus lebih dari 0!")

# --- HALAMAN UTAMA ---
st.title("📊 Ringkasan Keuangan Anda")

df = muat_data()

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
    df.insert(0, 'No', range(1, len(df) + 1))
    df.insert(0, '📸 Lihat', False)

    st.markdown("**💡 Tips:** *Centang kotak di kolom **📸 Lihat** pada tabel di bawah untuk menampilkan foto bukti transaksi. Klik **Simpan Perubahan** jika Anda mengedit atau menghapus data.*")

    # Render Tabel
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

    # Simpan Tabel ke Supabase
    if st.button("💾 Simpan Perubahan Riwayat"):
        simpan_data_ke_sql(df_edited)
        st.success("✅ Perubahan riwayat berhasil disimpan permanen ke Database Cloud!")
        st.rerun()

    st.markdown("---")
    
    # Logika Menampilkan Foto yang sudah di-Encode di Database
    baris_terpilih = df_edited[df_edited['📸 Lihat'] == True]
    
    if not baris_terpilih.empty:
        baris_pertama = baris_terpilih.iloc[0]
        string_bukti = baris_pertama['Bukti']
        no_tx = baris_pertama['No']
        ket_tx = baris_pertama['Keterangan']
        
        if pd.notna(string_bukti) and str(string_bukti).strip() != '':
            try:
                # Mengubah teks sandi Base64 kembali menjadi gambar fisik
                image_bytes = base64.b64decode(str(string_bukti))
                st.markdown(f"### 🖼️ Bukti Transaksi No. {no_tx} ({ket_tx})")
                st.image(image_bytes, width=400)
            except:
                st.warning("⚠️ Data gambar korup atau tidak valid.")
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
st.caption("Aplikasi Manajemen Keuangan Pribadi Terintegrasi Cloud Database v2.0")