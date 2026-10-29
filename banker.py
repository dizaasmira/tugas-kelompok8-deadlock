#!/usr/bin/env python3
"""Algoritma Banker - K-3 Sistem Operasi Kelas D (Analisis dan Penanganan Deadlock).

Kasus : checkout Toko Online UMKM.
Sumber daya : R1 = lock tabel stok (7), R2 = lock transaksi pembayaran (4), R3 = slot kurir (8)
Proses      : P0..P4 = lima transaksi checkout dari pelanggan berbeda
CATATAN     : matriks di bawah adalah ASUMSI kelompok (matriks dosen tidak dibagikan).
              Ganti TOTAL, ALLOCATION, MAX bila matriks resmi tersedia.

Pemakaian:
  python3 banker.py                 # jalankan semua skenario
  python3 banker.py P4 1 1 0        # simulasi request P4 meminta (1,1,0)
"""
import sys

RESOURCES = ["R1", "R2", "R3"]
TOTAL = [7, 4, 8]
ALLOCATION = {
    "P0": [1, 1, 0],
    "P1": [2, 0, 1],
    "P2": [1, 0, 3],
    "P3": [0, 2, 1],
    "P4": [1, 0, 1],
}
MAX = {
    "P0": [3, 2, 1],
    "P1": [3, 1, 2],
    "P2": [2, 1, 4],
    "P3": [1, 3, 2],
    "P4": [4, 1, 2],
}


def le(a, b):
    """True bila a <= b untuk semua elemen."""
    return all(x <= y for x, y in zip(a, b))


def add(a, b):
    return [x + y for x, y in zip(a, b)]


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def fmt(v):
    return "(" + ",".join(str(x) for x in v) + ")"


def hitung_need(alloc, mx):
    return {p: sub(mx[p], alloc[p]) for p in alloc}


def hitung_available(total, alloc):
    terpakai = [sum(a[j] for a in alloc.values()) for j in range(len(total))]
    return sub(total, terpakai)


def cetak_matriks(alloc, mx, need, available):
    print(f"{'Proses':<7}{'Allocation':<14}{'Max':<14}{'Need = Max - Alloc':<20}")
    for p in alloc:
        print(f"{p:<7}{fmt(alloc[p]):<14}{fmt(mx[p]):<14}{fmt(need[p]):<20}")
    print(f"Total     = {fmt(TOTAL)}")
    print(f"Available = Total - sum(Allocation) = {fmt(available)}")


def cek_safe(alloc, need, available, verbose=True):
    """Algoritma safety. Mengembalikan (safe, urutan)."""
    work = list(available)
    finish = {p: False for p in alloc}
    urutan = []
    if verbose:
        print(f"Work awal = Available = {fmt(work)}")
        print(f"{'Langkah':<9}{'Proses':<8}{'Need <= Work?':<26}{'Work sesudah':<14}")
    langkah = 0
    while True:
        ditemukan = False
        for p in alloc:
            if not finish[p] and le(need[p], work):
                langkah += 1
                work_baru = add(work, alloc[p])
                if verbose:
                    cek = f"{fmt(need[p])} <= {fmt(work)} Ya"
                    print(f"{langkah:<9}{p:<8}{cek:<26}{fmt(work_baru):<14}")
                work = work_baru
                finish[p] = True
                urutan.append(p)
                ditemukan = True
                break
        if not ditemukan:
            break
    safe = all(finish.values())
    if verbose:
        if safe:
            print(f"Semua Finish = true -> SAFE. Safe sequence: <{', '.join(urutan)}>")
        else:
            macet = [p for p, f in finish.items() if not f]
            print(f"Tidak ada proses yang bisa dilanjutkan. Finish=false: {macet} -> UNSAFE")
    return safe, urutan


def simulasi_request(proses, request, alloc, mx):
    """Algoritma resource-request Banker."""
    need = hitung_need(alloc, mx)
    available = hitung_available(TOTAL, alloc)
    print(f"\nRequest {proses} = {fmt(request)}")
    print(f"  Need[{proses}] = {fmt(need[proses])}, Available = {fmt(available)}")
    if not le(request, need[proses]):
        print("  DITOLAK: request melebihi Need (proses melampaui klaim maksimumnya).")
        return False
    if not le(request, available):
        print("  DITUNDA: request melebihi Available, proses harus menunggu.")
        return False
    # alokasi sementara
    alloc2 = {p: list(v) for p, v in alloc.items()}
    alloc2[proses] = add(alloc2[proses], request)
    need2 = hitung_need(alloc2, mx)
    avail2 = sub(available, request)
    print(f"  Alokasi sementara -> Available = {fmt(avail2)}, "
          f"Allocation[{proses}] = {fmt(alloc2[proses])}, Need[{proses}] = {fmt(need2[proses])}")
    safe, _ = cek_safe(alloc2, need2, avail2)
    if safe:
        print("  DIKABULKAN: sistem tetap safe.")
    else:
        print("  DITOLAK: jika dikabulkan sistem menjadi unsafe, proses harus menunggu.")
    return safe


def main():
    need = hitung_need(ALLOCATION, MAX)
    available = hitung_available(TOTAL, ALLOCATION)

    if len(sys.argv) == 5:
        simulasi_request(sys.argv[1], [int(x) for x in sys.argv[2:5]], ALLOCATION, MAX)
        return

    print("=== 1. Matriks Allocation, Max, Need ===")
    cetak_matriks(ALLOCATION, MAX, need, available)

    print("\n=== 2. Algoritma Safety (cek safe state) ===")
    safe, urutan = cek_safe(ALLOCATION, need, available)
    # verifikasi konsistensi: Work akhir harus sama dengan total sumber daya
    akhir = list(available)
    for p in urutan:
        akhir = add(akhir, ALLOCATION[p])
    print(f"Work akhir = {fmt(akhir)} (harus sama dengan Total {fmt(TOTAL)}): "
          f"{'konsisten' if akhir == TOTAL else 'TIDAK konsisten'}")

    print("\n=== 3. Simulasi Resource-Request ===")
    simulasi_request("P4", [1, 1, 0], ALLOCATION, MAX)   # skenario ditolak (unsafe)
    simulasi_request("P1", [1, 0, 1], ALLOCATION, MAX)   # skenario dikabulkan (safe)
    simulasi_request("P0", [3, 0, 0], ALLOCATION, MAX)   # melebihi Need
    simulasi_request("P4", [3, 0, 0], ALLOCATION, MAX)   # <= Need tapi melebihi Available (R1)


if __name__ == "__main__":
    main()
