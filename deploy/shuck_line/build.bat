sam validate

sam build --profile dev --use-container -b .aws-sam\build

sam package --s3-bucket algernonsolutions-layer-dev --template-file .aws-sam\build\template.yaml --profile dev --output-template-file .aws-sam\build\templated.yaml

sam publish --profile dev -t .aws-sam\build\templated.yaml
