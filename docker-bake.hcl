variable "REGISTRY" {
  default = "adh6"
}

variable "TAG" {
  default = "local"
}

# Builds prod and test images in one BuildKit session
group "backend" {
  targets = ["backend-prod", "backend-test"]
}

target "_backend" {
  context    = "."
  dockerfile = "backend/Dockerfile"
  args       = { BUILDKIT_INLINE_CACHE = "1" }
  attest     = ["type=provenance,disabled=true"]
}

target "backend-prod" {
  inherits   = ["_backend"]
  target     = "prod"
  tags       = ["${REGISTRY}/backend:${TAG}"]
  cache-from = ["type=registry,ref=${REGISTRY}/backend:${TAG}"]
}

target "backend-test" {
  inherits   = ["_backend"]
  target     = "test"
  tags       = ["${REGISTRY}/backend-test:${TAG}"]
  cache-from = ["type=registry,ref=${REGISTRY}/backend-test:${TAG}"]
}
