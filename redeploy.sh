#!/usr/bin/env bash
set -e

TOKEN=$($HOME/google-cloud-sdk/bin/gcloud auth print-access-token 2>/dev/null)
PROJECT="gen-lang-client-0803878197"
REGION="us-central1"
SERVICE="kurodot-agent"
IMAGE="gcr.io/${PROJECT}/kurodot-agent"
API="https://run.googleapis.com/v2/projects/${PROJECT}/locations/${REGION}/services/${SERVICE}"

echo "Fetching current service config..."
CURRENT=$(curl -s -H "Authorization: Bearer $TOKEN" "$API")
echo "$CURRENT" | python3 -c "
import json,sys
s=json.load(sys.stdin)
t=s.get('template',{})
c=t.get('containers',[{}])[0]
print('current image:', c.get('image',''))
"

echo ""
echo "Patching to latest image..."
PATCH=$(cat <<EOF
{
  "template": {
    "containers": [
      {
        "image": "${IMAGE}"
      }
    ]
  }
}
EOF
)

RESULT=$(curl -s -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PATCH" \
  "$API")

echo "$RESULT" | python3 -c "
import json,sys
r=json.load(sys.stdin)
print('response name:', r.get('name',''))
print('response metadata:', json.dumps(r.get('metadata',{}), indent=2)[:200])
err=r.get('error',{})
if err: print('ERROR:', err)
"
