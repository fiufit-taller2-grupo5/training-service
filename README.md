# Training Service

Microservice for managing trainings

## Running Locally

It has `user-service` as a dependency, so if you are running it without Docker, you should check user-service is running first.

The ideal way to run this project locally is with docker compose. Using the command:

`docker compose up --build` in the project `development-setup`, everything should run fine if the ports are not used.

However, if you want to run this project locally without docker you can do it with the following steps:

1. `pip install --no-cache-dir -r requirements.txt`
2. `uvicorn server:app  --port {port_number}`

Note: You need to have python3 installed in your machine, version 3.10 is recommended.

## Project Structure

The project is structured in the following way:

- firebase: Contains logic related to firebase storage
- models: Contains the models used in the project
- services: Contains service layer logic, such as recommendation system and user-service communication
- Dal: Contains data access layer logic, such as database queries
- Controller: Contains the controller logic, receives the request with the defined endpoints here

## Documentation and Endpoints

You can access `https://api-gateway-prod2-szwtomas.cloud.okteto.net/training-service/docs` to see all endpoints and their documentation.

Good Luck!
