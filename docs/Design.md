# Panduan Layout
> AI Generated. Tolong laporin kalo nemuin kesalahan, atau ada hal yang kurang jelas. -- Faeiz

Lihat "design.html" untuk contoh pemaikaian dalam html.

Ini panduan membangun halaman di html dengan CSS kita. Tidak perlu otak atik CSS: kebanyakan kamu cukup **memilih sebuah class lalu menempelkannya ke tag HTML**.

---

## Ide utamanya

Setiap halaman dibangun dari tiga level, dari luar ke dalam:

1. **Page** (`.layout`): header, main, footer. (gaperlu diotak atik, udah disetting di base.html!)
2. **Container** (`.container`): menjaga konten tetap di tengah dan tidak terlalu lebar.
3. **Helpers** (`.stack`, `.row`, `.grid`, ...): mengatur susunan elemen di dalamnya.


> Class .container kayaknya gaperlu dipake banget sih (karena dalem base.html, semua halaman otomatis punya div container), .stack .row .grid udah cukup harusnya kecuali lu mau nambah section beda ukuran. Gunain class 'container-padding' buat nambah padding diatas bawah containernya. -- Faeiz

Hampir tidak pernah kamu perlu menulis CSS baru untuk membuat halaman. Kamu tinggal menggabungkan class yang sudah ada.

---

## Cheat sheet "Saya ingin..."

| Saya ingin... | Pakai |
|---|---|
| Menaruh elemen atas-bawah | `.stack` |
| Menaruh elemen berdampingan (turun ke baris baru di HP) | `.row` |
| Mendorong elemen ke kiri dan kanan ujung | `.row row--between` |
| Menampilkan card dalam kolom yang responsive | `.grid` |
| Membuat sidebar di samping konten | `.with-sidebar` |
| Menampilkan artikel atau teks panjang | `.prose` |
| Mengelompokkan konten jadi blok berjudul | `.section` + `.section__title` |
| Membuat halaman form atau artikel lebih sempit | `.container container--narrow` |
| Membuat halaman dashboard lebih lebar | `.container container--wide` |
| Membuat teks jadi abu-abu | `.text-muted` |
| Membuat teks lebih kecil | `.text-sm` |
| Membuat teks lebih besar | `.text-lg` |

---

## Tools satu per satu

Gunain classnya buat nerapin sifatnya, .stack, .row, .grid dll. Beberapa class punya **variant**-nya sendiri, kayak .stack--sm, .row--between, dan lain lain. Itu **keduanya dipakai, basenya dan variantnya** misalnya `class="stack stack--sm"`. Ini berlaku juga buat `btn`. Kalau kurang jelas, lihat contoh pemakaian disini atau "design.html".
-- Faeiz

### `.stack` : daftar vertikal

```html
<div class="stack">
  <h2>Title</h2>
  <p>Text</p>
  <button class="btn">Click</button>
</div>
```

Pilihan jarak: `.stack--sm` (rapat), default, `.stack--lg` (renggang).

### `.row` : penataan horizontal

```html
<div class="row">
  <button class="btn btn--primary">Save</button>
  <button class="btn">Cancel</button>
</div>
```

Di HP, elemen yang tidak muat otomatis pindah ke baris berikutnya.
Tambahkan `row--between` untuk merentangkan elemen ke kedua ujung.


### `.grid` : kolom responsive

```html
<div class="grid">
  <div class="card">One</div>
  <div class="card">Two</div>
  <div class="card">Three</div>
</div>
```
> Ini bagus dipake buat list item atau semacamnya, soalnya otomatis berubah jadi stacking kalo layarnya kesempitan -- Faeiz

Kamu tidak perlu menentukan jumlah kolom. Grid muat sebanyak yang bisa: 1 di HP, 2 di tablet, 3 atau lebih di desktop.
Ingin card yang lebih kecil atau lebih besar? Pakai `.grid--sm` atau `.grid--lg`.

### `.with-sidebar` : layout dengan sidebar

> Gw belum setting ini biar bisa jadi dinamis, mungkin tergantung MVP, kalo sempet kita dinamisin. -- Faeiz

```html
<div class="with-sidebar">
  <aside>Sidebar (menu, filter...)</aside>
  <div>Konten utama</div>
</div>
```

Child pertama adalah sidebar, child kedua adalah konten. Di HP, sidebar berada di atas.
Ingin sidebar di kanan? Pakai `with-sidebar with-sidebar--right` dan taruh konten **lebih dulu**.

### `.section` : blok berjudul

```html
<section class="section">
  <h2 class="section__title">Recent orders</h2>
  <div class="grid">...</div>
</section>

<section class="section">
  <h2 class="section__title">Settings</h2>
  ...
</section>
```

Antar section otomatis diberi jarak.

### `.prose` : teks yang nyaman dibaca

```html
<article class="prose">
  <h1>Judul artikel</h1>
  <p>Teks panjang...</p>
  <p>Teks lainnya...</p>
</article>
```

Membatasi panjang baris dan menambah jarak antar paragraf dan heading.

### Menggabungkan semuanya

Class bisa ditumpuk seperti building blocks:

```html
<section class="section">
  <h2 class="section__title">Team</h2>
  <div class="grid">
    <div class="card stack stack--sm">
      <h3>Anna</h3>
      <p>Designer</p>
      <div class="row">
        <button class="btn btn--primary">Message</button>
      </div>
    </div>
    ...
  </div>
</section>
```

---

## 5 aturan

1. **Jangan pakai inline style.** Jangan pernah menulis `style="..."` di HTML. Kalau butuh style, pakai class (yang sudah ada atau yang baru).
2. **Spacing diambil dari scale.** Di CSS, hanya pakai `var(--space-1)` sampai `var(--space-6)` untuk margin, padding, dan gap. Jangan pakai angka mentah seperti `13px`.
3. **Warna dan ukuran diambil dari variable.** Pakai `var(--primary)`, `var(--text-lg)`, dan sebagainya. Jangan tulis kode hex mentah di luar block `:root`.
4. **Jangan pakai lebar pixel tetap untuk layout.** Jangan tulis `width: 600px`. Pakai `max-width` dengan satuan `rem` atau `ch`, atau biarkan `.container` dan `.grid` yang mengaturnya.
5. **Cek di HP.** Sebelum selesai, kecilkan lebar browser sampai sekitar 375px (atau pakai device mode di DevTools). Tidak boleh ada yang bisa di-scroll ke samping.

---

## Cara mengubah temanya (DISKUSI DULU -- Faeiz)

File CSS berurutan seperti ini, dari atas ke bawah:

1. **`:root`**: semua variable (warna, font, spacing, ukuran)
2. **Base tags**: style untuk tag HTML biasa seperti `body`, `h1`, `a`, `img`
3. **Page layout**: `.layout`, `.container`, `.header`, `.footer`, `.section`
4. **Layout helpers**: `.row`, `.stack`, `.grid`, `.with-sidebar`, `.prose`
5. **Components**: `.btn`, `.input`, `.card`, `.nav`
6. **Utilities**: `.text-muted`, `.text-sm`, `.text-lg` (di bawah comment `UTILITIES` di paling bawah)

Setiap jenis perubahan punya tempatnya sendiri:

| Saya perlu... | Pergi ke | Lakukan |
|---|---|---|
| Mengubah warna, ukuran font, spacing, atau lebar halaman | `:root` di paling atas | Edit nilai variable-nya. Selesai. |
| Menambah warna atau ukuran baru | `:root` di paling atas | Tambah variable baru, lalu pakai dengan `var(--nama)`. |
| Menambah UI piece baru yang reusable (badge, alert, modal) | Setelah `.nav`, sebelum `UTILITIES` | Tambah class baru. |
| Menambah variasi dari sesuatu yang sudah ada | Tepat di bawah class-nya | Tambah class `--modifier` (lihat di bawah). |
| Menambah cara baru mengatur susunan elemen | Di dekat `.row`, `.stack`, `.grid` | Tambah class baru. Tanya dulu: apakah ketiganya sudah bisa melakukan ini? |
| Menambah class kecil dengan satu fungsi | Di bawah `UTILITIES` di paling bawah | Tambahkan, tapi jaga daftarnya tetap sangat pendek. |

### Menambah variant (modifier)

Variant adalah perubahan kecil di atas class yang sudah ada. Namanya `base--variant`.

Contoh: kamu ingin tombol danger berwarna merah.

1. Tambah variable warna di dalam `:root`:
   ```css
   --danger: #C0392B;
   ```
2. Tambah variant-nya **tepat di bawah `.btn--primary`**:
   ```css
   .btn--danger {
       background: var(--danger);
       border-color: var(--danger);
       color: white;
   }
   ```
3. Pakai di HTML. Selalu sertakan juga base class-nya:
   ```html
   <button class="btn btn--danger">Delete</button>
   ```

**Penting:** variant harus ditulis **di bawah** base class-nya di dalam file, kalau tidak, base class akan menimpanya.

### Menambah component baru

Contoh: sebuah badge. Tambahkan setelah `.nav`, sebelum comment `UTILITIES`.

```css
.badge {
    display: inline-block;
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius);
    background: var(--primary);
    font-size: var(--text-sm);
}
```

```html
<span class="badge">New</span>
```

Checklist untuk component baru:

- [ ] Nama menjelaskan **apa itu** (`.badge`, `.alert`), bukan seperti apa tampilannya (`.yellow-box`)
- [ ] Hanya memakai `var(--...)` variable
- [ ] Tidak memakai lebar tetap
- [ ] Berfungsi baik di lebar 375px
- [ ] State-nya ada: `:hover`, `:focus` (untuk elemen yang bisa diklik)

### Menambah utility (hati-hati)

Utility adalah class satu baris seperti `.text-muted`. Jaga daftarnya **sangat kecil**. Kalau kamu memakai 2 atau 3 baris CSS yang sama di 3 tempat atau lebih, jadikan utility atau component. Kalau tidak, jangan.

---

## Kesalahan umum

**"Spacing-nya terlihat aneh."**
Jangan menambah margin ke elemen satu per satu. Bungkus dengan `.stack` atau `.row` dan biarkan `gap` yang mengatur jaraknya.

**"Class variant saya tidak berlaku."**
Kemungkinan besar posisinya ada di atas base class-nya di file CSS. Pindahkan ke bawahnya.

**"Halaman bisa di-scroll ke samping di HP."**
Ada elemen dengan lebar tetap. Cari `width: ...px` lalu ganti dengan `max-width`, atau cek apakah ada gambar atau tabel yang terlalu lebar.

**"Saya butuh kolom tapi `.grid` tidak cocok."**
Kalau butuh layout yang pas (misalnya 2/3 dan 1/3), itu berarti layout helper baru. Tambahkan di dekat `.grid`, jangan memaksa dengan inline style.

**"Ini perlu class baru atau bisa pakai yang sudah ada?"**
Coba gabungkan class yang sudah ada dulu (`card stack stack--sm`). Buat class baru hanya kalau penggabungan tidak cukup.

