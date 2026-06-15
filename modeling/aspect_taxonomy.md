# 🏷️ Aspect Taxonomy Definition (Kopi Kenangan ABSA)

Dokumen ini mendefinisikan taksonomi aspek yang digunakan untuk melakukan klasifikasi aspek berbasis ulasan pelanggan pada Google Maps Kopi Kenangan. 

Taksonomi ini dirancang berdasarkan kategori utama operasional industri F&B (Food & Beverages) khususnya coffee shop, serta disesuaikan dengan pola keluhan/pujian yang sering muncul pada data ulasan.

---

## 📌 Daftar Aspek & Kata Kunci (Keywords)

| ID Aspek | Nama Aspek | Penjelasan Kategori | Kata Kunci Terkait (Stemmed & Root) |
| :--- | :--- | :--- | :--- |
| **`aspek_rasa`** | Rasa & Kualitas Minuman | Rasa, suhu, konsistensi racikan produk kopi, non-kopi, dan roti. | `kopi`, `minuman`, `rasa`, `enak`, `pahit`, `manis`, `es`, `susu`, `roti`, `menu`, `cup`, `kualitas`, `asin`, `gurih`, `cokelat`, `latte`, `matcha`, `boba`, `tawar`, `encer`, `pekat`, `panas`, `dingin` |
| **`aspek_harga`** | Harga & Promo | Kesesuaian harga produk, adanya promo, diskon, cashback, atau paket bundling. | `harga`, `mahal`, `murah`, `promo`, `diskon`, `cashback`, `ovo`, `gopay`, `shopeepay`, `worth`, `saku`, `pas`, `hemat`, `paket`, `pahe`, `mehong` |
| **`aspek_pelayanan`** | Pelayanan Staf | Sikap, keramahan, kepedulian, dan etika komunikasi dari staf, kasir, atau barista. | `pelayanan`, `layan`, `kasir`, `barista`, `staff`, `karyawan`, `ramah`, `sopan`, `jutek`, `galak`, `cuek`, `etika`, `attitude`, `respect`, `sapa`, `senyum`, `baik`, `mbak`, `mas` |
| **`aspek_kecepatan`** | Kecepatan & Antrian | Durasi waktu tunggu pembuatan pesanan, antrian di kasir, dan kecepatan operasional. | `lama`, `cepat`, `antri`, `nunggu`, `lambat`, `tunggu`, `antrean`, `gercep`, `lelet`, `durasi`, `menit`, `jam`, `kelewat` |
| **`aspek_kebersihan`** | Kebersihan & Suasana | Kenyamanan tempat, AC, colokan listrik (WFC), kebersihan meja/kursi/toilet, serta kebisingan. | `bersih`, `kotor`, `toilet`, `tempat`, `nyaman`, `ac`, `meja`, `kursi`, `suasana`, `rapi`, `cozy`, `wfc`, `colokan`, `colok`, `colokan`, `sejuk`, `dingin`, `berisik`, `luas`, `sempit`, `sofa` |
| **`aspek_stok`** | Ketersediaan Stok/Menu | Kelengkapan menu, kehabisan bahan baku (boba, cup, roti), atau stok yang kosong. | `habis`, `stok`, `menu`, `sedia`, `kosong`, `varian`, `kehabisan`, `ready`, `sold`, `out` |
| **`aspek_aplikasi`** | Sistem Pemesanan & Apps | Pemesanan melalui aplikasi Kopi Kenangan, GrabFood, GoFood, ShopeeFood, self-order kiosk, dan sistem pick-up. | `app`, `aplikasi`, `grab`, `gojek`, `gofood`, `grabfood`, `order`, `pesan`, `sistem`, `pickup`, `kiosk`, `kks`, `down`, `error`, `apk` |

---

## 🛠️ Aturan Pelabelan (Labeling Rules)

1. **Multi-Label Classification:** Satu ulasan dapat memiliki nilai `1` pada lebih dari satu kolom aspek.
   - *Contoh:* *"Kopinya enak banget, tapi pelayanannya agak lambat"* → `aspek_rasa` = 1, `aspek_pelayanan` = 1.
2. **Review Umum/Tanpa Kategori:** Jika ulasan tidak menyebutkan aspek apa pun yang spesifik, maka seluruh kolom bernilai `0` (atau ditandai sebagai ulasan `umum`).
   - *Contoh:* *"Mantap lah"* atau *"Bagus"* → Semua aspek = 0.
3. **Keyword Matching vs. Context:** Keyword matching digunakan sebagai inisialisasi label. Namun, jika ada kata kunci yang maknanya berubah karena konteks (negasi/perbandingan), koreksi manual atau fine-tuning model ML (Stage 5) akan bertugas memperbaikinya.
