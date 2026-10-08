#!/usr/bin/env python3
"""Autoblog: generate 1 artikel Bahasa Indonesia via DeepSeek API.

Pakai:
  DEEPSEEK_API_KEY=xxx python3 scripts/autoblog.py --judul "Judul artikel" --kategori Kesehatan
  DEEPSEEK_API_KEY=xxx python3 scripts/autoblog.py              # ambil judul dari content/antrean-judul.txt
  python3 scripts/autoblog.py --dry-run --judul "Contoh"        # test tanpa API (tidak butuh key)

Key TIDAK BOLEH ditulis di file/repo/chat — cukup lewat environment variable
(di GitHub: Secrets and variables > Actions > DEEPSEEK_API_KEY).
"""
import argparse, json, os, re, sys, urllib.request
from datetime import date

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(REPO_DIR, "content", "antrean-judul.txt")
POSTS = os.path.join(REPO_DIR, "content", "posts")
INDEX = os.path.join(REPO_DIR, "content", "index.json")

SYSTEM = ("Kamu penulis blog asuransi/keuangan Indonesia. Tulis artikel ORISINAL Bahasa Indonesia "
          "yang santai tapi akurat, 600-900 kata, terstruktur (subjudul ##, list, contoh angka). "
          "Dilarang menjiplak artikel lain. Akhiri dengan disclaimer 1 kalimat bahwa ini edukasi, bukan saran finansial berlisensi.")

def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s).strip()
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", s))[:80] or "artikel"

def pop_queue():
    if not os.path.exists(QUEUE):
        return None
    lines = [l.strip() for l in open(QUEUE, encoding="utf-8") if l.strip()]
    if not lines:
        return None
    judul = lines[0]
    open(QUEUE, "w", encoding="utf-8").write("\n".join(lines[1:]) + ("\n" if len(lines) > 1 else ""))
    return judul

def generate(judul, kategori, dry_run):
    if dry_run:
        return (f"## Pengantar\n\nArtikel tentang **{judul}**.\n\n"
                f"## Poin penting\n\n- Poin 1\n- Poin 2\n\n*Draf percobaan (dry-run, bukan dari AI).*")
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        sys.exit("ERROR: DEEPSEEK_API_KEY kosong. Set environment variable dulu (jangan taruh di chat/file).")
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Tulis artikel lengkap berjudul: {judul}\nKategori: {kategori}\n"
             "Awali dengan ringkasan 1 kalimat diawali 'RINGKASAN: ', lalu isi artikel markdown."},
        ],
        "temperature": 0.8, "max_tokens": 2500,
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = json.load(r)
    except Exception as e:
        sys.exit(f"ERROR DeepSeek API: {e}")
    try:
        return body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        sys.exit(f"ERROR respons tak terduga: {str(body)[:200]}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judul", default="")
    ap.add_argument("--kategori", default="Umum")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    judul = a.judul.strip() or pop_queue()
    if not judul:
        sys.exit("Antrean kosong dan --judul tidak diisi. Tambah judul ke content/antrean-judul.txt")
    slug = slugify(judul)
    target = os.path.join(POSTS, slug + ".md")
    if os.path.exists(target):
        sys.exit(f"Slug {slug} sudah ada — pilih judul lain.")

    teks = generate(judul, a.kategori, a.dry_run)
    ringkasan, isi = "", teks
    m = re.match(r"RINGKASAN:\s*(.+)\n+(.*)$", teks, re.S)
    if m:
        ringkasan, isi = m.group(1).strip(), m.group(2).strip()
    else:
        ringkasan = isi.split("\n")[0][:160]

    os.makedirs(POSTS, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {json.dumps(judul)}\ndate: {date.today().isoformat()}\n"
                f"category: {a.kategori}\nexcerpt: {json.dumps(ringkasan)}\n---\n\n{isi}\n")

    idx = json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else []
    idx = [x for x in idx if x.get("slug") != slug]
    idx.insert(0, {"slug": slug, "title": judul, "date": date.today().isoformat(),
                   "category": a.kategori, "excerpt": ringkasan})
    idx.sort(key=lambda x: x.get("date", ""), reverse=True)
    json.dump(idx, open(INDEX, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"OK: {target} ({len(isi)} karakter)")

if __name__ == "__main__":
    main()
