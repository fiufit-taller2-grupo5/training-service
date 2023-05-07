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
    const response = await request(apiGatewayHost)
      .get('/user-service/health')
      .set('dev', 'true'); // add this line to set the Authorization header

    expect(response.statusCode).to.be.equal(200);
  });

  it('POST user', async () => {
    const response = await request(apiGatewayHost)
      .post('/user-service/api/users')
      .send({
        name: 'test',
        email: 'test@email.com',
      }).set('dev', 'true');

    expect(response.statusCode).to.be.equal(200);


    const response2 = await request(apiGatewayHost)
      .get('/user-service/api/users')
      .set('dev', 'true');

    expect(response2.statusCode).to.be.equal(200);
    expect(response2.body.length).to.be.equal(1);
    expect(response2.body[0].name).to.be.equal('test');
  });


  it('GET non-existent user', async () => {
    const response = await request(apiGatewayHost)
      .get('/user-service/api/users/123')
      .set('dev', 'true');

    expect(response.statusCode).to.be.equal(404);
  });

  it('POST user with missing fields', async () => {
    const response = await request(apiGatewayHost)
      .post('/user-service/api/users')
      .send({
        name: 'test'
      })
      .set('dev', 'true');

    expect(response.statusCode).to.be.equal(400);
    expect(response.body.error).to.be.equal('Missing name or email');
  });

  it('POST user with used email', async () => {
    const postResponse = await request(apiGatewayHost)
      .post('/user-service/api/users')
      .send({
        name: 'test',
        email: 'test@mail'
      })
      .set('dev', 'true');

    expect(postResponse.statusCode).to.be.equal(200);
    const postResponse2 = await request(apiGatewayHost)
      .post('/user-service/api/users')
      .send({
        name: 'test2',
        email: 'test@mail'
      })
      .set('dev', 'true');

    expect(postResponse2.statusCode).to.be.equal(409);
    expect(postResponse2.body.error).to.be.equal('User with email test@mail already exists');
  });

  it('User with name used', async () => {
    const postResponse = await request(apiGatewayHost)
      .post('/user-service/api/users')
      .send({
        name: 'test',
        email: 'test@mail'
      })
      .set('dev', 'true');

    expect(postResponse.statusCode).to.be.equal(200);
    const postResponse2 = await request(apiGatewayHost)
      .post('/user-service/api/users')
      .send({
        name: 'test',
        email: 'test2@mail'
      })
      .set('dev', 'true');
    expect(postResponse2.statusCode).to.be.equal(409);
    expect(postResponse2.body.error).to.be.equal('User with name test already exists');

  });

  it('DELETE user', async () => {
    const postResponse = await request(apiGatewayHost)
      .post('/user-service/api/users')
      .send({
        name: 'test',
        email: 'test@email.com',
      })
      .set('dev', 'true');

    expect(postResponse.statusCode).to.be.equal(200);

    const users = await request(apiGatewayHost)
      .get('/user-service/api/users')
      .set('dev', 'true');

    const userId = users.body[0].id;

    const deleteResponse = await request(apiGatewayHost)
      .delete(`/user-service/api/users/${userId}`)
      .set('dev', 'true');


    const getResponse = await request(apiGatewayHost)
      .get(`/user-service/api/users/${userId}`)
      .set('dev', 'true');

    expect(getResponse.statusCode).to.be.equal(404);
  });

});

// antes de todo levantar compose y depsues de todo bajarlo 
// dsp por cada est borrar la ifno en la base de datos
// hay un metodo hay uno que es before/after each (como hago para eso? una query que borre los datos de todas las tablas que hay en la base de datos)
    // ojo con el tema de tner dos schemas, habria que ver lso dos y nada eso basicamente

// hacer un docker compose de test 
// que se diferencie por no montar los volumenes a la base de datos postgress, asi no tiene mapeados cosas en lo local simplmeente se prende y apaga cuando se corre este dc
