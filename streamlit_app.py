import os
import json
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
    page_title="KosSemarang.id - Cari Kos di Semarang",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (White and Blue Theme)
st.markdown("""
<style>
    .main-title {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .kos-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
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
""", unsafe_allowed_html=True)

# ─── Initialize State ────────────────────────────────────────────────────────
if "selected_kos_id" not in st.session_state:
    st.session_state.selected_kos_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "booking_success" not in st.session_state:
    st.session_state.booking_success = None
if "payment_done" not in st.session_state:
    st.session_state.payment_done = False

# ─── Groq API Configuration ──────────────────────────────────────────────────
# Prioritize Streamlit secrets, then .env, then sidebar input
groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

# Sidebar Branding and Navigation
st.sidebar.markdown("<h2 style='color: #2563EB; font-weight:800; margin-bottom: 0;'>KosSemarang.id</h2>", unsafe_allowed_html=True)
st.sidebar.markdown("<p style='color: #6B7280; font-size:0.85rem; margin-bottom: 1.5rem;'>Cari Kos Terbaik di Semarang</p>", unsafe_allowed_html=True)

menu = st.sidebar.radio("Navigasi", ["🏠 Beranda", "💬 Tanya Kosi (Chatbot)", "ℹ️ Tentang Kami"])

# Sidebar Groq API Key Input if not configured
if not groq_api_key:
    st.sidebar.warning("⚠️ GROQ_API_KEY belum dikonfigurasi.")
    groq_api_key_input = st.sidebar.text_input("Masukkan Groq API Key:", type="password")
    if groq_api_key_input:
        groq_api_key = groq_api_key_input
else:
    groq_api_key_input = ""

# Setup System Prompt for Chatbot
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

# ─── NAVIGATION: 🏠 Beranda ──────────────────────────────────────────────────
if menu == "🏠 Beranda":
    # If a specific kos details page is selected
    if st.session_state.selected_kos_id is not None:
        kos_id = st.session_state.selected_kos_id
        kos = next((k for k in KOS_DATA if k["id"] == kos_id), None)
        
        if kos:
            st.button("⬅️ Kembali ke Daftar Kos", on_click=show_list)
            
            # Detail layout
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown(f"<h1 style='color:#1E3A8A;'>{kos['nama']}</h1>", unsafe_allowed_html=True)
                st.write(f"📍 {kos['alamat']} ({kos['kecamatan']})")
                
                # Badges & Info
                tipe_badge = f"<span class='badge-{kos['tipe']}'>Kos {kos['tipe'].capitalize()}</span>"
                st.markdown(f"{tipe_badge} &nbsp; ⭐ {kos['rating']} ({kos['ulasan']} Ulasan)", unsafe_allowed_html=True)
                
                st.markdown("### Foto Kos")
                # Show principal image
                st.image(kos["foto_utama"], use_container_width=True)
                
                # Show gallery
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
                # Booking Card
                st.markdown(
                    f"<div style='background-color:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:24px; margin-top:20px;'>"
                    f"<h4 style='margin:0;'>Harga Sewa</h4>"
                    f"<p class='price-text'>{kos['harga_display']}</p>"
                    f"<p style='color:#6B7280; font-size:0.85rem;'>Ukuran Kamar: {kos['luas']}</p>"
                    f"<p style='color:#6B7280; font-size:0.85rem;'>Jarak: {kos['jarak_kampus']}</p>"
                    f"<hr style='margin:16px 0;'>"
                    f"</div>",
                    unsafe_allowed_html=True
                )
                
                # Booking / Payment Area
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
                                    # Generate dummy booking id
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
                    # Booking Success & QR Payment
                    b = st.session_state.booking_success
                    
                    st.success("🎉 Booking Berhasil!")
                    st.markdown(f"**ID Booking:** `{b['booking_id']}`")
                    st.write(f"Penyewa: **{b['nama']}**")
                    st.write(f"Mulai: **{b['tanggal']}** ({b['durasi']} Bulan)")
                    
                    # QR Code box
                    if not st.session_state.payment_done:
                        st.markdown(
                            "<div style='border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; background-color: #F8FAFC; text-align: center; margin-bottom:16px;'>"
                            "<strong>Scan QR untuk Membayar</strong><br>"
                            "<p style='color:#6B7280; font-size:0.8rem; margin-top:4px;'>Gunakan aplikasi mobile banking Anda untuk scan QR Code di bawah</p>"
                            "</div>",
                            unsafe_allowed_html=True
                        )
                        
                        # Generate qr code image using public api
                        payment_url = f"http://localhost:5050/payment/confirm/{b['booking_id']}"
                        qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(payment_url)}"
                        
                        st.image(qr_api_url, width=200)
                        st.write(f"Jumlah Tagihan: **Rp {b['total_harga']:,}**")
                        
                        # Simulasikan Scan QR (Tombol Pembayaran)
                        if st.button("Simulasikan Pembayaran Berhasil (Scan QR)"):
                            st.session_state.payment_done = True
                            st.rerun()
                    else:
                        # QR Code disappears and booking is fully confirmed
                        st.balloons()
                        st.markdown(
                            "<div style='border: 2px solid #10B981; border-radius: 8px; padding: 20px; background-color: #ECFDF5; text-align: center;'>"
                            "<h3 style='color:#059669; margin-top:0;'>✅ Pembayaran Berhasil Dikonfirmasi!</h3>"
                            "<p style='margin-bottom:0;'>Kode QR telah dihapus. Pemilik kos akan segera menghubungi Anda melalui nomor WhatsApp.</p>"
                            "</div>",
                            unsafe_allowed_html=True
                        )
                        
                        if st.button("Kembali ke Daftar Kos", on_click=show_list):
                            pass
                            
    else:
        # Main Listings Page
        st.markdown("<h1 class='main-title'>Temukan Kos Terbaik di Semarang</h1>", unsafe_allowed_html=True)
        st.markdown("<p class='sub-title'>Temukan hunian kos nyaman, terjangkau, dan dekat dengan kampus Anda.</p>", unsafe_allowed_html=True)
        
        # Hero Search Card
        search_query = st.text_input("Cari kos berdasarkan nama atau alamat...", placeholder="Masukkan nama kos...")
        
        # Grid of Filters (Horizontal)
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            kecamatan_filter = st.selectbox("Kecamatan", ["Semua Kecamatan"] + KECAMATAN_LIST)
        with filter_col2:
            tipe_filter = st.radio("Tipe Kos", ["Semua", "Putra", "Putri", "Campur"], horizontal=True)
        with filter_col3:
            harga_max = st.slider("Budget Maksimal (Rp/bulan)", min_value=500000, max_value=2000000, value=2000000, step=100000)
        with filter_col4:
            fasilitas_filter = st.multiselect("Fasilitas Pilihan", FASILITAS_LIST)
            
        # Filtering Logic
        filtered_kos = KOS_DATA.copy()
        
        if search_query:
            filtered_kos = [k for k in filtered_kos if search_query.lower() in k["nama"].lower() or search_query.lower() in k["alamat"].lower()]
            
        if kecamatan_filter != "Semua Kecamatan":
            filtered_kos = [k for k in filtered_kos if k["kecamatan"] == kecamatan_filter]
            
        if tipe_filter != "Semua":
            filtered_kos = [k for k in filtered_kos if k["tipe"] == tipe_filter.lower()]
            
        filtered_kos = [k for k in filtered_kos if k["harga"] <= harga_max]
        
        if fasilitas_filter:
            filtered_kos = [k for k in filtered_kos if all(f in k["fasilitas"] for f in fasilitas_filter)]
            
        # Display Results
        st.markdown(f"### Ditemukan {len(filtered_kos)} Kos")
        
        # Display in a beautiful grid of 3 columns
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
                        f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                        f"<span class='price-text'>{kos['harga_display']}</span>"
                        f"<span style='font-size:0.85rem;'>⭐ {kos['rating']}</span>"
                        f"</div>"
                        f"</div>",
                        unsafe_allowed_html=True
                    )
                    
                    # Detail button
                    if st.button(f"Lihat Detail", key=f"det_{kos['id']}"):
                        st.session_state.selected_kos_id = kos["id"]
                        st.rerun()

# ─── NAVIGATION: 💬 Tanya Kosi (Chatbot) ──────────────────────────────────────
elif menu == "💬 Tanya Kosi (Chatbot)":
    st.markdown("<h1 class='main-title'>💬 Tanya Kosi (Chatbot AI)</h1>", unsafe_allowed_html=True)
    st.markdown("<p class='sub-title'>Tanyakan apa saja seputar kos di Semarang, survei layanan, atau minta rekomendasi.</p>", unsafe_allowed_html=True)
    
    if not groq_api_key:
        st.info("💡 Hubungkan Groq API Key Anda pada menu di sebelah kiri untuk mulai chatting!")
    else:
        # Chat history display
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
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Call Groq
            try:
                client = Groq(api_key=groq_api_key)
                
                # Build chat context
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
                
                # Display assistant message
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memanggil AI: {str(e)}")

# ─── NAVIGATION: ℹ️ Tentang Kami ──────────────────────────────────────────────
elif menu == "ℹ️ Tentang Kami":
    st.markdown("<h1 class='main-title'>Tentang KosSemarang.id</h1>", unsafe_allowed_html=True)
    st.write(
        "KosSemarang.id adalah platform pencarian kos digital di kota Semarang. "
        "Kami menyediakan berbagai pilihan kos mulai dari kos putra, putri, hingga campur dengan "
        "informasi harga, fasilitas, lokasi, dan jarak ke kampus-kampus ternama di Semarang "
        "secara transparan dan lengkap."
    )
    
    st.markdown("### Mengapa memilih platform kami?")
    st.write("1. **Data Kos Terpercaya:** Semua kos diverifikasi langsung.")
    st.write("2. **Chatbot Pintar (Kosi):** Siap memandu pencarian kos impian Anda 24 jam.")
    st.write("3. **Sistem Booking Instan:** Booking dengan QR Code yang praktis.")
    
    st.markdown("### Hubungi Kami")
    st.write("📧 Email: support@kossemarang.id")
    st.write("📞 Telepon: 024-12345678")
    st.write("🏢 Alamat Kantor: Jl. Pemuda No. 100, Kota Semarang, Jawa Tengah")
