FROM node:18-alpine

WORKDIR /app

COPY . .

RUN npm install prisma

RUN npm install

# todo change to prisma migrate
CMD ["npx", "prisma", "db", "push", "--force-reset"]
