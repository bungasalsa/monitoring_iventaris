from typing import Any, Dict, Optional, Tuple


def validate_row(row: Dict[str, Any], line_number: int) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Memvalidasi kolom, tipe data, dan nilai baris data inventaris."""
    required_keys = ["kode_barang", "nama_barang", "kategori", "stok", "harga"]

    for key in required_keys:
        if key not in row or row[key] is None or str(row[key]).strip() == "":
            return False, None, f"Baris {line_number}: Kolom '{key}' kosong atau tidak ditemukan."

    kode_barang = str(row["kode_barang"]).strip()
    nama_barang = str(row["nama_barang"]).strip()
    kategori = str(row["kategori"]).strip()
    raw_stok = str(row["stok"]).strip()
    raw_harga = str(row["harga"]).strip()

    try:
        stok = int(raw_stok)
    except ValueError:
        return False, None, f"Baris {line_number} ({kode_barang}): Nilai stok '{raw_stok}' bukan bilangan bulat valid."

    if stok < 0:
        return False, None, f"Baris {line_number} ({kode_barang}): Nilai stok ({stok}) tidak boleh negatif."

    try:
        harga_val = float(raw_harga)
    except ValueError:
        return False, None, f"Baris {line_number} ({kode_barang}): Nilai harga '{raw_harga}' bukan angka valid."

    if harga_val < 0:
        return False, None, f"Baris {line_number} ({kode_barang}): Nilai harga ({harga_val}) tidak boleh negatif."

    harga: int | float = int(harga_val) if harga_val.is_integer() else harga_val

    cleaned_data = {
        "kode_barang": kode_barang,
        "nama_barang": nama_barang,
        "kategori": kategori,
        "stok": stok,
        "harga": harga,
        "nilai_aset": stok * harga
    }

    return True, cleaned_data, None


def validate_non_negative_int(value: str) -> int:
    """Memvalidasi string input agar berupa bilangan bulat >= 0."""
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Input tidak boleh kosong.")

    try:
        val = int(cleaned)
    except ValueError:
        raise ValueError(f"'{value}' bukan bilangan bulat yang valid.")

    if val < 0:
        raise ValueError("Nilai tidak boleh negatif.")

    return val
