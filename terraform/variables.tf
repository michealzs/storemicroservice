variable "postgres_password" {
  type        = string
  default     = "postgres"
  sensitive   = true
  description = "Password for the local pgvector Postgres container."
}

variable "postgres_port" {
  type        = number
  default     = 5432
  description = "Host port to expose Postgres on."
}

variable "enable_pinecone" {
  type        = bool
  default     = false
  description = "Create a managed Pinecone index for the vector store."
}

variable "enable_weaviate" {
  type        = bool
  default     = false
  description = "Run a local Weaviate container for the vector store."
}

variable "pinecone_index_name" {
  type    = string
  default = "product-catalog"
}

variable "embedding_dimensions" {
  type    = number
  default = 1536
}
