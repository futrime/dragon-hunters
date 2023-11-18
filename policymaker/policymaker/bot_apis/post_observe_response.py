from typing import Dict

from .observation_data import ObservationData
from .response import Response


class PostObserveResponse(Response):
    def __init__(self, data: Dict):
        super().__init__(data, _JSON_SCHEMA)

    def data(self) -> ObservationData:
        return ObservationData(**(self._data["bot"]))


_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "bot": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "version": {"type": "string"},
                "entity": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "displayName": {"type": ["string", "null"]},
                        "name": {"type": ["string", "null"]},
                        "position": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"},
                                "z": {"type": "number"},
                            },
                            "required": ["x", "y", "z"],
                        },
                        "velocity": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"},
                                "z": {"type": "number"},
                            },
                            "required": ["x", "y", "z"],
                        },
                        "yaw": {"type": "number"},
                        "pitch": {"type": "number"},
                        "height": {"type": "number"},
                        "width": {"type": "number"},
                        "onGround": {"type": "boolean"},
                        "equipment": {
                            "type": "array",
                            "items": {
                                "oneOf": [
                                    {
                                        "type": "object",
                                        "properties": {
                                            "count": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "maxDurability": {"type": "number"},
                                            "durabilityUsed": {
                                                "type": ["number", "null"]
                                            },
                                            "enchants": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string"},
                                                        "lvl": {"type": "integer"},
                                                    },
                                                    "required": ["name", "lvl"],
                                                },
                                            },
                                        },
                                        "required": [
                                            "count",
                                            "name",
                                            "durabilityUsed",
                                            "enchants",
                                        ],
                                    },
                                    {"type": "null"},
                                ],
                            },
                        },
                        "health": {"type": ["number", "null"]},
                        "food": {"type": ["number", "null"]},
                        "foodSaturation": {"type": ["number", "null"]},
                        "effects": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "amplifier": {"type": "number"},
                                    "duration": {"type": "number"},
                                },
                                "required": ["id", "amplifier", "duration"],
                            },
                        },
                    },
                    "required": [
                        "id",
                        "position",
                        "velocity",
                        "yaw",
                        "pitch",
                        "height",
                        "width",
                        "onGround",
                        "equipment",
                        "effects",
                    ],
                },
                "entities": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "displayName": {"type": ["string", "null"]},
                                "name": {"type": ["string", "null"]},
                                "position": {
                                    "type": "object",
                                    "properties": {
                                        "x": {"type": "number"},
                                        "y": {"type": "number"},
                                        "z": {"type": "number"},
                                    },
                                    "required": ["x", "y", "z"],
                                },
                                "velocity": {
                                    "type": "object",
                                    "properties": {
                                        "x": {"type": "number"},
                                        "y": {"type": "number"},
                                        "z": {"type": "number"},
                                    },
                                    "required": ["x", "y", "z"],
                                },
                                "yaw": {"type": "number"},
                                "pitch": {"type": "number"},
                                "height": {"type": "number"},
                                "width": {"type": "number"},
                                "onGround": {"type": "boolean"},
                                "equipment": {
                                    "type": "array",
                                    "items": {
                                        "oneOf": [
                                            {
                                                "type": "object",
                                                "properties": {
                                                    "count": {"type": "integer"},
                                                    "name": {"type": "string"},
                                                    "maxDurability": {"type": "number"},
                                                    "durabilityUsed": {
                                                        "type": ["number", "null"]
                                                    },
                                                    "enchants": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "name": {
                                                                    "type": "string"
                                                                },
                                                                "lvl": {
                                                                    "type": "integer"
                                                                },
                                                            },
                                                            "required": ["name", "lvl"],
                                                        },
                                                    },
                                                },
                                                "required": [
                                                    "count",
                                                    "name",
                                                    "durabilityUsed",
                                                    "enchants",
                                                ],
                                            },
                                            {"type": "null"},
                                        ],
                                    },
                                },
                                "health": {"type": ["number", "null"]},
                                "food": {"type": ["number", "null"]},
                                "foodSaturation": {"type": ["number", "null"]},
                                "effects": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "amplifier": {"type": "number"},
                                            "duration": {"type": "number"},
                                        },
                                        "required": ["id", "amplifier", "duration"],
                                    },
                                },
                            },
                            "required": [
                                "id",
                                "position",
                                "velocity",
                                "yaw",
                                "pitch",
                                "height",
                                "width",
                                "onGround",
                                "equipment",
                                "effects",
                            ],
                        },
                    },
                },
                "game": {
                    "type": "object",
                    "properties": {"dimension": {"type": "string"}},
                    "required": ["dimension"],
                },
                "player": {
                    "type": "object",
                    "properties": {"username": {"type": "string"}},
                    "required": ["username"],
                },
                "players": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "properties": {"username": {"type": "string"}},
                            "required": ["username"],
                        },
                    },
                },
                "isRaining": {"type": "boolean"},
                "experience": {
                    "type": "object",
                    "properties": {
                        "level": {"type": "integer"},
                        "points": {"type": "integer"},
                        "progress": {"type": "number"},
                    },
                    "required": ["level", "points", "progress"],
                },
                "health": {"type": "number"},
                "food": {"type": "number"},
                "foodSaturation": {"type": "number"},
                "time": {
                    "type": "object",
                    "properties": {
                        "time": {"type": "integer"},
                        "timeOfDay": {"type": "integer"},
                        "day": {"type": "integer"},
                        "isDay": {"type": "boolean"},
                        "moonPhase": {"type": "number"},
                        "age": {"type": "number"},
                    },
                    "required": [
                        "time",
                        "timeOfDay",
                        "day",
                        "isDay",
                        "moonPhase",
                        "age",
                    ],
                },
                "quickBarSlot": {"type": "integer"},
                "isSleeping": {"type": "boolean"},
                "biome": {
                    "type": ["object", "null"],
                    "properties": {
                        "name": {"type": "string"},
                        "displayName": {"type": ["string", "null"]},
                        "rainfall": {"type": "number"},
                        "temperature": {"type": "number"},
                    },
                    "required": ["name", "rainfall", "temperature"],
                },
                "blocksNearby": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "displayName": {"type": ["string", "null"]},
                        },
                        "required": ["name", "displayName"],
                    },
                },
            },
            "required": [
                "username",
                "version",
                "entity",
                "entities",
                "game",
                "player",
                "players",
                "isRaining",
                "experience",
                "health",
                "food",
                "foodSaturation",
                "time",
                "quickBarSlot",
                "isSleeping",
                "biome",
                "blocksNearby",
            ],
        }
    },
    "required": ["bot"],
}
