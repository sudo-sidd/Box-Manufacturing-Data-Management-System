const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let loadingWindow;
let djangoProcess;
let serverReady = false;

const isDev = process.env.NODE_ENV === 'development';

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
        // Improved path resolution with debug logging
        const projectRoot = path.join(__dirname, '..');
        console.log('Project root:', projectRoot);
        
        const djangoPath = isDev
            ? path.join(projectRoot, 'corrugated_box_mfg', 'dist', 'django_app')
            : path.join(process.resourcesPath, 'django_app');

        const executablePath = process.platform === 'win32' 
            ? `${djangoPath}.exe` 
            : djangoPath;

        console.log('Django path:', djangoPath);
        console.log('Executable path:', executablePath);
        console.log('Path exists:', fs.existsSync(executablePath));
        
        // Check if file exists
        if (!fs.existsSync(executablePath)) {
            // List directory contents for debugging
            const dir = path.dirname(executablePath);
            if (fs.existsSync(dir)) {
                console.log('Directory contents:', fs.readdirSync(dir));
            } else {
                console.log('Directory does not exist:', dir);
            }
            throw new Error(`Django executable not found at: ${executablePath}`);
        }

        // Make file executable on Unix systems
        if (process.platform !== 'win32') {
            fs.chmodSync(executablePath, '755');
        }

        // Spawn process with more verbose logging
        console.log('Spawning Django process...');
        djangoProcess = spawn(executablePath, [], {
            stdio: ['ignore', 'pipe', 'pipe'],
            env: { 
                ...process.env, 
                PYTHONUNBUFFERED: '1',
                NODE_ENV: isDev ? 'development' : 'production'
            }
        });

        console.log('Process started with PID:', djangoProcess.pid);

        // Track server startup stages
        let migrationsComplete = false;
        let staticFilesCollected = false;

        djangoProcess.stdout.on('data', (data) => {
            const message = data.toString();
            console.log('Django stdout:', message);
            
            // Track migration completion
            if (message.includes('No migrations to apply.')) {
                migrationsComplete = true;
                console.log('Migrations completed');
            }
            
            // Track static files collection
            if (message.includes('static files copied')) {
                staticFilesCollected = true;
                console.log('Static files collected');
            }

            // Final server ready check
            if (migrationsComplete && staticFilesCollected) {
                console.log('All prerequisites complete, marking server as ready');
                serverReady = true;
            }
        });

        djangoProcess.stderr.on('data', (data) => {
            const message = data.toString();
            console.log('Django stderr:', message);
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
        console.error('Error starting Django server:', error);
        console.error('Stack trace:', error.stack);
        dialog.showErrorBox(
            'Startup Error',
            `Failed to start Django server: ${error.message}`
        );
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