# Set up

1. clona el repo en el mismo nivel de directorio que todos los otros repos
2. darle permisos de ejecución a los scripts (chmod +x ./*.sh)
3. ejecutar ./development-setup/clone-all-repos.sh desde fuera de la carpeta de development-setup
4. ```docker compose up```
5. ir a user-service y temporalmente cambiar postgres-service por localhost en la uri ejecutar ```yarn && npx prisma db push``` cada vez que haya que actualizar los esquemas de la db. 

cambiar de: DATABASE_URL="postgresql://postgres:12345678@postgres-service:5432/postgres?schema=public&connection_timeout=20"
a : DATABASE_URL="postgresql://postgres:12345678@localhost:5432/postgres?schema=public&connection_timeout=20"

revertir el cambio luego de ejecutar el comando

opcional
- cada vez que quieras actualizar todos los repos al mismo tiempo, ejecutar ./development-setup/pull-all-repos.sh desde fuera de la carpeta de development-setup
- cada vez que quieras hacer pushear en todos los repos al mismo tiempo, ejecutar ./development-setup/push-all-repos.sh desde fuera de la carpeta de development-setup


