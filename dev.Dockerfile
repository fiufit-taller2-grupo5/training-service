# Use the official Node.js image as the base image
FROM node:18.13.0-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and yarn.lock to the working directory
COPY package.json yarn.lock ./

# Install the dependencies
RUN yarn install --pure-lockfile

COPY . .

RUN yarn build

# Expose the default Vite development server port
EXPOSE 3000

# Start the development server
CMD ["yarn", "dev"]
