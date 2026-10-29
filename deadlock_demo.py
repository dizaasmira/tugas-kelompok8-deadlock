#!/usr/bin/env python3
"""Demo deadlock checkout Toko Online UMKM - K-3 Sistem Operasi Kelas D.

Tiga sumber daya (masing-masing 1 instance, dimodelkan sebagai lock):
  STOK       = lock tabel stok
  PEMBAYARAN = lock transaksi pembayaran
  KURIR      = slot kurir

Tiga transaksi checkout:
  T1 memegang STOK       lalu meminta PEMBAYARAN
  T2 memegang PEMBAYARAN lalu meminta KURIR
  T3 memegang KURIR      lalu meminta STOK
-> siklus T1 -> T2 -> T3 -> T1 (circular wait) = DEADLOCK.

Mode:
  python3 deadlock_demo.py deadlock   # urutan lock berbeda tiap transaksi (deadlock)
  python3 deadlock_demo.py fixed      # urutan lock global STOK -> PEMBAYARAN -> KURIR (aman)
  python3 deadlock_demo.py            # jalankan keduanya

Agar skrip tidak hang selamanya, permintaan lock memakai timeout (TIMEOUT detik).
Timeout di sini dipakai sebagai alat deteksi; di sistem nyata ia juga strategi
recovery (melepas lock, rollback, retry).
"""
import sys
import threading
import time

TIMEOUT = 2.0
LOCKS = {
    "STOK": threading.Lock(),
    "PEMBAYARAN": threading.Lock(),
    "KURIR": threading.Lock(),
}
URUTAN_GLOBAL = ["STOK", "PEMBAYARAN", "KURIR"]

# (nama transaksi, lock yang dipegang dulu, lock yang diminta berikutnya)
TRANSAKSI = [
    ("T1", "STOK", "PEMBAYARAN"),
    ("T2", "PEMBAYARAN", "KURIR"),
    ("T3", "KURIR", "STOK"),
]

log_lock = threading.Lock()
hasil = {}


def log(msg):
    with log_lock:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def checkout_deadlock(nama, pertama, kedua, barrier):
    """Mengambil lock sesuai kebutuhan masing-masing (urutan bisa berbeda -> deadlock)."""
    LOCKS[pertama].acquire()
    log(f"{nama}: memegang {pertama}")
    barrier.wait()          # pastikan semua transaksi sudah memegang lock pertama (hold and wait)
    log(f"{nama}: meminta {kedua} ...")
    if LOCKS[kedua].acquire(timeout=TIMEOUT):
        log(f"{nama}: SUKSES mendapat {kedua}")
        hasil[nama] = "selesai"
        LOCKS[kedua].release()
    else:
        log(f"{nama}: TIMEOUT menunggu {kedua} (dipegang transaksi lain) -> terdeteksi deadlock")
        hasil[nama] = "deadlock"
    LOCKS[pertama].release()   # recovery: lepas lock agar transaksi lain bisa lanjut


def checkout_fixed(nama, pertama, kedua, barrier):
    """Selalu mengambil lock sesuai urutan global, apa pun kebutuhan awalnya."""
    butuh = sorted([pertama, kedua], key=URUTAN_GLOBAL.index)
    barrier.wait()          # mulai bersamaan agar kondisinya sama dengan mode deadlock
    for nm in butuh:
        log(f"{nama}: meminta {nm} ...")
        if not LOCKS[nm].acquire(timeout=10):
            hasil[nama] = "timeout"
            return
        log(f"{nama}: memegang {nm}")
    time.sleep(0.05)        # simulasi proses checkout
    log(f"{nama}: checkout SELESAI")
    hasil[nama] = "selesai"
    for nm in reversed(butuh):
        LOCKS[nm].release()


def jalankan(mode):
    hasil.clear()
    fungsi = checkout_deadlock if mode == "deadlock" else checkout_fixed
    judul = ("MODE DEADLOCK: urutan lock berbeda antar transaksi" if mode == "deadlock"
             else "MODE FIXED: urutan lock global STOK -> PEMBAYARAN -> KURIR")
    print("\n" + "=" * 70 + f"\n{judul}\n" + "=" * 70)
    barrier = threading.Barrier(len(TRANSAKSI))
    threads = [threading.Thread(target=fungsi, args=(n, a, b, barrier), name=n) for n, a, b in TRANSAKSI]
    t0 = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"\nRingkasan ({time.time() - t0:.1f} detik): {dict(sorted(hasil.items()))}")
    if mode == "deadlock":
        print("Wait-for graph: T1 -> T2 -> T3 -> T1 (siklus = circular wait).")
        print("Empat kondisi Coffman terpenuhi: mutual exclusion, hold and wait, no preemption, circular wait.")
    else:
        print("Circular wait terputus: semua transaksi mengambil lock dengan urutan yang sama.")
    return hasil


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "semua"
    if mode in ("deadlock", "semua"):
        jalankan("deadlock")
    if mode in ("fixed", "semua"):
        jalankan("fixed")
