import json
from pathlib import Path

from inventaris.validator import validate_row, validate_non_negative_int
from inventaris.io_handler import load_inventory_csv, save_report_json
from inventaris.processor import (
    remove_duplicates,
    get_unique_categories,
    search_items,
    filter_low_stock,
    summarize_by_category,
    build_full_report,
)

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "inventaris.csv"
JSON_OUTPUT_PATH = BASE_DIR / "output" / "laporan_inventaris.json"


def test_validator():
    valid_row = {"kode_barang": "B01", "nama_barang": "Pensil", "kategori": "ATK", "stok": "10", "harga": "2000"}
    ok, data, err = validate_row(valid_row, 1)
    assert ok is True and data is not None
    assert data["nilai_aset"] == 20000

    neg_stock = {"kode_barang": "B02", "nama_barang": "Buku", "kategori": "ATK", "stok": "-5", "harga": "5000"}
    ok, data, err = validate_row(neg_stock, 2)
    assert ok is False and "tidak boleh negatif" in err

    bad_price = {"kode_barang": "B03", "nama_barang": "Penggaris", "kategori": "ATK", "stok": "5", "harga": "gratis"}
    ok, data, err = validate_row(bad_price, 3)
    assert ok is False and "bukan angka valid" in err

    empty_col = {"kode_barang": "B04", "nama_barang": "", "kategori": "ATK", "stok": "5", "harga": "3000"}
    ok, data, err = validate_row(empty_col, 4)
    assert ok is False and "kosong" in err

    assert validate_non_negative_int("10") == 10
    try:
        validate_non_negative_int("-3")
        assert False
    except ValueError:
        pass

    try:
        validate_non_negative_int("abc")
        assert False
    except ValueError:
        pass


def test_io_and_processor():
    raw_items, warnings = load_inventory_csv(str(CSV_PATH))
    assert len(raw_items) == 7
    assert len(warnings) == 3

    clean_items, dupes = remove_duplicates(raw_items)
    assert len(clean_items) == 6
    assert "BRG001" in dupes

    categories = get_unique_categories(clean_items)
    assert categories == {"ATK", "Elektronik"}

    search_atk = search_items(clean_items, "ATK")
    assert len(search_atk) == 3
    search_kabel = search_items(clean_items, "hdmi")
    assert len(search_kabel) == 1 and search_kabel[0]["kode_barang"] == "BRG004"

    low_stock = filter_low_stock(clean_items, threshold=5)
    assert len(low_stock) == 3

    summary = summarize_by_category(clean_items)
    assert summary["ATK"]["total_stok"] == 73
    assert summary["ATK"]["total_nilai_aset"] == 1296000
    assert summary["Elektronik"]["total_stok"] == 14
    assert summary["Elektronik"]["total_nilai_aset"] == 1110000

    report = build_full_report(clean_items, low_stock_threshold=5)
    assert report["ringkasan"]["total_jenis_barang"] == 6
    assert report["ringkasan"]["total_unit_stok"] == 87
    assert report["ringkasan"]["total_nilai_aset"] == 2406000
    assert report["ringkasan"]["jumlah_barang_perlu_restock"] == 3

    saved_path = save_report_json(report, str(JSON_OUTPUT_PATH))
    assert Path(saved_path).exists()

    with open(saved_path, "r", encoding="utf-8") as f:
        loaded_json = json.load(f)
    assert loaded_json["ringkasan"]["total_nilai_aset"] == 2406000


if __name__ == "__main__":
    test_validator()
    test_io_and_processor()
    print("[V] Semua pengujian berhasil lulus 100%.")
