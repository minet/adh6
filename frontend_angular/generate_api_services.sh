DIR=$(dirname "$0")
rm -r "$DIR/src/app/api"
wget http://central.maven.org/maven2/io/swagger/codegen/v3/swagger-codegen-cli/3.0.15/swagger-codegen-cli-3.0.15.jar -O swagger-codegen-cli.jar
java -jar swagger-codegen-cli.jar generate -i "$DIR/swagger.yaml" -l typescript-angular -o "$DIR/src/app/api" --additional-properties ngVersion=7
rm swagger-codegen-cli.jar
