FROM node:18.13.0-alpine

WORKDIR /app

COPY . .

RUN npm install prisma

# todo change to prisma migrate!
CMD ["npx", "prisma", "db", "push", "--force-reset"]
