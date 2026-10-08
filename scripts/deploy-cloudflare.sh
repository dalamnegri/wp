#!/bin/bash
# Deploy manual ke Cloudflare Pages tanpa Node — memakai API via curl + python3.
# Butuh: CLOUDFLARE_API_TOKEN (Pages:Edit) dan CLOUDFLARE_ACCOUNT_ID.
# Cara pakai:
#   export CLOUDFLARE_API_TOKEN="cf_token_anda"
#   export CLOUDFLARE_ACCOUNT_ID="account_id_anda"
#   export CLOUDFLARE_PROJECT_NAME="bloginsurance"  # samakan dengan nama Pages project
#   bash scripts/deploy-cloudflare.sh
set -euo pipefail
: "${CLOUDFLARE_API_TOKEN:?Isi dulu CLOUDFLARE_API_TOKEN}"
: "${CLOUDFLARE_ACCOUNT_ID:?Isi dulu CLOUDFLARE_ACCOUNT_ID}"
PROJECT="${CLOUDFLARE_PROJECT_NAME:-bloginsurance}"

echo "==> Cek project Pages: $PROJECT"
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects/$PROJECT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success'), d.get('result',{}).get('name') if d.get('success') else d)"

echo ""
echo "Catatan: upload file-by-file via API rumit tanpa wrangler."
echo "Cara termudah (disarankan):"
echo " 1. Push folder ini ke GitHub (lihat INSTRUKSI-CLOUDFLARE.md langkah 2)"
echo " 2. Di Cloudflare Dashboard > Workers & Pages > Create > Pages > Connect to Git > pilih repo > Build command KOSONGKAN, output directory '/' atau '.'"
echo " 3. Setiap git push ke main = deploy otomatis."
echo ""
echo "Atau install wrangler lalu: wrangler pages deploy . --project-name=$PROJECT"
