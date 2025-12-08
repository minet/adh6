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


# BACKEND

backend_tmp=$(mktemp -d -t adh6_backend)
echo "[BACKEND] Temporary directory created in $backend_tmp"

echo "[BACKEND] Generating code in $backend_tmp"
# Comme openapi-generator-cli a besoin de java pour fonctionner, et qu'on ne veut pas forcément installer java sur notre système juste pour ADH6 (fuck Java), on utilise Docker !
docker run --rm -v $backend_tmp:/local -v ./openapi/spec.yaml:/spec.yaml openapitools/openapi-generator-cli:v7.12.0 generate -i /spec.yaml -g python-flask -o /local --additional-properties packageName=adh6 --additional-properties=modelPackage=entity > /dev/null

echo "[BACKEND] Removing current entities in $BACKEND_DIR/adh6/entity..."
rm $BACKEND_DIR/adh6/entity/*.py

# On ajoute un message et on spécifie d'ignorer les erreurs de type sur tous les fichiers python, car les fichiers générés ne sont malheureusement pas strictement typés
echo "[BACKEND] Patching python files..."
for file in $backend_tmp/**/*.py; do
    tmpfile=$(mktemp)
    {
        echo "# File generated using spec-to-code.sh, DO NOT EDIT MANUALLY."
        echo "# type: ignore"
        echo
        cat "$file"
    } > "$tmpfile"
    mv "$tmpfile" "$file"
done

# On fix base_model.py à cause d'une issue non fixée... https://github.com/OpenAPITools/openapi-generator/issues/9332
echo "[BACKEND] Fixing base_model.py file..."
sed -i'' -e 's/result\[attr\]/result\[self.attribute_map\[attr\]\]/g' $backend_tmp/adh6/entity/base_model.py

echo "[BACKEND] Copying generated files in code..."
cp $backend_tmp/adh6/entity/*.py $BACKEND_DIR/adh6/entity
cp $backend_tmp/adh6/typing_utils.py $BACKEND_DIR/adh6/
cp $backend_tmp/adh6/util.py $BACKEND_DIR/adh6/


echo "[BACKEND] Removing $backend_tmp"
rm -r $backend_tmp


# FRONTEND

frontend_tmp=$(mktemp -d -t adh6_backend)
echo "[FRONTEND] Temporary directory created in $frontend_tmp"

echo "[FRONTEND] Generating code in $frontend_tmp"
docker run --rm  -v $frontend_tmp:/local -v ./openapi/spec.yaml:/spec.yaml openapitools/openapi-generator-cli:v7.11.0 generate -i /spec.yaml -g typescript-angular -o "/local" --additional-properties=queryParamObjectFormat=key > /dev/null

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

echo "[FRONTEND] Removing $frontend_tmp"
rm -r $frontend_tmp
