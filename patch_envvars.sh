#!/usr/bin/env bash
set -e

if [ -z "$GEMINI_API_KEY" ]; then
  echo "ERROR: set GEMINI_API_KEY env var before running this script"
  echo "  export GEMINI_API_KEY=your_key_here"
  exit 1
fi

if [ -z "$GCS_BUCKET_NAME" ]; then
  echo "WARNING: GCS_BUCKET_NAME not set, using empty string"
  GCS_BUCKET_NAME=""
fi

TOKEN=$($HOME/google-cloud-sdk/bin/gcloud auth print-access-token 2>/dev/null)
PROJECT="gen-lang-client-0803878197"
REGION="us-central1"
SERVICE="kurodot-agent"
IMAGE="gcr.io/${PROJECT}/kurodot-agent"
API="https://run.googleapis.com/v2/projects/${PROJECT}/locations/${REGION}/services/${SERVICE}"

echo "Patching service with image + env vars..."

PATCH=$(python3 - <<EOF
import json
patch = {
  "template": {
    "containers": [
      {
        "image": "${IMAGE}",
        "env": [
          {"name": "GEMINI_API_KEY", "value": "${GEMINI_API_KEY}"},
          {"name": "GCS_BUCKET_NAME", "value": "${GCS_BUCKET_NAME}"}
        ]
      }
    ]
  }
}
print(json.dumps(patch))
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
name=r.get('name','')
err=r.get('error',{})
if err:
  print('ERROR:', err)
else:
  print('OK - operation:', name)
"

echo ""
echo "Waiting 45s for revision to roll out..."
sleep 45

echo "Re-applying IAM (allUsers invoker)..."
IAM_URL="${API}:setIamPolicy"
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"policy":{"bindings":[{"role":"roles/run.invoker","members":["allUsers"]}]}}' \
  "$IAM_URL" | python3 -c "import json,sys; r=json.load(sys.stdin); print('IAM:', r.get('etag','err'))"

echo ""
echo "Verifying /api/settings..."
curl -s https://kurodot-agent-1063202705342.us-central1.run.app/api/settings
