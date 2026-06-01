output "database_url" {
  value       = module.postgres.database_url
  sensitive   = true
  description = "SQLAlchemy async connection string for the provisioned Postgres."
}

output "pinecone_index_host" {
  value       = var.enable_pinecone ? module.pinecone[0].index_host : null
  description = "Host of the managed Pinecone index, when enabled."
}
