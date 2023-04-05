FROM okteto/okteto:latest

COPY entrypoint.sh /entrypoint.sh
COPY okteto.yml /okteto.yml
COPY kubernetes /kubernetes

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"] 