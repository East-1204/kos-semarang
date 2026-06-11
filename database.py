"""
database.py — Modul Database KosSemarang
=========================================
Mengelola semua operasi database untuk aplikasi pencarian kos di Semarang.
Menggunakan SQLite3 sebagai database engine.

Jalankan langsung: python database.py
Untuk membuat database dan mengisi data awal.
"""

import sqlite3
import os
import json

# Path database — disimpan di direktori yang sama dengan file ini
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kos_semarang.db')


# =============================================================================
# KONEKSI & INISIALISASI DATABASE
# =============================================================================

def get_db():
    """Mendapatkan koneksi database dengan row_factory dict."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Membuat tabel dan mengisi data awal jika kosong."""
    conn = get_db()
    cursor = conn.cursor()

    # --- Tabel kos ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            alamat TEXT NOT NULL,
            kecamatan TEXT NOT NULL,
            harga INTEGER NOT NULL,
            tipe TEXT NOT NULL,
            fasilitas TEXT NOT NULL,
            deskripsi TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            foto TEXT NOT NULL,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            available_rooms INTEGER DEFAULT 1,
            total_rooms INTEGER DEFAULT 10,
            kontak TEXT NOT NULL,
            pemilik TEXT NOT NULL
        )
    ''')

    # --- Tabel bookings ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kos_id INTEGER NOT NULL,
            nama TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            tanggal_masuk TEXT NOT NULL,
            durasi INTEGER DEFAULT 1,
            pesan TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kos_id) REFERENCES kos(id)
        )
    ''')

    # --- Tabel chat_history ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()

    # Cek apakah data kos sudah ada, jika belum seed data
    cursor.execute("SELECT COUNT(*) FROM kos")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_data()
        print(f"✅ Data awal berhasil dimasukkan ke {DB_PATH}")
    else:
        print(f"ℹ️  Database sudah berisi {count} data kos.")

    conn.close()


# =============================================================================
# SEED DATA — 31 KOS REALISTIS DI SEMARANG
# =============================================================================

def seed_data():
    """Mengisi database dengan 31 data kos realistis di Semarang."""
    conn = get_db()
    cursor = conn.cursor()

    kos_data = [
        # =====================================================================
        # TEMBALANG (dekat UNDIP) — 8 entri, harga 600rb - 1.8jt
        # =====================================================================
        {
            "nama": "Kos Putri Griya Ayu",
            "alamat": "Jl. Tirto Agung No. 15, Tembalang",
            "kecamatan": "Tembalang",
            "harga": 850000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "Parkir Motor", "Laundry"]),
            "deskripsi": "Kos putri eksklusif dengan suasana tenang dan nyaman, dekat kampus UNDIP. Dilengkapi fasilitas lengkap untuk menunjang kegiatan belajar mahasiswi.",
            "lat": -7.0498,
            "lng": 110.4381,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+1",
            "rating": 4.7,
            "review_count": 45,
            "available_rooms": 3,
            "total_rooms": 12,
            "kontak": "0812-3456-7890",
            "pemilik": "Ibu Sri Wahyuni"
        },
        {
            "nama": "Kos Putra Wisma Mandiri",
            "alamat": "Jl. Sirojudin No. 8, Tembalang",
            "kecamatan": "Tembalang",
            "harga": 750000,
            "tipe": "putra",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Dalam", "Dapur Bersama"]),
            "deskripsi": "Kos putra strategis dekat UNDIP dengan harga terjangkau. Lingkungan aman dan tenang, cocok untuk mahasiswa yang fokus kuliah.",
            "lat": -7.0512,
            "lng": 110.4375,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+2",
            "rating": 4.3,
            "review_count": 32,
            "available_rooms": 2,
            "total_rooms": 10,
            "kontak": "0813-2567-8901",
            "pemilik": "Bapak Hartono"
        },
        {
            "nama": "Kos Campur Pondok Indah Tembalang",
            "alamat": "Jl. Prof. Soedarto No. 22, Tembalang",
            "kecamatan": "Tembalang",
            "harga": 1200000,
            "tipe": "campur",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "Parkir Motor", "Dapur Bersama", "Laundry", "CCTV"]),
            "deskripsi": "Kos premium campur dengan fasilitas hotel bintang. Lokasi strategis di jalan utama Tembalang, dekat pusat kuliner dan kampus.",
            "lat": -7.0485,
            "lng": 110.4362,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+3",
            "rating": 4.8,
            "review_count": 67,
            "available_rooms": 1,
            "total_rooms": 15,
            "kontak": "0857-1234-5678",
            "pemilik": "Bapak Eko Prasetyo"
        },
        {
            "nama": "Kos Putri Sakura Residence",
            "alamat": "Jl. Banjarsari Selatan No. 5, Tembalang",
            "kecamatan": "Tembalang",
            "harga": 1000000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "Parkir Motor", "Laundry", "Dapur Bersama"]),
            "deskripsi": "Kos putri modern dengan desain minimalis Jepang. Keamanan 24 jam dan lingkungan asri, sangat cocok untuk mahasiswi UNDIP.",
            "lat": -7.0530,
            "lng": 110.4395,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+4",
            "rating": 4.6,
            "review_count": 38,
            "available_rooms": 4,
            "total_rooms": 14,
            "kontak": "0821-3344-5566",
            "pemilik": "Ibu Dewi Kartika"
        },
        {
            "nama": "Kos Putra Graha Pelajar",
            "alamat": "Jl. Tembalang Pesona No. 11, Tembalang",
            "kecamatan": "Tembalang",
            "harga": 600000,
            "tipe": "putra",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Luar"]),
            "deskripsi": "Kos putra murah meriah dekat UNDIP. Cocok untuk mahasiswa hemat dengan fasilitas dasar yang memadai.",
            "lat": -7.0545,
            "lng": 110.4410,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+5",
            "rating": 4.0,
            "review_count": 21,
            "available_rooms": 5,
            "total_rooms": 8,
            "kontak": "0856-7788-9900",
            "pemilik": "Bapak Sugeng Riyadi"
        },
        {
            "nama": "Kos Putri Bunga Melati",
            "alamat": "Jl. Ngesrep Timur V No. 3, Tembalang",
            "kecamatan": "Tembalang",
            "harga": 1500000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "TV", "Parkir Motor", "Laundry", "Dapur Bersama", "Ruang Tamu"]),
            "deskripsi": "Kos putri mewah dengan fasilitas lengkap bak hotel. Kamar luas, AC dingin, dan lingkungan elit di kawasan Ngesrep.",
            "lat": -7.0470,
            "lng": 110.4345,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+6",
            "rating": 4.9,
            "review_count": 82,
            "available_rooms": 2,
            "total_rooms": 10,
            "kontak": "0878-1122-3344",
            "pemilik": "Ibu Ratna Sari"
        },
        {
            "nama": "Kos Campur Rumah Kita",
            "alamat": "Jl. Banjarsari No. 18, Tembalang",
            "kecamatan": "Tembalang",
            "harga": 900000,
            "tipe": "campur",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Dalam", "Dapur Bersama", "Ruang Bersama"]),
            "deskripsi": "Kos campur dengan konsep rumah sendiri. Suasana kekeluargaan, cocok untuk mahasiswa yang ingin suasana homey.",
            "lat": -7.0515,
            "lng": 110.4388,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+7",
            "rating": 4.4,
            "review_count": 29,
            "available_rooms": 3,
            "total_rooms": 10,
            "kontak": "0822-5566-7788",
            "pemilik": "Bapak Bambang Sutrisno"
        },
        {
            "nama": "Kos Putra Wisma Undip",
            "alamat": "Jl. Taman Tirto No. 7, Tembalang",
            "kecamatan": "Tembalang",
            "harga": 1800000,
            "tipe": "putra",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "TV", "Meja Belajar", "Lemari", "Parkir Motor", "Laundry", "Cleaning Service"]),
            "deskripsi": "Kos putra premium terbaik di Tembalang. Full furnished dengan cleaning service mingguan. Lokasi hanya 5 menit dari gerbang UNDIP.",
            "lat": -7.0492,
            "lng": 110.4370,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+8",
            "rating": 4.8,
            "review_count": 56,
            "available_rooms": 1,
            "total_rooms": 8,
            "kontak": "0815-6677-8899",
            "pemilik": "Bapak Drs. Agus Salim"
        },

        # =====================================================================
        # BANYUMANIK — 5 entri, harga 500rb - 1.5jt
        # =====================================================================
        {
            "nama": "Kos Putri Permata Banyumanik",
            "alamat": "Jl. Srondol Kulon No. 12, Banyumanik",
            "kecamatan": "Banyumanik",
            "harga": 800000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "Parkir Motor"]),
            "deskripsi": "Kos putri bersih dan rapi di kawasan Banyumanik. Akses mudah ke jalan tol dan pusat kota Semarang.",
            "lat": -7.0638,
            "lng": 110.4175,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+9",
            "rating": 4.5,
            "review_count": 33,
            "available_rooms": 3,
            "total_rooms": 10,
            "kontak": "0812-9988-7766",
            "pemilik": "Ibu Endang Lestari"
        },
        {
            "nama": "Kos Putra Griya Banyumanik",
            "alamat": "Jl. Pudak Payung No. 20, Banyumanik",
            "kecamatan": "Banyumanik",
            "harga": 500000,
            "tipe": "putra",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Luar"]),
            "deskripsi": "Kos putra ekonomis dengan lokasi strategis di Banyumanik. Dekat dengan pusat perbelanjaan dan akses transportasi umum.",
            "lat": -7.0710,
            "lng": 110.4120,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+10",
            "rating": 3.9,
            "review_count": 18,
            "available_rooms": 4,
            "total_rooms": 8,
            "kontak": "0856-1122-3345",
            "pemilik": "Bapak Slamet Widodo"
        },
        {
            "nama": "Kos Campur Harmoni Residence",
            "alamat": "Jl. Ngesrep Barat No. 9, Banyumanik",
            "kecamatan": "Banyumanik",
            "harga": 1100000,
            "tipe": "campur",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "Parkir Motor", "Dapur Bersama", "Laundry"]),
            "deskripsi": "Kos campur modern dengan fasilitas lengkap. Suasana harmonis dan nyaman, cocok untuk pekerja muda dan mahasiswa.",
            "lat": -7.0590,
            "lng": 110.4198,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+11",
            "rating": 4.6,
            "review_count": 41,
            "available_rooms": 2,
            "total_rooms": 12,
            "kontak": "0878-5544-3322",
            "pemilik": "Ibu Siti Aminah"
        },
        {
            "nama": "Kos Putri Cendana House",
            "alamat": "Jl. Sumurboto No. 14, Banyumanik",
            "kecamatan": "Banyumanik",
            "harga": 1500000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "TV", "Parkir Motor", "Laundry", "Dapur Bersama", "CCTV"]),
            "deskripsi": "Kos putri premium dengan keamanan CCTV 24 jam. Kamar luas dan bersih, lingkungan elit di kawasan Sumurboto.",
            "lat": -7.0560,
            "lng": 110.4210,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+12",
            "rating": 4.7,
            "review_count": 52,
            "available_rooms": 1,
            "total_rooms": 8,
            "kontak": "0813-7788-9911",
            "pemilik": "Ibu Hj. Fatimah"
        },
        {
            "nama": "Kos Putra Elang Jaya",
            "alamat": "Jl. Srondol Wetan No. 6, Banyumanik",
            "kecamatan": "Banyumanik",
            "harga": 700000,
            "tipe": "putra",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Dalam", "Dapur Bersama"]),
            "deskripsi": "Kos putra nyaman dengan harga bersahabat. Lokasi tenang di kawasan Srondol Wetan, cocok untuk mahasiswa dan pekerja.",
            "lat": -7.0625,
            "lng": 110.4155,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+13",
            "rating": 4.2,
            "review_count": 25,
            "available_rooms": 3,
            "total_rooms": 10,
            "kontak": "0821-9900-1122",
            "pemilik": "Bapak Joko Susanto"
        },

        # =====================================================================
        # PEDURUNGAN — 4 entri, harga 400rb - 1.2jt
        # =====================================================================
        {
            "nama": "Kos Campur Pedurungan Asri",
            "alamat": "Jl. Pedurungan Tengah No. 10, Pedurungan",
            "kecamatan": "Pedurungan",
            "harga": 600000,
            "tipe": "campur",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Dalam"]),
            "deskripsi": "Kos campur sederhana dan bersih di kawasan Pedurungan. Dekat pasar tradisional dan pusat kuliner lokal.",
            "lat": -6.9910,
            "lng": 110.4530,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+14",
            "rating": 4.1,
            "review_count": 19,
            "available_rooms": 5,
            "total_rooms": 10,
            "kontak": "0857-2233-4455",
            "pemilik": "Bapak Wahyu Hidayat"
        },
        {
            "nama": "Kos Putri Mawar Indah",
            "alamat": "Jl. Plamongan Sari No. 7, Pedurungan",
            "kecamatan": "Pedurungan",
            "harga": 450000,
            "tipe": "putri",
            "fasilitas": json.dumps(["Parkir Motor", "Kamar Mandi Luar", "Dapur Bersama"]),
            "deskripsi": "Kos putri murah dan nyaman di Pedurungan. Pilihan tepat bagi mahasiswi yang mencari kos dengan harga ekonomis.",
            "lat": -6.9935,
            "lng": 110.4575,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+15",
            "rating": 3.8,
            "review_count": 14,
            "available_rooms": 6,
            "total_rooms": 10,
            "kontak": "0822-6677-8800",
            "pemilik": "Ibu Nurjannah"
        },
        {
            "nama": "Kos Putra Pedurungan Jaya",
            "alamat": "Jl. Pedurungan Lor No. 15, Pedurungan",
            "kecamatan": "Pedurungan",
            "harga": 400000,
            "tipe": "putra",
            "fasilitas": json.dumps(["Parkir Motor", "Kamar Mandi Luar"]),
            "deskripsi": "Kos putra paling terjangkau di Pedurungan. Fasilitas dasar dengan lingkungan yang aman dan nyaman.",
            "lat": -6.9888,
            "lng": 110.4498,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+16",
            "rating": 3.5,
            "review_count": 11,
            "available_rooms": 7,
            "total_rooms": 10,
            "kontak": "0815-3344-5567",
            "pemilik": "Bapak Mulyono"
        },
        {
            "nama": "Kos Campur Graha Pedurungan",
            "alamat": "Jl. Soekarno Hatta No. 45, Pedurungan",
            "kecamatan": "Pedurungan",
            "harga": 1200000,
            "tipe": "campur",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "Parkir Motor", "Laundry", "CCTV", "Dapur Bersama"]),
            "deskripsi": "Kos campur premium di jalan utama Pedurungan. Akses mudah ke mana saja dengan fasilitas lengkap dan keamanan terjamin.",
            "lat": -6.9870,
            "lng": 110.4550,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+17",
            "rating": 4.5,
            "review_count": 37,
            "available_rooms": 2,
            "total_rooms": 12,
            "kontak": "0878-9900-1123",
            "pemilik": "Bapak Ir. Supriyanto"
        },

        # =====================================================================
        # GAJAHMUNGKUR — 4 entri, harga 700rb - 2jt
        # =====================================================================
        {
            "nama": "Kos Putri Gajahmungkur Permai",
            "alamat": "Jl. Menoreh Utara No. 8, Gajahmungkur",
            "kecamatan": "Gajahmungkur",
            "harga": 950000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "Parkir Motor", "Laundry"]),
            "deskripsi": "Kos putri asri di kawasan Gajahmungkur. Dekat dengan Tugu Muda dan pusat kota, lingkungan tenang dan hijau.",
            "lat": -7.0140,
            "lng": 110.4085,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+18",
            "rating": 4.6,
            "review_count": 40,
            "available_rooms": 2,
            "total_rooms": 10,
            "kontak": "0812-5566-7789",
            "pemilik": "Ibu Dra. Sulistyowati"
        },
        {
            "nama": "Kos Putra Wisma Diponegoro",
            "alamat": "Jl. Sultan Agung No. 30, Gajahmungkur",
            "kecamatan": "Gajahmungkur",
            "harga": 1300000,
            "tipe": "putra",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "TV", "Parkir Motor", "Laundry", "Dapur Bersama"]),
            "deskripsi": "Kos putra eksklusif dekat RS Kariadi dan kampus UNDIP Pleburan. Fasilitas lengkap dengan suasana tenang.",
            "lat": -7.0165,
            "lng": 110.4110,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+19",
            "rating": 4.4,
            "review_count": 35,
            "available_rooms": 3,
            "total_rooms": 10,
            "kontak": "0856-8899-0012",
            "pemilik": "Bapak Prof. Suherman"
        },
        {
            "nama": "Kos Campur Panorama Hill",
            "alamat": "Jl. Menoreh Tengah No. 15, Gajahmungkur",
            "kecamatan": "Gajahmungkur",
            "harga": 2000000,
            "tipe": "campur",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "TV", "Parkir Mobil", "Parkir Motor", "Laundry", "Dapur Bersama", "Kolam Renang", "Gym"]),
            "deskripsi": "Kos campur mewah dengan pemandangan kota Semarang. Fasilitas setara apartemen dengan kolam renang dan gym.",
            "lat": -7.0125,
            "lng": 110.4070,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+20",
            "rating": 4.9,
            "review_count": 73,
            "available_rooms": 1,
            "total_rooms": 15,
            "kontak": "0813-1122-3346",
            "pemilik": "Bapak H. Rachman Hakim"
        },
        {
            "nama": "Kos Putri Sekar Arum",
            "alamat": "Jl. Papandayan No. 5, Gajahmungkur",
            "kecamatan": "Gajahmungkur",
            "harga": 700000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Dalam", "Dapur Bersama"]),
            "deskripsi": "Kos putri sederhana namun nyaman di kawasan Gajahmungkur. Harga terjangkau dengan fasilitas yang memadai.",
            "lat": -7.0155,
            "lng": 110.4095,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+21",
            "rating": 4.2,
            "review_count": 22,
            "available_rooms": 4,
            "total_rooms": 8,
            "kontak": "0821-4455-6678",
            "pemilik": "Ibu Wulandari"
        },

        # =====================================================================
        # SEMARANG TENGAH — 3 entri, harga 800rb - 2.5jt
        # =====================================================================
        {
            "nama": "Kos Campur City Center Residence",
            "alamat": "Jl. Pandanaran No. 55, Semarang Tengah",
            "kecamatan": "Semarang Tengah",
            "harga": 2500000,
            "tipe": "campur",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "TV", "Parkir Mobil", "Parkir Motor", "Laundry", "Cleaning Service", "CCTV", "Resepsionis"]),
            "deskripsi": "Kos premium di jantung kota Semarang. Lokasi paling strategis dekat Simpang Lima, cocok untuk profesional dan eksekutif muda.",
            "lat": -6.9847,
            "lng": 110.4103,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+22",
            "rating": 4.8,
            "review_count": 89,
            "available_rooms": 2,
            "total_rooms": 20,
            "kontak": "0812-7788-9902",
            "pemilik": "PT. Graha Kos Nusantara"
        },
        {
            "nama": "Kos Putra Simpang Lima Inn",
            "alamat": "Jl. Ahmad Yani No. 18, Semarang Tengah",
            "kecamatan": "Semarang Tengah",
            "harga": 1500000,
            "tipe": "putra",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "TV", "Parkir Motor", "Laundry"]),
            "deskripsi": "Kos putra strategis dekat Simpang Lima. Akses mudah ke pusat bisnis, mall, dan hiburan kota Semarang.",
            "lat": -6.9870,
            "lng": 110.4130,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+23",
            "rating": 4.5,
            "review_count": 48,
            "available_rooms": 3,
            "total_rooms": 12,
            "kontak": "0857-3344-5568",
            "pemilik": "Bapak Hendra Gunawan"
        },
        {
            "nama": "Kos Putri Lawang Sewu Residence",
            "alamat": "Jl. Pemuda No. 40, Semarang Tengah",
            "kecamatan": "Semarang Tengah",
            "harga": 800000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Dalam", "Dapur Bersama", "Ruang Tamu"]),
            "deskripsi": "Kos putri nyaman di kawasan bersejarah dekat Lawang Sewu. Suasana kota tua yang unik dengan harga terjangkau.",
            "lat": -6.9835,
            "lng": 110.4115,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+24",
            "rating": 4.3,
            "review_count": 27,
            "available_rooms": 4,
            "total_rooms": 10,
            "kontak": "0878-2233-4457",
            "pemilik": "Ibu Kartini Susilo"
        },

        # =====================================================================
        # NGALIYAN (dekat UNNES) — 4 entri, harga 500rb - 1.3jt
        # =====================================================================
        {
            "nama": "Kos Putri Griya UNNES",
            "alamat": "Jl. Taman Siswa No. 10, Ngaliyan",
            "kecamatan": "Ngaliyan",
            "harga": 650000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Dalam", "Dapur Bersama"]),
            "deskripsi": "Kos putri strategis dekat kampus UNNES. Lingkungan mahasiswa yang ramah dan nyaman untuk belajar.",
            "lat": -7.0045,
            "lng": 110.3540,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+25",
            "rating": 4.3,
            "review_count": 30,
            "available_rooms": 3,
            "total_rooms": 10,
            "kontak": "0812-1122-3348",
            "pemilik": "Ibu Nur Hidayah"
        },
        {
            "nama": "Kos Putra Wisma Ngaliyan",
            "alamat": "Jl. Prof. Hamka No. 22, Ngaliyan",
            "kecamatan": "Ngaliyan",
            "harga": 500000,
            "tipe": "putra",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Luar"]),
            "deskripsi": "Kos putra murah dekat UNNES. Pilihan tepat bagi mahasiswa baru yang mencari kos dengan budget terbatas.",
            "lat": -7.0060,
            "lng": 110.3515,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+26",
            "rating": 3.8,
            "review_count": 16,
            "available_rooms": 6,
            "total_rooms": 10,
            "kontak": "0856-4455-6679",
            "pemilik": "Bapak Suparman"
        },
        {
            "nama": "Kos Campur Ngaliyan Residence",
            "alamat": "Jl. Raya Ngaliyan No. 35, Ngaliyan",
            "kecamatan": "Ngaliyan",
            "harga": 1300000,
            "tipe": "campur",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "Parkir Motor", "Laundry", "Dapur Bersama", "CCTV"]),
            "deskripsi": "Kos campur premium di jalan utama Ngaliyan. Fasilitas lengkap dengan keamanan 24 jam, cocok untuk mahasiswa dan pekerja.",
            "lat": -7.0025,
            "lng": 110.3560,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+27",
            "rating": 4.6,
            "review_count": 44,
            "available_rooms": 2,
            "total_rooms": 12,
            "kontak": "0813-5566-7790",
            "pemilik": "Bapak Drs. Mulyadi"
        },
        {
            "nama": "Kos Putri Melati Ngaliyan",
            "alamat": "Jl. Kliwonan No. 8, Ngaliyan",
            "kecamatan": "Ngaliyan",
            "harga": 750000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "AC", "Parkir Motor", "Kamar Mandi Dalam"]),
            "deskripsi": "Kos putri bersih dan terawat di kawasan Ngaliyan. Dekat UNNES dengan suasana asri dan udara sejuk.",
            "lat": -7.0038,
            "lng": 110.3548,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+28",
            "rating": 4.4,
            "review_count": 26,
            "available_rooms": 3,
            "total_rooms": 8,
            "kontak": "0821-7788-9913",
            "pemilik": "Ibu Rahayu Ningsih"
        },

        # =====================================================================
        # CANDISARI — 3 entri, harga 500rb - 1.5jt
        # =====================================================================
        {
            "nama": "Kos Putra Candisari Sejahtera",
            "alamat": "Jl. Karanganyar No. 12, Candisari",
            "kecamatan": "Candisari",
            "harga": 550000,
            "tipe": "putra",
            "fasilitas": json.dumps(["WiFi", "Parkir Motor", "Kamar Mandi Luar", "Dapur Bersama"]),
            "deskripsi": "Kos putra ekonomis di kawasan Candisari. Dekat dengan pusat kota dan akses transportasi yang mudah.",
            "lat": -7.0058,
            "lng": 110.4195,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+29",
            "rating": 3.9,
            "review_count": 15,
            "available_rooms": 5,
            "total_rooms": 10,
            "kontak": "0857-6677-8802",
            "pemilik": "Bapak Suroto"
        },
        {
            "nama": "Kos Putri Candi Indah Residence",
            "alamat": "Jl. Tegalsari Raya No. 20, Candisari",
            "kecamatan": "Candisari",
            "harga": 1500000,
            "tipe": "putri",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "TV", "Parkir Motor", "Laundry", "Dapur Bersama", "CCTV"]),
            "deskripsi": "Kos putri mewah di Candisari dengan fasilitas lengkap. Keamanan terjamin dengan CCTV dan penjaga 24 jam.",
            "lat": -7.0040,
            "lng": 110.4220,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+30",
            "rating": 4.7,
            "review_count": 50,
            "available_rooms": 1,
            "total_rooms": 10,
            "kontak": "0878-1122-3349",
            "pemilik": "Ibu Hj. Sumiati"
        },
        {
            "nama": "Kos Campur Candisari Residence",
            "alamat": "Jl. Jomblang Tengah No. 5, Candisari",
            "kecamatan": "Candisari",
            "harga": 900000,
            "tipe": "campur",
            "fasilitas": json.dumps(["WiFi", "AC", "Kamar Mandi Dalam", "Parkir Motor", "Dapur Bersama"]),
            "deskripsi": "Kos campur nyaman di kawasan Candisari. Lokasi strategis antara pusat kota dan kawasan pendidikan Semarang.",
            "lat": -7.0072,
            "lng": 110.4182,
            "foto": "https://placehold.co/800x600/1a1a2e/00d4aa?text=Kos+31",
            "rating": 4.3,
            "review_count": 28,
            "available_rooms": 3,
            "total_rooms": 10,
            "kontak": "0822-9900-1124",
            "pemilik": "Bapak Agus Purnomo"
        },
    ]

    # Masukkan semua data kos ke database
    for kos in kos_data:
        cursor.execute('''
            INSERT INTO kos (nama, alamat, kecamatan, harga, tipe, fasilitas, deskripsi,
                           lat, lng, foto, rating, review_count, available_rooms, total_rooms,
                           kontak, pemilik)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            kos["nama"], kos["alamat"], kos["kecamatan"], kos["harga"],
            kos["tipe"], kos["fasilitas"], kos["deskripsi"],
            kos["lat"], kos["lng"], kos["foto"], kos["rating"],
            kos["review_count"], kos["available_rooms"], kos["total_rooms"],
            kos["kontak"], kos["pemilik"]
        ))

    conn.commit()
    conn.close()
    print(f"✅ Berhasil memasukkan {len(kos_data)} data kos ke database.")


# =============================================================================
# FUNGSI QUERY — CRUD OPERATIONS
# =============================================================================

def get_all_kos(filters=None):
    """
    Mendapatkan semua data kos dengan filter opsional.

    Args:
        filters (dict): Dictionary filter opsional:
            - kecamatan (str): Filter berdasarkan kecamatan
            - tipe (str): Filter berdasarkan tipe kos ('putra', 'putri', 'campur')
            - harga_min (int): Harga minimum
            - harga_max (int): Harga maksimum
            - q (str): Kata kunci pencarian (nama, alamat, deskripsi)
            - sort (str): Pengurutan ('harga_asc', 'harga_desc', 'rating', 'terbaru')

    Returns:
        list[dict]: Daftar kos dalam format dict
    """
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM kos WHERE 1=1"
    params = []

    if filters:
        # Filter kecamatan
        if filters.get("kecamatan"):
            query += " AND kecamatan = ?"
            params.append(filters["kecamatan"])

        # Filter tipe
        if filters.get("tipe"):
            query += " AND tipe = ?"
            params.append(filters["tipe"])

        # Filter harga minimum
        if filters.get("harga_min"):
            query += " AND harga >= ?"
            params.append(int(filters["harga_min"]))

        # Filter harga maksimum
        if filters.get("harga_max"):
            query += " AND harga <= ?"
            params.append(int(filters["harga_max"]))

        # Pencarian kata kunci
        if filters.get("q"):
            query += " AND (nama LIKE ? OR alamat LIKE ? OR deskripsi LIKE ?)"
            search_term = f"%{filters['q']}%"
            params.extend([search_term, search_term, search_term])

        # Pengurutan
        sort = filters.get("sort", "rating")
        if sort == "harga_asc":
            query += " ORDER BY harga ASC"
        elif sort == "harga_desc":
            query += " ORDER BY harga DESC"
        elif sort == "rating":
            query += " ORDER BY rating DESC"
        elif sort == "terbaru":
            query += " ORDER BY id DESC"
        else:
            query += " ORDER BY rating DESC"
    else:
        query += " ORDER BY rating DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_kos_by_id(kos_id):
    """
    Mendapatkan detail kos berdasarkan ID.

    Args:
        kos_id (int): ID kos yang dicari

    Returns:
        dict or None: Data kos dalam format dict, atau None jika tidak ditemukan
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kos WHERE id = ?", (kos_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def get_popular_kos(limit=6):
    """
    Mendapatkan kos dengan rating tertinggi.

    Args:
        limit (int): Jumlah maksimum kos yang dikembalikan (default: 6)

    Returns:
        list[dict]: Daftar kos populer dalam format dict
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM kos ORDER BY rating DESC, review_count DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_kecamatan_list():
    """
    Mendapatkan daftar kecamatan unik beserta jumlah kos di masing-masing.

    Returns:
        list[dict]: Daftar kecamatan dengan format {'kecamatan': str, 'count': int}
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT kecamatan, COUNT(*) as count FROM kos GROUP BY kecamatan ORDER BY count DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_stats():
    """
    Mendapatkan statistik keseluruhan data kos.

    Returns:
        dict: Statistik dengan key:
            - total_kos (int): Jumlah total kos
            - total_area (int): Jumlah kecamatan/area
            - avg_rating (float): Rata-rata rating
            - total_rooms (int): Jumlah total kamar tersedia
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM kos")
    total_kos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT kecamatan) FROM kos")
    total_area = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(rating) FROM kos")
    avg_rating = round(cursor.fetchone()[0] or 0, 1)

    cursor.execute("SELECT SUM(available_rooms) FROM kos")
    total_rooms = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "total_kos": total_kos,
        "total_area": total_area,
        "avg_rating": avg_rating,
        "total_rooms": total_rooms
    }


# =============================================================================
# FUNGSI BOOKING
# =============================================================================

def create_booking(kos_id, nama, email, phone, tanggal_masuk, durasi, pesan=''):
    """
    Membuat booking baru untuk kos tertentu.

    Args:
        kos_id (int): ID kos yang akan dibooking
        nama (str): Nama lengkap pemesan
        email (str): Email pemesan
        phone (str): Nomor telepon pemesan
        tanggal_masuk (str): Tanggal mulai masuk (format: YYYY-MM-DD)
        durasi (int): Durasi sewa dalam bulan
        pesan (str): Pesan tambahan (opsional)

    Returns:
        dict: Hasil booking dengan key 'success' (bool) dan 'message' (str)
    """
    # Cek apakah kos tersedia
    kos = get_kos_by_id(kos_id)
    if not kos:
        return {"success": False, "message": "Kos tidak ditemukan."}

    if kos["available_rooms"] <= 0:
        return {"success": False, "message": "Maaf, kamar sudah penuh. Tidak ada kamar tersedia."}

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Simpan booking
        cursor.execute('''
            INSERT INTO bookings (kos_id, nama, email, phone, tanggal_masuk, durasi, pesan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (kos_id, nama, email, phone, tanggal_masuk, durasi, pesan))

        # Kurangi jumlah kamar tersedia
        cursor.execute(
            "UPDATE kos SET available_rooms = available_rooms - 1 WHERE id = ?",
            (kos_id,)
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": f"Booking berhasil! Kos '{kos['nama']}' telah dibooking atas nama {nama}. "
                       f"Silakan hubungi pemilik di {kos['kontak']} untuk konfirmasi."
        }
    except Exception as e:
        conn.rollback()
        conn.close()
        return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}


# =============================================================================
# FUNGSI CHAT HISTORY
# =============================================================================

def save_chat(session_id, role, content):
    """
    Menyimpan pesan chat ke database.

    Args:
        session_id (str): ID sesi chat
        role (str): Peran pengirim ('user' atau 'assistant')
        content (str): Isi pesan
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
    )
    conn.commit()
    conn.close()


def get_chat_history(session_id):
    """
    Mendapatkan riwayat chat berdasarkan session_id.

    Args:
        session_id (str): ID sesi chat

    Returns:
        list[dict]: Daftar pesan chat dalam format dict
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# =============================================================================
# FUNGSI AI HELPER
# =============================================================================

def get_kos_summary_for_ai():
    """
    Menghasilkan ringkasan data kos untuk konteks AI chatbot.
    Format teks yang mudah dibaca oleh model AI untuk menjawab pertanyaan pengguna.

    Returns:
        str: Ringkasan seluruh data kos dalam format teks terstruktur
    """
    all_kos = get_all_kos()
    stats = get_stats()

    summary = "=== DATA KOS SEMARANG ===\n"
    summary += f"Total: {stats['total_kos']} kos di {stats['total_area']} kecamatan\n"
    summary += f"Rating rata-rata: {stats['avg_rating']}\n"
    summary += f"Total kamar tersedia: {stats['total_rooms']}\n\n"

    for kos in all_kos:
        # Parse fasilitas dari JSON string
        try:
            fasilitas = json.loads(kos['fasilitas'])
            fasilitas_str = ", ".join(fasilitas)
        except (json.JSONDecodeError, TypeError):
            fasilitas_str = kos['fasilitas']

        summary += f"--- {kos['nama']} (ID: {kos['id']}) ---\n"
        summary += f"  Alamat: {kos['alamat']}\n"
        summary += f"  Kecamatan: {kos['kecamatan']}\n"
        summary += f"  Harga: Rp {kos['harga']:,}/bulan\n"
        summary += f"  Tipe: {kos['tipe']}\n"
        summary += f"  Fasilitas: {fasilitas_str}\n"
        summary += f"  Rating: {kos['rating']} ({kos['review_count']} review)\n"
        summary += f"  Kamar tersedia: {kos['available_rooms']}/{kos['total_rooms']}\n"
        summary += f"  Kontak: {kos['kontak']} ({kos['pemilik']})\n"
        summary += f"  Deskripsi: {kos['deskripsi']}\n\n"

    return summary


# =============================================================================
# MAIN — Jalankan langsung untuk membuat dan mengisi database
# =============================================================================

if __name__ == "__main__":
    print("🏠 KosSemarang — Inisialisasi Database")
    print("=" * 50)
    init_db()

    # Tampilkan statistik
    stats = get_stats()
    print(f"\n📊 Statistik Database:")
    print(f"   Total Kos     : {stats['total_kos']}")
    print(f"   Total Area    : {stats['total_area']} kecamatan")
    print(f"   Rating Rata²  : {stats['avg_rating']}")
    print(f"   Kamar Tersedia: {stats['total_rooms']}")

    # Tampilkan daftar kecamatan
    kecamatan_list = get_kecamatan_list()
    print(f"\n📍 Sebaran Kos per Kecamatan:")
    for kec in kecamatan_list:
        print(f"   {kec['kecamatan']}: {kec['count']} kos")

    print(f"\n✅ Database siap digunakan: {DB_PATH}")
