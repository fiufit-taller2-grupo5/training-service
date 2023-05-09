const path = require("path");
const compose = require('docker-compose');

const composeFilePath = path.join(__dirname);

console.log(composeFilePath);
const { exec } = require("child_process");

async function startDockerCompose() {
    console.log("Building images...");
    
    return compose
        .buildAll({
            cwd: composeFilePath,
            log: true,
            config: "docker-test-compose.yml"
        })
        .then(
            () => {
                console.log("Done building images.");
                console.log("Starting containers...");
                return compose.upAll({
                    cwd: composeFilePath,
                    log: true,
                    config: "docker-test-compose.yml"
                });
            },
            err => {
                console.log("Something went wrong:", err.message);
            }
        );
}

async function stopDockerCompose() {
    console.log("stopping containers");
    return compose
        .down({ cwd: composeFilePath, log: true, config: "docker-test-compose.yml" })
        .then(
            () => {
                console.log("done stopping containers");
            },
            (err) => {
                console.log("something went wrong:", err.message);
            }
        );
}


module.exports = { startDockerCompose, stopDockerCompose };
