# Provisions the data stores for the Stock Intelligence Service.
#
#   - postgres : local pgvector container (primary vector store + app DB)
#   - pinecone : optional managed serverless index   (enable_pinecone = true)
#   - weaviate : optional local container            (enable_weaviate = true)

module "postgres" {
  source            = "./modules/postgres"
  postgres_password = var.postgres_password
  postgres_port     = var.postgres_port
}

module "pinecone" {
  source               = "./modules/pinecone"
  count                = var.enable_pinecone ? 1 : 0
  index_name           = var.pinecone_index_name
  embedding_dimensions = var.embedding_dimensions
}

module "weaviate" {
  source = "./modules/weaviate"
  count  = var.enable_weaviate ? 1 : 0
}
