# Dragon Hunters

Hunt the Ender Dragon with LLM

## Install

Dragon Hunters is composed of three parts: the bot, the policymaker and the registry.

### The Bot

To install the bot, you need to install NodeJS 18 and npm ahead of time. Then, run the following commands in `bot/` directory:

```bash
npm run build
```

### The Policymaker

To install the policymaker, you need to install Python 3.11 and Poetry ahead of time. Then, run the following commands in `policymaker/` directory:

```bash
poetry install
```

### The Registry

To install the registry, you need to install NodeJS 18 and npm ahead of time. Then, run the following commands in `registry/` directory:

```bash
npm run build
```

## Usage

### The Bot

To run the bot, run the following commands in `bot/` directory:

```bash
npm start
```

Some configuration options are available. You can set them in `bot/.env` file. Here is an example:

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

### The Policymaker

To run the policymaker, run the following commands in `policymaker/` directory:

```bash
poetry run python main.py
```

Some configuration options are available. You can set them in `policymaker/.env` file. Here is an example:

```bash
# The host of the bot, no effect if REGISTRY_ADDRESS is set
BOT_HOST="127.0.0.1"
# The port of the bot, no effect if REGISTRY_ADDRESS is set
BOT_PORT="8080"
# The log level
LOG_LEVEL="INFO"
# The OpenAI API key (required)
OPENAI_API_KEY="sk-xxx"
# The registry address, unset to disable registry
REGISTRY_ADDRESS="http://127.0.0.1:8081"
```

### The Registry

To run the registry, run the following commands in `registry/` directory:

```bash
npm start
```

Some configuration options are available. You can set them in `registry/.env` file. Here is an example:

```bash
# The random seed for faker.js
FAKER_SEED="114514"
# The port the registry listens on
LISTEN_PORT="8081"
# The log level
LOG_LEVEL="3"
```
