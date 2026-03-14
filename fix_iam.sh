#!/usr/bin/env bash
set -e

TOKEN=$($HOME/google-cloud-sdk/bin/gcloud auth print-access-token 2>/dev/null)
PROJECT="gen-lang-client-0803878197"
REGION="us-central1"
SERVICE="kurodot-agent"
IAM_URL="https://run.googleapis.com/v2/projects/${PROJECT}/locations/${REGION}/services/${SERVICE}:setIamPolicy"

echo "Setting allUsers invoker IAM policy..."
POLICY=$(cat <<'EOF'
{
  "policy": {
    "bindings": [
      {
        "role": "roles/run.invoker",
        "members": ["allUsers"]
      }
    ]
  }
}
EOF
)

RESULT=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$POLICY" \
  "$IAM_URL")

echo "$RESULT"
