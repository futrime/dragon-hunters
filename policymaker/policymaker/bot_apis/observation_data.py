from typing import List, NotRequired, Optional, TypedDict


class Vec3(TypedDict):
    x: float
    y: float
    z: float


class Biome(TypedDict):
    name: str
    displayName: Optional[str]
    rainfall: float
    temperature: float


class Block(TypedDict):
    name: str
    displayName: str


class Effect(TypedDict):
    id: int
    amplifier: float
    duration: float


class Enchant(TypedDict):
    name: str
    lvl: int


class Item(TypedDict):
    count: int
    name: str
    maxDurability: NotRequired[float]
    durabilityUsed: Optional[float]
    enchants: List[Enchant]


class Entity(TypedDict):
    id: int
    displayName: Optional[str]
    name: Optional[str]
    position: Vec3
    velocity: Vec3
    yaw: float
    pitch: float
    height: float
    width: float
    onGround: bool
    equipment: List[Optional[Item]]
    health: Optional[float]
    food: Optional[float]
    foodSaturation: Optional[float]
    effects: List[Effect]


class Experience(TypedDict):
    level: int
    points: int
    progress: float


class GameState(TypedDict):
    dimension: str


class Player(TypedDict):
    username: str


class Time(TypedDict):
    time: int
    timeOfDay: int
    day: int
    isDay: bool
    moonPhase: float
    age: float


class ObservationData(TypedDict):
    username: str
    version: str
    entity: Entity
    entities: List[Entity]
    game: GameState
    player: Player
    players: List[Player]
    isRaining: bool
    experience: Experience
    health: float
    food: float
    foodSaturation: float
    time: Time
    quickBarSlot: int
    isSleeping: bool
    biome: Optional[Biome]
    blocksNearby: List[Block]
