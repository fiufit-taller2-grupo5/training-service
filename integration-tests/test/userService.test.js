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
        schema: 'user-service',
        synchronize: false,
    });

    const tables = ['User'];

    for (const table of tables) {
        await connection.query(`TRUNCATE TABLE "user-service"."${table}" CASCADE`);
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

    it('GET health user service', async () => {
        const response = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/health'))

        expect(response.statusCode).to.be.equal(200);
    });

    it('POST user', async () => {
        await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/users')
                .send({
                    name: 'test',
                    email: 'test@email.com',
                }))


        const response = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/api/users')
        )

        expect(response.statusCode).to.be.equal(200);
        expect(response.body.length).to.be.equal(1);
        expect(response.body[0].name).to.be.equal('test');
    });


    it('GET non-existent user', async () => {
        const response = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/api/users/123')
        )

        expect(response.statusCode).to.be.equal(404);
    });

    it('POST user with missing fields', async () => {
        const response = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/users')
                .send({
                    name: 'test'
                })
        );

        expect(response.statusCode).to.be.equal(400);
        expect(response.body.error).to.be.equal('Missing name or email');
    });

    it('POST user with used email', async () => {
        await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/users')
                .send({
                    name: 'test',
                    email: 'test@mail'
                }));

        const postResponse = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/users')
                .send({
                    name: 'test2',
                    email: 'test@mail'
                }));

        expect(postResponse.statusCode).to.be.equal(409);
        expect(postResponse.body.error).to.be.equal('Email already in use');
    });


    it('DELETE user', async () => {
        const postResponse = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/users')
                .send({
                    name: 'test',
                    email: 'test@email.com',
                }));

        expect(postResponse.statusCode).to.be.equal(200);

        const users = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/api/users'));


        const userId = users.body[0].id;

        await await authedRequest(
            request(apiGatewayHost)
                .delete(`/user-service/api/users/${userId}`));

        const getResponse = await authedRequest(
            request(apiGatewayHost)
                .get(`/user-service/api/users/${userId}`));

        expect(getResponse.statusCode).to.be.equal(404);

    });

    it('POST new Admin', async () => {


        // create new admin with email and password with header test=true
        const postResponse = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/admins')
                .send({
                    name: 'test',
                    email: 'test@mail',
                    password: 'test'
                }).set('test', 'true'));

        expect(postResponse.statusCode).to.be.equal(200);


        const response = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/api/admins')
        )

        expect(response.statusCode).to.be.equal(200);
        expect(response.body.length).to.be.equal(1);
        expect(response.body[0].name).to.be.equal('test');
        expect(response.body[0].email).to.be.equal('test@mail');
    });




    it('GET non-existent admin', async () => {
        const response = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/api/admins/123')
        )

        expect(response.statusCode).to.be.equal(404);
    });

    it('POST admin with missing fields', async () => {
        const response = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/admins')
                .send({
                    name: 'test'
                }).set('test', 'true'));


        expect(response.statusCode).to.be.equal(400);
        expect(response.body.error).to.be.equal('Missing name or email');
    });

    it('POST admin with used email', async () => {
        await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/admins')
                .send({
                    name: 'test',
                    email: 'test@mail'
                }).set('test', 'true'));

        const postResponse = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/admins')
                .send({
                    name: 'test',
                    email: 'test@mail'
                }).set('test', 'true'));

        expect(postResponse.statusCode).to.be.equal(409);
        expect(postResponse.body.error).to.be.equal('Email already in use');
    });


    it('DELETE admin', async () => {
        const postResponse = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/admins')
                .send({
                    name: 'test',
                    email: 'test@email.com',
                }).set('test', 'true'));

        expect(postResponse.statusCode).to.be.equal(200);

        const users = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/api/admins'));


        const userId = users.body[0].id;

        await await authedRequest(
            request(apiGatewayHost)
                .delete(`/user-service/api/admins/${userId}`));

        const getResponse = await authedRequest(
            request(apiGatewayHost)
                .get(`/user-service/api/admins/${userId}`));

        expect(getResponse.statusCode).to.be.equal(404);
    });

    // change metadata in user 
    it('PUT user', async () => {
        const postResponse = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/users')
                .send({
                    name: 'test',
                    email: 'test@mail'
                }
                ));

        const users = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/api/users'));

        const userId = users.body[0].id;

        const putResponse = await authedRequest(
            request(apiGatewayHost)
                .put(`/user-service/api/users/${userId}/metadata`)
                .send({
                    name: 'test2',
                    email: 'test2@mail',
                    location: 'test'
                }));

        const getResponse = await authedRequest(
            request(apiGatewayHost)
                .get(`/user-service/api/users/${userId}/metadata`));

        expect(getResponse.statusCode).to.be.equal(200);
        expect(getResponse.body.location).to.be.equal('test');
    });

    it('PUT user with invalid id', async () => {
        const putResponse = await authedRequest(
            request(apiGatewayHost)
                .put(`/user-service/api/users/123/metadata`)
                .send({
                    name: 'test2',
                    email: 'test2@mail',
                    location: 'test'
                }));
        expect(putResponse.statusCode).to.be.equal(404);
        expect(putResponse.body.error).to.be.equal('User not found');
    });

    it('PUT user with invalid metadata, location missing', async () => {
        const postResponse = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/users')
                .send({
                    name: 'test',
                    email: 'test@mail'
                }
                ));
        const users = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/api/users'));

        const userId = users.body[0].id;
        const putResponse = await authedRequest(
            request(apiGatewayHost)
                .put(`/user-service/api/users/${userId}/metadata`)
                .send({
                    name: 'test2',
                    email: 'test2@mail'
                }));

        expect(putResponse.statusCode).to.be.equal(400);
        expect(putResponse.body.error).to.be.equal('Missing location');
    });

    it('GET user with entire information', async () => {
        const postResponse = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/users')
                .send({
                    name: 'test',
                    email: 'test@mail'
                }
                ));
        const users = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/api/users'));

        const userId = users.body[0].id;
        const putResponse = await authedRequest(
            request(apiGatewayHost)
                .put(`/user-service/api/users/${userId}/metadata`)
                .send({
                    location: 'test'
                }));

        const getResponse = await authedRequest(
            request(apiGatewayHost)
                .get(`/user-service/api/users/${userId}`));

        expect(getResponse.statusCode).to.be.equal(200);
        expect(getResponse.body.name).to.be.equal('test');
        expect(getResponse.body.email).to.be.equal('test@mail');
        expect(getResponse.body.UserMetadata.location).to.be.equal('test');

    });

    it('GET user with metadata in null', async () => {
        const postResponse = await authedRequest(
            request(apiGatewayHost)
                .post('/user-service/api/users')
                .send({
                    name: 'test',
                    email: 'test@mail'
                }
                ));
        const users = await authedRequest(
            request(apiGatewayHost)
                .get('/user-service/api/users'));

        const userId = users.body[0].id;
        const getResponse = await authedRequest(
            request(apiGatewayHost)
                .get(`/user-service/api/users/${userId}`));

        expect(getResponse.statusCode).to.be.equal(200);
        expect(getResponse.body.name).to.be.equal('test');
        expect(getResponse.body.email).to.be.equal('test@mail');
        expect(getResponse.body.UserMetadata).to.be.equal(null);
    });
});
