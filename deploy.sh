#!/bin/bash
# deploy.sh — Deploy to Google Cloud Run
# Usage: ./deploy.sh
# Prereq: gcloud auth login && gcloud config set project YOUR_PROJECT_ID

set -e

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="kurodot-agent"
REGION="us-central1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo ">>> Building container image: ${IMAGE}"
gcloud builds submit --tag "${IMAGE}"

echo ">>> Deploying to Cloud Run (region: ${REGION})"
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},GCS_BUCKET_NAME=${GCS_BUCKET_NAME}" \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5

echo ">>> Deployment complete."
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format "value(status.url)"
