DIR=$(dirname "$0")
[ -f swagger-codegen-cli.jar ] || wget https://repo1.maven.org/maven2/io/swagger/codegen/v3/swagger-codegen-cli/3.0.16/swagger-codegen-cli-3.0.16.jar -O swagger-codegen-cli.jar


rm -rf "$DIR/frontend_angular/src/app/api"
rm -rf "$DIR/api_server/src/entity"

java -jar swagger-codegen-cli.jar generate -i "$DIR/openapi/spec.yaml" -l typescript-angular -o "$DIR/frontend_angular/src/app/api" --additional-properties ngVersion=7
java -jar swagger-codegen-cli.jar generate -i "$DIR/openapi/spec.yaml" -l python -o "$DIR/tmpsrc/"

mv "$DIR/tmpsrc/swagger_client/models/" "$DIR/api_server/src/entity"
sed -i 's/swagger_client.models/src.entity/' "$DIR/api_server/src/entity/__init__.py"

rm -rf "$DIR/tmpsrc"
