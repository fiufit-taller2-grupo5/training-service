#!/bin/sh
set -e

tag=$1
file=$2
global=$5

BUILDPARAMS=""

if [ ! -z "$OKTETO_CA_CERT" ]; then
   echo "Custom certificate is provided"
   echo "$OKTETO_CA_CERT" > /usr/local/share/ca-certificates/okteto_ca_cert.crt
   update-ca-certificates
fi

params=$(eval echo --progress plain -t "$tag" -f "$file")

if [ "$global" = "true" ]; then
    params="${params} --global"
fi

params=$(eval echo "$params")

echo running: okteto build $params
okteto build $params
echo build completed successfully
# print files of directory
ls -la
okteto deploy -f okteto.yml
