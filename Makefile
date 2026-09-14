BACKEND_PATH = backend
FRONTEND_PATH = frontend
OPENAPI_SPEC_PATH = openapi/spec.yaml

FDPUSER_PATH ?= ../fdpuserstoragefederation
KEYCLOAK_THEME_PATH ?= ../theme/MiNET
KEYCLOAK_JAR = $(FDPUSER_PATH)/target/UserStorageFederation-1.0.0.jar
export FDPUSER_PATH KEYCLOAK_THEME_PATH

CURRENT_UID := $(shell id -u)
CURRENT_GID := $(shell id -g)

.PHONY: all
all: run-dev

.PHONY: run-dev
run-dev: keycloak-jar
	docker compose up --build --force-recreate --watch

.PHONY: run-debug
run-debug: keycloak-jar
	docker compose -f compose.yaml -f compose.debug-api.yaml up --build --force-recreate --watch

.PHONY: keycloak
keycloak: keycloak-jar
	docker compose up -d keycloak
	$(MAKE) keycloak-client

.PHONY: keycloak-client
keycloak-client:
	docker compose run --rm keycloak_init

.PHONY: seed
seed:
	docker compose run --rm database_seed

.PHONY: keycloak-jar
keycloak-jar: $(KEYCLOAK_JAR)

$(KEYCLOAK_JAR): $(FDPUSER_PATH)/pom.xml $(shell find $(FDPUSER_PATH)/src -type f 2>/dev/null)
	@[ -d $(FDPUSER_PATH) ] || { echo "$(FDPUSER_PATH) introuvable, cloner fdpuserstoragefederation ou passer FDPUSER_PATH=..."; exit 1; }
	docker run --rm -v "$(abspath $(FDPUSER_PATH))":/build -v maven-cache:/root/.m2 -w /build \
		maven:3.9-eclipse-temurin-21 mvn clean package -DskipTests -q

.PHONY: clean-keycloak
clean-keycloak:
	docker compose rm -sfv keycloak keycloak_init
	docker volume rm -f adh6_keycloak_data

# spec-to-code.sh est le générateur de référence (voir backend/adh6/entity/README)
.PHONY: generate
generate:
	./spec-to-code.sh

.PHONY: generate-backend
generate-backend:
	./spec-to-code.sh --backend-only

.PHONY: generate-frontend
generate-frontend:
	./spec-to-code.sh --frontend-only

.PHONY: test-backend
test-backend:
	cd $(BACKEND_PATH) && uv run pytest

.PHONY: check-backend
check-backend:
	cd $(BACKEND_PATH) && uv run tox -e dev

.PHONY: lint-frontend
lint-frontend:
	cd $(FRONTEND_PATH) && yarn lint && yarn prettier:check

.PHONY: clean
clean: clean-backend clean-frontend clean-docker

.PHONY: clean-backend
clean-backend:
	find $(BACKEND_PATH) -depth -name __pycache__ -type d -exec rm -r {} \;
	rm -rf $(BACKEND_PATH)/.pytest_cache $(BACKEND_PATH)/.coverage $(BACKEND_PATH)/htmlcov $(BACKEND_PATH)/.ruff_cache $(BACKEND_PATH)/.tox $(BACKEND_PATH)/.venv

.PHONY: clean-frontend
clean-frontend:
	rm -rf $(FRONTEND_PATH)/node_modules $(FRONTEND_PATH)/.angular $(FRONTEND_PATH)/dist
	find $(FRONTEND_PATH)/src/assets -name "*.min.svg" -type f -exec rm {} \;

.PHONY: clean-docker
clean-docker:
	docker compose down -v --rmi all --remove-orphans
