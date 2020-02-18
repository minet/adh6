DIR=$(dirname "$0")
[ -f swagger-codegen-cli.jar ] || wget https://repo1.maven.org/maven2/io/swagger/codegen/v3/swagger-codegen-cli/3.0.16/swagger-codegen-cli-3.0.16.jar -O swagger-codegen-cli.jar

function generate_frontend() {
  rm -rf "$DIR/frontend_angular/src/app/api"
  java -jar swagger-codegen-cli.jar generate -i "$DIR/openapi/spec.yaml" -l typescript-angular -o "$DIR/frontend_angular/src/app/api" --additional-properties ngVersion=7
}

function generate_backend() {
  java -jar swagger-codegen-cli.jar generate -i "$DIR/openapi/spec.yaml" -l python -o "$DIR/tmpsrc/"

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
