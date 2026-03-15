output "service_url" {
  description = "Public URL of the deployed kurodot-agent Cloud Run service"
  value       = google_cloud_run_v2_service.kurodot_agent.uri
}

output "gcs_bucket_name" {
  description = "GCS bucket used for canvas exports"
  value       = google_storage_bucket.exports.name
}
