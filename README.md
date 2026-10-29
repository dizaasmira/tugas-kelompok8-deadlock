# Analisis dan Penanganan Deadlock pada Transaksi Toko UMKM

Repository tugas kelompok mata kuliah *Sistem Operasi* (Tugas Kelompok K-3 / TK-3D, Kelas D).
Proyek ini menganalisis **deadlock** pada tiga transaksi toko online UMKM (stok, pembayaran, kurir) menggunakan dua pendekatan: **algoritma Banker** (penghindaran) dan **demo deadlock dengan thread Python** (terjadi, dicegah, dan dipulihkan), dijalankan pada lingkungan Ubuntu Server 26.04.

## Lingkungan & Spesifikasi Sistem

**Sistem Operasi:** Ubuntu Server 26.04 (`srv-toko-250660121024`)

**Bahasa Pemrograman:** Python 3 (modul `threading`, tanpa pustaka tambahan)

**Konteks Kasus:** Toko UMKM Kelas D saat flash sale, dengan tiga lock: `STOK`, `PEMBAYARAN`, `KURIR`

**Transaksi:** `T1` (STOK lalu PEMBAYARAN), `T2` (PEMBAYARAN lalu KURIR), `T3` (KURIR lalu STOK)

## Struktur Berkas Repository

| Berkas | Fungsi | Cara Kerja |
|--------|--------|------------|
| `banker.py` | Perhitungan Need, Available, safe sequence, dan keputusan permintaan | Algoritma Banker, 5 proses (P0-P4) dan 3 sumber daya |
| `deadlock_demo.py` | Demo deadlock tiga transaksi | 3 thread, `MODE=deadlock` atau `MODE=fixed` |
| `README.md` | Dokumentasi repository | - |

## Panduan Menjalankan Program & Pengujian

### A. Pengujian Algoritma Banker

```bash
python3 banker.py
```

Keluaran yang diharapkan: keadaan awal `SAFE ['P0', 'P1', 'P2', 'P3', 'P4']`, lalu empat permintaan uji:

| Permintaan | Keputusan |
|------------|-----------|
| P4 (1,1,0) | Ditolak (unsafe) |
| P1 (1,0,1) | Dikabulkan (safe), urutan P1, P0, P2, P3, P4 |
| P0 (3,0,0) | Ditolak, melebihi Need |
| P4 (3,0,0) | Ditunda, melebihi Available |

### B. Pengujian Demo Deadlock

1. **Mode deadlock** (deadlock terjadi, pulih lewat timeout 2 detik):
   ```bash
   MODE=deadlock TIMEOUT=2 python3 deadlock_demo.py
   ```
   Hasil bisa berbeda tiap run karena urutan timeout antar thread tidak deterministik (semua `deadlock`, atau satu transaksi sempat `selesai`).

2. **Mode fixed** (pencegahan dengan urutan lock `STOK < PEMBAYARAN < KURIR`):
   ```bash
   MODE=fixed TIMEOUT=5 python3 deadlock_demo.py
   ```
   Hasil yang diharapkan: `{'T1': 'selesai', 'T2': 'selesai', 'T3': 'selesai'}` tanpa timeout.

Di Windows PowerShell: `$env:MODE="fixed"; $env:TIMEOUT="5"; python deadlock_demo.py`

## Hasil Pengujian di VM

| Pengujian | Hasil |
|-----------|-------|
| Banker, safe state awal | SAFE `<P0, P1, P2, P3, P4>` |
| Deadlock run 1 (PID 2421) | T1, T2, T3 semua deadlock |
| Deadlock run 2 (PID 2434) | T1 dan T3 deadlock, T2 selesai |
| Mode fixed (PID 2875) | T1, T2, T3 selesai tanpa timeout |

## Anggota Kelompok

| Nama | NIM | Peran |
|------|-----|-------|
| (isi) | (isi) | (isi) |
