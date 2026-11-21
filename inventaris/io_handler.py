import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .validator import validate_row


def load_inventory_csv(filepath: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Membaca dan memvalidasi file CSV inventaris barang."""
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan di path: '{filepath}'")

    if not path.is_file():
        raise ValueError(f"Path '{filepath}' bukan merupakan file.")

    items: List[Dict[str, Any]] = []
    warnings: List[str] = []

    try:
        with open(path, mode="r", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                raise ValueError(f"File CSV '{filepath}' kosong atau tidak memiliki baris header.")

            required_columns = {"kode_barang", "nama_barang", "kategori", "stok", "harga"}
            actual_columns = {col.strip() for col in reader.fieldnames if col}

            missing = required_columns - actual_columns
            if missing:
                missing_str = ", ".join(sorted(missing))
                raise ValueError(f"Header CSV tidak sesuai spesifikasi. Kolom hilang: {missing_str}")

            for line_number, row in enumerate(reader, start=2):
                cleaned_row = {k.strip(): v for k, v in row.items() if k is not None}
                is_valid, cleaned_data, err_msg = validate_row(cleaned_row, line_number)

                if is_valid and cleaned_data is not None:
                    items.append(cleaned_data)
                elif err_msg:
                    warnings.append(err_msg)

    except PermissionError:
        raise PermissionError(f"Izin akses ditolak saat membaca file '{filepath}'.")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Gagal mendecode file CSV (pastikan format teks UTF-8): {exc}")

    return items, warnings


def save_report_json(report: Dict[str, Any], filepath: str) -> str:
    """Menyimpan laporan analisis inventaris ke dalam file JSON."""
    path = Path(filepath)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, mode="w", encoding="utf-8") as json_file:
            json.dump(report, json_file, indent=2, ensure_ascii=False)
        return str(path.resolve())

    except PermissionError:
        raise PermissionError(f"Izin akses ditolak saat menyimpan laporan ke '{filepath}'.")
    except OSError as exc:
        raise OSError(f"Terjadi kesalahan I/O saat menyimpan file '{filepath}': {exc}")
