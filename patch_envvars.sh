#!/usr/bin/env bash
set -e

if [ -z "$GEMINI_API_KEY" ]; then
  echo "ERROR: set GEMINI_API_KEY env var before running this script"
  echo "  export GEMINI_API_KEY=your_key_here"
  exit 1
fi

GCS_BUCKET_NAME="${GCS_BUCKET_NAME:-}"

TOKEN=$($HOME/google-cloud-sdk/bin/gcloud auth print-access-token 2>/dev/null)
PROJECT="gen-lang-client-0803878197"
REGION="us-central1"
SERVICE="kurodot-agent"
IMAGE="gcr.io/${PROJECT}/kurodot-agent@sha256:c91c02907149986a84339db8e8a45b87223d15015a5c0a36430eec41c03de155"
API="https://run.googleapis.com/v2/projects/${PROJECT}/locations/${REGION}/services/${SERVICE}"

echo "Patching service with image + env vars..."

# Use printf to build JSON to avoid heredoc quoting issues
PATCH=$(printf '{
  "template": {
    "containers": [{
      "image": "%s",
      "env": [
        {"name": "GEMINI_API_KEY", "value": "%s"},
        {"name": "GCS_BUCKET_NAME", "value": "%s"}
      ]
    }]
  }
}' "$IMAGE" "$GEMINI_API_KEY" "$GCS_BUCKET_NAME")

RESULT=$(curl -s -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PATCH" \
  "$API")

echo "$RESULT" | python3 -c "
import json,sys
r=json.load(sys.stdin)
err=r.get('error',{})
if err:
  print('ERROR:', err)
else:
  print('OK - operation started')
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
