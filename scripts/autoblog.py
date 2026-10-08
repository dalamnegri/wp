#!/usr/bin/env python3
"""Autoblog: generate 1 artikel Bahasa Indonesia via DeepSeek API.

Pakai:
  DEEPSEEK_API_KEY=xxx python3 scripts/autoblog.py --judul "Judul artikel" --kategori Kesehatan
  DEEPSEEK_API_KEY=xxx python3 scripts/autoblog.py              # ambil judul dari content/antrean-judul.txt
  python3 scripts/autoblog.py --dry-run --judul "Contoh"        # test tanpa API (tidak butuh key)

Key TIDAK BOLEH ditulis di file/repo/chat — cukup lewat environment variable
(di GitHub: Secrets and variables > Actions > DEEPSEEK_API_KEY).
"""
import argparse, json, os, re, sys, urllib.request, urllib.parse
from datetime import date

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
PEXELS_SEARCH = "https://api.pexels.com/v1/search"
KATEGORI_QUERY = {
    "Kesehatan": "family health doctor hospital",
    "Jiwa": "happy family parents children",
    "Kendaraan": "car driving road",
    "Pendidikan": "children school education",
    "Perjalanan": "travel airplane vacation",
    "Syariah": "mosque islamic architecture",
    "Keuangan": "money finance savings",
    "Properti": "house home exterior",
}
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(REPO_DIR, "content", "antrean-judul.txt")
POSTS = os.path.join(REPO_DIR, "content", "posts")
INDEX = os.path.join(REPO_DIR, "content", "index.json")

SYSTEM = ("Kamu penulis blog asuransi/keuangan Indonesia. Tulis artikel ORISINAL Bahasa Indonesia "
          "yang santai tapi akurat, WAJIB 300-400 KATA (jangan berhenti sebelum 300 kata), "
          "terstruktur (3-4 subjudul ##, satu list, satu contoh angka rupiah). "
          "Dilarang menjiplak artikel lain. "
          "Akhiri dengan disclaimer 1 kalimat bahwa ini edukasi, bukan saran finansial berlisensi.")

def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s).strip()
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", s))[:80] or "artikel"

def hitung_kata(s):
    return len(re.findall(r"\S+", s))

def clean_excerpt(s, limit=200):
    s = re.sub(r"^#+\s*", "", s)
    for ch in ('*', '_', '`', '"'):
        s = s.replace(ch, "")
    return re.sub(r"\s+", " ", s).strip()[:limit].rstrip()

def split_hasil(teks):
    """Pisahkan ringkasan 1 baris dan isi artikel. Kembalikan (ringkasan, isi)."""
    lines = teks.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].strip().upper().startswith("RINGKASAN:"):
        ringkas = lines[0].split(":", 1)[1].strip()
        isi = "\n".join(lines[1:]).strip()
        if ringkas:
            return clean_excerpt(ringkas), (isi or teks.strip())
    first = next((l.strip() for l in lines if l.strip()), "")
    return clean_excerpt(first), teks.strip()

def baca_antrean():
    if not os.path.exists(QUEUE):
        return []
    return [l.strip() for l in open(QUEUE, encoding="utf-8") if l.strip()]

def pop_queue():
    lines = baca_antrean()
    if not lines:
        return None, None
    first = lines[0]
    if " | " in first:
        kat, judul = first.split(" | ", 1)
        return kat.strip() or "Umum", judul.strip()
    return "Umum", first

def hapus_kepala(baris_mentah):
    """Hapus baris antrean teratas HANYA setelah artikel sukses ditulis."""
    lines = baca_antrean()
    if lines and lines[0] == baris_mentah:
        open(QUEUE, "w", encoding="utf-8").write("\n".join(lines[1:]) + ("\n" if len(lines) > 1 else ""))

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
             "Panjang WAJIB minimal 300 kata. Awali dengan ringkasan 1 kalimat diawali 'RINGKASAN: ', lalu isi artikel markdown."},
        ],
        "temperature": 0.8, "max_tokens": 1200,
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

def ambil_gambar_pexels(slug, kategori):
    """Unduh 1 foto relevan dari Pexels. Kembalikan dict atau None bila dilewati.
    Key dari env PEXELS_API_KEY (GitHub Secrets) — tidak pernah di-hardcode."""
    key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not key:
        print("INFO: PEXELS_API_KEY kosong — artikel tanpa foto.")
        return None
    try:
        q = KATEGORI_QUERY.get(kategori, "insurance family")
        ua = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
        req = urllib.request.Request(
            PEXELS_SEARCH + "?" + urllib.parse.urlencode(
                {"query": q, "per_page": 3, "orientation": "landscape"}),
            headers={"Authorization": key, **ua})
        with urllib.request.urlopen(req, timeout=30) as r:
            fotos = (json.load(r) or {}).get("photos") or []
        if not fotos:
            print("INFO: Pexels tidak mengembalikan foto — artikel tanpa foto.")
            return None
        foto = fotos[0]
        src = (foto.get("src") or {}).get("large") or (foto.get("src") or {}).get("medium")
        if not src:
            return None
        dest = os.path.join(REPO_DIR, "content", "images", slug + ".jpg")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        dl = urllib.request.Request(src, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"})
        with urllib.request.urlopen(dl, timeout=60) as fr, open(dest, "wb") as fw:
            fw.write(fr.read())
        print(f"OK gambar: content/images/{slug}.jpg")
        return {"image": f"/content/images/{slug}.jpg",
                "credit": f"Foto oleh {foto.get('photographer', 'Pexels')} dari Pexels",
                "url": foto.get("photographer_url", "https://www.pexels.com")}
    except Exception as e:
        print(f"INFO: gambar dilewati ({e})")
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judul", default="")
    ap.add_argument("--kategori", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    q_kat, q_judul = pop_queue() if not a.judul.strip() else ("", "")
    judul = a.judul.strip() or q_judul
    kategori = a.kategori.strip() or q_kat or "Umum"
    if not judul:
        sys.exit("Antrean kosong dan --judul tidak diisi. Tambah judul ke content/antrean-judul.txt")
    dari_antrean = not a.judul.strip()
    baris_mentah = next((l for l in baca_antrean()
                         if l == judul or l.endswith(" | " + judul)), judul)
    slug = slugify(judul)
    target = os.path.join(POSTS, slug + ".md")
    if os.path.exists(target):
        sys.exit(f"Slug {slug} sudah ada — pilih judul lain.")

    teks = generate(judul, kategori, a.dry_run)
    ringkasan, isi = split_hasil(teks)
    if not a.dry_run and hitung_kata(isi) < 200:
        sys.exit(f"ERROR: artikel terlalu pendek ({hitung_kata(isi)} kata, minimal 200) — "
                 f"tidak diterbitkan agar blog tidak rusak.")

    os.makedirs(POSTS, exist_ok=True)
    gbr = None if a.dry_run else ambil_gambar_pexels(slug, kategori)
    img_meta = ""
    if gbr:
        img_meta = (f"image: {gbr['image']}\n"
                    f"image_credit: {json.dumps(gbr['credit'], ensure_ascii=False)}\n"
                    f"image_url: {gbr['url']}\n")
    with open(target, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {json.dumps(judul)}\ndate: {date.today().isoformat()}\n"
                f"category: {kategori}\nexcerpt: {json.dumps(ringkasan)}\n{img_meta}---\n\n{isi}\n")

    idx = json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else []
    idx = [x for x in idx if x.get("slug") != slug]
    entry = {"slug": slug, "title": judul, "date": date.today().isoformat(),
             "category": kategori, "excerpt": ringkasan}
    if gbr:
        entry.update({"image": gbr["image"], "image_credit": gbr["credit"], "image_url": gbr["url"]})
    idx.insert(0, entry)
    idx.sort(key=lambda x: x.get("date", ""), reverse=True)
    json.dump(idx, open(INDEX, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if dari_antrean and not a.dry_run:
        hapus_kepala(baris_mentah)
    print(f"OK: {target} ({hitung_kata(isi)} kata)")

if __name__ == "__main__":
    main()
