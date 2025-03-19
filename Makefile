BACKEND_PATH = api_server
FRONTEND_PATH = frontend_angular
OPENAPI_PATH = openapi
BACKEND_ENV_NAME = .venv
BACKEND_ENV_PATH = $(BACKEND_PATH)/$(BACKEND_ENV_NAME)
FRONTEND_ENV_PATH = $(FRONTEND_PATH)/node_modules

OPENAPI_SPEC_PATH = $(OPENAPI_PATH)/spec.yaml

CURRENT_UID := $(shell id -u)
CURRENT_GID := $(shell id -g)

.PHONY: all
all: generate run

.PHONY: clean
clean: clean-frontend clean-backend clean-docker-run clean-docker-run-dev

.PHONY: clean-backend
clean-backend:
	find $(BACKEND_PATH) -name __pycache__ -type d -exec rm -r {} \;
	find $(BACKEND_PATH)/adh6/entity/ -depth 1 -name "*.py" -type f -exec rm {} \;
	[ -f $(BACKEND_PATH)/adh6/typing_utils.py ] && rm $(BACKEND_PATH)/adh6/typing_utils.py || echo "File not found"
	[ -f $(BACKEND_PATH)/adh6/util.py ] && rm $(BACKEND_PATH)/adh6/util.py || echo "File not found"
	[ -d $(BACKEND_PATH)/.pytest_cache ] && rm -r $(BACKEND_PATH)/.pytest_cache || echo "No cache for pytest"
	[ -f $(BACKEND_PATH)/.coverage ] && rm $(BACKEND_PATH)/.coverage || echo "No cache for coverage"
	[ -d $(BACKEND_PATH)/.ruff_cache ] && rm -r $(BACKEND_PATH)/.ruff_cache || echo "No cache for ruff"
	[ -d $(BACKEND_PATH)/.tox ] && rm -r $(BACKEND_PATH)/.tox || echo "No cache for tox"
	[ -d $(BACKEND_ENV_PATH) ] && rm -r $(BACKEND_ENV_PATH) || echo "No virtual environment for python"

.PHONY: clean-frontend
clean-frontend:
	[ -d $(FRONTEND_ENV_PATH) ] && rm -r $(FRONTEND_ENV_PATH) || echo "The frontend dependencies has not been downloads"
	[ -d $(FRONTEND_PATH)/src/app/api ] && rm -r $(FRONTEND_PATH)/src/app/api || echo "API module has not been generated"
	[ -d $(FRONTEND_PATH)/.angular ] && rm -r $(FRONTEND_PATH)/.angular || echo "No cache for angular"
	[ -d $(FRONTEND_PATH)/dist ] && rm -r $(FRONTEND_PATH)/dist || echo "No dist folder"
	find $(FRONTEND_PATH)/src/assets -name "*.min.svg" -type f -exec rm {} \;

.PHONY: clean-backend-coverage-report
clean-coverage-report:
	[ -f $(BACKEND_PATH)/.coverage ] && rm $(BACKEND_PATH)/.coverage || echo "No cache for coverage"
	[ -d $(BACKEND_PATH)/htmlcov ] && rm -r $(BACKEND_PATH)/htmlcov || echo "No coverage report"

.PHONY: clean-docker
clean-docker-run:
	docker compose down -v --rmi all --remove-orphans

.PHONY: clean-docker-dev
clean-docker-run-dev:
	docker compose -f docker-compose-deploy.yml down -v --rmi all --remove-orphans


# .PHONY: dev-environment
# dev-environment: $(BACKEND_ENV_PATH) $(FRONTEND_ENV_PATH)

# $(BACKEND_VENV_PATH): $(BACKEND_PATH)/requirements.txt
# 	python3 -m venv $(BACKEND_VENV_PATH)
# 	cd $(BACKEND_PATH) && source $(BACKEND_VENV_PATH)/bin/activate && pip3 install --ignore-pipfile -r requirements.txt

# $(FRONTEND_ENV_PATH): $(FRONTEND_PATH)/package.json
# 	cd $(FRONTEND_PATH) && docker run --rm -w /app -u $(CURRENT_UID):$(CURRENT_GID) -v $(CURDIR)/$(FRONTEND_PATH):/app node:22-alpine yarn install --frozen-lockfile


##### Generate the needed element for the application to execute
.PHONY: generate
generate: $(BACKEND_PATH)/adh6/entity/*.py $(BACKEND_PATH)/openapi/swagger.yaml $(FRONTEND_PATH)/src/app/api

$(BACKEND_PATH)/openapi/swagger.yaml: $(OPENAPI_SPEC_PATH)
	cp $(OPENAPI_SPEC_PATH) $(BACKEND_PATH)/openapi/swagger.yaml	

$(BACKEND_PATH)/adh6/entity/*.py: $(OPENAPI_SPEC_PATH) $(BACKEND_PATH)/openapi/swagger.yaml
	docker run --rm  -u $(CURRENT_UID):$(CURRENT_GID) -v ${PWD}:/local openapitools/openapi-generator-cli:v7.12.0 generate -i /local/openapi/spec.yaml -g python-flask -o /local/tmpsrc --additional-properties packageName=adh6 --additional-properties=modelPackage=entity
	cp -r tmpsrc/adh6/entity/* $(BACKEND_PATH)/adh6/entity/
	cp tmpsrc/adh6/typing_utils.py $(BACKEND_PATH)/adh6/
	cp tmpsrc/adh6/util.py $(BACKEND_PATH)/adh6/
	sed -i'' -e 's/result\[attr\]/result\[self.attribute_map\[attr\]\]/g' api_server/adh6/entity/base_model.py
	rm -rf tmpsrc

$(FRONTEND_PATH)/src/app/api: $(OPENAPI_SPEC_PATH)
	rm -rf "$(FRONTEND_PATH)/src/app/api"
	docker run --rm  -u $(CURRENT_UID):$(CURRENT_GID) -v ${PWD}:/local openapitools/openapi-generator-cli:latest-release@sha256:c49d9c99124fe2ad94ccef54cc6d3362592e7ca29006a8cf01337ab10d1c01f4 generate -i /local/openapi/spec.yaml -g typescript-angular -o "/local/frontend_angular/src/app/api" --additional-properties=queryParamObjectFormat=key
	find $(FRONTEND_PATH)/src/app/api/api -type f -name "*.service.ts" -exec sed -i'' -e 's/private addToHttpParams(/private addToHttpParamsBad(/g' {} \;
	find $(FRONTEND_PATH)/src/app/api/api -type f -name "*.service.ts" -exec sed -i'' -e 's/addToHttpParamsRecursive/addToHttpParams/g' {} \;

# TODO: include this in the Dockerfile, no need to generate this on user side ?
# $(FRONTEND_PATH)/src/assets/*.min.svg: $(FRONTEND_PATH)/src/assets/*.svg
#    docker run --rm -w /local -v $(PWD)/$(FRONTEND_PATH)/src/assets:/local node:22-alpine /bin/sh -c "yarn global add svgo && svgo minet.svg minet-dark.svg adh6-logo.svg -o minet.min.svg minet-dark.min.svg adh6.min.svg"

### Generate database fixture, only for test purpose
.PHONY: generate-database-fixtures
generate-database-fixtures: $(BACKEND_ENV_PATH)
	cd $(BACKEND_PATH) && source $(BACKEND_ENV_NAME)/bin/activate && ENVIRONMENT=development ./manage.sh db upgrade
	cd $(BACKEND_PATH) && source $(BACKEND_ENV_NAME)/bin/activate && ENVIRONMENT=development ./manage.sh seed
	cd $(BACKEND_PATH) && source $(BACKEND_ENV_NAME)/bin/activate && ENVIRONMENT=development ./manage.sh fake $(LOGIN)

# TODO: run & run-dev are swapped...
.PHONY: run
run:
	docker compose up --build --force-recreate

.PHONY: run-dev
run-dev:
	docker compose -f docker-compose-deploy.yml up --build --force-recreate

# TODO: all the checks will be refactored (tox + uv)
# .PHONY: check
# check: $(BACKEND_PATH)/src/entity/*.py $(BACKEND_ENV_PATH) test-install-environment-python test-backend test-uninstall-environment-python

# .PHONY: test-environment-python
# test-install-environment-python:
# 	cd $(CURDIR)/api_server && source venv/bin/activate && pip3 install --ignore-pipfile pytest pytest-cov pytest-lazy-fixture faker

# .PHONY: test-environment-python
# test-uninstall-environment-python:
# 	cd $(CURDIR)/api_server && source venv/bin/activate && pip uninstall pytest pytest-cov pytest-lazy-fixture faker

# .PHONY: test-backend
# test-backend: dev-environment-backend generate-backend
# 	cd $(CURDIR)/api_server && source venv/bin/activate && pytest -vvv

# .PHONY: lint-backend
# lint-backend:
# 	cd $(CURDIR)/api_server && source venv/bin/activate && pip3 install --ignore-pipfile black isort
# 	cd $(CURDIR)/api_server && source venv/bin/activate && black . --extend-exclude migrations,venv
# 	cd $(CURDIR)/api_server && source venv/bin/activate && isort . --skip venv --skip migrations
# #	cd $(CURDIR)/api_server && source venv/bin/activate && flake8 .
# #	cd $(CURDIR)/api_server && source venv/bin/activate && pep8 .
# 	cd $(CURDIR)/api_server && source venv/bin/activate && pip uninstall black flake8 mypy isort pylint
