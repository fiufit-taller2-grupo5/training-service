// const request = require('supertest');
// const expect = require('chai').expect;
// const { startDockerCompose, stopDockerCompose } = require('./dockerComposeManager');
// const apiGatewayHost = 'http://localhost:3000';

// const { execSync } = require('child_process');
// const { describe, beforeEach, afterEach, it, beforeAll, afterAll } = require('mocha');

// const axios = require('axios');


// const waitOn = require('wait-on');

// describe('Integration Tests ', () => {
//   // before(async () => {
//   //   await startDockerCompose();
//   //   // wait 10 seconds 

//   //   // await new Promise(resolve => setTimeout(resolve, 10000));
//   // });

//   // after(async () => {
//   //   await stopDockerCompose();
//   // });


//   before(async () => {
//     // Execute docker-compose up --build before all tests
//     execSync('sudo docker-compose up --build -d', { stdio: 'inherit' });
//     // Wait until the containers are ready
//     // Start the containers in detached mode
//     execSync('sudo docker-compose up --build -d', { stdio: 'inherit' });

//     // Wait until all services are ready
//     let isReady = false;
//     const services = ['training-service', 'user-service', 'admin-frontend', 'api-gateway'];
//     while (!isReady) {
//       try {
//         // Check if all services are running
//         const output = execSync('sudo docker ps', { encoding: 'utf-8' });
//         const isRunning = services.every(service => output.includes(service));
//         if (isRunning) {
//           isReady = true;
//         } else {
//           console.log('Waiting for all services to start...');
//           // Wait for a few seconds before checking again
//           setTimeout(() => { }, 100000);
//         }
//       } catch (err) {
//         // The containers are not ready yet
//         console.log('Waiting for all services to start...');
//         // Wait for a few seconds before checking again
//         setTimeout(() => { }, 100000);
//       }
//     }
//     console.log('All services are ready!');
//   });
//   // after(async () => {
//   //   // Execute docker-compose down after all tests
//   //   execSync('sudo docker-compose down', { stdio: 'inherit' });
//   // });


//   // let originalData = null;

//   // const storeOriginalData = async () => {
//   //   const response = await request(apiGatewayHost)
//   //     .get('/user-service/api/users')
//   //     .set('dev', 'true');
//   //   originalData = response.body;
//   // };


//   // const restoreOriginalData = async () => {
//   //   for (const user of originalData) {
//   //     await request(apiGatewayHost)
//   //       .post('/user-service/api/users')
//   //       .send(user)
//   //       .set('dev', 'true');
//   //   }
//   // };

//   // afterEach(async () => {
//   //   await request(apiGatewayHost)
//   //     .delete('/user-service/api/users')
//   //     .set('dev', 'true');
//   //   await restoreOriginalData();
//   // });

//   // beforeEach(async () => {
//   //   await storeOriginalData();
//   //   await request(apiGatewayHost)
//   //     .delete('/user-service/api/users')
//   //     .set('dev', 'true');
//   // });


//   it('GET health user service', async () => {
//     const response = await request(apiGatewayHost)
//       .get('/user-service/health-check')
//       .set('dev', 'true'); // add this line to set the Authorization header

//     expect(response.statusCode).to.be.equal(200);
//   });

//   it('POST user', async () => {
//     const response = await request(apiGatewayHost)
//       .post('/user-service/api/users')
//       .send({
//         name: 'test',
//         email: 'test@email.com',
//       }).set('dev', 'true');;

//     expect(response.statusCode).to.be.equal(200);


//     const response2 = await request(apiGatewayHost)
//       .get('/user-service/api/users')
//       .set('dev', 'true');

//     expect(response2.statusCode).to.be.equal(200);
//     expect(response2.body.length).to.be.equal(1);
//     expect(response2.body[0].name).to.be.equal('test');
//   });


//   it('GET non-existent user', async () => {
//     const response = await request(apiGatewayHost)
//       .get('/user-service/api/users/123')
//       .set('dev', 'true');

//     expect(response.statusCode).to.be.equal(404);
//   });

//   it('POST user with missing fields', async () => {
//     const response = await request(apiGatewayHost)
//       .post('/user-service/api/users')
//       .send({
//         name: 'test'
//       })
//       .set('dev', 'true');

//     expect(response.statusCode).to.be.equal(400);
//     expect(response.body.error).to.be.equal('Missing name or email');
//   });

//   it('POST user with used email', async () => {
//     const postResponse = await request(apiGatewayHost)
//       .post('/user-service/api/users')
//       .send({
//         name: 'test',
//         email: 'test@mail'
//       })
//       .set('dev', 'true');

//     expect(postResponse.statusCode).to.be.equal(200);
//     const postResponse2 = await request(apiGatewayHost)
//       .post('/user-service/api/users')
//       .send({
//         name: 'test2',
//         email: 'test@mail'
//       })
//       .set('dev', 'true');

//     expect(postResponse2.statusCode).to.be.equal(409);
//     expect(postResponse2.body.error).to.be.equal('User with email test@mail already exists');
//   });

//   it('User with name used', async () => {
//     const postResponse = await request(apiGatewayHost)
//       .post('/user-service/api/users')
//       .send({
//         name: 'test',
//         email: 'test@mail'
//       })
//       .set('dev', 'true');

//     expect(postResponse.statusCode).to.be.equal(200);
//     const postResponse2 = await request(apiGatewayHost)
//       .post('/user-service/api/users')
//       .send({
//         name: 'test',
//         email: 'test2@mail'
//       })
//       .set('dev', 'true');
//     expect(postResponse2.statusCode).to.be.equal(409);
//     expect(postResponse2.body.error).to.be.equal('User with name test already exists');

//   });

//   it('DELETE user', async () => {
//     const postResponse = await request(apiGatewayHost)
//       .post('/user-service/api/users')
//       .send({
//         name: 'test',
//         email: 'test@email.com',
//       })
//       .set('dev', 'true');

//     expect(postResponse.statusCode).to.be.equal(200);

//     const users = await request(apiGatewayHost)
//       .get('/user-service/api/users')
//       .set('dev', 'true');

//     const userId = users.body[0].id;

//     const deleteResponse = await request(apiGatewayHost)
//       .delete(`/user-service/api/users/${userId}`)
//       .set('dev', 'true');


//     const getResponse = await request(apiGatewayHost)
//       .get(`/user-service/api/users/${userId}`)
//       .set('dev', 'true');

//     expect(getResponse.statusCode).to.be.equal(404);
//   });

// });

// // antes de todo levantar compose y depsues de todo bajarlo 
// // dsp por cada est borrar la ifno en la base de datos
// // hay un metodo hay uno que es before/after each (como hago para eso? una query que borre los datos de todas las tablas que hay en la base de datos)
//     // ojo con el tema de tner dos schemas, habria que ver lso dos y nada eso basicamente

// // hacer un docker compose de test 
// // que se diferencie por no montar los volumenes a la base de datos postgress, asi no tiene mapeados cosas en lo local simplmeente se prende y apaga cuando se corre este dc
