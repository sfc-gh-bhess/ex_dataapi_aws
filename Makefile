all: build

clean:
	- rm -rf .aws-sam/*

build: template.yaml
	sam build --use-container

deploy:
	sam deploy --capabilities CAPABILITY_NAMED_IAM --guided
