from typing import Any, Dict, List, Set, Tuple


def remove_duplicates(items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Menyaring dan membuang duplikasi kode_barang."""
    seen_codes: Set[str] = set()
    unique_items: List[Dict[str, Any]] = []
    duplicate_codes: List[str] = []

    for item in items:
        code = item["kode_barang"]
        if code in seen_codes:
            duplicate_codes.append(code)
        else:
            seen_codes.add(code)
            unique_items.append(item)

    return unique_items, duplicate_codes


def get_unique_categories(items: List[Dict[str, Any]]) -> Set[str]:
    """Mengambil seluruh kategori barang unik."""
    return {item["kategori"] for item in items}


def search_items(items: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
    """Mencari barang berdasarkan nama atau kategori (case-insensitive)."""
    kw = keyword.strip().lower()
    if not kw:
        return items

    return [
        item for item in items
        if kw in item["nama_barang"].lower() or kw in item["kategori"].lower()
    ]


def filter_low_stock(items: List[Dict[str, Any]], threshold: int) -> List[Dict[str, Any]]:
    """Menyaring barang dengan stok di bawah atau sama dengan threshold."""
    return [item for item in items if item["stok"] <= threshold]


def summarize_by_category(items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Menghitung ringkasan stok dan total nilai aset per kategori."""
    summary: Dict[str, Dict[str, Any]] = {}

    for item in items:
        cat = item["kategori"]
        if cat not in summary:
            summary[cat] = {
                "jumlah_jenis_barang": 0,
                "total_stok": 0,
                "total_nilai_aset": 0
            }
        summary[cat]["jumlah_jenis_barang"] += 1
        summary[cat]["total_stok"] += item["stok"]
        summary[cat]["total_nilai_aset"] += item["nilai_aset"]

    return summary


def build_full_report(items: List[Dict[str, Any]], low_stock_threshold: int = 5) -> Dict[str, Any]:
    """Menyusun laporan lengkap inventaris untuk diekspor ke JSON."""
    rekap_kategori = summarize_by_category(items)
    daftar_kategori = sorted(list(get_unique_categories(items)))
    barang_restock = filter_low_stock(items, low_stock_threshold)

    return {
        "ringkasan": {
            "total_jenis_barang": len(items),
            "total_unit_stok": sum(item["stok"] for item in items),
            "total_nilai_aset": sum(item["nilai_aset"] for item in items),
            "batas_stok_menipis": low_stock_threshold,
            "jumlah_barang_perlu_restock": len(barang_restock)
        },
        "kategori_unik": daftar_kategori,
        "rekap_per_kategori": rekap_kategori,
        "barang_stok_menipis": barang_restock
    }
