# INSTRUKSI LENGKAP — GitHub → Cloudflare Pages → bloginsurance.my.id

## 0. KEAMANAN DULU (PENTING)

Anda memposting token `ghp_...` di chat. Itu **bocor dan harus dianggap tidak aman**:

1. Buka https://github.com/settings/tokens → Revoke/Delete token tersebut SEKARANG.
2. Buat token baru bila perlu, dan JANGAN pernah paste di chat / file / screenshot.
3. Token GitHub TIDAK dipakai untuk deploy ke Cloudflare Pages via "Connect to Git" (pakai OAuth GitHub, bukan token manual).
4. Yang Anda butuhkan dari Cloudflare (bukan GitHub):
   - `CLOUDFLARE_API_TOKEN` — buat di https://dash.cloudflare.com/profile/api-tokens → Create Token → template "Edit Cloudflare Workers" + izin Pages:Edit, atau Custom token dengan Account > Cloudflare Pages > Edit.
   - `CLOUDFLARE_ACCOUNT_ID` — ada di Dashboard kanan bawah (Overview domain mana pun).
   - `CLOUDFLARE_PROJECT_NAME` — misal `bloginsurance` (Anda tentukan saat Create Pages project).

Saya TIDAK menyimpan token Anda dan TIDAK menanam token apa pun di repo ini.

---

## 1. Konsep: kenapa bukan WordPress mentah?

| Opsi | Bisa di Pages? | Keterangan |
|---|---|---|
| WordPress PHP + MySQL mentah | ❌ TIDAK | Pages hanya file statis + Functions serverless, tidak ada MySQL/PHP persistent |
| Blog statis ini (gaya WP) | ✅ YA | Inilah isi folder ini — langsung deploy |
| WP lokal → export statis (Simply Static) | ✅ YA | Nulis enak di WP, tayang murah di Pages |
| Headless WP (WP di hosting lain + frontend Next/Astro di Pages) | ✅ YA | Lebih kompleks, butuh 2 hosting |

Untuk `bloginsurance.my.id` yang murah & kencang: pakai **opsi 2** (repo ini). Sudah jadi.

---

## 2. Push ke GitHub (otomatisasi #1)

Di terminal, dari folder ini:

```bash
bash scripts/init-github.sh
# lalu (ganti USERNAME):
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/USERNAME/bloginsurance.git
git push -u origin main
```

Atau via GitHub Desktop / VS Code Source Control → Publish.

Jangan sertakan token di URL remote. Login via browser (`gh auth login`) saat diminta.

---

## 3. Sambungkan ke Cloudflare Pages (otomatisasi #2 — DISARANKAN, tanpa API key)

Ini otomasi resmi: setiap `git push` ke `main` = deploy otomatis.

1. Login https://dash.cloudflare.com → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Authorize GitHub → pilih repo `bloginsurance`.
3. Build settings:
   - Framework preset: **None**
   - Build command: **(kosongkan)**
   - Build output directory: `/` (atau `.`)
   - Root directory: `/`
4. Klik **Save and Deploy**. Tunggu ~1 menit → dapat URL `https://bloginsurance.pages.dev`.
5. Test: buka URL tersebut, semua halaman harus tampil.

Tidak perlu API key untuk cara ini.

---

## 4. Koneksikan domain bloginsurance.my.id

Syarat: domain `my.id` dikelola di Cloudflare (nameserver menunjuk ke Cloudflare).

A. Jika domain BELUM di Cloudflare:
1. Dashboard → **Add domain** → masukkan `bloginsurance.my.id` (atau root `my.id` bila Anda pemiliknya — di sini Anda menyebut subdomain `bloginsurance.my.id`, jadi tambahkan root domain yang Anda miliki, misal `bloginsurance.my.id` sebagai site, atau `my.id` turunan — ikuti wizard).
2. Cloudflare memberi 2 nameserver → ganti di panel registrar (tempat beli domain, misal Niagahoster/IDCloudHost/Domainesia) → tunggu propagasi 5 mnt–24 jam.
3. Pastikan status **Active**.

B. Pasang custom domain ke Pages:
1. Workers & Pages → project Anda → **Custom domains** → **Set up a custom domain** → ketik `bloginsurance.my.id` → Activate.
2. Cloudflare otomatis membuat record CNAME. Jangan buat A-record manual ke IP Pages.
3. Tunggu 1–5 menit → buka `https://bloginsurance.my.id`. Gembok hijau = beres (SSL otomatis).
4. Di **SSL/TLS → Overview**: set mode **Full (strict)** bila origin ada, untuk Pages murni biarkan default; aktifkan **Always Use HTTPS**.

C. Verifikasi DNS (di terminal):

```bash
dig +short bloginsurance.my.id
# harus mengarah ke Cloudflare (atau CNAME ke <project>.pages.dev)
curl -I https://bloginsurance.my.id | head
```

---

## 5. Otomatisasi via GitHub Actions (opsional, butuh API token)

Jika tidak mau pakai "Connect to Git" dan lebih suka `wrangler pages deploy` dari Actions, file `.github/workflows/deploy-pages.yml` sudah disediakan.

1. Buat Pages project dulu (langkah 3) untuk mendapatkan `CLOUDFLARE_PROJECT_NAME`.
2. GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**:
   - `CLOUDFLARE_API_TOKEN` = token dari profil API Cloudflare
   - `CLOUDFLARE_ACCOUNT_ID` = ID akun
   - `CLOUDFLARE_PROJECT_NAME` = misal `bloginsurance`
3. `git push` → tab **Actions** akan hijau dan deploy jalan.

Script `scripts/deploy-cloudflare.sh` hanya untuk cek koneksi API dari laptop (butuh `export` 3 variabel di atas). Upload massal tetap disarankan via Connect-to-Git atau `wrangler` (perlu Node).

---

## 6. Cara nambah artikel baru (ala WordPress)

Tanpa database — cukup duplikat file:

1. Copy `blog/asuransi-kesehatan-terbaik-2026.html` → `blog/judul-baru.html`, edit `<h1>` + isi.
2. Tambahkan kartu di `blog/index.html` dan `index.html`.
3. Tambahkan `<url>` di `sitemap.xml`.
4. Commit + push → tayang otomatis 1–2 menit.

Mau editor WP beneran? `docker compose up -d` → buka `http://localhost:8080` → tulis di WP → plugin **Simply Static** → Generate → ekstrak ZIP → timpa file di repo ini → push.

---

## 7. Troubleshooting

- **Build gagal**: pastikan Build command kosong & output `/`. Repo ini tidak butuh npm.
- **Domain 522/525**: tunggu DNS, jangan proxy ganda. Custom domain Pages jangan di-A-record manual.
- **Actions 401**: token salah / kurang izin Pages:Edit, atau Account ID salah.
- **Halaman 404**: Cloudflare Pages butuh file `404.html` (sudah ada) — pastikan di root.
- **CSS tidak load**: pastikan link `/styles.css` absolut dan file ada di root.

---

## Checklist selesai

- [ ] Token ghp lama di-revoke
- [ ] Repo GitHub `main` berisi file ini
- [ ] Pages URL `*.pages.dev` tampil
- [ ] `https://bloginsurance.my.id` tampil + gembok hijau
- [ ] (Opsional) Secrets Actions terisi, Actions hijau
