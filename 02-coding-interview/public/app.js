const languageMode = {
  javascript: 'text/javascript',
  python: 'text/x-python',
  java: 'text/x-java',
  cpp: 'text/x-c++src',
};

const statusEl = document.getElementById('status');
const languageSelect = document.getElementById('language-select');
const outputEl = document.getElementById('output');
const runBtn = document.getElementById('run-btn');
const shareBtn = document.getElementById('share-btn');
const clearBtn = document.getElementById('clear-output');

let sessionId = new URLSearchParams(window.location.search).get('session') || null;
let suppressBroadcast = false;
let runnerFrame = null;
let quickjsReady = null;
let pyodideReady = null;

async function getQuickJS() {
  if (!quickjsReady) {
    if (!window.quickjs || typeof window.quickjs.getQuickJS !== 'function') {
      throw new Error('QuickJS WASM not loaded');
    }
    quickjsReady = window.quickjs.getQuickJS();
  }
  return quickjsReady;
}

async function getPyodide() {
  if (!pyodideReady) {
    if (typeof window.loadPyodide !== 'function') {
      throw new Error('Pyodide WASM not loaded');
    }
    pyodideReady = window
      .loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/',
      })
      .then((pyodide) => {
        pyodide.setStdout({ batched: (s) => appendOutput('log', s.trim()) });
        pyodide.setStderr({ batched: (s) => appendOutput('error', s.trim()) });
        return pyodide;
      });
  }
  return pyodideReady;
}

const editor = CodeMirror(document.getElementById('editor'), {
  value: '// Loading session...\n',
  mode: languageMode.javascript,
  theme: 'default',
  lineNumbers: true,
  autoCloseBrackets: true,
  tabSize: 2,
});

const socket = io();

function setStatus(text) {
  statusEl.textContent = text;
}

function setLanguage(language) {
  languageSelect.value = language;
  editor.setOption('mode', languageMode[language] || 'javascript');
}

async function createSession() {
  const res = await fetch('/api/session', { method: 'POST' });
  const data = await res.json();
  return data.id;
}

async function loadSession(id) {
  const res = await fetch(`/api/session/${id}`);
  const data = await res.json();
  return data;
}

async function ensureSession() {
  if (!sessionId) {
    sessionId = await createSession();
    const url = new URL(window.location.href);
    url.searchParams.set('session', sessionId);
    window.history.replaceState({}, '', url.toString());
  }
  const session = await loadSession(sessionId);
  setLanguage(session.language);
  editor.setValue(session.code || '');
}

function appendOutput(type, message) {
  const prefix = type === 'error' ? '⚠️ ' : '▶ ';
  outputEl.textContent += `${prefix}${message}\n`;
  outputEl.scrollTop = outputEl.scrollHeight;
}

function clearRunner() {
  if (runnerFrame) {
    runnerFrame.remove();
    runnerFrame = null;
  }
}

async function runJsWithQuickJs(code) {
  appendOutput('log', 'Running with QuickJS (WASM) ...');
  try {
    const quickjs = await getQuickJS();
    const vm = quickjs.createVm();

    const logFn = vm.newFunction('log', (...args) => {
      const rendered = args.map((arg) => vm.dump(arg)).join(' ');
      appendOutput('log', rendered);
    });

    const errorFn = vm.newFunction('error', (...args) => {
      const rendered = args.map((arg) => vm.dump(arg)).join(' ');
      appendOutput('error', rendered);
    });

    const consoleObj = vm.newObject();
    vm.setProp(consoleObj, 'log', logFn);
    vm.setProp(consoleObj, 'error', errorFn);
    vm.setProp(vm.global, 'console', consoleObj);

    const result = vm.evalCode(code);
    if (result.error) {
      appendOutput('error', vm.dump(result.error));
      result.error.dispose();
    } else if (result.value) {
      const value = vm.dump(result.value);
      if (value !== undefined) appendOutput('log', String(value));
      result.value.dispose();
    }

    logFn.dispose();
    errorFn.dispose();
    consoleObj.dispose();
    vm.dispose();
  } catch (err) {
    appendOutput('error', err?.message || String(err));
  }
}

async function runPythonWithPyodide(code) {
  appendOutput('log', 'Running with Pyodide (WASM) ...');
  try {
    const pyodide = await getPyodide();
    const result = await pyodide.runPythonAsync(code);
    if (result !== undefined) {
      appendOutput('log', String(result));
    }
  } catch (err) {
    appendOutput('error', err?.message || String(err));
  }
}

async function runCode(language, code) {
  clearRunner();
  if (language === 'javascript') {
    return runJsWithQuickJs(code);
  }
  if (language === 'python') {
    return runPythonWithPyodide(code);
  }
  appendOutput('error', `Execution for ${language} not supported in-browser.`);
}

socket.on('connect', async () => {
  setStatus('Connected');
  await ensureSession();
  socket.emit('join-session', sessionId);
});

socket.on('disconnect', () => setStatus('Disconnected'));

socket.on('session-data', ({ code, language }) => {
  suppressBroadcast = true;
  editor.setValue(code || '');
  setLanguage(language || 'javascript');
  suppressBroadcast = false;
});

socket.on('code-change', ({ code }) => {
  suppressBroadcast = true;
  editor.setValue(code);
  suppressBroadcast = false;
});

socket.on('language-change', ({ language }) => setLanguage(language));

editor.on('change', () => {
  if (suppressBroadcast || !sessionId) return;
  const code = editor.getValue();
  socket.emit('code-change', { sessionId, code });
});

languageSelect.addEventListener('change', (e) => {
  const language = e.target.value;
  setLanguage(language);
  if (sessionId) {
    socket.emit('language-change', { sessionId, language });
  }
});

runBtn.addEventListener('click', () => {
  runCode(languageSelect.value, editor.getValue());
});

shareBtn.addEventListener('click', async () => {
  const url = new URL(window.location.href);
  if (!sessionId) {
    sessionId = await createSession();
    url.searchParams.set('session', sessionId);
  }
  try {
    await navigator.clipboard.writeText(url.toString());
    setStatus('Link copied!');
  } catch {
    setStatus('Copy failed. Share the URL manually.');
  }
});

clearBtn.addEventListener('click', () => {
  outputEl.textContent = '';
  clearRunner();
});

window.addEventListener('message', (event) => {
  if (!event.data?.type) return;
  appendOutput(event.data.type, event.data.payload);
});

