import request from 'supertest';
import { io as Client } from 'socket.io-client';
import { app, server } from '../server.js';

const connectClient = (url, sessionId) =>
  new Promise((resolve, reject) => {
    const client = new Client(url, {
      transports: ['websocket'],
      forceNew: true,
    });

    const timeout = setTimeout(() => reject(new Error('Socket connect timeout')), 5000);

    client.on('connect', () => {
      client.emit('join-session', sessionId);
    });

    client.on('session-data', () => {
      clearTimeout(timeout);
      resolve(client);
    });

    client.on('connect_error', reject);
  });

describe('integration: REST + realtime', () => {
  let port;

  beforeAll(async () => {
    await new Promise((resolve) => server.listen(0, resolve));
    port = server.address().port;
  });

  afterAll(async () => {
    await new Promise((resolve) => server.close(resolve));
  });

  test('creates and fetches a session', async () => {
    const createRes = await request(app).post('/api/session').expect(201);
    expect(createRes.body.id).toBeDefined();

    const fetchRes = await request(app).get(`/api/session/${createRes.body.id}`).expect(200);
    expect(fetchRes.body).toMatchObject({
      id: createRes.body.id,
      code: expect.any(String),
      language: 'javascript',
    });
  });

  test('broadcasts code and language changes between clients', async () => {
    const { body } = await request(app).post('/api/session').expect(201);
    const sessionId = body.id;
    const baseUrl = `http://localhost:${port}`;

    const clientA = await connectClient(baseUrl, sessionId);
    const clientB = await connectClient(baseUrl, sessionId);

    const codeUpdate = new Promise((resolve) => {
      clientB.on('code-change', resolve);
    });
    const languageUpdate = new Promise((resolve) => {
      clientB.on('language-change', resolve);
    });

    clientA.emit('code-change', { sessionId, code: 'console.log(42);' });
    clientA.emit('language-change', { sessionId, language: 'python' });

    await expect(codeUpdate).resolves.toEqual({ code: 'console.log(42);' });
    await expect(languageUpdate).resolves.toEqual({ language: 'python' });

    clientA.close();
    clientB.close();
  });
});

