const request = require('supertest');
const expect = require('chai').expect;
const { createConnection, Exclusion } = require('typeorm');
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

  it('complete POST training plan', async () => {
    await authedRequest(
      request(apiGatewayHost)
        .post('/user-service/api/users')
        .set('dev', 'true')
        .send({
          name: 'user',
          email: 'user@email.com',
        })
    );

    const response = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .set('dev', 'true')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: 1
        })
    );
    expect(response.statusCode).to.be.equal(200);
    expect(response.body).to.have.property('title', 'Test plan');
    expect(response.body).to.have.property('type', 'Running');
    const trainings = await authedRequest(
      request(apiGatewayHost)
        .get('/training-service/api/trainings')
        .set('dev', 'true')
    );
    expect(trainings.body).to.have.lengthOf(1);
    expect(trainings.body[0]).to.have.property('title', 'Test plan');
    expect(trainings.body[0]).to.have.property('type', 'Running');
  });
  it('GET training plan', async () => {
    const response = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .set('dev', 'true')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: 1
        })
    );

    const trainingId = response.body.id;
    const training = await authedRequest(
      request(apiGatewayHost)
        .get(`/training-service/api/trainings/${trainingId}`)
        .set('dev', 'true')
    );
    expect(training.statusCode).to.be.equal(200);
    expect(training.body).to.have.property('title', 'Test plan');
    expect(training.body).to.have.property('type', 'Running');
  });

  it('GET training plan not found', async () => {
    const training = await authedRequest(
      request(apiGatewayHost)
        .get(`/training-service/api/trainings/1`)
        .set('dev', 'true')
    );
    console.log(training);
    expect(training.statusCode).to.be.equal(404);
    expect(training.body).to.have.property('message', 'Training with id 1 does not exist');
  });


  it('GET training plans', async () => {
    const response = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .set('dev', 'true')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: 1
        })
    );

    const response2 = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .set('dev', 'true')
        .send({
          title: 'Test plan 2',
          type: 'Swimming',
          description: 'Test description',
          difficulty: 2,
          state: 'active',
          trainerId: 1
        })
    );

    const trainings = await authedRequest(
      request(apiGatewayHost)
        .get('/training-service/api/trainings')
        .set('dev', 'true')
    );
    expect(trainings.statusCode).to.be.equal(200);
    expect(trainings.body).to.have.lengthOf(2);
    expect(trainings.body[0]).to.have.property('title', 'Test plan');
    expect(trainings.body[0]).to.have.property('type', 'Running');

    expect(trainings.body[1]).to.have.property('title', 'Test plan 2');
    expect(trainings.body[1]).to.have.property('type', 'Swimming');
  });

  it('POST user favorite trainings', async () => {
    const response = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .set('dev', 'true')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: 1
        })
    );

    const users = await authedRequest(
      request(apiGatewayHost)
        .get('/user-service/api/users')
        .set('dev', 'true')
    );

    const trainingId = response.body.id;
    const userId = users.body[0].id;

    const favorite = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/favorite/${userId}`)
        .set('dev', 'true')
    );

    expect(favorite.statusCode).to.be.equal(200);
    expect(favorite.body).to.have.property('userId', userId);
    expect(favorite.body).to.have.property('trainingPlanId', trainingId);
  });


  it('GET user favorite trainings', async () => {
    const training1 = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .set('dev', 'true')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: 1
        })
    );

    const training2 = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .set('dev', 'true')
        .send({
          title: 'Test plan 2',
          type: 'Swimming',
          description: 'Test description 2',
          difficulty: 4,
          state: 'active',
          trainerId: 1
        })
    );

    const trainingId1 = training1.body.id;
    const trainingId2 = training2.body.id;

    let res = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId1}/favorite/1`)
        .set('dev', 'true')
    );
    expect(res.statusCode).to.be.equal(200);
    expect(res.body).to.have.property('userId', 1);
    expect(res.body).to.have.property('trainingPlanId', trainingId1);

    res = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId2}/favorite/1`)
        .set('dev', 'true')
    );

    expect(res.statusCode).to.be.equal(200);
    expect(res.body).to.have.property('userId', 1);
    expect(res.body).to.have.property('trainingPlanId', trainingId2);

    const favorites = await authedRequest(
      request(apiGatewayHost)
        .get(`/training-service/api/trainings/favorites/1`)
        .set('dev', 'true')
    );
    expect(favorites.statusCode).to.be.equal(200);
    console.log(favorites);
    expect(favorites.body).to.have.lengthOf(2);
    expect(favorites.body[0]).to.have.property('title', 'Test plan');
    expect(favorites.body[0]).to.have.property('type', 'Running');
    expect(favorites.body[1]).to.have.property('title', 'Test plan 2');
    expect(favorites.body[1]).to.have.property('type', 'Swimming');
  });
});