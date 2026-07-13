## 🚀 Panduan Instalasi (Dari Awal)

Ikuti langkah-langkah berikut untuk menjalankan bot di komputer atau server Anda:

### Langkah 1: Clone atau Siapkan Folder

```
git clone https://github.com/erwindobp98/gxt-auto-mining.git
```

### Langkah 2: Instalasi Library/Dependensi
Install semua modul eksternal yang dibutuhkan oleh bot menggunakan berkas requirements.txt yang telah disediakan:
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
PASSWORD_GXT = "PasswordGXTAnda123!"     # <--- Password khusus untuk login GXT (Metode 1)
PASSWORD_GOOGLE = "PasswordGoogleAnda123!" # <--- Password asli akun Google/Gmail Anda (Metode 2)
```
### Langkah 4: Jalankan Bot
Jalankan bot menggunakan perintah Python standar berikut di terminal Anda:
```
python gxt.py
```
📊 Visualisasi Tampilan UI Terminal
Ketika dijalankan, terminal Anda akan dibersihkan secara otomatis dan menampilkan antarmuka simetris seperti berikut:

                         ┌───────────────────────────────────────────┐
                         │           GXT MINING AUTO-CLAIM           │
                         │               Status: LIVE                │
                         ├───────────────────────────────────────────┤
                         │ 💰 SALDO UTAMA  :       124.5050 GXT     │
                         │ ⚡ SPEED MINING :         0.1500 /jam    │
                         │ ⛏️ TOTAL MINED  :        45.1200 GXT     │
                         ├───────────────────────────────────────────┤
                         │ 🕒 WAKTU UPDATE : 2026-07-11 12:45:20     │
                         └───────────────────────────────────────────┘
                         ℹ️ Siklus selesai. Cek ulang dalam: 64m 58s

### Install untuk login menggunakan google auth jika login menggunakan email dan passwoard gagal.

1. Pastikan Anda sudah mengisi baris PASSWORD_GXT dan PASSWORD_GOOGLE di bagian paling atas script dengan password Anda masing-masing.

2. Saat pertama kali dijalankan, jendela browser Chromium akan muncul.

3. Perhatikan proses pengisian otomatisnya. Jika Google memicu verifikasi/OTP, silakan klik atau input kode keamanan tersebut di jendela browser secara manual.

4. Setelah bot berhasil melewati verifikasi Google dan mulai membaca saldo Anda di layar terminal, biarkan siklus pertama selesai.

5. (Opsional) Jika Anda ingin bot ini berjalan diam-diam tanpa memunculkan browser di kemudian hari, matikan script (Ctrl + C), ganti parameter headless=False menjadi headless=True di baris ke-104, lalu jalankan kembali scriptnya.
```
playwright install chromium

```
Atau
```
python -m playwright install
```
⚠️ Disclaimer
Penggunaan bot ini sepenuhnya menjadi tanggung jawab masing-masing pengguna. Pastikan untuk selalu memantau performa akun secara berkala.
