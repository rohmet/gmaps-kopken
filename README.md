# Gmaps Kopken ABSA Modeling

Proyek ini bertujuan untuk melakukan **Aspect-Based Sentiment Analysis (ABSA)** pada ulasan pelanggan Kopi Kenangan dari Google Maps. Pipeline analisis ini mencakup seluruh proses mulai dari pra-pemrosesan data mentah, pemodelan topik, pelabelan aspek, pelatihan model klasifikasi (SVM/IndoBERT), analisis sentimen berbasis leksikon, hingga agregasi data untuk visualisasi dashboard.

## Struktur Direktori

```text
.
├── modeling/               # Berisi seluruh pipeline pemodelan dan analisis utama
│   ├── eda/                # Eksplorasi Data Analisis (EDA)
│   ├── topic_modelling/    # Pemodelan topik untuk mengidentifikasi aspek utama
│   ├── aspect_labeling/    # Pelabelan aspek pada dataset
│   ├── training_model_aspek/ # Pelatihan model klasifikasi aspek (IndoBERT/SVM)
│   ├── model_sentiment_absa/ # Analisis sentimen ABSA menggunakan pendekatan leksikon
│   ├── aggregasi_insight/  # Agregasi data di tingkat gerai untuk metrik bisnis
│   ├── weights/            # Model yang telah dilatih (disimpan secara lokal)
│   └── export_dashboard_data.py # Skrip inferensi dan ekspor data untuk dashboard
├── preprocessing/          # Pembersihan data dan pra-pemrosesan ulasan
└── reports/                # Laporan analisis dan metrik performa model
```

## Persyaratan (Requirements)

Pastikan lingkungan Python Anda telah terinstal library yang dibutuhkan, antara lain:
- `pandas`
- `numpy`
- `scikit-learn`
- `transformers`
- `datasets`
- `torch`
- `joblib`

Anda dapat menggunakan `pip` untuk menginstal dependensi tersebut. Disarankan menggunakan *virtual environment*.

## Penggunaan (Usage)

Proyek ini dirancang sebagai pipeline berurutan. Berikut adalah tahapan yang perlu dijalankan:

### 1. Preprocessing Data
Jalankan notebook di dalam folder `preprocessing/` untuk membersihkan ulasan mentah dan menyimpannya sebagai `cleaned_reviews.csv`. Proses ini meliputi normalisasi teks, penghapusan karakter khusus, dan tokenisasi dasar.

### 2. Pipeline Pemodelan (Modeling)
Tahapan pemodelan terdapat di dalam folder `modeling/` dan disusun secara berurutan:
- **EDA (`eda/`)**: Analisis distribusi ulasan, panjang teks, dan metrik dasar lainnya.
- **Topic Modelling (`topic_modelling/`)**: Mengidentifikasi topik utama yang sering dibicarakan dalam ulasan untuk menentukan kelas aspek (seperti Rasa, Harga, Pelayanan, dll).
- **Aspect Labeling (`aspect_labeling/`)**: Melabeli dataset secara semi-otomatis atau berbasis aturan untuk menyiapkan data latih.
- **Training Model (`training_model_aspek/`)**: Melatih model klasifikasi (SVM atau IndoBERT) untuk memprediksi aspek dari suatu ulasan. Model yang dihasilkan akan disimpan di folder `weights/`.
- **ABSA & Sentimen (`model_sentiment_absa/`)**: Menggunakan pendekatan berbasis leksikon (Kamus Sentimen Bahasa Indonesia) yang disesuaikan untuk menentukan sentimen (Positif, Negatif, Netral) pada setiap aspek yang terdeteksi.
- **Agregasi Insight (`aggregasi_insight/`)**: Menghitung skor rata-rata, sentimen dominan, dan frekuensi penyebutan aspek per gerai.

### 3. Inferensi & Ekspor Data Dashboard
Untuk menjalankan seluruh *pipeline* inferensi pada data ulasan terbaru dan mengekspor hasilnya untuk visualisasi dashboard, jalankan skrip berikut dari dalam direktori `modeling/`:

```bash
cd modeling
python export_dashboard_data.py
```

Skrip ini akan:
1. Memuat model yang telah dilatih dari direktori `weights/`.
2. Membaca dataset bersih dari direktori `preprocessing/`.
3. Memecah kalimat berdasarkan klausa untuk deteksi multi-aspek.
4. Memprediksi aspek dan menghitung sentimen menggunakan leksikon.
5. Menyimpan dataset akhir yang siap divisualisasikan.

## Catatan Tambahan
- Folder `weights/`, `results/`, dan file sementara lainnya diabaikan oleh Git (via `.gitignore`) karena ukurannya yang besar. Pastikan model telah dilatih secara lokal sebelum menjalankan *inference script*.
- Pendekatan hibrida digunakan di mana identifikasi aspek menggunakan **Machine Learning/Deep Learning**, sedangkan klasifikasi sentimen menggunakan **Lexicon-based approach**.

---
*Dibuat untuk keperluan Capstone Project.*
