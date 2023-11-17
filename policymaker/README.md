# Policymaker

The brain of Dragon Hunters

## Install

Before installing Policymaker, make sure you have installed Python 3.11 and Poetry.

Run the following commands to install Policymaker:

```bash
poetry install
```

## Usage

Create a `.env` file. Here is an example:

```bash
# The host of the bot, no effect if REGISTRY_ADDRESS is set
BOT_HOST="127.0.0.1"

# The port of the bot, no effect if REGISTRY_ADDRESS is set
BOT_PORT="8080"

# The log level. For most cases, INFO is recommended. For debugging, DEBUG is recommended.
LOG_LEVEL="INFO"

# The OpenAI API key (required)
OPENAI_API_KEY="sk-xxx"

# The registry address, unset to disable registry
REGISTRY_ADDRESS="http://127.0.0.1:8081"
```

To run the policymaker, run the following commands:

```bash
poetry run python main.py
```
