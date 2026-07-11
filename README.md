## 🚀 Panduan Instalasi (Dari Awal)

Ikuti langkah-langkah berikut untuk menjalankan bot di komputer atau server Anda:

### Langkah 1: Clone atau Siapkan Folder

```
git clone https://github.com/erwindobp98/gxt.git
```

### Langkah 2: Instalasi Library/Dependensi
Instal semua modul eksternal yang dibutuhkan oleh bot menggunakan berkas requirements.txt yang telah disediakan:
```
pip install -r requirements.txt
```

### Langkah 3: Konfigurasi Akun
Buka file utama gxt.py menggunakan teks editor pilihan Anda (VS Code, Notepad++, dll). Cari baris CONFIG di bagian atas, lalu ganti dengan kredensial akun Anda:
```
# ═══════════════════════════════════════════
# CONFIG (Isi Email & Password Anda di sini)
# ═══════════════════════════════════════════
EMAIL = "email_anda@gmail.com"
PASSWORD = "password_anda_123"
```

### Langkah 4: Jalankan Bot
Jalankan bot menggunakan perintah Python standar berikut di terminal Anda:
```
python gxt.py
```

📊 Visualisasi Tampilan UI Terminal
Ketika dijalankan, terminal Anda akan dibersihkan secara otomatis dan menampilkan antarmuka simetris seperti berikut:

                         ┌───────────────────────────────────────────┐
                         │         GXT MINING AUTO-CLAIM BOT         │
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
