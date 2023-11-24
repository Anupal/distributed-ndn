# Scalable Computing UI
## Prerequisites
1. Install node v20.9.0 with corresponding npm version
2. Install yarn using npm install -g yarn
## Configuration
Use the constants file located in frontend/ui/src/consts/constants.js to change
any configuration options before running the project. This will configure both
ui and ui-proxy. If use_sample_json is set to true the static json located at frontend/ui/public/sample_stats.json
will be used for the visualisation.
## How to run the project
1. run yarn build in this directory
3. Run the node application in the folder ui-proxy use an env variable to set the port
