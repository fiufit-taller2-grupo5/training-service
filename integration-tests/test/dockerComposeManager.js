const { promisify } = require('util');
const exec = promisify(require('child_process').exec);

const path = require('path');
const compose = require('docker-compose');

const dockerComposeFilePath = path.resolve(__dirname, './docker-test-compose.yml');

const { spawnSync } = require('child_process');
// const path = require('path');

async function startDockerCompose() {
    const dirPath = path.dirname(dockerComposeFilePath);
    const childProcess = spawnSync('sudo', ['docker-compose', 'up', '--build', '--abort-on-container-exit'], { stdio: 'inherit', cwd: dirPath });
    if (childProcess.status !== 0) {
        throw new Error(`docker-compose failed with exit code ${childProcess.status}`);
    }
    console.log('docker-compose completed successfully!');
}



async function stopDockerCompose() {
    try {
        await exec('sudo docker-compose down', { cwd: path.dirname(dockerComposeFilePath) });
        console.log('Docker Compose stopped successfully!');
    } catch (err) {
        console.error("Error Stopping Docker Compose: ", err.message);
        process.exit(1);
    }
}

module.exports = { startDockerCompose, stopDockerCompose };
