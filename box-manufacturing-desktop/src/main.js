const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const log = require('electron-log');
const isDev = require('electron-is-dev');

let mainWindow;
let loadingWindow;
let djangoProcess;
let serverReady = false;

const djangoExeName = process.platform === 'win32' ? 'django_app.exe' : 'django_app';

function createLoadingWindow() {
    try {
        loadingWindow = new BrowserWindow({
            width: 400,
            height: 300,
            frame: false,
            center: true, // Center the loading window
            webPreferences: {
                nodeIntegration: true
            }
        });
        loadingWindow.loadFile(path.join(__dirname, 'loading.html'));
        
        loadingWindow.on('closed', () => {
            loadingWindow = null;
        });
    } catch (error) {
        console.error('Error creating loading window:', error);
    }
}

function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        show: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    // Check if server is ready before loading URL
    const checkServerAndLoad = () => {
        if (serverReady) {
            mainWindow.loadURL('localhost:8000');
            mainWindow.show();
            if (loadingWindow) {
                loadingWindow.close();
            }
        } else {
            setTimeout(checkServerAndLoad, 1000);
        }
    };

    checkServerAndLoad();

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

function startDjangoServer() {
    console.log('Starting Django server...');
    
    try {
        const djangoPath = isDev
            ? path.join(__dirname, '..', 'corrugated_box_mfg', djangoExeName)
            : path.join(process.resourcesPath, 'django_app', djangoExeName);

        log.info(`Starting Django server from: ${djangoPath}`);
        
        djangoProcess = spawn(djangoPath);
        
        djangoProcess.stdout.on('data', (data) => {
            log.info(`Django: ${data}`);
        });
        
        djangoProcess.stderr.on('data', (data) => {
            log.error(`Django Error: ${data}`);
        });
        
        djangoProcess.on('close', (code) => {
            log.info(`Django process exited with code ${code}`);
        });

        // Set timeout to prevent infinite loading
        setTimeout(() => {
            if (!serverReady) {
                console.error('Server startup timeout');
                dialog.showErrorBox(
                    'Startup Error',
                    'Django server failed to start within timeout period'
                );
                app.quit();
            }
        }, 30000);

    } catch (error) {
        log.error('Failed to start Django server:', error);
    }
}

function cleanup() {
    if (loadingWindow) {
        loadingWindow.close();
        loadingWindow = null;
    }
    if (djangoProcess) {
        djangoProcess.kill('SIGTERM');
    }
}

app.on('ready', () => {
    createLoadingWindow();
    startDjangoServer();
    createMainWindow();
});

app.on('window-all-closed', function () {
    cleanup();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', function () {
    if (mainWindow === null) {
        createMainWindow();
    }
});

app.on('will-quit', () => {
    if (djangoProcess) {
        djangoProcess.kill('SIGTERM');
        
        setTimeout(() => {
            if (djangoProcess) {
                djangoProcess.kill('SIGKILL');
            }
        }, 5000);
    }
});