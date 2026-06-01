terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

variable "postgres_password" {
  type      = string
  sensitive = true
}

variable "postgres_port" {
  type    = number
  default = 5432
}

resource "docker_image" "pgvector" {
  name = "pgvector/pgvector:pg16"
}

resource "docker_container" "postgres" {
  name  = "store-pgvector"
  image = docker_image.pgvector.image_id

  env = [
    "POSTGRES_USER=postgres",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=app",
  ]

  ports {
    internal = 5432
    external = var.postgres_port
  }
}

output "database_url" {
  value     = "postgresql+asyncpg://postgres:${var.postgres_password}@localhost:${var.postgres_port}/app"
  sensitive = true
}
