Markdown
# ⛏️ GXT Mining Auto-Claim Bot

Bot otomatis berbasis Python untuk melakukan klaim berkala (*auto-claim*) pada platform **GXT Mining Exchange**. Bot ini dilengkapi dengan antarmuka terminal (*UI Console*) yang bersih, simetris, terpusat secara otomatis, serta dilengkapi dengan fitur **Live Time Clock** (waktu berdetik secara *real-time*).

## ✨ Fitur Utama
* **All-in-One Console Box:** Judul, status, detail saldo, dan waktu terintegrasi dalam satu kotak rapi.
* **Live Update Timer:** Detik pada jam pembaruan bergerak secara *real-time* setiap detik.
* **Auto Slider Puzzle Solver:** Mampu mendeteksi dan menyelesaikan tantangan *captcha/puzzle* dari server secara otomatis.
* **Jeda Acak (Anti-Bot):** Menggunakan rentang waktu tunggu acak aman (62-68 menit) setelah klaim berhasil.
* **Responsive Layout:** Tampilan otomatis mendeteksi lebar terminal Anda agar posisi teks selalu berada tepat di tengah.

---

## 🚀 Panduan Instalasi (Dari Awal)

Ikuti langkah-langkah berikut untuk menjalankan bot di komputer atau server Anda:

### Langkah 1: Clone atau Siapkan Folder
Pastikan Anda sudah menginstal **Python (versi 3.8 atau yang lebih baru)** dan **Git Bash** (jika menggunakan Windows). Buka terminal Anda dan masuk ke folder bot:
```bash
cd path/to/your/folder/gxt-bot
Langkah 2: Instalasi Library/Dependensi
Instal semua modul eksternal yang dibutuhkan oleh bot menggunakan berkas requirements.txt yang telah disediakan:

Bash
pip install -r requirements.txt
Langkah 3: Konfigurasi Akun
Buka file utama gxt.py menggunakan teks editor pilihan Anda (VS Code, Notepad++, dll). Cari baris CONFIG di bagian atas, lalu ganti dengan kredensial akun Anda:

Python
# ═══════════════════════════════════════════
# CONFIG (Isi Email & Password Anda di sini)
# ═══════════════════════════════════════════
EMAIL = "email_anda@gmail.com"
PASSWORD = "password_anda_123"
Langkah 4: Jalankan Bot
Jalankan bot menggunakan perintah Python standar berikut di terminal Anda:

Bash
python gxt.py
📊 Visualisasi Tampilan UI Terminal
Ketika dijalankan, terminal Anda akan dibersihkan secara otomatis dan menampilkan antarmuka simetris seperti berikut:

Plaintext
                         ┌───────────────────────────────────────────┐
                         │    GXT MINING AUTO-CLAIM BOT (PYTHON)     │
                         │         Status: LIVE & COLORIZED          │
                         ├───────────────────────────────────────────┤
                         │ 💰 SALDO UTAMA  :       124.5050 GXT     │
                         │ ⚡ SPEED MINING :         0.1500 /jam    │
                         │ ⛏️ TOTAL MINED  :        45.1200 GXT     │
                         ├───────────────────────────────────────────┤
                         │ 🕒 WAKTU UPDATE : 2026-07-11 12:45:20     │
                         └───────────────────────────────────────────┘
                         ℹ️ Siklus selesai. Cek ulang dalam: 64m 58s
Catatan: Bagian 🕒 WAKTU UPDATE dan hitung mundur di bawahnya akan terus bergerak dan berganti secara live setiap detik.

⚠️ Disclaimer
Penggunaan bot ini sepenuhnya menjadi tanggung jawab masing-masing pengguna. Pastikan untuk selalu memantau performa akun secara berkala.
