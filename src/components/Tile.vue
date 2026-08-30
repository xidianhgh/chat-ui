<template>
  <div class="tile" :class="tileClasses" :style="tileStyle" @click="$emit('click', tile)">
    <div v-if="tile.group" class="color-bar" :style="{ background: groupColor }"></div>
    <div class="tile-icon">{{ tileIcon }}</div>
    <div class="tile-name">{{ tile.name }}</div>
    <div v-if="tile.price" class="tile-price">{{ tile.price }}</div>
    <div v-if="building > 0" class="buildings">{{ buildingIcon }}</div>
    <div v-if="owner" class="owner-dot" :style="{ background: owner.color }"></div>
    <div v-if="isMortgaged" class="mortgage-mark">抵</div>
    <!-- 玩家棋子 -->
    <div class="players-on-tile">
      <div v-for="p in playersHere" :key="p.id" class="player-token" :style="{ background: p.color }">
        {{ p.name[0] }}
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
  owners: Object // tileIndex -> player
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
  font-size: 10px;
  font-weight: 600;
  color: #333;
  text-align: center;
  line-height: 1.1;
  max-width: 100%;
  overflow: hidden;
  padding: 0 2px;
}

.tile-corner .tile-name {
  font-size: 12px;
}

.tile-price {
  font-size: 9px;
  color: #888;
}

.buildings {
  font-size: 10px;
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
  bottom: 1px;
  left: 1px;
  display: flex;
  gap: 2px;
}

.player-token {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  color: #fff;
  border: 1px solid rgba(0,0,0,0.3);
  transition: all 0.5s ease;
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
