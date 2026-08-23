const { app, BrowserWindow } = require("electron");
const { spawn } = require("child_process");
const http = require("http");
const path = require("path");
const fs = require("fs");

const VITE_DEV_SERVER_URL = "http://localhost:5173";
const BACKEND_HEALTH_URL = "http://127.0.0.1:8000/api/health";

let backendProcess = null;

// packaged renderer logs land here since uvicorn output is swallowed
function logLine(message) {
  try {
    fs.appendFileSync(path.join(app.getPath("temp"), "betsim-packaged.log"), `${new Date().toISOString()} ${message}\n`);
  } catch {
    // best effort only
  }
}

function waitForHttp(url, retries = 40, delayMs = 500) {
  return new Promise((resolve) => {
    const attempt = (remaining) => {
      const req = http.get(url, (res) => {
        res.resume();
        resolve(true);
      });
      req.on("error", () => {
        if (remaining <= 0) {
          resolve(false);
        } else {
          setTimeout(() => attempt(remaining - 1), delayMs);
        }
      });
    };
    attempt(retries);
  });
}

/**
 * When packaged, the exe lives at <repo>/release/win-unpacked/Betsim.exe, so
 * the repo root is two levels up from the app dir. If a sibling .venv exists
 * we spawn uvicorn ourselves so the packaged exe is a single-launch full
 * stack. Sentinel's CDP sandbox passes --user-data-dir; pointing
 * BETSIM_DB_PATH inside it gives every sandboxed run a fresh database.
 * No .venv -> degrade gracefully (renderer shows "Backend unreachable").
 */
function userDataDirFromArgv() {
  const flag = process.argv.findIndex((a) => a === "--user-data-dir");
  if (flag !== -1 && process.argv[flag + 1]) return process.argv[flag + 1];
  const inline = process.argv.find((a) => a.startsWith("--user-data-dir="));
  return inline ? inline.split("=").slice(1).join("=") : null;
}

function startPackagedBackend() {
  // exe lives at <repo>/release/win-unpacked/Betsim.exe -> repo root is two
  // levels up from the exe dir (NOT from __dirname, which is inside app.asar)
  const exeDir = path.dirname(app.getPath("exe"));
  const repoRoot = path.resolve(exeDir, "..", "..");
  const python = path.join(repoRoot, ".venv", "Scripts", "python.exe");
  const backendDir = path.join(repoRoot, "backend");
  if (!fs.existsSync(python) || !fs.existsSync(backendDir)) return false;

  const env = { ...process.env };
  const sandbox = userDataDirFromArgv();
  if (sandbox && fs.existsSync(sandbox)) {
    env.BETSIM_DB_PATH = path.join(sandbox, "betsim.db");
  }

  backendProcess = spawn(
    python,
    ["-m", "uvicorn", "main:app", "--port", "8000", "--app-dir", backendDir],
    { cwd: repoRoot, env, stdio: "ignore", windowsHide: true },
  );
  backendProcess.on("error", (err) => {
    logLine(`backend spawn failed: ${err.message}`);
    backendProcess = null;
  });
  backendProcess.on("exit", () => {
    backendProcess = null;
  });
  return true;
}

function httpGet(url) {
  return new Promise((resolve) => {
    const req = http.get(url, { timeout: 1500 }, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => resolve({ status: res.statusCode, body: data }));
    });
    req.on("timeout", () => {
      req.destroy();
      resolve(null);
    });
    req.on("error", () => resolve(null));
  });
}

/** Identity of whatever serves :8000 — "Betsim API", some foreign title, or
 * null when nothing answers. Guards against foreign backends squatting the
 * port (real incident: Career OS's orphaned server made every betsim tab
 * fail while /api/health looked "healthy"). */
async function portIdentity() {
  const response = await httpGet("http://127.0.0.1:8000/openapi.json");
  if (!response || response.status !== 200) return null;
  try {
    return JSON.parse(response.body)?.info?.title ?? "unknown";
  } catch {
    return "unknown";
  }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Ensure OUR backend serves :8000. Reuses an existing healthy instance;
 * spawns one otherwise. Returns "reused" | "spawned" | "foreign" | "failed".
 */
async function ensureBackend() {
  let spawned = false;
  for (let i = 0; i < 60; i++) {
    const identity = await portIdentity();
    if (identity === "Betsim API") return spawned ? "spawned" : "reused";
    if (!spawned && identity !== null) {
      // foreign server holds the port - spawning would fail with EADDRINUSE
      logLine(`port 8000 occupied by "${identity}"; not ours`);
      return "foreign";
    }
    if (!spawned) {
      startPackagedBackend();
      spawned = true;
    }
    await sleep(500);
  }
  logLine("backend did not become healthy in time");
  return spawned ? "spawned" : "failed";
}

function stopBackend() {
  if (backendProcess !== null) {
    if (process.platform === "win32") {
      // negative-PID process.kill() is POSIX-only; on Windows it no-ops and
      // leaves orphaned uvicrons squatting on :8000 (real incident)
      spawn("taskkill", ["/PID", String(backendProcess.pid), "/T", "/F"], {
        stdio: "ignore",
        windowsHide: true,
      });
    } else {
      try {
        process.kill(-backendProcess.pid);
      } catch {
        // already gone
      }
    }
    backendProcess = null;
  }
}

async function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  if (app.isPackaged) {
    const outcome = await ensureBackend();
    logLine(`backend: ${outcome}`);
    try {
      await win.loadFile(path.join(__dirname, "dist", "index.html"));
      logLine("renderer loaded");
    } catch (err) {
      logLine(`loadFile failed: ${err.message}`);
    }
  } else {
    await waitForHttp(VITE_DEV_SERVER_URL);
    win.loadURL(VITE_DEV_SERVER_URL).catch(() => {
      win.loadURL("data:text/html,<h1>Betsim: Vite dev server not reachable</h1>");
    });
  }
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  stopBackend();
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
