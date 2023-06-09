#!/bin/sh
set -e

tag=$1
file=$2
sha=$3
okteto_yml=$4
k8s_deploment_file=$5
OPENAI_KEY=$6

if [ ! -z "$OKTETO_CA_CERT" ]; then
   echo "Custom certificate is provided"
   echo "$OKTETO_CA_CERT" > /usr/local/share/ca-certificates/okteto_ca_cert.crt
   update-ca-certificates
fi

params=$(eval echo --progress plain -t "$tag" -f "$file")

params=$(eval echo "$params")

echo running: okteto build $params --build-arg OPENAI_KEY=$OPENAI_KEY

okteto build $params --build-arg OPENAI_KEY=$OPENAI_KEY

echo build completed successfully

# replace the word latest with the tag of the image in the /kubernetes/deployment.yml file
sed -i "s|latest|$sha|g" $k8s_deploment_file

okteto deploy -f $okteto_yml