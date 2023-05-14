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

  it("POST training review", async () => {

    const trainer = await authedRequest(
      request(apiGatewayHost)
        .post('/user-service/api/users')
        .set('dev', 'true')
        .send({
          name: 'trainer',
          email: 'trainer@mail.com'
        })
    );

    const user = await authedRequest(
      request(apiGatewayHost)
        .post('/user-service/api/users')
        .set('dev', 'true')
        .send({
          name: 'user',
          email: 'user@mail.com'
        })
    );


    const users = await authedRequest(
      request(apiGatewayHost)
        .get(`/user-service/api/users`)
        .set('dev', 'true')
    );

    const trainerId = users.body[0].id;
    const userId = users.body[1].id;

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
          trainerId: trainerId
        })
    );

    const trainingId = response.body.id;

    const review = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/${userId}`)
        .set('dev', 'true')
        .send({
          score: 5,
          comment: 'Test comment'
        })
    );

    expect(review.statusCode).to.be.equal(200);
    expect(review.body).to.have.property('userId', userId);
    expect(review.body).to.have.property('trainingPlanId', trainingId);
    expect(review.body).to.have.property('score', 5);
    expect(review.body).to.have.property('comment', 'Test comment');
  });

  it("GET training reviews", async () => {
    const trainer = await authedRequest(
      request(apiGatewayHost)
        .post('/user-service/api/users')
        .set('dev', 'true')
        .send({
          name: 'trainer',
          email: 'trainer@mail.com'
        })
    );

    const user1 = await authedRequest(
      request(apiGatewayHost)
        .post('/user-service/api/users')
        .set('dev', 'true')
        .send({
          name: 'user1',
          email: 'user1@mail.com'
        })
    );

    const user2 = await authedRequest(
      request(apiGatewayHost)
        .post('/user-service/api/users')
        .set('dev', 'true')
        .send({
          name: 'user2',
          email: 'user2@mail.com'
        })
    );

    const users = await authedRequest(
      request(apiGatewayHost)
        .get(`/user-service/api/users`)
        .set('dev', 'true')
    );

    const trainerId = users.body[0].id;
    const userId1 = users.body[1].id;
    const userId2 = users.body[2].id;

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
          trainerId: trainerId
        })
    );

    const trainingId = response.body.id;

    const review = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/${userId1}`)
        .set('dev', 'true')
        .send({
          score: 5,
          comment: 'Test comment'
        })
    );

    const review2 = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/${userId2}`)
        .set('dev', 'true')
        .send({
          score: 2,
          comment: 'Test comment'
        })
    );

    const reviews = await authedRequest(
      request(apiGatewayHost)
        .get(`/training-service/api/trainings/${trainingId}/reviews`)
        .set('dev', 'true')
    );

    expect(reviews.statusCode).to.be.equal(200);
    expect(reviews.body).to.have.lengthOf(2);
    expect(reviews.body[0]).to.have.property('userId', userId1);
    expect(reviews.body[0]).to.have.property('trainingPlanId', trainingId);
    expect(reviews.body[0]).to.have.property('score', 5);
    expect(reviews.body[0]).to.have.property('comment', 'Test comment');
    expect(reviews.body[1]).to.have.property('userId', userId2);
    expect(reviews.body[1]).to.have.property('trainingPlanId', trainingId);
    expect(reviews.body[1]).to.have.property('score', 2);
    expect(reviews.body[1]).to.have.property('comment', 'Test comment');

  });

  it("POST invalid training review", async () => {
    const trainer = await authedRequest(
      request(apiGatewayHost)
        .post('/user-service/api/users')
        .set('dev', 'true')
        .send({
          name: 'trainer',
          email: 'trainer@mail.com'
        })
    );

    const user1 = await authedRequest(
      request(apiGatewayHost)
        .post('/user-service/api/users')
        .set('dev', 'true')
        .send({
          name: 'user1',
          email: 'user1@mail.com'
        })
    );

    const user2 = await authedRequest(
      request(apiGatewayHost)
        .post('/user-service/api/users')
        .set('dev', 'true')
        .send({
          name: 'user2',
          email: 'user2@mail.com'
        })
    );

    const users = await authedRequest(
      request(apiGatewayHost)
        .get(`/user-service/api/users`)
        .set('dev', 'true')
    );

    const trainerId = users.body[0].id;
    const userId1 = users.body[1].id;
    const userId2 = users.body[2].id;

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
          trainerId: trainerId
        })
    );

    const trainingId = response.body.id;


    // not puting valid training 
    const review = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/40000/review/${userId1}`)
        .set('dev', 'true')
        .send({
          score: 5,
          comment: 'Test comment'
        })
    );

    expect(review.statusCode).to.be.equal(404);
    expect(review.body).to.have.property('message', 'Training plan not found');


    // not puting valid user
    const review2 = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/40000`)
        .set('dev', 'true')
        .send({
          score: 5,
          comment: 'Test comment'
        })
    );

    expect(review2.statusCode).to.be.equal(404);
    expect(review2.body).to.have.property('message', 'User not found');


    // not puting valid score
    const review3 = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/${userId1}`)
        .set('dev', 'true')
        .send({
          score: 6,
          comment: 'Test comment'
        })
    );

    expect(review3.statusCode).to.be.equal(400);
    expect(review3.body).to.have.property('message', 'Score must be between 1 and 5');

    // missing score
    const review4 = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/${userId1}`)
        .set('dev', 'true')
        .send({
          comment: 'Test comment'
        })
    );

    expect(review4.statusCode).to.be.equal(400);
    expect(review4.body).to.have.property('message', 'Missing required fields (user_id, training_plan_id or score))');

    // trainer cannot review his own training
    const review5 = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/${trainerId}`)
        .set('dev', 'true')
        .send({
          score: 5,
          comment: 'Test comment'
        })
    );

    expect(review5.statusCode).to.be.equal(409);
    expect(review5.body).to.have.property('message', "Trainer can't review his own training plan");

  });


});