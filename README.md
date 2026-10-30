# Sewalayan

Sewalayan adalah platform sewa-menyewa barang antar-pengguna dengan sub-tema Conscious Shopping (Sustainable Living). Banyak barang-barang yang biasanya hanya dibutuhkan sesekali, sehingga membelinya sendiri jadi pemborosan. Sewalayan memungkinkan para pengguna untuk saling menyewakan barang yang jarang dipakai, membuat konsumsi lebih bijak sekaligus membuka peluang penghasilan tambahan bagi pemilik barang.

## Anggota Kelompok
- Asmiranda Ghina Winandari - 25006564882
- Jordan Manaksak Hutahaean - 2506532580
- Faeiz Faiza Fasha - 2506602196
- Lavida Yuthiana Faizah - 2506605941

## 🧩 Modul yang Diimplementasikan
- User & Profile (Asmiranda Ghina Winandari - 25006564882)

Mengelola autentikasi dan profil pengguna, termasuk registrasi, login, logout, serta pembuatan dan pembaruan informasi profil seperti nama, foto, bio, lokasi, dan kontak dengan pembatasan akses sesuai hak pengguna.

- Item (Jordan Manaksak Hutahaean - 2506532580)

Mengelola seluruh data barang yang disewakan, mulai dari menambah, melihat, mengubah, hingga menghapus barang. Modul ini juga menyediakan pencarian, filter berdasarkan kategori, harga, kondisi, dan lokasi, serta integrasi OpenStreetMap untuk informasi lokasi barang.

- Rental (Faeiz Faiza Fasha - 2506602196)

Mengelola proses penyewaan barang dari pengajuan hingga selesai, termasuk memilih tanggal sewa, menghitung total biaya, melihat riwayat penyewaan, serta mengatur status rental seperti Pending, Accepted, Active, Completed, dan Cancelled.

- Review and Report (Lavida Yuthiana Faizah - 2506605941)

Mengelola sistem ulasan dan pelaporan. Penyewa dapat memberikan rating (1–5) dan ulasan untuk setiap pesanan yang sudah selesai, serta mengubah atau menghapus ulasannya. Ulasan ditampilkan di halaman detail barang beserta rata-rata ratingnya. Pengguna juga dapat melaporkan barang atau pengguna yang bermasalah dari halaman detail pesanan. Barang yang dilaporkan akan dinonaktifkan sementara hingga laporan ditinjau oleh admin, yang dapat menandai laporan, memblokir pengguna terlapor, atau mengaktifkan kembali barang.

## 🙍🏼‍♂️ Role User
- User

Pengguna dapat menyewakan barang, mencari dan meminjam barang milik pengguna lain, mengelola profil, melakukan transaksi penyewaan, memberikan ulasan, serta membuat laporan apabila menemukan barang atau pengguna yang bermasalah.


- Admin

Admin bertugas mengelola data platform, memantau dan menangani laporan pengguna, serta melakukan moderasi terhadap konten atau akun yang melanggar aturan agar ekosistem Sewalayan tetap aman dan nyaman.

## Public API yang digunakan
- [OpenStreepMap](https://www.openstreetmap.org)


## AI DISCLOSURE 
- Modul Review and Report (Lavida Yuthiana Faizah - 2506605941)
Alat yang digunakan: Claude Anthropic

Bentuk Penggunaan:
1. Pembelajaran & penjelasan konsep: memahami struktur app Django (models, views, urls, forms, templates), relasi 'ForeignKey' dan 'OneToOneField', AJAX dengan 'fetch', CSRF.
2. Menyusun pseudocode: Membantu menyusun pseudocode dan membantu beberapa penyusunan kode modul Review dan Report, desain ulang landing page dan navbar.
3. Debugging: Membantu membaca dan memperbaiki error (test yang gagal), serta menyelesaikan merge conflict di Git.
4. Pengecekan: Memeriksa kode sebelum di-push, menjalankan unit test, dan mengecek kompatibilitas dengan modul anggota lain.

Peran saya:
1. Menentukan alur fitur bersama kelompok (misalnya review hanya bisa ditulis setelah order berstatus finished).
2. Menerapkan kode ke proyek, menyesuaikannya dengan modul anggota lain, dan mengintegrasikannya lewat Git (branch, pull, request, merge).
3. Menguji fitur secara manual melalui 'runserver' dan memastikan semua unit test lulus.
4. Memahami dan dapat menjelaskan setiap bagian kode yang digunakan.

Seluruh kode hasil bantuan AI telah ditinjau, diuji, dan disesuaikan sebelum digabungkan ke branch 'main'.