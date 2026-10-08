# BlogInsurance.my.id — Autoblog Asuransi (DeepSeek + Pexels + Cloudflare)

Blog otomatis berbahasa Indonesia tentang asuransi & keuangan: artikel ditulis AI
(DeepSeek, ±300–400 kata), berfoto otomatis (Pexels), terbit otomatis ke
**Cloudflare Worker** dengan domain `bloginsurance.my.id`.

## Cara kerja (alur)

```
Judul di content/antrean-judul.txt
  → GitHub Actions (jadwal 09:00 WIB / tombol Run workflow)
  → DeepSeek API menulis artikel → Pexels API mengunduh foto
  → commit "Autoblog: artikel baru" ke branch main
  → Cloudflare Worker membangun ulang otomatis → artikel tayang ±2 menit
```

Menulis manual juga bisa lewat halaman `/admin/` di blog (login token GitHub,
tersimpan di browser saja).

## Fitur

- Tema majalah lebar (1200px): topbar, ticker berita berjalan, featured,
  tab kategori, sidebar Populer/Terbaru, newsletter, footer 4 kolom.
- Arsip `/blog/` dengan filter kategori (`?cat=`) dan pencarian (`?s=`).
- Halaman admin Git-based (`/admin/`): tulis & terbitkan dari browser.
- Foto otomatis per artikel + kredit fotografer (aturan lisensi Pexels).
- Sitemap, robots, 404, SEO meta dasar.

## Struktur repo

```
index.html                 Beranda gaya majalah
blog/index.html            Arsip + filter kategori/pencarian
blog/post.html             Template artikel dinamis (baca .md + render)
tentang.html, kontak.html, 404.html
styles.css                 Seluruh tema (orisinal, tanpa framework)
admin/index.html           Editor Git-based (pakai token via browser)
content/posts/*.md         Artikel (Markdown + frontmatter)
content/images/*.jpg       Foto Pexels per artikel
content/index.json         Indeks artikel (dibaca homepage/arsip)
content/antrean-judul.txt  Antrean judul (format: "Kategori | Judul")
scripts/autoblog.py        Generator artikel (DeepSeek + Pexels)
src/worker.js              Cloudflare Worker (statis + route /api/berita)
wrangler.toml              Konfigurasi Worker (deploy: npx wrangler deploy)
functions/api/berita.js    Cadangan proxy NewsAPI (rute Pages, nonaktif)
.github/workflows/autoblog.yml  Jadwal + tombol generate (via web GitHub)
docker-compose.yml         WordPress lokal opsional (arsip cara lama)
```

## Langkah setup dari nol

1. **Repo GitHub**: buat repo, push folder ini ke branch `main`.
2. **Rahasia GitHub** (repo > Settings > Secrets > Actions):
   - `DEEPSEEK_API_KEY` — key DeepSeek (akun harus ada balance, error 402 = saldo habis).
   - `PEXELS_API_KEY` — key Pexels (gratis, 200 request/jam).
   - Jangan pernah paste key di chat/file.
3. **Workflow autoblog**: buat via web GitHub (Add file > Create new file)
   `.github/workflows/autoblog.yml` (jadwal `0 2 * * *` = 09:00 WIB + tombol manual).
4. **Cloudflare Worker**: Workers & Pages > Create > **Worker** > Connect to Git >
   pilih repo, branch `main`, Build: None, Deploy: `npx wrangler deploy`, Root: `/`.
5. **Domain**: Worker > Custom domains > tambah `bloginsurance.my.id` (+ `www`),
   pastikan nameserver domain ke Cloudflare.
6. **Rahasia Worker** (bila memakai `/api/berita`): Settings > Variables and
   secrets > `NEWS_API_KEY` (tipe Secret) > Save > Redeploy.
7. **Tes**: Actions > Autoblog DeepSeek > Run workflow → hijau → commit
   "Autoblog: artikel baru" → Worker rebuild → artikel tayang. Tiap ganti
   secret/variabel wajib redeploy sekali.

## Menambah artikel (3 cara)

- **Otomatis**: biarkan jadwal harian (1 judul teratas antrean per run).
- **Manual**: Actions > Run workflow, isi `judul` (paten) atau kosongkan (antrean).
- **Via admin**: buka `/admin/`, isi token GitHub (scope Contents read+write repo
  ini), tulis, Publikasikan.

## Contoh 1 artikel jadi

**Cara Memilih Asuransi Kesehatan untuk Orang Tua di Atas 60 Tahun**
- Live: `https://bloginsurance.my.id/blog/post.html?p=cara-memilih-asuransi-kesehatan-untuk-orang-tua-di-atas-60-tahun`
- Kategori: Kesehatan • 384 kata • Foto: Pexels + kredit fotografer
- Ringkasan: *"Memilih asuransi kesehatan untuk orang tua di atas 60 tahun butuh
  strategi khusus karena premi lebih mahal, ada batas usia masuk, dan risiko
  kesehatan yang meningkat."*
- Struktur isi: Kenali Dulu Kondisi Kesehatan dan Riwayat Medis → Bandingkan
  Jenis Produk dan Manfaatnya → Contoh Perhitungan Sederhana (premi Rp2,5 jt/bln
  untuk usia 62 thn, limit Rp500 jt) → Tips Praktis Sebelum Membeli →
  disclaimer edukasi.

Contoh artikel bergambar (Pexels): `https://bloginsurance.my.id/blog/post.html?p=asuransi-kesehatan-untuk-anak-manfaat-yang-wajib-ada`

File sumbernya (`content/posts/...md`): frontmatter `title/date/category/excerpt`
(+ `image/image_credit/image_url` bila bergambar) lalu isi Markdown.

## Troubleshooting

| Gejala | Penyebab umum |
|---|---|
| Actions merah `402 Payment Required` | Saldo DeepSeek habis → top up |
| Actions merah `403` di gambar | Key Pexels salah → Update secret |
| Run hijau tapi tanpa commit | `git diff` tanpa `--cached` (sudah diperbaiki) |
| Situs tidak berubah setelah push | Build belum Success / traffic masih di versi manual → Promote versi Git terbaru 100% |
| `/api/berita` 404/500 | Route hanya di Worker (bukan Pages); butuh `NEWS_API_KEY` + redeploy |
| Kategori kosong (0 artikel) | Antrean digilir per kategori — terisi bertahap tiap run |

## Catatan keamanan

- Semua key (DeepSeek, Pexels, NewsAPI, GitHub) hanya lewat Secrets/Env,
  tidak pernah di-hardcode. Key yang pernah bocor di chat harus di-revoke.
- Token yang dipakai skrip lokal tersimpan di keychain/OS, bukan di repo.
