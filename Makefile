CODEGEN = java -jar "$(CURDIR)/openapi/swagger-codegen-cli.jar" generate -i "$(CURDIR)/openapi/spec.yaml"

FRONTEND_GENERATOR_PATH="$(CURDIR)/openapi/swagger-codegen-generators/src/main/resources/handlebars/typescript-angular/"
BACKEND_GENERATOR_PATH="$(CURDIR)/openapi/swagger-codegen-generators/src/main/resources/handlebars/python/"

BACKEND_PATH = $(CURDIR)/api_server
FRONTEND_PATH = $(CURDIR)/frontend_angular
BACKEND_VENV_PATH = $(BACKEND_PATH)/venv

SHELL = /bin/sh
CURRENT_UID := $(shell id -u)
CURRENT_GID := $(shell id -g)

.PHONY: all
all: clean generate run

.PHONY: run-dev
run-dev:
	docker compose -f docker-compose-deploy.yml up --build --force-recreate

.PHONY: run
run:
	docker compose up --build --force-recreate

.PHONY: generate
generate: generate-backend generate-frontend generate-frontend-assets

.PHONY: generate-frontend
generate-frontend:
	rm -rf "$(FRONTEND_PATH)/src/app/api"
	$(CODEGEN) -l typescript-angular -o "$(FRONTEND_PATH)/src/app/api" -t "$(FRONTEND_GENERATOR_PATH)" --additional-properties ngVersion=7
	sed -i 's/: ModuleWithProviders/: ModuleWithProviders<ApiModule>/g' "$(FRONTEND_PATH)/src/app/api/api.module.ts"

.PHONY: generate-frontend-assets
generate-frontend-assets:
	docker run --rm -w /app -u $(CURRENT_UID):$(CURRENT_GID) -v $(FRONTEND_PATH)/src/assets:/app node:16-alpine /bin/sh -c "yarn global add svgo && /home/node/.yarn/bin/svgo minet.svg adh6-logo.svg -o minet.min.svg adh6.min.svg"

.PHONY: generate-backend
generate-backend:
	$(CODEGEN) -l python -t "${BACKEND_GENERATOR_PATH}" -o "${CURDIR}/tmpsrc/"
	cp -r "$(CURDIR)/tmpsrc/swagger_client/models/"* "$(BACKEND_PATH)/src/entity/"
	sed -i 's/swagger_client.models/src.entity/' "$(BACKEND_PATH)/src/entity/__init__.py"
	rm -rf "${CURDIR}/tmpsrc"

.PHONY: dev-environment
dev-environment: dev-environment-backend dev-environment-frontend

.PHONY: dev-environment-backend
dev-environment-backend:
	python3 -m venv $(BACKEND_VENV_PATH)
	cd $(BACKEND_PATH) && source $(BACKEND_VENV_PATH)/bin/activate && pip3 install -r requirements.txt

.PHONY: dev-environment-frontend
dev-environment-frontend:
	cd $(FRONTEND_PATH) && docker run --rm -w /app -u $(CURRENT_UID):$(CURRENT_GID) -v $(FRONTEND_PATH):/app node:16-alpine yarn install

.PHONY: backend-tests
test-backend:
	cd $(CURDIR)/api_server && pytest -vvv

.PHONY: clean
clean: clean-frontend clean-backend clean-docker-run clean-docker-run-dev

.PHONY: clean-frontend
clean-frontend:
	[ -d $(FRONTEND_PATH)/node_modules ] && rm -rf $(FRONTEND_PATH)/node_modules || echo "The frontend dependencies has not been downloads"
	[ -d $(FRONTEND_PATH)/src/app/api ] && rm -rf $(FRONTEND_PATH)/src/app/api || echo "API module has not been generated"
	[ -d $(FRONTEND_PATH)/dist ] && rm -rf $(FRONTEND_PATH)/dist || echo "No dist folder"
	[ -f $(FRONTEND_PATH)/src/assets/adh6.min.svg ] && rm $(FRONTEND_PATH)/src/assets/adh6.min.svg || echo "File not found"
	[ -f $(FRONTEND_PATH)/src/assets/minet.min.svg ] && rm $(FRONTEND_PATH)/src/assets/minet.min.svg || echo "File not found"

.PHONY: clean-backend
clean-backend:
	find $(CURDIR)/api_server -depth -name __pycache__ -type d -exec rm -rf {} \;
	find $(CURDIR) -depth -name .pytest_cache -type d -exec rm -rf {} \;
	find $(CURDIR) -name .coverage -type f -exec rm -rf {} \;
	[ -d $(BACKEND_VENV_PATH) ] && rm -rf $(BACKEND_VENV_PATH) || echo "No virtual environment for python"

.PHONY: clean-docker-run
clean-docker-run:
	docker compose down -v --rmi all --remove-orphans

.PHONY: clean-docker-run-dev
clean-docker-run-dev:
	docker compose -f docker-compose-deploy.yml down -v --rmi all --remove-orphans

.PHONY: generate-database-fixtures
generate-database-fixtures: dev-environment-backend
	cd $(BACKEND_PATH) && ENVIRONMENT=development ./manage.sh db upgrade
	cd $(BACKEND_PATH) && ENVIRONMENT=development ./manage.sh seed
	cd $(BACKEND_PATH) && ENVIRONMENT=development ./manage.sh fake $(LOGIN)
