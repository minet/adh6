#!/usr/bin/env bash
# Petit script utilitaire pour générer le code python et javascript depuis la spec OpenAPI.

# On utilise OpenAPI pour écrire une spec avec tous les endpoints API.
# Depuis cette spec, on peut générer du code avec openapi-generator (https://github.com/OpenAPITools/openapi-generator).
# On utilise ça pour générer les entités (classes python pour représenter les données transmises) dans le backend, et les fonctions d'appels à l'API pour le frontend.

BACKEND_DIR=./backend
FRONTEND_DIR=./frontend
# NB: il y a un problème dans les versions ultérieurs à la v7.11.0 : https://github.com/OpenAPITools/openapi-generator/issues/21182
OPENAPI_GENERATOR_CLI_VERSION="v7.11.0"

# On active l'option glob '**' désactivée par défaut sur bash
shopt -s globstar

if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install Docker to use this script."
    exit
fi

if [[ "$1" == "--backend-only" ]]; then
    echo "Generating code for backend only..."
    generate_backend=true
    generate_frontend=false
elif [[ "$1" == "--frontend-only" ]]; then
    echo "Generating code for frontend only..."
    generate_backend=false
    generate_frontend=true
else
    echo "Generating code for both backend and frontend..."
    generate_backend=true
    generate_frontend=true
fi

if [ "$generate_backend" = true ]; then
# BACKEND

backend_tmp=$(mktemp -d -t adh6_backend_XXXX)
echo "[BACKEND] Temporary directory created in $backend_tmp"

echo "[BACKEND] Generating code in $backend_tmp"
# Comme openapi-generator-cli a besoin de java pour fonctionner, et qu'on ne veut pas forcément installer java sur notre système juste pour ADH6 (fuck Java), on utilise Docker !
docker run --rm -v $backend_tmp:/local -v ./openapi/spec.yaml:/spec.yaml openapitools/openapi-generator-cli:$OPENAPI_GENERATOR_CLI_VERSION generate -i /spec.yaml -g python -o /local --additional-properties packageName=adh6 --additional-properties=modelPackage=entity

echo "[BACKEND] Generation complete. Checking what was generated..."
ls -la $backend_tmp/

echo "[BACKEND] Removing current entities in $BACKEND_DIR/adh6/entity..."
rm -r $BACKEND_DIR/adh6/entity

# On ajoute un message sur tous les fichiers python
echo "[BACKEND] Copying python files..."
for file in $backend_tmp/adh6/entity/**/*.py $backend_tmp/adh6/typing_utils.py $backend_tmp/adh6/util.py; do
    # Skip if file doesn't exist
    if [ ! -f "$file" ]; then
        continue
    fi
    
    # on enlève le répertoire temporaire du nom
    dest="$BACKEND_DIR/${file#$backend_tmp/}"

    # on créer le dossier parent si besoin
    mkdir -p "$(dirname "$dest")"
    {
        echo "# File generated using spec-to-code.sh, DO NOT EDIT MANUALLY."
        echo
        cat "$file"
    } > "$dest"

    echo "[BACKEND] Patching $dest..."
    # Fix import paths occasionally generated with the legacy package name.
    sed -i.bak -e 's/from adh6\.models\./from adh6.entity./g' "$dest" && rm -f "$dest.bak"
    # Replace         return json.dumps(self.to_dict())
    # With         return self.model_dump_json(by_alias=True, exclude_none=True)
    sed -i.bak -e 's/return json.dumps(self.to_dict())/return self.model_dump_json(by_alias=True, exclude_none=True)/g' "$dest" && rm -f "$dest.bak" 
done

echo "[BACKEND] Add notice file..."
echo "Directory managed by spec-to-code.sh script, DO NOT add manually any new file here." > $BACKEND_DIR/adh6/entity/README

echo "[BACKEND] Removing $backend_tmp"
rm -rf $backend_tmp
fi


if [ "$generate_frontend" = true ]; then
# FRONTEND

frontend_tmp=$(mktemp -d -t adh6_frontend_XXXX)
echo "[FRONTEND] Temporary directory created in $frontend_tmp"

echo "[FRONTEND] Generating code in $frontend_tmp"
docker run --rm  -v $frontend_tmp:/local -v ./openapi/spec.yaml:/spec.yaml openapitools/openapi-generator-cli:$OPENAPI_GENERATOR_CLI_VERSION generate -i /spec.yaml -g typescript-angular -o "/local" --additional-properties=queryParamObjectFormat=key > /dev/null

echo "[FRONTEND] Removing current api in $FRONTEND_DIR/src/app/api..."
rm -r $FRONTEND_DIR/src/app/api

# On ajoute un message sur tous les fichiers typescript
echo "[FRONTEND] Copy typescript files..."
for file in $frontend_tmp/**/*.ts; do
    # on enlève le répertoire temporaire du nom
    dest="$FRONTEND_DIR/src/app/api/${file#$frontend_tmp/}"

    # on créer le dossier parent si besoin
    mkdir -p "$(dirname "$dest")"
    {
        echo "// File generated using spec-to-code.sh, DO NOT EDIT MANUALLY."
        echo
        cat "$file"
    } > "$dest"
done

# Je ne sais pas pourquoi, mais flemme d'investiguer, je fais comme c'était déjà fait
echo "[FRONTEND] Patching *.service.ts files..."
find $FRONTEND_DIR/src/app/api/api -type f -name "*.service.ts" -exec sed -i '' -e 's/private addToHttpParams(/private addToHttpParamsBad(/g' {} \;
find $FRONTEND_DIR/src/app/api/api -type f -name "*.service.ts" -exec sed -i '' -e 's/addToHttpParamsRecursive/addToHttpParams/g' {} \;

echo "[FRONTEND] Add notice file..."
echo "Directory managed by spec-to-code.sh script, DO NOT add manually any new file here." > $FRONTEND_DIR/src/app/api/README

echo "[FRONTEND] Removing $frontend_tmp"
rm -rf $frontend_tmp
fi
