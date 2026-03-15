variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region to deploy into"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "kurodot-agent"
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 5
}

variable "gemini_api_key" {
  description = "Google Gemini API key (sensitive)"
  type        = string
  sensitive   = true
}

variable "gcs_bucket_name" {
  description = "GCS bucket name for Tech Producer canvas exports"
  type        = string
}
