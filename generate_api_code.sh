DIR=$(dirname "$0")
#[ -f "$DIR/openapi/swagger-codegen-cli.jar" ] || wget https://repo1.maven.org/maven2/io/swagger/codegen/v3/swagger-codegen-cli/3.0.16/swagger-codegen-cli-3.0.16.jar -O "$DIR/openapi/swagger-codegen-cli.jar"

function codegencmd() {
  java -jar "$DIR/openapi/swagger-codegen-cli.jar" generate -i "$DIR/openapi/spec.yaml" $@
}

function generate_frontend() {
  GENERATOR_PATH="$DIR/openapi/swagger-codegen-generators/src/main/resources/handlebars/typescript-angular/"
  rm -rf "$DIR/frontend_angular/src/app/api"
  codegencmd -l typescript-angular -o "$DIR/frontend_angular/src/app/api" -t "$GENERATOR_PATH" --additional-properties ngVersion=7
}

function generate_backend() {
  codegencmd -Dmodels -l python -o "$DIR/tmpsrc/"
  cp -r -n tmpsrc/swagger_client/models/* api_server/src/entity/
  diff -ruN api_server/src/entity tmpsrc/swagger_client/models/ > entities.patch
  patch -p0 < entities.patch

  sed -i 's/swagger_client.models/src.entity/' "$DIR/api_server/src/entity/__init__.py"

  rm -rf "$DIR/tmpsrc"
  rm entities.patch
}

while true; do
  read -p "Do you wish to regenerate the frontend API code? [y/n]:" yn
  case $yn in
      [Yy]* ) generate_frontend; break;;
      [Nn]* ) echo "Skipping frontend generation"; break;;
      * ) echo "Please answer yes or no.";;
  esac
done

while true; do
  read -p "Do you wish to patch the backend entities? [y/n]:" yn
  case $yn in
      [Yy]* ) generate_backend; break;;
      [Nn]* ) echo "Skipping backend generation"; break;;
      * ) echo "Please answer yes or no.";;
  esac
done

echo "Done!"
