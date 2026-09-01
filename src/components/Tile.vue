<template>
  <div class="tile" :class="tileClasses" :style="tileStyle" @click="$emit('click', tileIndex)">
    <div v-if="tile.group" class="color-bar" :style="{ background: groupColor }"></div>
    <div class="tile-icon">{{ tileIcon }}</div>
    <div class="tile-name">{{ tile.name }}</div>
    <div v-if="tile.price" class="tile-price">{{ tile.price }}</div>
    <div v-if="building > 0" class="buildings">{{ buildingIcon }}</div>
    <div v-if="owner" class="owner-dot" :style="{ background: owner.color }"></div>
    <div v-if="isMortgaged" class="mortgage-mark">抵</div>
    <!-- 玩家棋子 -->
    <div class="players-on-tile">
      <div v-for="p in playersHere" :key="p.id" class="player-token" :class="{ moving: movingPlayerId === p.id }" :style="{ '--token-color': p.color }">
        <div class="token-base"></div>
        <div class="token-head"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TILE_TYPES, COLOR_GROUPS, BOARD } from '../game/constants.js'

const props = defineProps({
  tile: Object,
  players: Array,
  tileIndex: Number,
  owners: Object, // tileIndex -> player
  movingPlayerId: { type: Number, default: null }
})

defineEmits(['click'])

const groupColor = computed(() => COLOR_GROUPS[props.tile.group] || '#999')

const tileIcon = computed(() => {
  switch (props.tile.type) {
    case TILE_TYPES.GO: return '🚀'
    case TILE_TYPES.JAIL: return '🔒'
    case TILE_TYPES.FREE_PARKING: return '🅿️'
    case TILE_TYPES.GO_TO_JAIL: return '👮'
    case TILE_TYPES.CHANCE: return '❓'
    case TILE_TYPES.DESTINY: return '🌟'
    case TILE_TYPES.TAX: return '💰'
    case TILE_TYPES.RAILROAD: return '🚂'
    case TILE_TYPES.UTILITY: return props.tile.name.includes('电力') ? '💡' : '💧'
    default: return ''
  }
})

const building = computed(() => {
  const owner = props.owners?.[props.tileIndex]
  return owner?.buildings?.[props.tileIndex] || 0
})

const buildingIcon = computed(() => {
  const b = building.value
  if (b === 5) return '🏨'
  return '🏠'.repeat(b)
})

const owner = computed(() => props.owners?.[props.tileIndex] || null)
const isMortgaged = computed(() => owner.value?.mortgaged?.includes(props.tileIndex))

const playersHere = computed(() => {
  return (props.players || []).filter(p => p.position === props.tileIndex && !p.bankrupt)
})

const tileClasses = computed(() => ({
  [`tile-${props.tile.type}`]: true,
  'tile-corner': [0, 10, 20, 30].includes(props.tileIndex),
  'tile-property': props.tile.type === TILE_TYPES.PROPERTY
}))

const tileStyle = computed(() => ({}))
</script>

<style scoped>
.tile {
  position: absolute;
  width: 82px;
  height: 82px;
  background: #f5f0e8;
  border: 1px solid #c9b99a;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  font-size: 10px;
}

.tile:hover {
  z-index: 10;
  box-shadow: 0 0 8px rgba(0,0,0,0.3);
  transform: scale(1.05);
}

.tile-corner {
  width: 97px;
  height: 97px;
}

.color-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 14px;
}

.tile-icon {
  font-size: 18px;
  line-height: 1;
  margin-top: 2px;
}

.tile-corner .tile-icon {
  font-size: 26px;
}

.tile-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  text-align: center;
  line-height: 1.1;
  max-width: 100%;
  overflow: hidden;
  padding: 0 2px;
}

.tile-corner .tile-name {
  font-size: 14px;
}

.tile-price {
  font-size: 11px;
  color: #888;
}

.buildings {
  font-size: 12px;
  line-height: 1;
}

.owner-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.mortgage-mark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 16px;
  font-weight: 700;
  color: rgba(231, 76, 60, 0.6);
}

.players-on-tile {
  position: absolute;
  bottom: 2px;
  left: 2px;
  display: flex;
  gap: 3px;
  align-items: flex-end;
}

.player-token {
  position: relative;
  width: 22px;
  height: 26px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.4));
  transition: all 0.5s ease;
  transform: rotate(180deg);
}

/* 慧星尾拖效果 */
.player-token.moving {
  animation: cometPulse 0.4s ease-in-out infinite alternate;
}

.player-token.moving .token-head {
  box-shadow:
    0 0 6px var(--token-color),
    0 0 12px var(--token-color),
    0 0 20px var(--token-color),
    inset 0 -2px 3px rgba(0,0,0,0.2),
    inset 0 2px 3px rgba(255,255,255,0.3);
}

.player-token.moving .token-base {
  box-shadow:
    0 0 6px var(--token-color),
    0 0 12px var(--token-color),
    inset 0 -2px 3px rgba(0,0,0,0.15),
    0 1px 2px rgba(0,0,0,0.2);
}

.player-token.moving::before,
.player-token.moving::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.player-token.moving::before {
  width: 16px;
  height: 16px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, var(--token-color) 0%, transparent 70%);
  opacity: 0.6;
  animation: cometGlow 0.5s ease-in-out infinite alternate;
}

.player-token.moving::after {
  width: 28px;
  height: 28px;
  top: 60%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, var(--token-color) 0%, transparent 60%);
  opacity: 0.3;
  animation: cometGlow 0.7s ease-in-out infinite alternate-reverse;
}

@keyframes cometPulse {
  from {
    filter: drop-shadow(0 0 4px var(--token-color)) drop-shadow(0 0 8px var(--token-color));
  }
  to {
    filter: drop-shadow(0 0 8px var(--token-color)) drop-shadow(0 0 16px var(--token-color)) drop-shadow(0 0 24px var(--token-color));
  }
}

@keyframes cometGlow {
  from {
    opacity: 0.3;
    transform: translate(-50%, -50%) scale(0.8);
  }
  to {
    opacity: 0.7;
    transform: translate(-50%, -50%) scale(1.2);
  }
}

/* 棋子头部 - 圆形 */
.token-head {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--token-color);
  border: 1.5px solid rgba(0,0,0,0.25);
  box-shadow: inset 0 -2px 3px rgba(0,0,0,0.2), inset 0 2px 3px rgba(255,255,255,0.3);
  z-index: 1;
}

/* 棋子底座 - 梯形 */
.token-base {
  width: 18px;
  height: 10px;
  background: var(--token-color);
  border: 1.5px solid rgba(0,0,0,0.25);
  border-radius: 3px 3px 5px 5px;
  margin-top: -3px;
  box-shadow: inset 0 -2px 3px rgba(0,0,0,0.15), 0 1px 2px rgba(0,0,0,0.2);
}

.tile-go { background: #ffeaa7; }
.tile-jail { background: #fab1a0; }
.tile-free_parking { background: #b8e994; }
.tile-go_to_jail { background: #ff7675; }
.tile-chance { background: #dfe6e9; }
.tile-destiny { background: #dfe6e9; }
.tile-tax { background: #ffeaa7; }
.tile-railroad { background: #dfe6e9; }
.tile-utility { background: #dfe6e9; }
</style>
