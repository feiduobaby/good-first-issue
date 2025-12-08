import express from 'express';
import http from 'http';
import { Server as SocketIOServer } from 'socket.io';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';
import { fileURLToPath } from 'url';
import cors from 'cors';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const createSessionStore = () => new Map();

const createServer = () => {
  const app = express();
  const server = http.createServer(app);
  const io = new SocketIOServer(server, {
    cors: {
      origin: '*',
      methods: ['GET', 'POST'],
    },
  });

  const sessions = createSessionStore();

  app.use(cors());
  app.use(express.json());

  const createSession = () => ({
    code: '// Start coding here\n',
    language: 'javascript',
    createdAt: Date.now(),
  });

  app.post('/api/session', (req, res) => {
    const id = uuidv4();
    sessions.set(id, createSession());
    res.status(201).json({ id });
  });

  app.get('/api/session/:id', (req, res) => {
    const { id } = req.params;
    if (!sessions.has(id)) {
      sessions.set(id, createSession());
    }
    const session = sessions.get(id);
    res.json({ id, ...session });
  });

  // Serve the collaborative editor
  app.use(express.static(path.join(__dirname, 'public')));

  io.on('connection', (socket) => {
    socket.on('join-session', (sessionId) => {
      if (!sessionId) return;

      if (!sessions.has(sessionId)) {
        sessions.set(sessionId, createSession());
      }

      socket.join(sessionId);

      const session = sessions.get(sessionId);
      socket.emit('session-data', {
        code: session.code,
        language: session.language,
        createdAt: session.createdAt,
      });
    });

    socket.on('code-change', ({ sessionId, code }) => {
      if (!sessionId || !sessions.has(sessionId)) return;
      const session = sessions.get(sessionId);
      session.code = code;
      socket.to(sessionId).emit('code-change', { code });
    });

    socket.on('language-change', ({ sessionId, language }) => {
      if (!sessionId || !sessions.has(sessionId)) return;
      const session = sessions.get(sessionId);
      session.language = language;
      socket.to(sessionId).emit('language-change', { language });
    });
  });

  return { app, server, io };
};

const instance = createServer();

const PORT = process.env.PORT || 3000;
if (process.env.NODE_ENV !== 'test') {
  instance.server.listen(PORT, () => {
    console.log(`Server listening on http://localhost:${PORT}`);
  });
}

export const app = instance.app;
export const server = instance.server;
export const io = instance.io;
export default instance;

