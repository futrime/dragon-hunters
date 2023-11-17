# Registry

The bot registry of Dragon Hunters

## Install

Before installing Registry, make sure you have installed Node.js 18 and corresponding version of npm.

Run the following commands to build Registry:

```bash
npm run build
```

## Usage

Create a `.env` file with content like this:

```bash
# The random seed for faker.js
FAKER_SEED="114514"

# The port the registry listens on
LISTEN_PORT=8081

# The log level. For most cases, 3 is recommended. For debugging, 4 is recommended.
LOG_LEVEL=3
```

Run the following command to start Registry:

```bash
npm start
```
