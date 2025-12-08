# Collaborative Coding Interview Platform

Real-time code interview sandbox with sharable rooms, multi-language syntax highlighting, and safe in-browser JavaScript execution.

## Features
- Create and share session links for candidates.
- Collaborative code editing with Socket.IO syncing.
- Syntax highlighting for JS, Python, Java, and C++ (via CodeMirror).
- Sandbox JS execution in-browser (iframe + sandbox).

## Prerequisites
- Node.js 18+ (tested with Node 22)
- npm

## Install
```bash
cd /Users/zhangxiaoyu/wk2
npm install
```

## Run the app
```bash
npm start
# open http://localhost:3000
```

## Development (concurrent client + server)
```bash
npm run dev
# server: http://localhost:3000
# client static server (live reload): http://localhost:5173
```

## Docker
```bash
docker build -t coding-interview .
docker run -p 3000:3000 coding-interview
# then open http://localhost:3000
```

## Tests
Integration tests exercise REST + Socket.IO interactions.
```bash
npm test
```

## Project structure
- `server.js` – Express + Socket.IO server and session API.
- `public/` – Frontend (CodeMirror editor, runtime sandbox).
- `__tests__/integration.test.js` – end-to-end interaction tests.

## Notes
- In-memory session store; replace with Redis/DB for production.
- JavaScript executes client-side via QuickJS (WASM); Python executes via Pyodide (WASM); other languages are highlight-only.

