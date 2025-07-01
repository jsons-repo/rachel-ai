// rachel-view/scripts/gen-config.ts

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

function getPythonPath(): string {
    // 🧠 Go up to project root: ../..
    const projectRoot = path.resolve(__dirname, '..', '..');

    // 🧠 1. Explicit venv fallback
    const fallbackVenvPython = path.join(projectRoot, 'venv', 'bin', 'python');
    if (fs.existsSync(fallbackVenvPython)) return fallbackVenvPython;

    // 🧠 2. Environment-based venv
    if (process.env.VIRTUAL_ENV) {
        const venvPython = path.join(process.env.VIRTUAL_ENV, 'bin', 'python');
        if (fs.existsSync(venvPython)) return venvPython;
    }

    // 🧠 3. Fallback to system python
    const tryWhich = (cmd: string) => spawnSync('which', [cmd]).stdout.toString().trim();
    for (const cmd of ['python', 'python3']) {
        const sysPath = tryWhich(cmd);
        if (sysPath && fs.existsSync(sysPath)) return sysPath;
    }

    return '';
}

const pythonCmd = getPythonPath();

if (!pythonCmd || !fs.existsSync(pythonCmd)) {
    console.error('❌ No valid Python interpreter found in VIRTUAL_ENV or system PATH.');
    process.exit(1);
}

const result = spawnSync(pythonCmd, ['../src/rachel/scripts/export_fe_config.py'], {
    stdio: 'inherit',
    cwd: path.resolve(__dirname, '..'),
    env: {
        ...process.env,
        PYTHONPATH: path.resolve(__dirname, '..', '..', 'src'),
    },
});






if (result.status !== 0) {
    console.error('❌ Failed to run configvalues.py');
    console.error('💡 Try running: `source venv/bin/activate` before running frontend build');
    process.exit(result.status || 1);
}
