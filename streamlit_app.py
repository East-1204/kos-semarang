import os
import json
import base64
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import urllib.parse
from datetime import datetime

# Load environment variables
load_dotenv()

# Import data directly from local file
from data.kos_data import KOS_DATA, KECAMATAN_LIST, FASILITAS_LIST

# Page Config
st.set_page_config(
    page_title="KosSemarang.id - Cari Kos Terbaik di Semarang",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── NAVIGATION (Query Params) ────────────────────────────────────────────────
query_params = st.query_params
if "nav" in query_params:
    st.session_state.page = query_params["nav"]
else:
    st.session_state.page = "Beranda"

# ─── CUSTOM CSS FOR 100% VISUAL MATCH ─────────────────────────────────────────
st.markdown("""
<style>
    /* Hide Streamlit sidebar and adjust top padding */
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stHeader"] {
        background-color: transparent;
        z-index: 1;
    }
    .block-container {
        padding-top: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Global Font Settings */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Layout Styling */
    .main-content {
        padding: 0 40px;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Custom selectbox styling matching Flask */
    div[data-testid="stSelectbox"] label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
        background-color: #FFFFFF !important;
        font-size: 0.92rem !important;
        height: 42px !important;
    }
    
    /* Custom button styling */
    div[data-testid="stButton"] button {
        border-radius: 6px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        height: 42px !important;
    }
    
    /* Blue Search Button */
    div[element-id="btn_search_submit"] button {
        background-color: #2563EB !important;
        color: white !important;
        border: none !important;
        font-size: 0.95rem !important;
        transition: background-color 0.2s !important;
    }
    div[element-id="btn_search_submit"] button:hover {
        background-color: #1D4ED8 !important;
    }
    
    /* Popular Tags Styling */
    div[element-id^="tag_"] button {
        background-color: #EFF6FF !important;
        color: #2563EB !important;
        border: 1px solid #DBEAFE !important;
        border-radius: 20px !important;
        font-size: 0.8rem !important;
        height: 30px !important;
        padding: 0 14px !important;
        font-weight: 500 !important;
    }
    div[element-id^="tag_"] button:hover {
        background-color: #DBEAFE !important;
        color: #1D4ED8 !important;
        border-color: #BFDBFE !important;
    }
    
    /* Kos Cards */
    .kos-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        font-family: 'Inter', sans-serif;
    }
    .badge-putri {
        background-color: #FDF2F8;
        color: #DB2777;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-putra {
        background-color: #EFF6FF;
        color: #2563EB;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-campur {
        background-color: #F5F3FF;
        color: #7C3AED;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .price-text {
        color: #2563EB;
        font-weight: 700;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Initialize State ────────────────────────────────────────────────────────
if "selected_kos_id" not in st.session_state:
    st.session_state.selected_kos_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "booking_success" not in st.session_state:
    st.session_state.booking_success = None
if "payment_done" not in st.session_state:
    st.session_state.payment_done = False

# Search/Filter State
if "search_area" not in st.session_state:
    st.session_state.search_area = "Semua Area"
if "search_tipe" not in st.session_state:
    st.session_state.search_tipe = "Semua Tipe"
if "search_budget" not in st.session_state:
    st.session_state.search_budget = "Semua Budget"

# ─── Groq API Configuration ──────────────────────────────────────────────────
groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

SYSTEM_PROMPT = """Kamu adalah Kosi, asisten virtual dari KosSemarang.id — platform cari kos di Semarang.

Karakter kamu:
- Santai, ramah, dan natural seperti teman ngobrol — bukan robot kaku
- Pakai bahasa Indonesia yang natural, bisa campurkan kata santai seperti "oke", "yuk", "boleh banget", "tenang aja" sesekali
- Jawaban singkat dan to the point — tidak perlu panjang-panjang kalau tidak perlu
- Kalau pengguna singkat, kamu juga bisa singkat. Kalau pengguna detail, baru kamu jelaskan lebih lengkap
- Jangan mulai jawaban dengan "Tentu!", "Baik!", "Halo!" terus-terusan — variasikan pembuka kalimat
- Hindari nada terlalu formal atau kaku

Kamu bisa bantu:
1. Cari kos sesuai budget, tipe (putra/putri/campur), lokasi, atau fasilitas
2. Info detail kos: harga, fasilitas, jarak kampus, ketersediaan kamar
3. Booking/reservasi — minta nama, nomor HP, tanggal mulai, dan durasi sewa
4. Rekomendasi area kos terbaik di Semarang
5. Tips milih kos yang bagus
6. Survei kepuasan — kalau pengguna menyebut kata 'survei', tanyakan pertanyaan berikut SATU PER SATU (jangan sekaligus):
   - Pertanyaan 1: "Gimana pengalaman kamu pakai KosSemarang.id?" [Sangat Puas | Puas | Cukup | Kurang Puas]
   - Pertanyaan 2: "Info kos yang tersedia udah lengkap belum?" [Sangat Lengkap | Cukup Lengkap | Kurang Lengkap]
   - Pertanyaan 3: "Fitur favorit kamu apa?" [Pencarian Kos | Peta Lokasi | Chatbot AI | Booking Online]
   - Pertanyaan 4: "Ada masukan atau saran buat kami?" (jawaban bebas, jangan beri pilihan)
   Setelah semua dijawab, ucapkan terima kasih dan beri ringkasan jawaban mereka.

Data Kos yang Tersedia:
""" + json.dumps([{
    "id": k["id"],
    "nama": k["nama"],
    "tipe": k["tipe"],
    "harga": k["harga_display"],
    "alamat": k["alamat"],
    "kecamatan": k["kecamatan"],
    "fasilitas": k["fasilitas"],
    "tersedia": k["tersedia"],
    "kamar_tersisa": k["kamar_tersisa"],
    "rating": k["rating"],
    "luas": k["luas"],
    "pemilik": k["pemilik"],
    "no_hp": k["no_hp"],
    "jarak_kampus": k["jarak_kampus"]
} for k in KOS_DATA], ensure_ascii=False, indent=2) + """

Panduan tambahan:
- Saat rekomendasikan kos, sebutkan nama, harga, lokasi, dan 1-2 keunggulannya saja
- Format harga: Rp 800.000/bulan
- Kalau kos penuh, langsung tawarkan alternatif tanpa banyak basa-basi
- Konfirmasi dulu ketersediaan sebelum proses booking
- Jangan gunakan bullet point berlebihan — kalau cukup 1-2 baris, ya 1-2 baris saja
"""

# Helper function to reset selected kos
def show_list():
    st.session_state.selected_kos_id = None
    st.session_state.booking_success = None
    st.session_state.payment_done = False

# ─── HEADER & NAVBAR (100% identical HTML/CSS) ────────────────────────────────
active_page = st.session_state.page

def get_nav_link_html(name):
    is_active = (active_page == name)
    active_style = "color: #2563EB; border-bottom: 2px solid #2563EB; font-weight: 700; padding-bottom: 4px;" if is_active else "color: #4B5563; font-weight: 500;"
    return f'<a href="?nav={urllib.parse.quote(name)}" target="_self" style="text-decoration: none; {active_style} font-size: 0.95rem; margin: 0 12px; transition: color 0.2s; font-family: \'Inter\', sans-serif;">{name}</a>'

header_html = f"""
<!-- Top Bar -->
<div style="background-color: #0F2C59; color: rgba(255,255,255,0.9); padding: 8px 40px; display: flex; justify-content: space-between; font-size: 0.78rem; font-family: 'Inter', sans-serif;">
    <div>📍 Semarang, Jawa Tengah &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 📞 (024) 1234-567</div>
    <div style="display: flex; gap: 20px;">
        <span style="cursor: pointer;">Tentang Kami</span>
        <span style="cursor: pointer;">Bantuan</span>
        <span style="color: #10B981; font-weight: 600; cursor: pointer;">🟢 WhatsApp</span>
    </div>
</div>

<!-- Nav Bar -->
<div style="display: flex; justify-content: space-between; align-items: center; padding: 14px 40px; background-color: white; border-bottom: 1px solid #E5E7EB; font-family: 'Inter', sans-serif; position: relative; z-index: 10;">
    <!-- Logo -->
    <a href="?nav=Beranda" target="_self" style="display: flex; align-items: center; gap: 8px; text-decoration: none;">
        <span style="background: #2563EB; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold; font-size: 1.1rem;">🏠</span>
        <span style="font-weight: 800; font-size: 1.35rem; color: #1F2937;">Kos<span style="color: #2563EB;">Semarang</span>.id</span>
    </a>
    
    <!-- Navigation Links -->
    <div style="display: flex; align-items: center;">
        {get_nav_link_html("Beranda")}
        {get_nav_link_html("Cari Kos")}
        {get_nav_link_html("Peta Lokasi")}
        {get_nav_link_html("Tentang")}
        {get_nav_link_html("Kontak")}
    </div>
    
    <!-- Orange Chat Button -->
    <div>
        <a href="?nav=Chatbot" target="_self" style="background-color: #FF5A36; color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold; text-decoration: none; font-size: 0.9rem; display: flex; align-items: center; gap: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: background-color 0.2s;">
            🤖 Tanya Kosi
        </a>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Load base64 city background
try:
    with open("static/img/hero-semarang.jpg", "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode()
    hero_bg_style = f"background-image: linear-gradient(to bottom, rgba(0, 20, 60, 0.45) 0%, rgba(0, 5, 25, 0.7) 100%), url('data:image/jpeg;base64,{img_b64}');"
except Exception:
    hero_bg_style = "background-image: linear-gradient(to bottom, rgba(0, 20, 60, 0.45) 0%, rgba(0, 5, 25, 0.7) 100%), url('https://images.unsplash.com/photo-1605538032432-a9f0c8d9baac?w=1600');"

# ─── PAGE: Beranda & Cari Kos ──────────────────────────────────────────────────
if st.session_state.page in ["Beranda", "Cari Kos"]:
    
    # Detail View
    if st.session_state.selected_kos_id is not None:
        st.markdown("<div class='main-content'>", unsafe_allow_html=True)
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        kos_id = st.session_state.selected_kos_id
        kos = next((k for k in KOS_DATA if k["id"] == kos_id), None)
        
        if kos:
            st.button("⬅️ Kembali ke Daftar Kos", on_click=show_list)
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown(f"<h1 style='color:#1E3A8A;'>{kos['nama']}</h1>", unsafe_allow_html=True)
                st.write(f"📍 {kos['alamat']} ({kos['kecamatan']})")
                
                tipe_badge = f"<span class='badge-{kos['tipe']}'>Kos {kos['tipe'].capitalize()}</span>"
                st.markdown(f"{tipe_badge} &nbsp; ⭐ {kos['rating']} ({kos['ulasan']} Ulasan)", unsafe_allow_html=True)
                
                st.markdown("### Foto Kos")
                st.image(kos["foto_utama"], use_container_width=True)
                
                gallery_cols = st.columns(len(kos["foto"]))
                for idx, img_url in enumerate(kos["foto"]):
                    with gallery_cols[idx]:
                        st.image(img_url, use_container_width=True)
                
                st.markdown("### Deskripsi")
                st.write(kos["deskripsi"])
                
                st.markdown("### Fasilitas")
                fac_cols = st.columns(3)
                for idx, f in enumerate(kos["fasilitas"]):
                    with fac_cols[idx % 3]:
                        st.write(f"✓ {f}")

            with col2:
                st.markdown(
                    f"<div style='background-color:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:24px; margin-top:20px;'>"
                    f"<h4 style='margin:0;'>Harga Sewa</h4>"
                    f"<p class='price-text'>{kos['harga_display']}</p>"
                    f"<p style='color:#6B7280; font-size:0.85rem;'>Ukuran Kamar: {kos['luas']}</p>"
                    f"<p style='color:#6B7280; font-size:0.85rem;'>Jarak: {kos['jarak_kampus']}</p>"
                    f"<hr style='margin:16px 0;'>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
                if not st.session_state.booking_success:
                    st.markdown("### Form Booking")
                    if not kos["tersedia"]:
                        st.error("Maaf, kos ini sudah penuh saat ini.")
                    else:
                        with st.form("booking_form"):
                            nama = st.text_input("Nama Lengkap", placeholder="Masukkan nama Anda")
                            no_hp = st.text_input("Nomor WhatsApp/HP", placeholder="Contoh: 08123456789")
                            tanggal_mulai = st.date_input("Tanggal Mulai Kos", min_value=datetime.today())
                            durasi = st.number_input("Durasi Sewa (Bulan)", min_value=1, max_value=12, value=1)
                            
                            submit_booking = st.form_submit_button("Pesan Sekarang")
                            
                            if submit_booking:
                                if not nama or not no_hp:
                                    st.error("Harap isi semua kolom form.")
                                else:
                                    booking_id = f"BK{kos['id']:03d}{len(nama)}{durasi:02d}"
                                    st.session_state.booking_success = {
                                        "booking_id": booking_id,
                                        "nama": nama,
                                        "no_hp": no_hp,
                                        "tanggal": str(tanggal_mulai),
                                        "durasi": durasi,
                                        "total_harga": kos["harga"] * durasi,
                                        "pemilik": kos["pemilik"]
                                    }
                                    st.rerun()
                else:
                    b = st.session_state.booking_success
                    st.success("🎉 Booking Berhasil!")
                    st.markdown(f"**ID Booking:** `{b['booking_id']}`")
                    st.write(f"Penyewa: **{b['nama']}**")
                    st.write(f"Mulai: **{b['tanggal']}** ({b['durasi']} Bulan)")
                    
                    if not st.session_state.payment_done:
                        st.markdown(
                            "<div style='border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; background-color: #F8FAFC; text-align: center; margin-bottom:16px;'>"
                            "<strong>Scan QR untuk Membayar</strong><br>"
                            "<p style='color:#6B7280; font-size:0.8rem; margin-top:4px;'>Gunakan aplikasi mobile banking Anda untuk scan QR Code di bawah</p>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                        
                        payment_url = f"http://localhost:5050/payment/confirm/{b['booking_id']}"
                        qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(payment_url)}"
                        
                        st.image(qr_api_url, width=200)
                        st.write(f"Jumlah Tagihan: **Rp {b['total_harga']:,}**")
                        
                        if st.button("Simulasikan Pembayaran Berhasil (Scan QR)"):
                            st.session_state.payment_done = True
                            st.rerun()
                    else:
                        st.balloons()
                        st.markdown(
                            "<div style='border: 2px solid #10B981; border-radius: 8px; padding: 20px; background-color: #ECFDF5; text-align: center;'>"
                            "<h3 style='color:#059669; margin-top:0;'>✅ Pembayaran Berhasil Dikonfirmasi!</h3>"
                            "<p style='margin-bottom:0;'>Kode QR telah dihapus. Pemilik kos akan segera menghubungi Anda melalui nomor WhatsApp.</p>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                        
                        if st.button("Kembali ke Daftar Kos", on_click=show_list):
                            pass
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        # 1. Hero banner section with city panorama background
        st.markdown(f"""
        <div style="{hero_bg_style} background-size: cover; background-position: center; padding: 84px 40px 100px 40px; text-align: center; color: white; font-family: 'Inter', sans-serif;">
            <h1 style="font-size: 2.8rem; font-weight: 800; color: white; margin-bottom: 8px; letter-spacing: -0.5px;">Hai, mau cari kos di mana?</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-bottom: 0;">Temukan ratusan kos terverifikasi di Semarang — murah, nyaman, dekat kampus.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Main Page Container
        st.markdown("<div class='main-content'>", unsafe_allow_html=True)
        
        # 3. Search Box Card
        st.markdown("""<div style="height: 15px;"></div>""", unsafe_allow_html=True)
        with st.container(border=True):
            # Custom Search Tabs mimicking Flask App exactly
            search_card_tabs_html = f"""
            <div style="display: flex; gap: 24px; border-bottom: 1px solid #E5E7EB; margin-bottom: 16px; padding-bottom: 10px; font-family: 'Inter', sans-serif;">
                <a href="?nav=Cari Kos" target="_self" style="color: #2563EB; font-weight: 700; border-bottom: 2px solid #2563EB; padding-bottom: 10px; text-decoration: none; font-size: 0.95rem;">🏠 Cari Kos</a>
                <a href="?nav=Peta Lokasi" target="_self" style="color: #6B7280; font-weight: 500; padding-bottom: 10px; text-decoration: none; font-size: 0.95rem;">🗺️ Lihat Peta</a>
                <a href="?nav=Chatbot" target="_self" style="color: #6B7280; font-weight: 500; padding-bottom: 10px; text-decoration: none; font-size: 0.95rem;">🤖 Tanya AI</a>
            </div>
            """
            st.markdown(search_card_tabs_html, unsafe_allow_html=True)
            
            # Select boxes row
            s_col1, s_col2, s_col3, s_col4 = st.columns([2, 1, 1, 0.8])
            with s_col1:
                st.session_state.search_area = st.selectbox("Lokasi / Area", ["Semua Area"] + KECAMATAN_LIST, index=(["Semua Area"] + KECAMATAN_LIST).index(st.session_state.search_area))
            with s_col2:
                st.session_state.search_tipe = st.selectbox("Tipe Kos", ["Semua Tipe", "Putra", "Putri", "Campur"], index=["Semua Tipe", "Putra", "Putri", "Campur"].index(st.session_state.search_tipe))
            with s_col3:
                st.session_state.search_budget = st.selectbox("Budget per Bulan", ["Semua Budget", "< 1 Juta", "1 - 1.5 Juta", "> 1.5 Juta"], index=["Semua Budget", "< 1 Juta", "1 - 1.5 Juta", "> 1.5 Juta"].index(st.session_state.search_budget))
            with s_col4:
                st.write("") # Spacer labels
                st.write("")
                if st.button("🔍 Cari Kos", key="btn_search_submit", use_container_width=True):
                    st.session_state.page = "Cari Kos"
                    st.rerun()
            
            # Popular Suggestion Tags Row
            tag_cols = st.columns([0.8, 1, 1, 1, 1, 1.2, 4])
            with tag_cols[0]:
                st.markdown("<p style='color:#6B7280; font-size:0.85rem; padding-top: 8px; font-weight: 500;'>Populer:</p>", unsafe_allow_html=True)
            with tag_cols[1]:
                if st.button("Tembalang", key="tag_tembalang"):
                    st.session_state.search_area = "Tembalang"
                    st.session_state.page = "Cari Kos"
                    st.rerun()
            with tag_cols[2]:
                if st.button("Banyumanik", key="tag_banyumanik"):
                    st.session_state.search_area = "Banyumanik"
                    st.session_state.page = "Cari Kos"
                    st.rerun()
            with tag_cols[3]:
                if st.button("Kos Putri", key="tag_putri"):
                    st.session_state.search_tipe = "Putri"
                    st.session_state.page = "Cari Kos"
                    st.rerun()
            with tag_cols[4]:
                if st.button("Kos Putra", key="tag_putra"):
                    st.session_state.search_tipe = "Putra"
                    st.session_state.page = "Cari Kos"
                    st.rerun()
            with tag_cols[5]:
                if st.button("Semarang Tengah", key="tag_tengah"):
                    st.session_state.search_area = "Semarang Tengah"
                    st.session_state.page = "Cari Kos"
                    st.rerun()
                    
        # 4. Stats Section (Exactly like Flask App dividers)
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        with stats_col1:
            st.markdown("""
            <div style="text-align: center; border-right: 1px solid #E5E7EB; padding: 12px 0;">
                <h2 style="color: #2563EB; font-weight: 800; font-size: 2.1rem; margin: 0; font-family: 'Inter', sans-serif;">8+</h2>
                <p style="color: #6B7280; font-size: 0.85rem; margin: 0; font-weight: 500;">Kos Terdaftar</p>
            </div>
            """, unsafe_allow_html=True)
        with stats_col2:
            st.markdown("""
            <div style="text-align: center; border-right: 1px solid #E5E7EB; padding: 12px 0;">
                <h2 style="color: #2563EB; font-weight: 800; font-size: 2.1rem; margin: 0; font-family: 'Inter', sans-serif;">7+</h2>
                <p style="color: #6B7280; font-size: 0.85rem; margin: 0; font-weight: 500;">Kamar Tersedia</p>
            </div>
            """, unsafe_allow_html=True)
        with stats_col3:
            st.markdown("""
            <div style="text-align: center; border-right: 1px solid #E5E7EB; padding: 12px 0;">
                <h2 style="color: #2563EB; font-weight: 800; font-size: 2.1rem; margin: 0; font-family: 'Inter', sans-serif;">10</h2>
                <p style="color: #6B7280; font-size: 0.85rem; margin: 0; font-weight: 500;">Kecamatan</p>
            </div>
            """, unsafe_allow_html=True)
        with stats_col4:
            st.markdown("""
            <div style="text-align: center; padding: 12px 0;">
                <h2 style="color: #2563EB; font-weight: 800; font-size: 2.1rem; margin: 0; font-family: 'Inter', sans-serif;">2.500+</h2>
                <p style="color: #6B7280; font-size: 0.85rem; margin: 0; font-weight: 500;">Pengguna Aktif</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<hr style='margin: 10px 0 30px 0; border:0; border-top:1px solid #E5E7EB;'>", unsafe_allow_html=True)
        
        # 5. Filtering list based on user selections
        filtered_kos = KOS_DATA.copy()
        
        # Filter by Area/Kecamatan
        if st.session_state.search_area != "Semua Area":
            filtered_kos = [k for k in filtered_kos if k["kecamatan"] == st.session_state.search_area]
            
        # Filter by Tipe Kos
        if st.session_state.search_tipe != "Semua Tipe":
            filtered_kos = [k for k in filtered_kos if k["tipe"] == st.session_state.search_tipe.lower()]
            
        # Filter by Budget range
        if st.session_state.search_budget == "< 1 Juta":
            filtered_kos = [k for k in filtered_kos if k["harga"] < 1000000]
        elif st.session_state.search_budget == "1 - 1.5 Juta":
            filtered_kos = [k for k in filtered_kos if 1000000 <= k["harga"] <= 1500000]
        elif st.session_state.search_budget == "> 1.5 Juta":
            filtered_kos = [k for k in filtered_kos if k["harga"] > 1500000]
            
        # 6. Displaying results in columns
        st.markdown(f"<h3 style='color:#1F2937; margin-bottom: 20px; font-family: Inter, sans-serif;'>Ditemukan {len(filtered_kos)} Kos</h3>", unsafe_allow_html=True)
        
        if not filtered_kos:
            st.warning("Tidak ada kos yang cocok dengan kriteria Anda.")
        else:
            cols = st.columns(3)
            for idx, kos in enumerate(filtered_kos):
                col = cols[idx % 3]
                with col:
                    tipe_style = f"badge-{kos['tipe']}"
                    badge_text = f"Kos {kos['tipe'].capitalize()}"
                    
                    st.markdown(
                        f"<div class='kos-card'>"
                        f"<img src='{kos['foto_utama']}' style='width:100%; height:180px; object-fit:cover; border-radius:6px; margin-bottom:12px;'>"
                        f"<span class='{tipe_style}'>{badge_text}</span>"
                        f"<h3 style='margin: 8px 0 4px 0; font-size:1.15rem; color:#1F2937;'>{kos['nama']}</h3>"
                        f"<p style='color:#6B7280; font-size:0.85rem; margin-bottom:8px;'>📍 {kos['kecamatan']}</p>"
                        f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>"
                        f"<span class='price-text'>{kos['harga_display']}</span>"
                        f"<span style='font-size:0.85rem;'>⭐ {kos['rating']}</span>"
                        f"</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    if st.button(f"Lihat Detail", key=f"det_{kos['id']}", use_container_width=True):
                        st.session_state.selected_kos_id = kos["id"]
                        st.rerun()
                        
        st.markdown("</div>", unsafe_allow_html=True)

# ─── PAGE: Chatbot ────────────────────────────────────────────────────────────
elif st.session_state.page == "Chatbot":
    st.markdown("<div class='main-content' style='margin-top: 24px;'>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>💬 Tanya Kosi (Chatbot AI)</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Tanyakan apa saja seputar kos di Semarang, survei layanan, atau minta rekomendasi.</p>", unsafe_allow_html=True)
    
    if not groq_api_key:
        st.info("💡 Hubungkan Groq API Key Anda pada menu di sebelah kiri untuk mulai chatting!")
    else:
        # Chat message display
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Handle suggestions click
        suggested_prompt = None
        
        st.write("Saran pertanyaan:")
        sug_cols = st.columns(3)
        with sug_cols[0]:
            if st.button("📝 Ikut Survei"):
                suggested_prompt = "Saya mau ikut survei"
        with sug_cols[1]:
            if st.button("🔍 Kos Putri Tembalang"):
                suggested_prompt = "Rekomendasikan kos putri di daerah Tembalang"
        with sug_cols[2]:
            if st.button("💰 Kos di bawah 1 Juta"):
                suggested_prompt = "Ada kos murah di bawah 1 juta sebulan?"
                
        # Input chat
        user_input = st.chat_input("Tulis pesan Anda di sini...")
        
        # If suggestion button was clicked, use it as user input
        if suggested_prompt:
            user_input = suggested_prompt
            
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            try:
                client = Groq(api_key=groq_api_key)
                
                messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in st.session_state.messages[-10:]:
                    messages_for_api.append({"role": msg["role"], "content": msg["content"]})
                    
                with st.spinner("Kosi sedang mengetik..."):
                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages_for_api,
                        temperature=0.7,
                        max_tokens=1024
                    )
                    
                reply = completion.choices[0].message.content
                
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memanggil AI: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── PAGE: Tentang ────────────────────────────────────────────────────────────
elif st.session_state.page == "Tentang":
    st.markdown("<div class='main-content' style='margin-top: 24px;'>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>Tentang KosSemarang.id</h1>", unsafe_allow_html=True)
    st.write(
        "KosSemarang.id adalah platform pencarian kos digital di kota Semarang. "
        "Kami menyediakan berbagai pilihan kos mulai dari kos putra, putri, hingga campur dengan "
        "informasi harga, fasilitas, lokasi, dan jarak ke kampus-kampus ternama di Semarang "
        "secara transparan dan lengkap."
    )
    st.markdown("### Visi dan Misi Kami")
    st.write("- Mempermudah mahasiswa dan pekerja dalam mencari kos impian mereka.")
    st.write("- Menyediakan informasi harga dan fasilitas secara jujur tanpa manipulasi.")
    st.write("- Memberikan proses booking online yang aman dan terpercaya.")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── PAGE: Kontak ─────────────────────────────────────────────────────────────
elif st.session_state.page == "Kontak":
    st.markdown("<div class='main-content' style='margin-top: 24px;'>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>Hubungi Kami</h1>", unsafe_allow_html=True)
    st.write("Ada pertanyaan, keluhan, atau ingin bermitra dengan kami? Silakan hubungi kontak berikut:")
    st.write("📧 **Email:** support@kossemarang.id")
    st.write("📞 **Telepon:** (024) 1234-567")
    st.write("🟢 **WhatsApp:** +62 812-3456-7890")
    st.write("🏢 **Alamat Kantor:** Jl. Pemuda No. 100, Sekayu, Semarang Tengah, Kota Semarang")
    st.markdown("</div>", unsafe_allow_html=True)
