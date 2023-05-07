# Set up

1. clona el repo en el mismo nivel de directorio que todos los otros repos
2. darle permisos de ejecución a los scripts (chmod +x ./*.sh)
3. ejecutar ./development-setup/clone-all-repos.sh desde dentro de la carpeta development-setup
4. ejecutar ./update-local-db-schema.sh --service <nombre de servicio, por ejemplo user-service> desde dentro de la carpeta de development-setup
5. ejecutar docker compose up para levantar los contenedores y ver los logs

# Correr tests

1. navegar a integration-tests/test
2. ejecutar ./run-tests.sh

esto levanta una db en memoria, le actualiza los esquemas y corre los tests

opcional
- cada vez que quieras actualizar todos los repos al mismo tiempo, ejecutar ./development-setup/pull-all-repos.sh desde dentro de la carpeta de development-setup
- cada vez que quieras hacer pushear en todos los repos al mismo tiempo, ejecutar ./development-setup/push-all-repos.sh desde dentro de la carpeta de development-setup


