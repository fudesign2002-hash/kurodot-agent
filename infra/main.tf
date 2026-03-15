terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── Cloud Run Service ─────────────────────────────────────────────────────────
resource "google_cloud_run_v2_service" "kurodot_agent" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/${var.service_name}"

      resources {
        limits = {
          memory = "1Gi"
          cpu    = "1"
        }
      }

      env {
        name  = "GEMINI_API_KEY"
        value = var.gemini_api_key
      }

      env {
        name  = "GCS_BUCKET_NAME"
        value = var.gcs_bucket_name
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = var.max_instances
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# ── Allow unauthenticated public access ──────────────────────────────────────
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.kurodot_agent.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── GCS Bucket for Tech Producer exports ─────────────────────────────────────
resource "google_storage_bucket" "exports" {
  name                        = var.gcs_bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = false

  cors {
    origin          = [google_cloud_run_v2_service.kurodot_agent.uri]
    method          = ["GET"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.exports.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
