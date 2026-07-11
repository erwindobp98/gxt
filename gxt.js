#!/usr/bin/env node
/**
 * GXT Mining Auto-Claim Bot
 * Works on VPS, Termux, or any Node.js environment.
 * 
 * Setup:
 *   npm install
 *   cp .env.example .env
 *   nano .env  (fill in credentials)
 *   node gxt-miner.mjs
 * 
 * Background:
 *   screen -dmS gxt node gxt-miner.mjs  (VPS)
 *   nohup node gxt-miner.mjs &           (Termux)
 */

import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// ═══════════════════════════════════════════
// LOAD .env (works on VPS + Termux)
// ═══════════════════════════════════════════
function loadEnv() {
  // Try script directory first, then cwd
  let envPath;
  try {
    const __dirname = dirname(fileURLToPath(import.meta.url));
    envPath = join(__dirname, '.env');
  } catch {
    envPath = join(process.cwd(), '.env');
  }
  
  if (!existsSync(envPath)) return;
  for (const line of readFileSync(envPath, 'utf8').split('\n')) {
    const t = line.trim();
    if (!t || t.startsWith('#')) continue;
    const i = t.indexOf('=');
    if (i === -1) continue;
    const k = t.slice(0, i).trim();
    let v = t.slice(i + 1).trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
    if (!process.env[k]) process.env[k] = v;
  }
}
loadEnv();

// ═══════════════════════════════════════════
// CONFIG
// ═══════════════════════════════════════════
const SUPABASE_URL = 'https://eoerppzmsxhgmrcxrika.supabase.co';
const SUPABASE_KEY = 'sb_publishable_j-w0ixQxY1i505RyOrepyQ_9KosAIBA';
const EMAIL = process.env.GXT_EMAIL;
const PASSWORD=process.env.GXT_PASSWORD;
const CHECK_INTERVAL = 60 * 1000;
const GXT_BASE_URL = 'https://gxtexchange.com';

if (!EMAIL || !PASSWORD) {
  console.error('❌ Missing GXT_EMAIL or GXT_PASSWORD');
  console.error('   cp .env.example .env && nano .env');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY, {
  auth: { persistSession: false, autoRefreshToken: false }
});

function log(level, msg) {
  const ts = new Date().toLocaleString('en-US', { timeZone: 'Asia/Jakarta', hour12: false });
  const icons = { info: 'ℹ️', success: '✅', error: '❌', warn: '⚠️' };
  console.log(`[${ts}] ${icons[level] || '•'} ${msg}`);
}

// ═══════════════════════════════════════════
// AUTH
// ═══════════════════════════════════════════
let accessToken = null;
let tokenExpiry = 0;

async function authenticate() {
  if (accessToken && Date.now() < tokenExpiry - 5 * 60 * 1000) return accessToken;
  log('info', 'Authenticating...');
  const { data, error } = await supabase.auth.signInWithPassword({ email: EMAIL, password: PASSWORD });
  if (error) { log('error', `Auth failed: ${error.message}`); return null; }
  accessToken = data.session.access_token;
  tokenExpiry = Date.now() + (data.session.expires_in * 1000);
  log('success', `Authenticated as ${data.user.email}`);
  return accessToken;
}

// ═══════════════════════════════════════════
// PUZZLE SOLVER
// ═══════════════════════════════════════════
async function solvePuzzle() {
  log('info', 'Solving slider puzzle...');
  
  const getRes = await fetch(`${GXT_BASE_URL}/api/public/puzzle`, {
    method: 'GET',
    cache: 'no-store',
    headers: { 'User-Agent': 'Mozilla/5.0' }
  });
  if (!getRes.ok) { log('error', `Puzzle GET failed: ${getRes.status}`); return null; }

  const puzzle = await getRes.json();
  if (!puzzle.ok || !puzzle.id || typeof puzzle.target_ratio !== 'number') {
    log('error', `Invalid puzzle: ${JSON.stringify(puzzle)}`);
    return null;
  }

  log('info', `Puzzle target: ${(puzzle.target_ratio * 100).toFixed(1)}%`);

  const deviceHash = crypto.createHash('sha256').update(`gxt-bot-${Date.now()}`).digest('hex').slice(0, 32);
  
  const postRes = await fetch(`${GXT_BASE_URL}/api/public/puzzle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0' },
    body: JSON.stringify({ id: puzzle.id, ratio: puzzle.target_ratio, device_hash: deviceHash })
  });

  const result = await postRes.json();
  if (result.ok) {
    log('success', 'Puzzle solved!');
    return puzzle.id;
  }

  log('error', `Puzzle failed: ${JSON.stringify(result)}`);
  return null;
}

// ═══════════════════════════════════════════
// CLAIM
// ═══════════════════════════════════════════
async function claimMining() {
  const key = crypto.randomUUID();
  log('info', `Claiming (${key.slice(0, 8)}...)`);

  let { data, error } = await supabase.rpc('claim_mining_v1', {
    _idempotency_key: key,
    _puzzle_id: null,
  });

  if (error) {
    const msg = error.message || '';
    if (msg.includes('puzzle_required') || msg.includes('puzzle_invalid')) {
      log('warn', 'Puzzle required, solving...');
      const puzzleId = await solvePuzzle();
      if (!puzzleId) return { status: 'puzzle_failed' };

      const newKey = crypto.randomUUID();
      ({ data, error } = await supabase.rpc('claim_mining_v1', {
        _idempotency_key: newKey,
        _puzzle_id: puzzleId,
      }));
      if (error) { log('error', `Claim failed: ${error.message}`); return { status: 'error' }; }
    } else {
      log('error', `Claim failed: ${msg}`);
      return { status: 'error', error: msg };
    }
  }

  if (data?.ok) {
    const reward = Number(data.reward || 0);
    const next = data.next_claim_at ? new Date(data.next_claim_at) : null;
    log('success', `+${reward.toFixed(4)} GXT! Next: ${next?.toLocaleString('en-US', { timeZone: 'Asia/Jakarta' }) || '?'}`);
    return { status: 'success', reward, nextClaim: next };
  }

  if (data?.next_in_seconds) {
    const s = Math.ceil(Number(data.next_in_seconds));
    log('info', `Too soon. Next in ${Math.floor(s/3600)}h ${Math.floor(s%3600/60)}m`);
    return { status: 'too_soon', nextIn: s };
  }

  return { status: 'unknown', data };
}

// ═══════════════════════════════════════════
// MAIN LOOP
// ═══════════════════════════════════════════
async function runCycle() {
  const token = await authenticate();
  if (!token) return 5 * 60 * 1000;

  const { data: state } = await supabase.from('mining_state').select('*').maybeSingle();
  const { data: rateData } = await supabase.from('admin_settings').select('value').eq('key', 'mining_rate_per_hour').maybeSingle();
  const { data: balData } = await supabase.from('balances').select('amount').eq('asset', 'GXT').maybeSingle();

  const rate = Number(rateData?.value || 0.1);
  const balance = Number(balData?.amount || 0);
  const totalMined = Number(state?.total_mined || 0);
  const lastClaim = state?.last_claim_at ? new Date(state.last_claim_at).getTime() : 0;
  const hoursAgo = ((Date.now() - lastClaim) / 3600000).toFixed(1);

  log('info', `Balance: ${balance.toFixed(4)} GXT | Rate: ${rate}/hr | Mined: ${totalMined.toFixed(4)} | Last: ${hoursAgo}h`);

  const result = await claimMining();

  if (result.status === 'success') {
    const wait = result.nextClaim ? (result.nextClaim.getTime() - Date.now() + 60000) : 3600000;
    return Math.max(CHECK_INTERVAL, wait);
  }
  if (result.status === 'too_soon') return Math.max(CHECK_INTERVAL, result.nextIn * 1000 + 60000);
  if (result.status === 'puzzle_failed') return 10 * 60 * 1000;
  return 5 * 60 * 1000;
}

// ═══════════════════════════════════════════
// START
// ═══════════════════════════════════════════
const platform = typeof process.env.PREFIX === 'string' && process.env.PREFIX.includes('termux') ? 'Termux' : 'Server';
console.log('===========================================');
console.log('       GXT MINING AUTO-CLAIM BOT');
console.log(`       Platform: ${platform}`);
console.log(`       LIVE - ${new Date().toLocaleString('en-US', { timeZone: 'Asia/Jakarta', hour12: false })} WIB`);
console.log('===========================================');
console.log('');

while (true) {
  try {
    const wait = await runCycle();
    log('info', `Next check in ${Math.round(wait / 60000)} min\n`);
    await new Promise(r => setTimeout(r, wait));
  } catch (err) {
    log('error', `Unexpected: ${err.message}`);
    await new Promise(r => setTimeout(r, 60000));
  }
}
