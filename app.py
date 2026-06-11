import os
import json
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
import sys
sys.path.insert(0, os.path.dirname(__file__))
from data.kos_data import KOS_DATA, KECAMATAN_LIST, FASILITAS_LIST

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "kossemarang2024")
CORS(app)

# ─── Inisialisasi Groq client ─────────────────────────────────────────────────
groq_api_key = os.getenv("GROQ_API_KEY", "")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

# ─── Sistem prompt chatbot ───────────────────────────────────────────────────
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


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    featured = sorted(KOS_DATA, key=lambda x: x["rating"], reverse=True)[:6]
    stats = {
        "total_kos": len(KOS_DATA),
        "total_tersedia": sum(1 for k in KOS_DATA if k["tersedia"]),
        "kecamatan": len(KECAMATAN_LIST),
        "pengguna": 2500
    }
    return render_template("index.html", featured=featured, stats=stats)

@app.route("/kos")
def kos_list():
    data = KOS_DATA.copy()
    
    # Filter
    tipe = request.args.get("tipe", "")
    kecamatan = request.args.get("kecamatan", "")
    harga_min = request.args.get("harga_min", 0, type=int)
    harga_max = request.args.get("harga_max", 9999999, type=int)
    fasilitas = request.args.getlist("fasilitas")
    tersedia = request.args.get("tersedia", "")
    sort_by = request.args.get("sort", "rating")
    
    if tipe:
        data = [k for k in data if k["tipe"] == tipe]
    if kecamatan:
        data = [k for k in data if k["kecamatan"] == kecamatan]
    if harga_min:
        data = [k for k in data if k["harga"] >= harga_min]
    if harga_max < 9999999:
        data = [k for k in data if k["harga"] <= harga_max]
    if fasilitas:
        data = [k for k in data if all(f in k["fasilitas"] for f in fasilitas)]
    if tersedia == "true":
        data = [k for k in data if k["tersedia"]]
    
    # Sort
    if sort_by == "harga_asc":
        data = sorted(data, key=lambda x: x["harga"])
    elif sort_by == "harga_desc":
        data = sorted(data, key=lambda x: x["harga"], reverse=True)
    elif sort_by == "rating":
        data = sorted(data, key=lambda x: x["rating"], reverse=True)
    
    return render_template("kos_list.html",
                           kos_list=data,
                           kecamatan_list=KECAMATAN_LIST,
                           fasilitas_list=FASILITAS_LIST,
                           total=len(data),
                           filters=request.args)

@app.route("/kos/<int:kos_id>")
def kos_detail(kos_id):
    kos = next((k for k in KOS_DATA if k["id"] == kos_id), None)
    if not kos:
        return render_template("404.html"), 404
    related = [k for k in KOS_DATA if k["kecamatan"] == kos["kecamatan"] and k["id"] != kos_id][:3]
    return render_template("kos_detail.html", kos=kos, related=related)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/lokasi")
def lokasi():
    kos_json = json.dumps(KOS_DATA, ensure_ascii=False)
    return render_template("lokasi.html", kos_json=kos_json)

@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")

# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"reply": "❌ Request tidak valid."}), 400

        user_message = data.get("message", "").strip()
        history = data.get("history", [])
        # Izinkan override API key dari frontend (opsional, untuk mode pengaturan)
        custom_api_key = data.get("api_key", "").strip()

        if not user_message:
            return jsonify({"reply": "Pesan tidak boleh kosong."}), 400

        # Tentukan client yang aktif
        active_client = None
        if custom_api_key:
            active_client = Groq(api_key=custom_api_key)
        elif groq_client:
            active_client = groq_client

        # Jika tidak ada client sama sekali
        if not active_client:
            return jsonify({
                "reply": (
                    "⚠️ **Groq API Key belum dikonfigurasi.**\n\n"
                    "Silakan lakukan salah satu:\n"
                    "1. Tambahkan `GROQ_API_KEY=gsk_...` di file `.env` lalu restart server.\n"
                    "2. Masukkan API Key melalui ikon ⚙️ Pengaturan di chatbot ini.\n\n"
                    "Dapatkan API Key gratis di: https://console.groq.com"
                )
            })

        # Bangun pesan untuk Groq
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Tambahkan history (max 10 pesan terakhir)
        for msg in history[-10:]:
            if msg.get("role") in ("user", "assistant") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        # Panggil Groq API
        completion = active_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )

        reply = completion.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        err_msg = str(e)

        # Error autentikasi
        if any(code in err_msg for code in ["401", "invalid_api_key", "unauthorized"]) or \
           any(kw in err_msg.lower() for kw in ["api_key", "unauthorized", "invalid"]):
            return jsonify({
                "reply": (
                    "⚠️ **Groq API Key Tidak Valid (Error 401)**\n\n"
                    "API Key yang digunakan tidak valid atau sudah kedaluwarsa.\n\n"
                    "**Solusi:**\n"
                    "1. Klik ikon ⚙️ **Pengaturan** di chatbot ini, lalu tempelkan **Groq API Key** Anda yang valid.\n"
                    "2. Atau periksa file `.env` dan pastikan `GROQ_API_KEY` diisi dengan benar (diawali `gsk_`)."
                )
            })

        # Error rate limit
        if "429" in err_msg or "rate_limit" in err_msg.lower():
            return jsonify({
                "reply": "⏳ Terlalu banyak permintaan. Mohon tunggu beberapa detik lalu coba lagi."
            })

        # Error umum
        return jsonify({
            "reply": f"Maaf, terjadi kesalahan sistem. Silakan coba lagi.\n\nDetail: {err_msg[:200]}"
        }), 500


@app.route("/api/kos", methods=["GET"])
def api_kos():
    return jsonify(KOS_DATA)

@app.route("/api/kos/<int:kos_id>", methods=["GET"])
def api_kos_detail(kos_id):
    kos = next((k for k in KOS_DATA if k["id"] == kos_id), None)
    if not kos:
        return jsonify({"error": "Kos tidak ditemukan"}), 404
    return jsonify(kos)

@app.route("/api/booking", methods=["POST"])
def booking():
    try:
        data = request.get_json()
        kos_id = data.get("kos_id")
        nama = data.get("nama", "").strip()
        no_hp = data.get("no_hp", "").strip()
        tanggal_mulai = data.get("tanggal_mulai", "").strip()
        durasi = data.get("durasi", 1)

        if not all([kos_id, nama, no_hp, tanggal_mulai]):
            return jsonify({"success": False, "message": "Data tidak lengkap"}), 400

        kos = next((k for k in KOS_DATA if k["id"] == kos_id), None)
        if not kos:
            return jsonify({"success": False, "message": "Kos tidak ditemukan"}), 404

        if not kos["tersedia"]:
            return jsonify({"success": False, "message": "Kos sudah penuh"}), 400

        booking_id = f"BK{kos_id:03d}{len(nama)}{durasi:02d}"

        return jsonify({
            "success": True,
            "message": (
                f"Booking berhasil! ID Booking Anda: {booking_id}. "
                f"Pemilik kos ({kos['pemilik']}) akan menghubungi Anda "
                f"di {no_hp} dalam 1x24 jam."
            ),
            "booking_id": booking_id,
            "kos": kos["nama"],
            "pemilik_hp": kos["no_hp"]
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/contact", methods=["POST"])
def contact_submit():
    return jsonify({
        "success": True,
        "message": "Pesan Anda telah diterima! Tim kami akan membalas dalam 1x24 jam."
    })

@app.route("/payment/confirm/<booking_id>")
def payment_confirm(booking_id):
    return render_template("payment_confirm.html", booking_id=booking_id)

# ─── Error handlers ───────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    print(f"\n🏠 KosSemarang.id berjalan di http://localhost:{port}")
    print(f"📡 Groq API: {'✅ Terkonfigurasi' if groq_api_key else '❌ Belum dikonfigurasi (set GROQ_API_KEY di .env)'}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)