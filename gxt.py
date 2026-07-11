import os
import sys
import time
import hmac
import hashlib
import random
import uuid
import re
from datetime import datetime, timedelta
import httpx
from supabase import create_client, Client

# ═══════════════════════════════════════════
# CONFIG (Isi Email & Password Anda di sini)
# ═══════════════════════════════════════════
EMAIL = "email_anda@gmail.com"
PASSWORD = "password_anda_123"

SUPABASE_URL = 'https://eoerppzmsxhgmrcxrika.supabase.co'
SUPABASE_KEY = 'sb_publishable_j-w0ixQxY1i505RyOrepyQ_9KosAIBA'
GXT_BASE_URL = 'https://gxtexchange.com'
CHECK_INTERVAL = 60  # 1 menit (dalam detik)

if not EMAIL or not PASSWORD or "DI_SINI" in EMAIL:
    print("\033[91m❌ Error: Silakan isi EMAIL dan PASSWORD Anda di dalam script terlebih dahulu!\033[0m")
    sys.exit(1)

# Inisialisasi Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ═══════════════════════════════════════════
# STATE & UTILS
# ═══════════════════════════════════════════
access_token = None
token_expiry = 0

# Simpan data balance secara global agar bisa di-refresh live setiap detik oleh loop utama
current_balance = 0.0
current_rate = 0.1
current_total_mined = 0.0

# ANSI Colors untuk tampilan terminal
C_RESET = "\033[0m"
C_TIME = "\033[90m"     # Abu-abu
C_INFO = "\033[94m"     # Biru
C_SUCCESS = "\033[92m"  # Hijau
C_WARN = "\033[93m"     # Kuning
C_ERROR = "\033[91m"    # Merah

def draw_interface(msg, level='info'):
    """Menggambar ulang Kotak Besar secara utuh dengan Live Time dan Log Status."""
    try:
        lebar = os.get_terminal_size().columns
    except:
        lebar = 80

    # Mengambil data timestamp real-time detik ini
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    box_width = 47
    pad_box = max(0, (lebar - box_width) // 2)
    spc = " " * pad_box
    
    # Reset kursor ke pojok kiri atas Git Bash & bersihkan layar ke bawah
    sys.stdout.write("\033[H\033[J")
    
    # 1. Cetak Kotak Utama
    print(f"{spc}{C_SUCCESS}┌───────────────────────────────────────────┐{C_RESET}")
    print(f"{spc}{C_SUCCESS}│    GXT MINING AUTO-CLAIM BOT (PYTHON)     │{C_RESET}")
    print(f"{spc}{C_SUCCESS}│         Status: LIVE & COLORIZED          │{C_RESET}")
    print(f"{spc}{C_SUCCESS}├───────────────────────────────────────────┤{C_RESET}")
    print(f"{spc}│ {C_INFO}💰 SALDO UTAMA  :{C_RESET} {current_balance:14.4f} GXT     │")
    print(f"{spc}│ {C_WARN}⚡ SPEED MINING :{C_RESET} {current_rate:14.4f} /jam    │")
    print(f"{spc}│ {C_SUCCESS}⛏️ TOTAL MINED  :{C_RESET} {current_total_mined:14.4f} GXT     │")
    print(f"{spc}{C_SUCCESS}├───────────────────────────────────────────┤{C_RESET}")
    print(f"{spc}│ {C_TIME}🕒 WAKTU UPDATE :{C_RESET} {ts:<18} │")
    print(f"{spc}{C_SUCCESS}└───────────────────────────────────────────┘{C_RESET}")
    
    # 2. Cetak Baris Status/Hitung Mundur di bawahnya
    icons = {'info': 'ℹ️', 'success': '✅', 'error': '❌', 'warn': '⚠️'}
    colors = {'info': C_INFO, 'success': C_SUCCESS, 'error': C_ERROR, 'warn': C_WARN}
    
    icon = icons.get(level, '•')
    color = colors.get(level, C_RESET)
    
    raw_len = len(f" {msg}") + 3
    padding_log = max(0, (lebar - raw_len) // 2)
    
    print(f"{' ' * padding_log}{color}{icon} {msg}{C_RESET}", end="", flush=True)

# ═══════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════
def authenticate():
    global access_token, token_expiry
    now_ms = time.time() * 1000
    
    if access_token and now_ms < (token_expiry - 5 * 60 * 1000):
        return access_token
        
    draw_interface('Sedang melakukan autentikasi...', level='info')
    try:
        res = supabase.auth.sign_in_with_password({"email": EMAIL, "password": PASSWORD})
        access_token = res.session.access_token
        token_expiry = (time.time() + res.session.expires_in) * 1000
        
        supabase.postgrest.auth(access_token)
        draw_interface('Berhasil login!', level='success')
        time.sleep(1)
        return access_token
    except Exception as e:
        draw_interface(f'Autentikasi gagal: {str(e)}', level='error')
        return None

# ═══════════════════════════════════════════
# PUZZLE SOLVER
# ═══════════════════════════════════════════
def solve_puzzle():
    draw_interface('Menyelesaikan slider puzzle...', level='info')
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        with httpx.Client() as client:
            get_res = client.get(f"{GXT_BASE_URL}/api/public/puzzle", headers=headers)
            if get_res.status_code != 200:
                draw_interface(f'Gagal mendapatkan puzzle. Status: {get_res.status_code}', level='error')
                return None
                
            puzzle = get_res.json()
            if not puzzle.get('ok') or not puzzle.get('id') or not isinstance(puzzle.get('target_ratio'), (int, float)):
                draw_interface('Struktur puzzle tidak valid.', level='error')
                return None
                
            target_pct = puzzle['target_ratio'] * 100
            draw_interface(f'Target Puzzle: {target_pct:.1f}%', level='info')
            time.sleep(1)
            
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
                draw_interface('Puzzle berhasil dipecahkan!', level='success')
                return puzzle['id']
                
            draw_interface('Gagal memecahkan puzzle.', level='error')
            return None
    except Exception as e:
        draw_interface(f'Error puzzle: {str(e)}', level='error')
        return None

# ═══════════════════════════════════════════
# CLAIM MINING
# ═══════════════════════════════════════════
def claim_mining():
    key = str(uuid.uuid4())
    draw_interface(f'Memulai klaim ({key[:8]}...)', level='info')
    
    try:
        res = supabase.rpc('claim_mining_v1', {'_idempotency_key': key, '_puzzle_id': None}).execute()
        data = res.data
    except Exception as e:
        msg = str(e)
        if 'puzzle_required' in msg or 'puzzle_invalid' in msg:
            draw_interface('Butuh puzzle, mencoba memecahkan...', level='warn')
            time.sleep(1)
            puzzle_id = solve_puzzle()
            if not puzzle_id:
                return {'status': 'puzzle_failed'}
                
            try:
                new_key = str(uuid.uuid4())
                res = supabase.rpc('claim_mining_v1', {'_idempotency_key': new_key, '_puzzle_id': puzzle_id}).execute()
                data = res.data
            except Exception as e2:
                draw_interface('Klaim gagal setelah puzzle.', level='error')
                return {'status': 'error'}
        else:
            draw_interface(f'Klaim gagal: {msg}', level='error')
            return {'status': 'error'}

    if data and data.get('ok'):
        reward = float(data.get('reward', 0))
        draw_interface(f'🎉 +{reward:.4f} GXT diklaim!', level='success')
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
            random_minutes = random.randint(62, 68)
            time.sleep(1.5)
            return random_minutes * 60
            
        if result['status'] == 'too_soon':
            return max(CHECK_INTERVAL, result['next_in'] + 10)
            
        if result['status'] == 'puzzle_failed':
            return 10 * 60
            
        return 5 * 60
    except Exception as e:
        draw_interface(f'Kesalahan Siklus: {str(e)}', level='error')
        return 5 * 60

# ═══════════════════════════════════════════
# EXECUTION ENGINE
# ═══════════════════════════════════════════
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        try:
            wait_seconds = run_cycle()
            
            # Loop hitung mundur ini sekarang memanggil draw_interface()
            # Sehingga waktu di dalam kotak ikut berdetik secara Live!
            while wait_seconds > 0:
                m, s = divmod(wait_seconds, 60)
                status_msg = f"Siklus selesai. Cek ulang dalam: {m:02d}m {s:02d}s"
                draw_interface(status_msg, level='info')
                time.sleep(1)
                wait_seconds -= 1
                
        except KeyboardInterrupt:
            print(f"\n\n{C_WARN}⚠️ Bot dimatikan oleh pengguna.{C_RESET}")
            sys.exit(0)
        except Exception as err:
            draw_interface(f"Kondisi tidak terduga: {str(err)}", level='error')
            time.sleep(60)
