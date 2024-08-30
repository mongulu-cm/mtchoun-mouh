#!/bin/bash
set -ex
container_name=lambda_docker
docker_image=aws_lambda_builder_image

docker build --tag $docker_image .

docker run -td --name=$container_name $docker_image
docker cp ../api/requirements.txt $container_name:/requirements.txt

docker exec -i $container_name /bin/bash < ./docker_install.sh
docker cp $container_name:/python.zip python.zip
docker stop $container_name
docker rm $container_name