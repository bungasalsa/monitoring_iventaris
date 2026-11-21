# Aplikasi CLI Monitor Stok & Inventaris Barang

Aplikasi Command Line Interface (CLI) interaktif untuk memantau, memvalidasi, menganalisis, dan merekapitulasi stok serta nilai aset inventaris barang berbasis Python.

Proyek ini disusun untuk memenuhi **Ujian Tengah Semester (UTS) Pemrograman Dasar (TK091)**.

---

## 1. Deskripsi Singkat & Fitur Utama

Aplikasi ini dikembangkan untuk membantu pemilik usaha mikro/kecil (UMKM) dan staf administrasi gudang dalam mengelola data inventaris yang berasal dari catatan mentah berbentuk tabel (CSV). Aplikasi menerapkan prinsip *defensive programming* untuk membersihkan data dari duplikasi dan baris rusak sebelum melakukan analisis bisnis.

### Fitur Utama:
1. **Muat & Validasi Data Otomatis:** Membaca file CSV (`data/inventaris.csv`), memvalidasi tipe data pada setiap baris, serta membuang data duplikat secara otomatis berdasarkan `kode_barang`.
2. **Pencarian Fleksibel:** Mencari barang berdasarkan `nama_barang` atau `kategori` secara *case-insensitive*.
3. **Filter Stok Menipis (*Low Stock Alert*):** Menyaring barang yang stoknya berada di bawah atau sama dengan ambang batas (*threshold*) tertentu (misalnya stok $\le 5$) untuk mendeteksi barang yang perlu segera di-*restock*.
4. **Rekapitulasi Nilai Aset:** Menghitung total jumlah jenis barang, total unit fisik stok, dan total nilai aset ($\text{stok} \times \text{harga}$) secara keseluruhan maupun terperinci per kategori barang.
5. **Ekspor Laporan ke JSON:** Menyimpan hasil analisis lengkap dalam format JSON yang terstruktur dan rapi ke direktori `output/laporan_inventaris.json`.
6. **Dukungan Custom CSV Path:** Memungkinkan pengguna memuat file CSV lain secara dinamis tanpa perlu me-restart aplikasi.

---

## 2. Struktur Direktori & Penjelasan Modul

Arsitektur kode dirancang modular mengikuti prinsip *Single Responsibility Principle* (SRP):

```text
monitor_inventaris/
├── main.py                     # Entry point & antarmuka menu CLI interaktif
├── inventaris/                 # Package kustom untuk logika inventaris
│   ├── __init__.py             # Inisialisasi package & ekspos fungsi publik
│   ├── validator.py            # Validasi baris data CSV & defensive input
│   ├── io_handler.py           # Penanganan baca CSV dan tulis laporan JSON
│   └── processor.py            # Logika bisnis: deduplikasi, pencarian, filter, rekap
├── data/
│   └── inventaris.csv          # File dataset uji (data normal + edge cases)
├── output/
│   └── laporan_inventaris.json # Hasil ekspor laporan terstruktur
├── test_inventaris.py          # Skrip pengujian otomatis (unit & integrasi)
└── README.md                   # Dokumentasi lengkap proyek
```

### Penjelasan Modul:
* **`inventaris/validator.py`**:
  * `validate_row()`: Memeriksa kelengkapan kolom wajib, memverifikasi nilai stok ($\ge 0$) dan harga ($\ge 0$), serta menghitung nilai aset per barang.
  * `validate_non_negative_int()`: Memvalidasi input angka dari pengguna di terminal agar tidak crash saat menerima nilai non-numerik atau negatif.
* **`inventaris/io_handler.py`**:
  * `load_inventory_csv()`: Membaca file CSV menggunakan `csv.DictReader`, mendeteksi file hilang/rusak, dan mengumpulkan data valid serta pesan peringatan.
  * `save_report_json()`: Menyimpan dictionary ringkasan analisis ke file JSON dengan indentasi rapi dan penanganan folder otomatis (`mkdir(parents=True)`).
* **`inventaris/processor.py`**:
  * `remove_duplicates()`: Membuang duplikat `kode_barang` dengan efisiensi $O(1)$ menggunakan `set`.
  * `get_unique_categories()`: Mengambil daftar kategori unik menggunakan *set comprehension*.
  * `search_items()`: Melakukan pencarian menggunakan *list comprehension*.
  * `filter_low_stock()`: Menyaring barang dengan stok menipis menggunakan *list comprehension*.
  * `summarize_by_category()`: Mengelompokkan dan merekap nilai aset per kategori.
  * `build_full_report()`: Mengompilasi seluruh statistik menjadi dictionary laporan siap ekspor.
* **`main.py`**: Mengatur alur program berbasis menu CLI, perulangan `while True`, penanganan `KeyboardInterrupt` (`Ctrl+C`), dan pemformatan tabel berbasis teks tanpa *library* luar.

---

## 3. Persyaratan Sistem & Dependensi

* **Bahasa Pemrograman:** Python 3.10+ (atau Python 3.8+)
* **Dependensi Eksternal:** **TIDAK ADA (Zero External Dependencies)**. Seluruh aplikasi dibangun hanya menggunakan **Python Standard Library**:
  * `csv` (pembacaan berkas tabel)
  * `json` (serialisasi data laporan)
  * `pathlib` (manajemen path berkas lintas platform)
  * `typing` (type hinting untuk kejelasan kontrak data)
  * `sys` (kontrol terminasi program)

---

## 4. Cara Menjalankan Aplikasi

1. Buka terminal atau Command Prompt / PowerShell.
2. Arahkan ke direktori proyek `monitor_inventaris`:
   ```bash
   cd monitor_inventaris
   ```
3. Jalankan aplikasi utama:
   ```bash
   python main.py
   ```
4. Untuk menjalankan pengujian otomatis:
   ```bash
   python test_inventaris.py
   ```

---

## 5. Contoh Format Data

### A. Input: File CSV (`data/inventaris.csv`)
File CSV wajib memiliki header: `kode_barang,nama_barang,kategori,stok,harga`.

Dataset uji sengaja memuat data normal dan beberapa *edge cases* untuk menguji ketahanan program:
```csv
kode_barang,nama_barang,kategori,stok,harga
BRG001,Pulpen Gel Hitam,ATK,50,3500
BRG002,Buku Tulis A5,ATK,3,7000
BRG003,Mouse Wireless,Elektronik,12,85000
BRG004,Kabel HDMI 2m,Elektronik,2,45000
BRG005,Kertas HVS A4,ATK,20,55000
BRG006,Flashdisk 32GB,Elektronik,0,65000
BRG001,Pulpen Gel Hitam Duplikat,ATK,10,3500
BRG007,Map Plastik,ATK,-5,2000
BRG008,Keyboard Mechanical,Elektronik,4,gratis
BRG009,,ATK,10,5000
```

*Penjelasan penanganan edge cases:*
* `BRG001` kedua diabaikan oleh `remove_duplicates()` karena kode barang sudah terdaftar sebelumnya.
* `BRG007` ditolak karena nilai stok negatif (`-5`).
* `BRG008` ditolak karena harga bukan angka (`gratis`).
* `BRG009` ditolak karena nama barang kosong.
* `BRG006` dengan stok `0` tetap valid dan terdeteksi pada fitur stok menipis.

### B. Output: File JSON (`output/laporan_inventaris.json`)
```json
{
  "ringkasan": {
    "total_jenis_barang": 6,
    "total_unit_stok": 87,
    "total_nilai_aset": 2406000,
    "batas_stok_menipis": 5,
    "jumlah_barang_perlu_restock": 3
  },
  "kategori_unik": [
    "ATK",
    "Elektronik"
  ],
  "rekap_per_kategori": {
    "ATK": {
      "jumlah_jenis_barang": 3,
      "total_stok": 73,
      "total_nilai_aset": 1296000
    },
    "Elektronik": {
      "jumlah_jenis_barang": 3,
      "total_stok": 14,
      "total_nilai_aset": 1110000
    }
  },
  "barang_stok_menipis": [
    {
      "kode_barang": "BRG002",
      "nama_barang": "Buku Tulis A5",
      "kategori": "ATK",
      "stok": 3,
      "harga": 7000,
      "nilai_aset": 21000
    },
    {
      "kode_barang": "BRG004",
      "nama_barang": "Kabel HDMI 2m",
      "kategori": "Elektronik",
      "stok": 2,
      "harga": 45000,
      "nilai_aset": 90000
    },
    {
      "kode_barang": "BRG006",
      "nama_barang": "Flashdisk 32GB",
      "kategori": "Elektronik",
      "stok": 0,
      "harga": 65000,
      "nilai_aset": 0
    }
  ]
}
```

---

## 6. Skenario Debugging & Defensive Programming

* **Skenario Masalah:**
  Saat pengguna menginput batas stok dengan huruf (misal `"lima"`) atau angka negatif (`"-2"`), atau saat file CSV memiliki data harga tidak valid (`"gratis"`), fungsi parsing bawaan melempar `ValueError` yang berpotensi mematikan aplikasi secara mendadak.
* **Investigasi & Analisis:**
  Operasi konversi tipe data seperti `int()` dan `float()` tidak boleh dipanggil tanpa pengawalan. Pada data eksternal (CSV/user input), nilai mentah rentan mengandung spasi berlebih atau tipe data yang tidak sesuai.
* **Solusi Implementasi:**
  1. Pemisahan tanggung jawab validasi ke `inventaris/validator.py`.
  2. Penerapan sanitasi string (`.strip()`) sebelum konversi.
  3. Penggunaan blok `try-except ValueError` sehingga baris data yang rusak tidak menghentikan pemrosesan, melainkan dikumpulkan ke dalam daftar *warnings* untuk dilaporkan secara ramah ke pengguna.
  4. Penanganan sinyal `KeyboardInterrupt` agar pengguna dapat keluar dari program kapan saja secara bersih tanpa menampilkan *traceback* merah di terminal.
