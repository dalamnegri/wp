#!/bin/bash
# Inisialisasi repo GitHub untuk blog ini.
# Cara pakai: bash scripts/init-github.sh
# Jangan pernah menaruh token di dalam file. Isi lewat prompt.
set -euo pipefail
git init 2>/dev/null || true
git add -A
git commit -m "Init bloginsurance.my.id - static blog for Cloudflare Pages" 2>/dev/null || echo "(tidak ada perubahan baru)"
git branch -M main
echo ""
echo "Selanjutnya buat repo kosong di https://github.com/new (misal: bloginsurance)"
echo "Lalu jalankan:"
echo "  git remote remove origin 2>/dev/null || true"
echo "  git remote add origin https://github.com/USERNAME/bloginsurance.git"
echo "  git push -u origin main"
echo ""
echo "Jangan paste token GitHub di chat / file. Gunakan 'gh auth login' atau credential helper."
