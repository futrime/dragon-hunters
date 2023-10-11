import {Bot, GameState, Player, Time} from 'mineflayer';
import {Biome} from 'prismarine-biome';
import {Block} from 'prismarine-block';
import {Effect, Entity} from 'prismarine-entity';
import {Item} from 'prismarine-item';
import {Vec3} from 'vec3';

export interface SerializedBot {
  readonly username: string;
  readonly version: string;
  readonly entity: SerializedEntity;
  readonly entities: Readonly<Record<string, SerializedEntity>>;
  readonly game: SerializedGameState;
  readonly player: SerializedPlayer;
  readonly players: Readonly<Record<string, SerializedPlayer>>;
  readonly isRaining: boolean;
  readonly experience: {
    readonly level: number; readonly points: number; readonly progress: number;
  };
  readonly health: number;
  readonly food: number;
  readonly foodSaturation: number;
  readonly oxygenLevel: number;
  readonly time: SerializedTime;
  readonly quickBarSlot: number;
  readonly isSleeping: boolean;
  readonly biome?: SerializedBiome;
  readonly blocksNearby: ReadonlyArray<SerializedBlock>;
}

export interface SerializedBiome {
  readonly name: string;
  readonly displayName?: string;
  readonly rainfall: number;
  readonly temperature: number;
}

export interface SerializedBlock {
  readonly name: string;
  readonly displayName: string;
}

export interface SerializedBlockDetailed extends SerializedBlock {
  readonly biome: SerializedBiome;
  readonly position: Vec3;
  readonly name: string;
  readonly displayName: string;
  readonly hardness: number;
  readonly diggable: boolean;
}

export interface SerializedEffect {
  readonly id: number;
  readonly amplifier: number;
  readonly duration: number;
}

export interface SerializedEntity {
  readonly id: number;
  readonly displayName?: string;
  readonly name?: string;
  readonly position: Vec3;
  readonly velocity: Vec3;
  readonly yaw: number;
  readonly pitch: number;
  readonly height: number;
  readonly width: number;
  readonly onGround: boolean;
  readonly equipment: ReadonlyArray<SerializedItem>;
  readonly health?: number;
  readonly food?: number;
  readonly foodSaturation?: number;
  readonly effects: ReadonlyArray<SerializedEffect>;
}

export interface SerializedGameState {
  readonly dimension: string;
}

export interface SerializedItem {
  readonly count: number;
  readonly name: string;
  readonly maxDurability: number;
  readonly durabilityUsed: number;
  readonly enchants: ReadonlyArray<{name: string; lvl: number;}>;
}

export interface SerializedPlayer {
  readonly username: string;
}

export interface SerializedTime {
  readonly time: number;
  readonly timeOfDay: number;
  readonly day: number;
  readonly isDay: boolean;
  readonly moonPhase: number;
  readonly age: number;
}

export function createSerializedBot(bot: Bot): SerializedBot {
  return botToJson(bot);
}

function biomeToJson(biome: Biome): SerializedBiome {
  return {
    name: biome.name,
    displayName: biome.displayName,
    rainfall: biome.rainfall,
    temperature: biome.temperature,
  };
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function blockToJson(block: Block): SerializedBlockDetailed {
  return {
    biome: biomeToJson(block.biome),
    position: block.position,
    name: block.name,
    displayName: block.displayName,
    hardness: block.hardness,
    diggable: block.diggable,
  };
}

function botToJson(bot: Bot): SerializedBot {
  return {
    username: bot.username,
    version: bot.version,
    entity: entityToJson(bot.entity),
    entities: Object.fromEntries(
        Object.entries(bot.entities)
            .map(([key, value]) => [key, entityToJson(value)])),
    game: gameStateToJson(bot.game),
    player: playerToJson(bot.player),
    players: Object.fromEntries(
        Object.entries(bot.players)
            .map(([key, value]) => [key, playerToJson(value)])),
    isRaining: bot.isRaining,
    experience: bot.experience,
    health: bot.health,
    food: bot.food,
    foodSaturation: bot.foodSaturation,
    oxygenLevel: bot.oxygenLevel,
    time: timeToJson(bot.time),
    quickBarSlot: bot.quickBarSlot,
    isSleeping: bot.isSleeping,

    biome: (() => {
      const position = bot.entity.position;
      const biome = bot.blockAt(position)?.biome;

      return biome !== undefined ? biomeToJson(biome) : undefined;
    })(),
    blocksNearby: (() => {
      const position = bot.entity.position;
      const blocks: Record < string, {
        name: string;
        displayName: string;
      }
      > = {};

      for (let x = -8; x <= 8; x++) {
        for (let y = -8; y <= 8; y++) {
          for (let z = -8; z <= 8; z++) {
            const block = bot.blockAt(position.offset(x, y, z));

            if (block !== null) {
              blocks[block.name] = {
                name: block.name,
                displayName: block.displayName,
              };
            }
          }
        }
      }

      return Array.from(Object.values(blocks));
    })(),
  };
}

function effectToJson(effect: Effect): SerializedEffect {
  return {
    id: effect.id,
    amplifier: effect.amplifier,
    duration: effect.duration,
  };
}

function entityToJson(entity: Entity): SerializedEntity {
  return {
    id: entity.id,
    displayName: entity.displayName,
    name: entity.name,
    position: entity.position,
    velocity: entity.velocity,
    yaw: entity.yaw,
    pitch: entity.pitch,
    height: entity.height,
    width: entity.width,
    onGround: entity.onGround,
    equipment: entity.equipment.map(itemToJson),
    health: entity.health,
    food: entity.food,
    foodSaturation: entity.foodSaturation,
    effects: Array.isArray(entity.effects) ? entity.effects.map(effectToJson) :
                                             [],
  };
}

function gameStateToJson(gameState: GameState): SerializedGameState {
  return {
    dimension: gameState.dimension,
  };
}

function itemToJson(item: Item): SerializedItem {
  return {
    count: item.count,
    name: item.name,
    maxDurability: item.maxDurability,
    durabilityUsed: item.durabilityUsed,
    enchants: item.enchants,
  };
}

function playerToJson(player: Player): SerializedPlayer {
  return {
    username: player.username,
  };
}

function timeToJson(time: Time): SerializedTime {
  return {
    time: time.time,
    timeOfDay: time.timeOfDay,
    day: time.day,
    isDay: time.isDay,
    moonPhase: time.moonPhase,
    age: time.age,
  };
}
