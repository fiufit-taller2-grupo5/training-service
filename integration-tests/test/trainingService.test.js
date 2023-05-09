const request = require('supertest');
const expect = require('chai').expect;
const { createConnection } = require('typeorm');
const { startDockerCompose, stopDockerCompose } = require('./dockerComposeManager');
const { describe, before, after, beforeEach } = require('mocha');

const apiGatewayHost = 'http://localhost:3000';

async function truncateTables() {
    const connection = await createConnection({
        type: 'postgres',
        host: 'localhost',
        port: 5434,
        username: 'postgres',
        password: '12345678',
        database: 'postgres',
        schema: 'training-service',
        synchronize: false,
    });

    const tables = ['TrainingPlan'];

    for (const table of tables) {
        await connection.query(`TRUNCATE TABLE "training-service"."${table}" CASCADE`);
    }

    await connection.close();
}

const isServiceHealthy = async (servicePath) => {
    try {
        console.log(`waiting for service ${servicePath} to be healthy`)
        const response = await request(apiGatewayHost)
            .get(servicePath)
            .set('dev', 'true');
        console.log(`service ${servicePath} response: ${response.statusCode}`)
        return response.statusCode === 200;
    } catch (error) {
        return false;
    }
};

const waitUntilServicesAreHealthy = async () => {
    const serviceHealthPaths = [
        '/user-service/health',
        '/training-service/health',
        '/health',
    ];

    let allServicesHealthy = false;

    while (!allServicesHealthy) {
        console.log('Checking services health...');
        const healthChecks = await Promise.all(
            serviceHealthPaths.map((path) => isServiceHealthy(path))
        );
        allServicesHealthy = healthChecks.every((check) => check);

        if (!allServicesHealthy) {
            console.log('Waiting for all services to be healthy...');
            await new Promise((resolve) => setTimeout(resolve, 5000));
        }
    }
};

describe('Integration Tests ', () => {


    const authedRequest = (request) => {
        return request.set('dev', 'true');
    }
    before(async () => {
        await startDockerCompose();
        await waitUntilServicesAreHealthy();
    });

    after(() => {
        return stopDockerCompose();
    });

    afterEach(async () => {
        await truncateTables();
    });

    it('GET health training service', async () => {
        const response = await authedRequest(
            request(apiGatewayHost)
                .get('/training-service/health'))

        expect(response.statusCode).to.be.equal(200);
    });
});