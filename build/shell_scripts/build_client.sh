#!/bin/bash
set -eox pipefail

# Get node
touch .bashrc
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
nvm install 20
nvm use 20
echo $(which node)
echo $(which npm)

# Install frontend dependencies and run build
rm -rf node_modules/

cd app/client

npm install
npm run build