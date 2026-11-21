import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from inventaris.io_handler import load_inventory_csv, save_report_json
from inventaris.processor import (
    build_full_report,
    filter_low_stock,
    remove_duplicates,
    search_items,
    summarize_by_category,
)
from inventaris.validator import validate_non_negative_int

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CSV_PATH = BASE_DIR / "data" / "inventaris.csv"
DEFAULT_JSON_PATH = BASE_DIR / "output" / "laporan_inventaris.json"


def format_rupiah(angka: int | float) -> str:
    """Mengubah angka ke format mata uang Rupiah."""
    return f"Rp {angka:,.0f}".replace(",", ".")


def print_divider(char: str = "=", length: int = 78) -> None:
    print(char * length)


def print_table(items: List[Dict[str, Any]], title: str = "DAFTAR BARANG INVENTARIS") -> None:
    """Menampilkan data barang dalam bentuk tabel CLI."""
    print_divider("=")
    print(f" {title} (Total: {len(items)} item)")
    print_divider("=")

    if not items:
        print(" [!] Tidak ada data barang untuk ditampilkan.")
        print_divider("-")
        return

    header = f"{'No':<4} | {'Kode':<8} | {'Nama Barang':<24} | {'Kategori':<12} | {'Stok':>6} | {'Harga':>14} | {'Nilai Aset':>16}"
    print(header)
    print_divider("-")

    for idx, item in enumerate(items, start=1):
        nama = item["nama_barang"]
        if len(nama) > 24:
            nama = nama[:21] + "..."
        harga_fmt = format_rupiah(item["harga"])
        aset_fmt = format_rupiah(item["nilai_aset"])
        row = f"{idx:<4} | {item['kode_barang']:<8} | {nama:<24} | {item['kategori']:<12} | {item['stok']:>6} | {harga_fmt:>14} | {aset_fmt:>16}"
        print(row)

    print_divider("-")


def print_recap_table(summary: Dict[str, Dict[str, Any]]) -> None:
    """Menampilkan tabel rekapitulasi nilai aset per kategori."""
    print_divider("=")
    print(" REKAPITULASI INVENTARIS PER KATEGORI")
    print_divider("=")

    if not summary:
        print(" [!] Tidak ada data rekapitulasi.")
        print_divider("-")
        return

    header = f"{'No':<4} | {'Kategori':<18} | {'Jenis Barang':>14} | {'Total Stok':>12} | {'Total Nilai Aset':>20}"
    print(header)
    print_divider("-")

    grand_total_stok = 0
    grand_total_aset = 0
    grand_total_jenis = 0

    for idx, (cat, val) in enumerate(summary.items(), start=1):
        grand_total_jenis += val["jumlah_jenis_barang"]
        grand_total_stok += val["total_stok"]
        grand_total_aset += val["total_nilai_aset"]
        aset_str = format_rupiah(val["total_nilai_aset"])
        print(f"{idx:<4} | {cat:<18} | {val['jumlah_jenis_barang']:>14} | {val['total_stok']:>12} | {aset_str:>20}")

    print_divider("=")
    total_str = format_rupiah(grand_total_aset)
    print(f"{'TOTAL KESELURUHAN':<25} | {grand_total_jenis:>14} | {grand_total_stok:>12} | {total_str:>20}")
    print_divider("=")


def load_data(filepath: Path | str) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
    raw_items, warnings = load_inventory_csv(str(filepath))
    clean_items, duplicate_codes = remove_duplicates(raw_items)
    return clean_items, warnings, duplicate_codes


def main() -> None:
    current_csv_path = DEFAULT_CSV_PATH
    items: List[Dict[str, Any]] = []

    print("\n" + "=" * 78)
    print(" SELAMAT DATANG DI APLIKASI MONITOR STOK & INVENTARIS BARANG")
    print(" UTS Pemrograman Dasar (TK091)")
    print("=" * 78)

    try:
        items, warnings, dupes = load_data(current_csv_path)
        print(f"[*] Berhasil memuat data dari '{current_csv_path.name}'.")
        print(f"    - Barang valid & unik : {len(items)} item")
        if dupes:
            print(f"    - Duplikat diabaikan  : {len(dupes)} baris (Kode: {', '.join(dupes)})")
        if warnings:
            print(f"    - Peringatan data rusak: {len(warnings)} baris dilewati.")
            for w in warnings:
                print(f"      * {w}")
    except Exception as exc:
        print(f"[!] Peringatan saat startup: {exc}")
        print("    Silakan gunakan Menu 6 untuk memilih file data CSV yang valid.")

    while True:
        print("\n" + "-" * 78)
        print(" MENU UTAMA:")
        print("  1. Tampilkan Semua Data Inventaris")
        print("  2. Cari Barang (Nama / Kategori)")
        print("  3. Filter Barang Stok Menipis")
        print("  4. Tampilkan Rekapitulasi Aset per Kategori")
        print("  5. Ekspor Laporan Analisis ke JSON")
        print("  6. Muat Ulang File CSV (Ganti Path)")
        print("  7. Keluar")
        print("-" * 78)

        try:
            choice = input("Pilih menu (1-7): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n[!] Sinyal interupsi terdeteksi. Menutup program...")
            sys.exit(0)

        if choice == "1":
            print_table(items, title="SEMUA DATA INVENTARIS")

        elif choice == "2":
            if not items:
                print("[!] Data inventaris masih kosong. Silakan muat file CSV terlebih dahulu.")
                continue
            keyword = input("Masukkan kata kunci pencarian (Nama/Kategori): ").strip()
            results = search_items(items, keyword)
            print_table(results, title=f"HASIL PENCARIAN DENGAN KATA KUNCI '{keyword}'")

        elif choice == "3":
            if not items:
                print("[!] Data inventaris masih kosong. Silakan muat file CSV terlebih dahulu.")
                continue
            threshold_input = input("Masukkan ambang batas stok menipis (default 5): ").strip()
            if threshold_input == "":
                threshold = 5
            else:
                try:
                    threshold = validate_non_negative_int(threshold_input)
                except ValueError as err:
                    print(f"[!] Input tidak valid: {err}")
                    continue

            low_stock_items = filter_low_stock(items, threshold)
            print_table(low_stock_items, title=f"BARANG DENGAN STOK MENIPIS (STOK <= {threshold})")

        elif choice == "4":
            if not items:
                print("[!] Data inventaris masih kosong. Silakan muat file CSV terlebih dahulu.")
                continue
            summary = summarize_by_category(items)
            print_recap_table(summary)

        elif choice == "5":
            if not items:
                print("[!] Data inventaris masih kosong. Tidak ada yang dapat diekspor.")
                continue
            threshold_input = input("Masukkan ambang batas stok untuk laporan (default 5): ").strip()
            if threshold_input == "":
                threshold = 5
            else:
                try:
                    threshold = validate_non_negative_int(threshold_input)
                except ValueError as err:
                    print(f"[!] Input tidak valid: {err}")
                    continue

            report = build_full_report(items, threshold)
            target_path = DEFAULT_JSON_PATH
            custom_path = input(f"Simpan ke [{target_path}]: ").strip()
            if custom_path:
                target_path = Path(custom_path)

            try:
                saved_location = save_report_json(report, str(target_path))
                print(f"[+] Laporan JSON berhasil disimpan di: {saved_location}")
            except Exception as err:
                print(f"[!] Gagal mengekspor laporan: {err}")

        elif choice == "6":
            path_input = input(f"Masukkan path file CSV baru (tekan Enter untuk '{DEFAULT_CSV_PATH}'): ").strip()
            new_path = Path(path_input) if path_input else DEFAULT_CSV_PATH
            try:
                new_items, warnings, dupes = load_data(new_path)
                items = new_items
                current_csv_path = new_path
                print(f"[+] Berhasil memuat data dari '{new_path}'.")
                print(f"    - Total item aktif   : {len(items)}")
                if dupes:
                    print(f"    - Duplikat diabaikan : {len(dupes)} baris ({', '.join(dupes)})")
                if warnings:
                    print(f"    - Data ditolak       : {len(warnings)} baris.")
                    for w in warnings:
                        print(f"      * {w}")
            except Exception as err:
                print(f"[!] Gagal membaca file: {err}")

        elif choice == "7":
            print("\nTerima kasih telah menggunakan Aplikasi Monitor Stok & Inventaris. Sampai jumpa!")
            break

        else:
            print("[!] Pilihan menu tidak valid. Harap pilih angka 1 sampai 7.")


if __name__ == "__main__":
    main()
