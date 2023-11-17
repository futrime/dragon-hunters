# Bot

The Minecraft bot powered by Mineflayer

## Install

Before installing Bot, make sure you have installed Node.js 18 and corresponding version of npm.

Run the following commands to build Bot:

```bash
npm run build
```

## Usage

Create a `.env` file with content like this:

```bash
# The username of the bot, no effect if REGISTRY_ADDRESS is set
BOT_USERNAME="Unnamed"

# The port the bot listens on
LISTEN_PORT="8080"

# The logging level
LOG_LEVEL="3"

# The host of the Minecraft server
MCSERVER_HOST="127.0.0.1"

# The port of the Minecraft server
MCSERVER_PORT="25565"

# The version of the Minecraft server
MCSERVER_VERSION="1.20.1"

# The address of the registry, unset to disable registry
REGISTRY_ADDRESS="http://127.0.0.1:8081"
```

Run the following command to start Bot:

```bash
npm start
```
