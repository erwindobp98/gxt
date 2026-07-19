import os
import sys
import time
import hmac
import hashlib
import random
import uuid
import re
import json
from datetime import datetime, timedelta
import httpx
from supabase import create_client, Client
from playwright.sync_api import sync_playwright

# ═══════════════════════════════════════════
# CONFIG (Isi Email & Password Anda di sini)
# ═══════════════════════════════════════════
EMAIL = "email_anda@gmail.com"
PASSWORD_GXT = "PasswordGXTAnda123!"     # <--- Password khusus untuk login GXT (Metode 1)
PASSWORD_GOOGLE = "PasswordGoogleAnda123!" # <--- Password asli akun Google/Gmail Anda (Metode 2)

SUPABASE_URL = 'https://eoerppzmsxhgmrcxrika.supabase.co'
SUPABASE_KEY = 'sb_publishable_j-w0ixQxY1i505RyOrepyQ_9KosAIBA'
GXT_BASE_URL = 'https://gxtexchange.com'
CHECK_INTERVAL = 60  # 1 menit (dalam detik)

if not EMAIL or not PASSWORD_GXT or not PASSWORD_GOOGLE or "DI_SINI" in EMAIL:
    print("\033[91m❌ Error: Silakan isi EMAIL, PASSWORD_GXT, dan PASSWORD_GOOGLE Anda di dalam script terlebih dahulu!\033[0m")
    sys.exit(1)

# Inisialisasi Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ═══════════════════════════════════════════
# STATE & UTILS
# ═══════════════════════════════════════════
access_token = None
token_expiry = 0

# State Global untuk menjaga Output Tetap Live Setiap Detik
current_balance = 0.0
current_rate = 0.1
current_total_mined = 0.0
current_msg = "Memulai sistem..."
current_level = "info"

# ANSI Colors untuk tampilan terminal
C_RESET = "\033[0m"
C_TIME = "\033[90m"     # Abu-abu
C_INFO = "\033[94m"     # Biru
C_SUCCESS = "\033[92m"  # Hijau
C_WARN = "\033[93m"     # Kuning
C_ERROR = "\033[91m"    # Merah

def draw_interface():
    """Menggambar ulang seluruh antarmuka dengan ukuran kotak yang lebih besar dan lebar (100% Live Time)"""
    try:
        lebar = os.get_terminal_size().columns
    except:
        lebar = 80

    # Mengambil data timestamp real-time detik ini
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    box_width = 57
    pad_box = max(0, (lebar - box_width) // 2)
    spc = " " * pad_box
    
    # Reset kursor ke pojok kiri atas & bersihkan layar ke bawah
    sys.stdout.write("\033[H\033[J")
    
    # 1. Cetak Kotak Utama
    print(f"{spc}{C_SUCCESS}┌─────────────────────────────────────────────────────────┐{C_RESET}")
    print(f"{spc}{C_SUCCESS}│                   GXT MINING AUTO-CLAIM                 │{C_RESET}")
    print(f"{spc}{C_SUCCESS}│                       Status: LIVE                      │{C_RESET}")
    print(f"{spc}{C_SUCCESS}├─────────────────────────────────────────────────────────┤{C_RESET}")
    print(f"{spc}│ {C_INFO}💰 SALDO UTAMA    :{C_RESET} {current_balance:18.4f} GXT           │")
    print(f"{spc}│ {C_WARN}⚡ SPEED MINING   :{C_RESET} {current_rate:18.4f} /jam          │")
    print(f"{spc}│ {C_SUCCESS}⛏️ TOTAL MINED    :{C_RESET} {current_total_mined:18.4f} GXT           │")
    print(f"{spc}{C_SUCCESS}├─────────────────────────────────────────────────────────┤{C_RESET}")
    print(f"{spc}│ {C_TIME}🕒 WAKTU UPDATE   :{C_RESET}      {ts:<22}      │")
    print(f"{spc}{C_SUCCESS}└─────────────────────────────────────────────────────────┘{C_RESET}")
    
    # 2. Cetak Baris Status Output di bawahnya
    icons = {'info': 'ℹ️', 'success': '✅', 'error': '❌', 'warn': '⚠️'}
    colors = {'info': C_INFO, 'success': C_SUCCESS, 'error': C_ERROR, 'warn': C_WARN}
    
    icon = icons.get(current_level, '•')
    color = colors.get(current_level, C_RESET)
    
    raw_len = len(f" {current_msg}") + 3
    padding_log = max(0, (lebar - raw_len) // 2)
    
    print(f"{' ' * padding_log}{color}{icon} {current_msg}{C_RESET}", end="", flush=True)

def update_status(level, msg):
    """Mengubah data status global dan langsung memicu pembaruan layar visual"""
    global current_msg, current_level
    current_level = level
    current_msg = msg
    draw_interface()

# ═══════════════════════════════════════════
# DUAL-METHOD AUTHENTICATION
# ═══════════════════════════════════════════
def authenticate():
    global access_token, token_expiry
    now_ms = time.time() * 1000
    
    # 0. Cek apakah token lama masih aktif & valid
    if access_token and now_ms < (token_expiry - 5 * 60 * 1000):
        return access_token
        
    # =========================================================================
    # METODE 1: Login Langsung via Email & Password Supabase (Sangat Cepat & Hemat RAM)
    # =========================================================================
    update_status('info', 'Mencoba login instan via Jalur Email & Password...')
    try:
        res = supabase.auth.sign_in_with_password({"email": EMAIL, "password": PASSWORD_GXT})
        access_token = res.session.access_token
        token_expiry = (time.time() + res.session.expires_in) * 1000
        
        supabase.postgrest.auth(access_token)
        update_status('success', 'Metode 1 Berhasil: Login Email Sukses!')
        time.sleep(1.5)
        return access_token
        
    except Exception as e_email:
        update_status('warn', 'Metode 1 Gagal. Mencoba cadangan Google Auth...')
        time.sleep(1.5)

    # =========================================================================
    # METODE 2: Cadangan Otomatis via Google Auth Simulator (Menggunakan Playwright)
    # =========================================================================
    update_status('info', 'Memicu Simulator Google Auth via Playwright...')
    
    username_clean = EMAIL.split('@')[0]
    folder_profil = f"./sesi_google/{username_clean}"
    
    try:
        with sync_playwright() as p:
            # headless=False dimunculkan agar Anda bisa memantau / mengisi OTP Google jika diminta saat pertama run.
            # Jika sudah sukses login sekali, Anda bisa mengubahnya kembali menjadi True.
            context = p.chromium.launch_persistent_context(
                user_data_dir=folder_profil, 
                headless=True, 
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            page = context.pages[0] if context.pages else context.new_page()
            
            # 1. Buka halaman login GXT
            page.goto(f"{GXT_BASE_URL}/login")
            page.wait_for_load_state("networkidle")
            
            # 2. Klik tombol "Sign in with Google"
            page.click("button:has-text('Google')")
            page.wait_for_load_state("networkidle")
            
            # 3. Otomatisasi pengisian form Google jika dialihkan ke halaman akun Google
            if "accounts.google.com" in page.url:
                update_status('info', 'Mengisi form login otomatis di halaman Google...')
                page.fill("input[type='email']", EMAIL)
                page.click("#identifierNext")
                page.wait_for_timeout(2500)
                
                page.fill("input[type='password']", PASSWORD_GOOGLE)
                page.click("#passwordNext")
                page.wait_for_load_state("networkidle")
            
            # 4. Tunggu kembali ke domain utama GXT setelah berhasil login
            page.wait_for_url(f"{GXT_BASE_URL}/**", timeout=60000)
            
            # 5. Ekstrak Local Storage untuk mengambil Token Supabase baru
            storage_data = page.evaluate("() => JSON.stringify(localStorage)")
            storage_dict = json.loads(storage_data)
            
            supabase_key = "sb-eoerppzmsxhgmrcxrika-auth-token"
            if supabase_key in storage_dict:
                token_data = json.loads(storage_dict[supabase_key])
                access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                token_expiry = (time.time() + expires_in) * 1000
                
                # Pasang token baru ke client Supabase
                supabase.postgrest.auth(access_token)
                update_status('success', 'Metode 2 Berhasil: Token Google Auth Diperbarui!')
                
                context.close()
                time.sleep(1.5)
                return access_token
            else:
                context.close()
                update_status('error', 'Google Auth sukses, tetapi token Supabase tidak ditemukan.')
                return None
                
    except Exception as e_google:
        update_status('error', f'Semua Metode Login Gagal! G-Auth Error: {str(e_google)}')
        return None

# ═══════════════════════════════════════════
# PUZZLE SOLVER
# ═══════════════════════════════════════════
def solve_puzzle():
    update_status('info', 'Menyelesaikan slider puzzle...')
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        with httpx.Client() as client:
            get_res = client.get(f"{GXT_BASE_URL}/api/public/puzzle", headers=headers)
            if get_res.status_code != 200:
                update_status('error', f'Gagal mendapatkan puzzle (Status: {get_res.status_code})')
                return None
                
            puzzle = get_res.json()
            if not puzzle.get('ok') or not puzzle.get('id') or not isinstance(puzzle.get('target_ratio'), (int, float)):
                update_status('error', 'Struktur puzzle tidak valid.')
                return None
                
            target_pct = puzzle['target_ratio'] * 100
            update_status('info', f'Target Puzzle: {target_pct:.1f}%')
            time.sleep(1.5)
            
            seed = f"gxt-bot-{int(time.time() * 1000)}".encode('utf-8')
            device_hash = hashlib.sha256(seed).hexdigest()[:32]
            
            payload = {
                "id": puzzle['id'],
                "ratio": puzzle['target_ratio'],
                "device_hash": device_hash
            }
            
            post_res = client.post(f"{GXT_BASE_URL}/api/public/puzzle", headers=headers, json=payload)
            result = post_res.json()
            
            if result.get('ok'):
                update_status('success', 'Puzzle berhasil dipecahkan!')
                return puzzle['id']
                
            update_status('error', 'Gagal memecahkan puzzle.')
            return None
    except Exception as e:
        update_status('error', f'Error puzzle: {str(e)}')
        return None

# ═══════════════════════════════════════════
# CLAIM MINING
# ═══════════════════════════════════════════
def claim_mining():
    key = str(uuid.uuid4())
    update_status('info', f'Memulai klaim ({key[:8]}...)')
    
    try:
        res = supabase.rpc('claim_mining_v1', {'_idempotency_key': key, '_puzzle_id': None}).execute()
        data = res.data
    except Exception as e:
        msg = str(e)
        if 'puzzle_required' in msg or 'puzzle_invalid' in msg:
            update_status('warn', 'Butuh puzzle, mencoba memecahkan...')
            time.sleep(1.5)
            puzzle_id = solve_puzzle()
            if not puzzle_id:
                return {'status': 'puzzle_failed'}
                
            try:
                new_key = str(uuid.uuid4())
                res = supabase.rpc('claim_mining_v1', {'_idempotency_key': new_key, '_puzzle_id': puzzle_id}).execute()
                data = res.data
            except Exception as e2:
                update_status('error', 'Klaim gagal setelah puzzle.')
                return {'status': 'error'}
        else:
            update_status('error', f'Klaim gagal: {msg}')
            return {'status': 'error'}

    if data and data.get('ok'):
        reward = float(data.get('reward', 0))
        update_status('success', f'🎉 +{reward:.4f} GXT diklaim!')
        return {'status': 'success', 'reward': reward}
        
    if data and data.get('next_in_seconds'):
        seconds = int(data['next_in_seconds'])
        return {'status': 'too_soon', 'next_in': seconds}
        
    return {'status': 'unknown', 'data': data}

# ═══════════════════════════════════════════
# MAIN LOOP CYCLE
# ═══════════════════════════════════════════
def run_cycle():
    global current_balance, current_rate, current_total_mined
    token = authenticate()
    if not token:
        return 5 * 60

    try:
        state_res = supabase.from_('mining_state').select('*').maybe_single().execute()
        rate_res = supabase.from_('admin_settings').select('value').eq('key', 'mining_rate_per_hour').maybe_single().execute()
        bal_res = supabase.from_('balances').select('amount').eq('asset', 'GXT').maybe_single().execute()
        
        state = state_res.data if state_res else None
        rate_data = rate_res.data if rate_res else None
        bal_data = bal_res.data if bal_res else None
        
        current_rate = float(rate_data['value']) if rate_data and rate_data.get('value') else 0.1
        current_balance = float(bal_data['amount']) if bal_data and bal_data.get('amount') else 0.0
        current_total_mined = float(state['total_mined']) if state and state.get('total_mined') else 0.0
        
        result = claim_mining()
        
        if result['status'] == 'success':
            random_minutes = random.randint(61, 64)
            time.sleep(1.5)
            return random_minutes * 60
            
        if result['status'] == 'too_soon':
            seconds = result['next_in']
            update_status('info', f'Terlalu cepat. Tunggu {seconds // 3600}j {(seconds % 3600) // 60}m lagi.')
            time.sleep(2)
            return max(CHECK_INTERVAL, result['next_in'] + 10)
            
        if result['status'] == 'puzzle_failed':
            time.sleep(2)
            return 10 * 60
            
        time.sleep(2)
        return 5 * 60
    except Exception as e:
        update_status('error', f'Kesalahan Siklus: {str(e)}')
        time.sleep(3)
        return 5 * 60

# ═══════════════════════════════════════════
# EXECUTION ENGINE
# ═══════════════════════════════════════════
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        try:
            wait_seconds = run_cycle()
            
            while wait_seconds > 0:
                m, s = divmod(wait_seconds, 60)
                status_countdown = f"Siklus selesai. Cek ulang dalam: {m:02d}m {s:02d}s"
                
                current_level = 'info'
                current_msg = status_countdown
                draw_interface()
                
                time.sleep(1)
                wait_seconds -= 1
                
        except KeyboardInterrupt:
            print(f"\n\n{C_WARN}⚠️ Bot dimatikan oleh pengguna.{C_RESET}")
            sys.exit(0)
        except Exception as err:
            current_level = 'error'
            current_msg = f"Kondisi tidak terduga: {str(err)}"
            draw_interface()
            time.sleep(60)
