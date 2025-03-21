const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const log = require('electron-log');
const isDev = require('electron-is-dev');

let mainWindow;
let djangoProcess = null;
let serverReady = false;

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'info';

// Set executable name based on platform
const djangoExeName = process.platform === 'win32' ? 'django_app.exe' : 'django_app';

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    show: true
  });

  // Load the loading screen first
  mainWindow.loadFile(path.join(__dirname, 'loading.html'));

  mainWindow.webContents.on('did-fail-load', (e, code, desc) => {
    log.error(`Failed to load: ${code} - ${desc}`);
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Start Django server and then load the actual content
  startDjangoServer();

  return mainWindow;
}

function findExecutableRecursively(dir, maxDepth = 3, currentDepth = 0) {
  if (currentDepth > maxDepth) return null;
  
  log.info(`Searching in directory: ${dir} (depth: ${currentDepth})`);
  
  if (!fs.existsSync(dir)) {
    log.error(`Directory does not exist: ${dir}`);
    return null;
  }
  
  try {
    // First check if executable exists directly in this directory
    const execPath = path.join(dir, djangoExeName);
    if (fs.existsSync(execPath)) {
      log.info(`Found executable at: ${execPath}`);
      return execPath;
    }
    
    // Then look in subdirectories
    const items = fs.readdirSync(dir, { withFileTypes: true });
    for (const item of items) {
      if (item.isDirectory()) {
        const subPath = path.join(dir, item.name);
        const result = findExecutableRecursively(subPath, maxDepth, currentDepth + 1);
        if (result) return result;
      }
    }
  } catch (err) {
    log.error(`Error reading directory ${dir}:`, err);
  }
  
  return null;
}

function startDjangoServer() {
  log.info('App ready, starting Django server...');
  
  const projectRoot = path.resolve(__dirname, '..');
  log.info(`Project root: ${projectRoot}`);
  
  let searchPath;
  let djangoExecutable;
  
  if (isDev) {
    // Development mode
    searchPath = path.join(projectRoot, 'corrugated_box_mfg', 'dist');
    log.info(`Development search path: ${searchPath}`);
    djangoExecutable = 'python'; // Use Python directly in dev mode
  } else {
    // Production mode
    searchPath = process.resourcesPath ? 
      path.join(process.resourcesPath, 'django_app') : 
      path.join(projectRoot, 'resources', 'django_app');
    
    log.info(`Production search path: ${searchPath}`);
    djangoExecutable = findExecutableRecursively(searchPath);
    
    // If not found in resources, try dist folder (for testing the build locally)
    if (!djangoExecutable) {
      const altPath = path.join(projectRoot, 'dist', 'win-unpacked', 'resources', 'django_app');
      log.info(`Trying alternative path: ${altPath}`);
      djangoExecutable = findExecutableRecursively(altPath);
    }
  }
  
  // Log all possible paths we might look in
  if (!isDev) {
    const possiblePaths = [
      path.join(searchPath, djangoExeName),
      path.join(searchPath, 'django_app', djangoExeName),
      process.resourcesPath && path.join(process.resourcesPath, djangoExeName),
      process.resourcesPath && path.join(process.resourcesPath, 'django_app', djangoExeName)
    ].filter(Boolean);
    
    log.info('Possible executable paths:');
    possiblePaths.forEach(p => {
      log.info(`  ${p} - exists: ${fs.existsSync(p)}`);
    });
  }
  
  // Check if we found the executable
  if (!djangoExecutable) {
    const errorMsg = `Could not find Django executable in ${searchPath}`;
    log.error(errorMsg);
    dialog.showErrorBox('Django Error', errorMsg);
    return;
  }
  
  log.info(`Found Django executable: ${djangoExecutable}`);
  
  // Set execute permissions on Unix systems
  if (!isDev && process.platform !== 'win32') {
    try {
      fs.chmodSync(djangoExecutable, '755');
      log.info('Set executable permissions');
    } catch (err) {
      log.error('Failed to set executable permissions:', err);
    }
  }
  
  // Configure the process
  const args = isDev ? ['manage.py', 'runserver'] : [];
  const cwd = isDev 
    ? path.join(projectRoot, 'corrugated_box_mfg')
    : path.dirname(djangoExecutable);
  
  const env = {
    ...process.env,
    PYTHONUNBUFFERED: '1',
    NODE_ENV: isDev ? 'development' : 'production'
  };
  
  log.info(`Starting Django process: ${djangoExecutable} ${args.join(' ')} in ${cwd}`);
  
  try {
    djangoProcess = spawn(djangoExecutable, args, { 
      cwd: cwd,
      env: env,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    
    log.info(`Django process started with PID: ${djangoProcess.pid}`);
    
    djangoProcess.stdout.on('data', (data) => {
      const message = data.toString();
      log.info(`Django: ${message}`);
      
      // Check for server ready state
      if (message.includes('Starting development server at') || 
          message.includes('Starting server')) {
        log.info('Django server is ready. Loading application...');
        setTimeout(() => {
          if (mainWindow) {
            mainWindow.loadURL('http://localhost:8000');
          }
        }, 2000);
      }
    });
    
    djangoProcess.stderr.on('data', (data) => {
      log.error(`Django error: ${data.toString()}`);
    });
    
    djangoProcess.on('error', (err) => {
      log.error(`Django process error: ${err.message}`);
      dialog.showErrorBox('Django Error', `Failed to start Django server: ${err.message}`);
    });
    
    djangoProcess.on('exit', (code) => {
      log.info(`Django process exited with code ${code}`);
      if (code !== 0) {
        dialog.showErrorBox('Django Server Error', 
          `The Django server exited unexpectedly with code ${code}`);
      }
    });
  } catch (error) {
    log.error(`Failed to spawn Django process: ${error.message}`);
    dialog.showErrorBox('Django Error', `Error starting Django server: ${error.message}`);
  }
}

function cleanup() {
  log.info('Cleaning up...');
  if (djangoProcess) {
    try {
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', djangoProcess.pid, '/f', '/t']);
      } else {
        process.kill(djangoProcess.pid);
      }
      log.info('Django process terminated');
    } catch (err) {
      log.error(`Error killing Django process: ${err.message}`);
    }
  }
}

app.on('ready', createMainWindow);

app.on('window-all-closed', () => {
  cleanup();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', cleanup);

app.on('activate', () => {
  if (mainWindow === null) {
    createMainWindow();
  }
});

process.on('uncaughtException', (error) => {
  log.error(`Uncaught exception: ${error.message}`);
  log.error(error.stack);
  dialog.showErrorBox('Uncaught Exception', error.message);
});
