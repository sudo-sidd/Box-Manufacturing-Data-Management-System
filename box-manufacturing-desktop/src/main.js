const { app, BrowserWindow, dialog } = require('electron')
const path = require('path')
const { PythonShell } = require('python-shell')
const fs = require('fs')

let mainWindow
let djangoServer
let serverReady = false

function findPythonPath() {
    const venvPath = path.join(__dirname, '../corrugated_box_mfg/venv')
    const possiblePaths = [
        path.join(venvPath, 'bin', 'python'),
        path.join(venvPath, 'Scripts', 'python.exe'),
        '/home/drackko/.pyenv/versions/3.13.1/bin/python'
    ]

    for (const pythonPath of possiblePaths) {
        if (fs.existsSync(pythonPath)) {
            console.log('Found Python at:', pythonPath)
            return pythonPath
        }
    }

    throw new Error('Python executable not found')
}

function startDjangoServer() {
    console.log('Starting Django server...')
    
    try {
        const pythonPath = findPythonPath()
        const options = {
            mode: 'text',
            pythonPath: pythonPath,
            pythonOptions: ['-u'],
            scriptPath: path.join(__dirname, '../corrugated_box_mfg'),
            args: ['runserver', '127.0.0.1:8000'],
            env: {
                ...process.env,
                PYTHONUNBUFFERED: '1',
                DJANGO_SETTINGS_MODULE: 'box_mfg.settings'
            }
        }

        console.log('Python path:', options.pythonPath)
        console.log('Script path:', options.scriptPath)

        djangoServer = new PythonShell('manage.py', options)

        djangoServer.on('message', function (message) {
            console.log('Django server message:', message)
            // Update condition to match actual Django output
            if (message.includes('Watching for file changes with StatReloader')) {
                console.log('Django server is ready')
                serverReady = true
            }
        })

        djangoServer.on('stderr', function (stderr) {
            console.error('Django server error:', stderr)
            // Consider stderr messages as potential startup indicators
            if (stderr.includes('Watching for file changes with StatReloader')) {
                console.log('Django server is ready (from stderr)')
                serverReady = true
            }
        })

        djangoServer.on('error', function (err) {
            console.error('Failed to start Django server:', err)
            dialog.showErrorBox(
                'Server Error',
                `Failed to start Django server: ${err.message}`
            )
        })

        djangoServer.on('close', function (code, signal) {
            console.log('Django server closed with code:', code)
            if (code !== 0) {
                dialog.showErrorBox(
                    'Server Closed',
                    `Django server closed unexpectedly with code ${code}`
                )
            }
        })

    } catch (error) {
        console.error('Error starting Django server:', error)
        dialog.showErrorBox(
            'Startup Error',
            `Failed to start Django server: ${error.message}`
        )
    }
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        show: false
    })

    mainWindow.loadFile(path.join(__dirname, 'loading.html'))
    mainWindow.show()

    // Add timeout for server startup
    let startupTimeout = setTimeout(() => {
        if (!serverReady) {
            dialog.showErrorBox(
                'Server Timeout',
                'Django server failed to start within expected time'
            )
        }
    }, 10000)

    const checkServer = setInterval(() => {
        if (serverReady) {
            clearInterval(checkServer)
            clearTimeout(startupTimeout)
            mainWindow.loadURL('http://127.0.0.1:8000')
        }
    }, 1000)

    mainWindow.on('closed', function () {
        mainWindow = null
    })
}

app.on('ready', () => {
    startDjangoServer()
    createWindow()
})

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

app.on('activate', function () {
    if (mainWindow === null) {
        createWindow()
    }
})

app.on('will-quit', () => {
    if (djangoServer) {
        djangoServer.end((err, code, signal) => {
            if (err) console.log('Error shutting down Django server:', err)
        })
    }
})
