terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

variable "http_port" {
  type    = number
  default = 8080
}

resource "docker_image" "weaviate" {
  name = "cr.weaviate.io/semitechnologies/weaviate:1.25.0"
}

resource "docker_container" "weaviate" {
  name  = "store-weaviate"
  image = docker_image.weaviate.image_id

  env = [
    "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true",
    "PERSISTENCE_DATA_PATH=/var/lib/weaviate",
    "DEFAULT_VECTORIZER_MODULE=none",
  ]

  ports {
    internal = 8080
    external = var.http_port
  }
}

output "weaviate_url" {
  value = "http://localhost:${var.http_port}"
}
