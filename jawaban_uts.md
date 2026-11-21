# DRAF JAWABAN LAPORAN UTS PEMROGRAMAN DASAR (TK091)
## Proyek: Aplikasi CLI Monitor Stok & Inventaris Barang

---

### SOAL 1: Analisis Masalah & Konsep Aplikasi (Bobot: 10)

1. **Permasalahan Nyata:**
   Banyak pemilik usaha mikro/kecil (UMKM) serta staf administrasi gudang yang masih mencatat dan mengelola data inventaris menggunakan file lembar sebar sederhana (format CSV). Namun, data mentah tersebut seringkali mengandung inkonsistensi, seperti data ganda (*duplicate entries*), salah ketik tipe data (misal: harga ditulis teks atau stok negatif), serta ketiadaan informasi otomatis mengenai total aset dan barang yang stoknya kritis. Memeriksa baris demi baris secara manual sangat memakan waktu dan berisiko tinggi terhadap kesalahan manusia (*human error*).

2. **Tujuan Aplikasi:**
   Membangun aplikasi berbasis teks (*Command Line Interface* / CLI) menggunakan Python yang mampu:
   * Membaca dan membersihkan data CSV secara otomatis (*data sanitization & deduplication*).
   * Memberikan fasilitas pencarian dan penyaringan stok menipis (*low stock filter*).
   * Menghitung total nilai aset barang secara keseluruhan dan dikelompokkan per kategori.
   * Mengekspor ringkasan laporan manajerial ke dalam format JSON yang terstruktur.

3. **Target Pengguna:**
   * Pemilik bisnis UMKM (toko kelontong, alat tulis kantor, toko elektronik kecil).
   * Staf pengelola atau operator gudang.

4. **Format Masukan (Input) & Keluaran (Output):**
   * **Input:** File CSV (`data/inventaris.csv`) dengan 5 atribut wajib: `kode_barang`, `nama_barang`, `kategori`, `stok`, dan `harga`.
   * **Output:**
     * Visualisasi data tabel dan rekapitulasi di layar terminal CLI.
     * File laporan JSON (`output/laporan_inventaris.json`) yang memuat metrik ringkasan, kategori unik, rekap per kategori, dan daftar barang yang memerlukan *restock*.

5. **Fitur Utama Aplikasi:**
   * *Fitur 1: Muat & Validasi Data Otomatis* (memverifikasi tipe data & membuang duplikat kode barang).
   * *Fitur 2: Pencarian Barang* (pencarian fleksibel berdasarkan nama atau kategori, *case-insensitive*).
   * *Fitur 3: Filter Stok Menipis* (menampilkan barang dengan stok $\le$ batas tertentu).
   * *Fitur 4: Rekapitulasi Nilai Aset per Kategori* (menghitung total jenis, total stok, dan total aset).
   * *Fitur 5: Ekspor Laporan JSON* (menyimpan data ringkasan ke file JSON).
   * *Fitur 6: Muat Ulang File CSV Dinamis* (dapat mengganti file input saat aplikasi berjalan).

---

### SOAL 2 & 3: Pemetaan Struktur Data & Control Flow (Bobot: 30)

#### A. Pemetaan dan Alasan Pemilihan Struktur Data
1. **`list`:**
   * **Penggunaan:** Menyimpan kumpulan seluruh barang yang valid (`list[dict]`), daftar barang hasil pencarian, daftar barang stok menipis, dan daftar pesan peringatan (*warnings*).
   * **Alasan:** `list` menjaga urutan kemunculan data (*ordered*), mendukung perulangan (*iterable*), dan sangat fleksibel untuk penambahan elemen baru (`.append()`).
2. **`dictionary`:**
   * **Penggunaan:**
     * Merepresentasikan satu entitas barang dengan atribut kunci: `kode_barang`, `nama_barang`, `kategori`, `stok`, `harga`, dan `nilai_aset`.
     * Menyimpan hasil agregasi/rekapitulasi nilai aset per kategori.
   * **Alasan:** Akses data berbasis pasangan *key-value* cepat, intuitif, dan memudahkan pemetaan data ke format standar JSON.
3. **`set`:**
   * **Penggunaan:**
     * Melacak `kode_barang` yang sudah pernah dibaca guna mencegah duplikasi.
     * Mengumpulkan daftar nama kategori yang unik.
   * **Alasan:** Elemen dalam `set` dijamin unik (*no duplicates*) dan operasi pengecekan keanggotaan (`if item in seen_set`) bekerja dalam kompleksitas waktu rata-rata $O(1)$.

#### B. Control Flow & Penerapan Pythonic Programming
* **Percabangan (`if/elif/else`):**
  Digunakan pada validasi menu pengguna (1-7), verifikasi validitas baris CSV (memeriksa nilai negatif dan kekosongan kolom), serta penentuan tipe bilangan.
* **Perulangan (`while`, `for`):**
  * `while True`: Menjaga siklus interaktif menu CLI agar aplikasi terus berjalan hingga pengguna memilih keluar.
  * `for`: Mengiterasi setiap baris pada `csv.DictReader` dan melakukan perhitungan rekapitulasi nilai aset.
* **Tiga Bentuk Comprehension:**
  1. *List Comprehension (Filter Stok Menipis):*
     ```python
     barang_restock = [item for item in items if item["stok"] <= threshold]
     ```
  2. *Set Comprehension (Pengambilan Kategori Unik):*
     ```python
     kategori_unik = {item["kategori"] for item in items}
     ```
  3. *Dictionary Comprehension (Ringkasan Cepat Jenis Barang):*
     ```python
     jenis_per_kategori = {cat: data["jumlah_jenis_barang"] for cat, data in rekap.items()}
     ```

---

### SOAL 4: Arsitektur Modular, Package, & Dependency (Bobot: 20)

#### A. Struktur Direktori Proyek
```text
monitor_inventaris/
├── main.py                     # Entry point & antarmuka CLI
├── inventaris/                 # Package Python kustom
│   ├── __init__.py             # Inisialisasi dan ekspos fungsi
│   ├── validator.py            # Validasi baris CSV & input terminal
│   ├── io_handler.py           # Baca CSV & tulis laporan JSON
│   └── processor.py            # Logika bisnis inventaris
├── data/
│   └── inventaris.csv          # Dataset uji coba
├── output/
│   └── laporan_inventaris.json # Hasil ekspor laporan
├── test_inventaris.py          # Skrip pengujian otomatis
└── README.md                   # Dokumentasi proyek
```

#### B. Pembagian Tanggung Jawab (Single Responsibility Principle)
1. **`inventaris/validator.py`:**
   Hanya fokus pada validasi aturan data (memastikan data tidak kosong, tipe angka benar, nilai $\ge 0$). Tidak melakukan operasi membaca/menulis file.
2. **`inventaris/io_handler.py`:**
   Hanya menangani operasi input/output berkas (`csv` dan `json`). Menangani error file fisik (`FileNotFoundError`, `PermissionError`).
3. **`inventaris/processor.py`:**
   Hanya memproses komputasi data murni: membuang duplikat dengan `set`, pencarian teks, pemfilteran stok, dan agregasi total nilai aset.
4. **`main.py`:**
   Bertanggung jawab sebagai antarmuka pengguna (tampilan CLI, menu interaktif, format tabel terminal).

#### C. Alur Dependensi Antarmodul
```text
main.py
  ├── memanggil -> inventaris.io_handler
  │                  └── memanggil -> inventaris.validator
  ├── memanggil -> inventaris.processor
  └── memanggil -> inventaris.validator
```
*Catatan: Tidak ada circular import, dependensi berjalan searah secara bersih.*

---

### SOAL 3 & 5: Rancangan Data Uji & Penanganan Edge Cases (Bobot: 15)

#### A. Dataset Uji (`data/inventaris.csv`)
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

#### B. Hasil Pengujian Edge Cases
1. **Duplikasi Kode (`BRG001` muncul dua kali):**
   * *Perilaku:* Baris kedua dibuang oleh fungsi `remove_duplicates()`.
   * *Hasil:* Hanya data pertama yang disimpan, dan dicatat peringatan `Duplikat diabaikan: BRG001`.
2. **Stok Negatif (`BRG007`, stok `-5`):**
   * *Perilaku:* Ditolak oleh `validator.py` (`Nilai stok (-5) tidak boleh negatif`). Baris dilewati secara aman.
3. **Harga Bukan Angka (`BRG008`, harga `"gratis"`):**
   * *Perilaku:* Ditangkap blok `try-except ValueError` di `validator.py`, dilewati dan dicatat sebagai peringatan.
4. **Nama Barang Kosong (`BRG009`):**
   * *Perilaku:* Ditolak validator karena kolom wajib tidak boleh kosong.
5. **Stok Bernilai 0 (`BRG006`):**
   * *Perilaku:* Diterima sebagai data valid, dan otomatis masuk ke daftar barang yang harus di-*restock*.
6. **Path File Tidak Ditemukan:**
   * *Perilaku:* Ditangkap `FileNotFoundError` dan program menampilkan pesan ramah tanpa *crash*.

---

### SOAL 6: Exception Handling & Skenario Debugging (Bobot: 25)

#### A. Daftar Exception yang Ditangani
* `FileNotFoundError`: Ditangani di `io_handler.py` saat path CSV tidak ditemukan.
* `ValueError`: Ditangani saat konversi angka (`int`/`float`) pada CSV dan input menu CLI.
* `KeyError`: Ditangani saat kolom header CSV tidak sesuai dengan nama kolom wajib.
* `PermissionError` & `OSError`: Ditangani saat gagal membaca berkas atau gagal menulis JSON ke disk.
* `KeyboardInterrupt` / `EOFError`: Ditangani di `main.py` sehingga saat pengguna menekan `Ctrl+C`, program keluar dengan ucapan terima kasih tanpa menampilkan *crash traceback*.

#### B. Skenario Debugging Nyata
* **Permasalahan:**
  Saat pengujian awal fungsi pembacaan CSV, file dengan data harga bernilai `"gratis"` atau spasi berlebih menyebabkan program berhenti (*crash*) dengan pesan `ValueError: invalid literal for int() with base 10: 'gratis'`.
* **Langkah Investigasi:**
  Mengamati *stack trace*, kesalahan terjadi langsung pada baris pemanggilan `int(row['harga'])`. Hal ini menunjukkan konversi tipe data mentah dari file eksternal tidak boleh diasumsikan selalu benar.
* **Solusi Implementasi:**
  1. Memisahkan logika validasi ke modul `validator.py` dengan fungsi `validate_row()`.
  2. Menambahkan sanitasi string `.strip()` untuk membersihkan spasi.
  3. Membungkus proses konversi dalam blok `try-except ValueError`. Jika terjadi error, fungsi mengembalikan `(False, None, error_message)` sehingga pembacaan CSV tetap berlanjut untuk baris lainnya tanpa mematikan program.

---

### CATATAN TRANSPARANSI PENGGUNAAN AI (Sesuai Aturan Akademik)
* **Tools AI yang Digunakan:** Google Antigravity (Model: Gemini 3.8 Flash).
* **Peran AI:**
  1. Membantu perancangan struktur arsitektur modular (*Separation of Concerns*).
  2. Membantu penyusunan *type hints* dan *docstrings* standar PEP 257.
  3. Memvalidasi skenario *edge cases* dan formula matematika rekapitulasi nilai aset.
* **Verifikasi Independen:**
  Seluruh kode telah diuji secara menyeluruh melalui skrip pengujian unit `test_inventaris.py`, memastikan tidak ada dependensi eksternal di luar Python Standard Library, dan logika program dipahami secara penuh oleh penulis.
