terraform {
  required_version = ">= 1.5"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    pinecone = {
      source  = "pinecone-io/pinecone"
      version = "~> 0.7"
    }
  }
}

provider "docker" {}

provider "pinecone" {
  # Reads PINECONE_API_KEY from the environment.
}
