terraform {
  required_providers {
    pinecone = {
      source  = "pinecone-io/pinecone"
      version = "~> 0.7"
    }
  }
}

variable "index_name" {
  type = string
}

variable "embedding_dimensions" {
  type    = number
  default = 1536
}

variable "cloud" {
  type    = string
  default = "aws"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

resource "pinecone_index" "this" {
  name      = var.index_name
  dimension = var.embedding_dimensions
  metric    = "cosine"

  spec = {
    serverless = {
      cloud  = var.cloud
      region = var.region
    }
  }
}

output "index_host" {
  value = pinecone_index.this.host
}
