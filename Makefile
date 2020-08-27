CODEGEN = java -jar "$(CURDIR)/openapi/swagger-codegen-cli.jar" generate -i "$(CURDIR)/openapi/spec.yaml"

FRONTEND_GENERATOR_PATH="$(CURDIR)/openapi/swagger-codegen-generators/src/main/resources/handlebars/typescript-angular/"
BACKEND_GENERATOR_PATH="$(CURDIR)/openapi/swagger-codegen-generators/src/main/resources/handlebars/python/"

.PHONY: run-dev
run-dev:
	docker-compose -f docker-compose-deploy.yml up --build --force-recreate
.PHONY: run
run:
	docker-compose up --build --force-recreate

.PHONY: clean
clean:
	docker-compose rm -vf

.PHONY: generate-front
generate-front:
	rm -rf "$(CURDIR)/frontend_angular/src/app/api"
	$(CODEGEN) -l typescript-angular -o "$(CURDIR)/frontend_angular/src/app/api" -t "$(FRONTEND_GENERATOR_PATH)" --additional-properties ngVersion=7

.PHONY: generate-back
generate-back:
	$(CODEGEN) -l python -t "${BACKEND_GENERATOR_PATH}" -o "${CURDIR}/tmpsrc/"
	cp -r "$(CURDIR)/tmpsrc/swagger_client/models/"* "$(CURDIR)/api_server/src/entity/"
	sed -i 's/swagger_client.models/src.entity/' "${CURDIR}/api_server/src/entity/__init__.py"
	rm -rf "${CURDIR}/tmpsrc"

.PHONY: generate
generate: generate-back generate-front


.PHONY: backend-unit-tests
backend-unit-tests:
	pytest -vvv "${CURDIR}/api_server/test/unit"

.PHONY: backend-integration-tests
backend-integration-tests:
	pytest -vvv "${CURDIR}/api_server/test/integration"

.PHONY: backend-tests
backend-tests: backend-unit-tests backend-integration-tests