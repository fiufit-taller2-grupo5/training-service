const request = require('supertest');
const expect = require('chai').expect;
const { createConnection, Exclusion } = require('typeorm');
const { startDockerCompose, stopDockerCompose } = require('./dockerComposeManager');
const { describe, before, after, beforeEach } = require('mocha');

const apiGatewayHost = 'http://localhost:3000';

const authedRequest = (request) => {
  return request.set('dev-email', 'test-athlete@mail.com');
}

async function truncateTables() {
  let connection = await createConnection({
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

  connection = await createConnection({
    type: 'postgres',
    host: 'localhost',
    port: 5434,
    username: 'postgres',
    password: '12345678',
    database: 'postgres',
    schema: 'training-service',
    synchronize: false,
  });

  await connection.query(`TRUNCATE TABLE "user-service"."User" CASCADE`);

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

  let testUser;
  let testUser2;
  let testTrainer;


  before(async () => {
    await startDockerCompose();
    await waitUntilServicesAreHealthy();
  });

  after(() => {
    return stopDockerCompose();
  });

  beforeEach(async () => {
    const response = await request(apiGatewayHost)
      .post('/user-service/api/users')
      .set('dev', 'true')
      .send({
        name: 'test athlete',
        email: 'test-athlete@mail.com',
      })

    testUser = response.body;

    const response2 = await request(apiGatewayHost)
      .post('/user-service/api/users')
      .set('dev', 'true')
      .send({
        name: 'test athlete 2',
        email: 'test-athlete-2@mail.com',
      })

    testUser2 = response2.body;

    const response3 = await request(apiGatewayHost)
      .post('/user-service/api/users')
      .set('dev', 'true')
      .send({
        name: 'test trainer',
        email: 'test-trainer@mail.com',
      })

    testTrainer = response3.body;
    console.log("the test trainer:", testTrainer)
    console.log("the test user:", testUser)
    console.log("the test user2:", testUser2)
  })

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
    const response = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );
    expect(response.statusCode).to.be.equal(200);
    expect(response.body).to.have.property('title', 'Test plan');
    expect(response.body).to.have.property('type', 'Running');
    const trainings = await authedRequest(
      request(apiGatewayHost)
        .get('/training-service/api/trainings')
    );
    expect(trainings.body).to.have.lengthOf(1);
    expect(trainings.body[0]).to.have.property('title', 'Test plan');
    expect(trainings.body[0]).to.have.property('type', 'Running');
  });
  it('GET training plan', async () => {
    const response = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );
    console.log("the response:", response.body)
    const trainingId = response.body.id;
    const training = await authedRequest(
      request(apiGatewayHost)
        .get(`/training-service/api/trainings/${trainingId}`)
    );
    expect(training.statusCode).to.be.equal(200);
    expect(training.body).to.have.property('title', 'Test plan');
    expect(training.body).to.have.property('type', 'Running');

  });

  it('GET training plan not found', async () => {
    const training = await authedRequest(
      request(apiGatewayHost)
        .get(`/training-service/api/trainings/1`)
    );
    console.log("the training:", training)
    expect(training.statusCode).to.be.equal(404);
    expect(training.body).to.have.property('message', 'Training plan not found');
  });


  it('GET training plans', async () => {
    const response = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const response2 = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan 2',
          type: 'Swimming',
          description: 'Test description',
          difficulty: 2,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const trainings = await authedRequest(
      request(apiGatewayHost)
        .get('/training-service/api/trainings')
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
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const users = await authedRequest(
      request(apiGatewayHost)
        .get('/user-service/api/users')
    );

    const trainingId = response.body.id;
    const userId = users.body[0].id;

    const favorite = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/favorite/${testUser.id}`)
    );

    expect(favorite.statusCode).to.be.equal(200);
    expect(favorite.body).to.have.property('userId', testUser.id);
    expect(favorite.body).to.have.property('trainingPlanId', trainingId);
  });


  it('GET user favorite trainings', async () => {
    const training1 = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const training2 = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan 2',
          type: 'Swimming',
          description: 'Test description 2',
          difficulty: 4,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const trainingId1 = training1.body.id;
    const trainingId2 = training2.body.id;

    let res = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId1}/favorite/1`)
    );
    expect(res.statusCode).to.be.equal(200);
    expect(res.body).to.have.property('userId', 1);
    expect(res.body).to.have.property('trainingPlanId', trainingId1);

    res = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId2}/favorite/1`)
    );

    expect(res.statusCode).to.be.equal(200);
    expect(res.body).to.have.property('userId', 1);
    expect(res.body).to.have.property('trainingPlanId', trainingId2);

    const favorites = await authedRequest(
      request(apiGatewayHost)
        .get(`/training-service/api/trainings/favorites/1`)
    );
    expect(favorites.statusCode).to.be.equal(200);
    expect(favorites.body).to.have.lengthOf(2);
    expect(favorites.body[0]).to.have.property('title', 'Test plan');
    expect(favorites.body[0]).to.have.property('type', 'Running');
    expect(favorites.body[1]).to.have.property('title', 'Test plan 2');
    expect(favorites.body[1]).to.have.property('type', 'Swimming');
  });

  it("POST training review", async () => {

    const response = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const trainingId = response.body.id;

    const review = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/${testUser.id}`)
        .send({
          score: 5,
          comment: 'Test comment'
        })
    );

    console.log("the review1 response:", review.body);
    expect(review.statusCode).to.be.equal(200);
    expect(review.body).to.have.property('userId', testUser.id);
    expect(review.body).to.have.property('trainingPlanId', trainingId);
    expect(review.body).to.have.property('score', 5);
    expect(review.body).to.have.property('comment', 'Test comment');
  });

  it("GET training reviews", async () => {

    const response = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const trainingId = response.body.id;

    const review = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/${testUser.id}`)
        .send({
          score: 5,
          comment: 'Test comment'
        })
    );

    console.log("the review1 response:", review.body);

    const review2 = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/${testUser2.id}`)
        .send({
          score: 2,
          comment: 'Test comment'
        })
    );
    console.log("re reviewer 2", testUser2)
    console.log("the review2 response:", review2.body);

    const reviews = await authedRequest(
      request(apiGatewayHost)
        .get(`/training-service/api/trainings/${trainingId}/reviews`)
    );

    expect(reviews.statusCode).to.be.equal(200);
    expect(reviews.body).to.have.lengthOf(2);
    expect(reviews.body[0]).to.have.property('userId', testUser.id);
    expect(reviews.body[0]).to.have.property('trainingPlanId', trainingId);
    expect(reviews.body[0]).to.have.property('score', 5);
    expect(reviews.body[0]).to.have.property('comment', 'Test comment');
    expect(reviews.body[1]).to.have.property('userId', testUser2.id);
    expect(reviews.body[1]).to.have.property('trainingPlanId', trainingId);
    expect(reviews.body[1]).to.have.property('score', 2);
    expect(reviews.body[1]).to.have.property('comment', 'Test comment');
  });

  it("POST invalid training review", async () => {
    const response = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const trainingId = response.body.id;

    // not puting valid training 
    const review = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/40000/review/${testUser.id}`)
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
        .post(`/training-service/api/trainings/${trainingId}/review/${testUser.id}`)
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
        .post(`/training-service/api/trainings/${trainingId}/review/${testUser.id}`)
        .send({
          comment: 'Test comment'
        })
    );

    expect(review4.statusCode).to.be.equal(400);
    expect(review4.body).to.have.property('message', 'Missing required fields (user_id, training_plan_id or score))');

    // trainer cannot review his own training
    const review5 = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${trainingId}/review/${testTrainer.id}`)
        .send({
          score: 5,
          comment: 'Test comment'
        })
    );

    expect(review5.statusCode).to.be.equal(409);
    expect(review5.body).to.have.property('message', "Trainer can't review his own training plan");
  });

  it("POST user training", async () => {

    const training = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const response = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${training.body.id}/user_training/${testUser.id}`)
        .send(
          {
            "distance": 15,
            "calories": 15,
            "duration": 15,
            "date": 15,
            "steps": 15
          }
        )
    );

    console.log("the response!:", response.body)
    expect(response.statusCode).to.be.equal(200);
    expect(response.body).to.have.property('userId', testUser.id);
    expect(response.body).to.have.property('distance', 15);

  });

  it("POST invalid user training", async () => {
    const training = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const response = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${training.body.id}/user_training/${testUser.id}`)
        .send(
          {
            "distance": -8,
            "calories": -8,
            "duration": -8,
            "date": -8,
            "steps": -8
          }
        )
    );

    expect(response.statusCode).to.be.equal(400);
    expect(response.body).to.have.property('message', 'Distance, duration, steps and calories must be positive');

    // const response2 = await authedRequest(
    //   request(apiGatewayHost)
    //     .post(`/training-service/api/trainings/${training.body.id}/user_training/4000`)
    //     .send(
    //       {
    //         "distance": 1,
    //         "calories": 1,
    //         "duration": 1,
    //         "date": 1,
    //         "steps": 1
    //       }
    //     )
    // );

    // expect(response2.statusCode).to.be.equal(400);
    // expect(response2.body).to.have.property('message', 'User not found');

    const response3 = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${training.body.id}/user_training/${testUser.id}`)
        .send(
          {
          }
        )
    );

    expect(response3.statusCode).to.be.equal(400);
    expect(response3.body).to.have.property('message', 'Missing required fields (distance, duration, steps, calories or date)');


    // const response4 = await authedRequest(
    //   request(apiGatewayHost)
    //     .post(`/training-service/api/trainings/${training.body.id}/user_training/4000`)
    //     .send(
    //       {
    //         "distance": -8,
    //         "calories": -8,
    //         "duration": -8,
    //         "date": -8,
    //         "steps": -8,
    //         "trainingPlanId": 155555
    //       }
    //     )
    // );

    // expect(response4.statusCode).to.be.equal(404);
    // expect(response4.body).to.have.property('message', 'Training plan not found');
  });

  it("GET user trainings", async () => {

    const training = await authedRequest(
      request(apiGatewayHost)
        .post('/training-service/api/trainings')
        .send({
          title: 'Test plan',
          type: 'Running',
          description: 'Test description',
          difficulty: 1,
          state: 'active',
          trainerId: testTrainer.id
        })
    );

    const training_session1 = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${training.body.id}/user_training/${testUser.id}`)
        .send(
          {
            "distance": 20,
            "calories": 15,
            "duration": 15,
            "date": 15,
            "steps": 15
          }
        )
    );

    const training_session2 = await authedRequest(
      request(apiGatewayHost)
        .post(`/training-service/api/trainings/${training.body.id}/user_training/${testUser.id}`)
        .send(
          {
            "distance": 10,
            "calories": 15,
            "duration": 15,
            "date": 15,
            "steps": 15
          }
        )
    );

    const response = await authedRequest(
      request(apiGatewayHost)
        .get(`/training-service/api/trainings/${training.body.id}/user_training/${testUser.id}`)
    );

    console.log("what? really?:", response.body);
    // expect(response.statusCode).to.be.equal(200);
    // expect(response.body).to.be.an('array');
    // expect(response.body).to.have.lengthOf(2);
    // expect(response.body[0]).to.have.property('distance', 20);
    // expect(response.body[1]).to.have.property('distance', 10);
  });


});