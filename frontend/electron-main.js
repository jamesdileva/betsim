const { app, BrowserWindow } = require("electron");
const http = require("http");

const VITE_DEV_SERVER_URL = "http://localhost:5173";

function waitForDevServer(url, retries = 60, delayMs = 500) {
  return new Promise((resolve) => {
    const attempt = (remaining) => {
      const req = http.get(url, () => resolve(true));
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

async function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  if (process.env.VITE_DEV_SERVER_URL || !app.isPackaged) {
    await waitForDevServer(VITE_DEV_SERVER_URL);
    win.loadURL(VITE_DEV_SERVER_URL).catch(() => {
      win.loadURL("data:text/html,<h1>Betsim: Vite dev server not reachable</h1>");
    });
  }
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
