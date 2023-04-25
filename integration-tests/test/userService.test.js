const request = require('supertest');
const expect = require('chai').expect;
const apiGatewayHost = 'http://localhost:3000';

describe('Health Check test', () => {
  it('GET health user service', async () => {
    const response = await request(apiGatewayHost)
      .get('/user-service/health-check')
      .set('dev', 'true'); // add this line to set the Authorization header

    expect(response.statusCode).to.be.equal(200);
  });

  // Add more tests for other endpoints
});

