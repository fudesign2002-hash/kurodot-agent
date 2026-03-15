#!/usr/bin/env bash
set -e

GEMINI_API_KEY="AIzaSyBvyDweMmat0rICQ9owPiMLDR4bjnf4CAY"
GCS_BUCKET_NAME="kurodot-agent"
TOKEN=$($HOME/google-cloud-sdk/bin/gcloud auth print-access-token 2>/dev/null)
API="https://run.googleapis.com/v2/projects/gen-lang-client-0803878197/locations/us-central1/services/kurodot-agent"
IMAGE="gcr.io/gen-lang-client-0803878197/kurodot-agent@sha256:cb0275542cb48926736b3aefcd371e40b3cf792026f69d6e24eaffa189a73df9"

echo "Patching with pinned digest..."
PATCH=$(printf '{"template":{"containers":[{"image":"%s","env":[{"name":"GEMINI_API_KEY","value":"%s"},{"name":"GCS_BUCKET_NAME","value":"%s"}]}]}}' "$IMAGE" "$GEMINI_API_KEY" "$GCS_BUCKET_NAME")

curl -s -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PATCH" \
  "$API" | python3 -c "import json,sys; r=json.load(sys.stdin); print('ERROR:',r['error']) if r.get('error') else print('OK - operation started')"

echo "Waiting 50s..."
sleep 50

echo "Re-applying IAM..."
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"policy":{"bindings":[{"role":"roles/run.invoker","members":["allUsers"]}]}}' \
  "${API}:setIamPolicy" | python3 -c "import json,sys; r=json.load(sys.stdin); print('IAM:', r.get('etag','ERROR'))"

echo "Testing /api/interleaved-story..."
curl -s -X POST https://kurodot-agent-1063202705342.us-central1.run.app/api/interleaved-story \
  -H "Content-Type: application/json" \
  -d '{"exhibition_info": "Bauhaus Blueprint: geometric forms, primary colours, industrial design"}' \
  | python3 -c "
import json,sys
r=json.load(sys.stdin)
texts=r.get('text_parts',[])
images=r.get('image_data',[])
err=r.get('error','')
print(f'text_parts: {len(texts)}, image_data: {len(images)}')
if err: print('error:', err)
if texts: print('preview:', texts[0][:300])
if images: print('image base64 length:', len(images[0]))
"
