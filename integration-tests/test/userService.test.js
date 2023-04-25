const request = require('supertest');
const apiGatewayHost = 'http://localhost:3000';

describe('API Gateway tests', () => {
  it('GET health user service', async () => {
    const response = await request(apiGatewayHost).get('/user-service/health');
    expect(response.statusCode).toBe(200);
  });

  // Add more tests for other endpoints
});