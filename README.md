# BlogInsurance.my.id — Blog Statis Siap Cloudflare Pages

Situs statis gaya WordPress untuk domain `bloginsurance.my.id`.
Tanpa build, tanpa Node. Push ke GitHub = otomatis tayang di Cloudflare Pages.

## Struktur

```
index.html  Beranda
blog/       3 artikel contoh (asuransi kesehatan, jiwa, mobil)
tentang.html, kontak.html, 404.html
styles.css
_headers, _redirects, robots.txt, sitemap.xml
.github/workflows/deploy-pages.yml  Auto-deploy via Actions (butuh 3 secrets)
scripts/deploy-cloudflare.sh  Cek API + panduan deploy manual
scripts/init-github.sh  Inisialisasi git + push
docker-compose.yml  WordPress lokal opsional (untuk editor WP -> export statis)
```

## Deploy cepat (5–10 menit) — lihat detail di INSTRUKSI-CLOUDFLARE.md

1. Buat repo GitHub baru, push folder ini ke branch `main`.
2. Cloudflare Dashboard > Workers & Pages > Create > Pages > Connect to Git > pilih repo.
   - Build command: (kosongkan)
   - Output directory: `/` (atau `.`)
3. Pages > Custom domain > `bloginsurance.my.id` > Activate. Arahkan nameserver domain ke Cloudflare jika belum.
4. (Opsional) Aktifkan GitHub Actions auto-deploy: isi Secrets `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_PROJECT_NAME`.

## Fakta penting

- WordPress asli (PHP + MySQL) **tidak bisa** jalan murni di Workers & Pages. Solusi resmi: statiskan dulu (plugin Simply Static / WP2Static) atau pakai Headless WP + frontend statis.
- Repo ini sudah dalam bentuk statis, jadi langsung bisa di-host di Pages.
