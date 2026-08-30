<template>
  <div class="board">
    <div class="board-grid">
      <!-- 40个格子 -->
      <Tile
        v-for="(tile, idx) in BOARD"
        :key="idx"
        :tile="tile"
        :tileIndex="idx"
        :players="players"
        :owners="ownersMap"
        :movingPlayerId="movingPlayerId"
        :style="getTilePosition(idx)"
        @click="onTileClick"
      />
      <!-- 中心区域 -->
      <div class="board-center">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { BOARD } from '../game/constants.js'
import Tile from './Tile.vue'

const props = defineProps({
  players: Array,
  movingPlayerId: { type: Number, default: null }
})

const emit = defineEmits(['tile-click'])

// 计算每个格子的所有者映射
const ownersMap = computed(() => {
  const map = {}
  if (!props.players) return map
  for (const player of props.players) {
    for (const tileIdx of player.properties) {
      map[tileIdx] = player
    }
  }
  return map
})

// 计算每个格子在棋盘上的位置
// 棋盘是 11x11 的网格，每格 70px，角落 82px
const TILE_SIZE = 85
const CORNER_SIZE = 100

function getTilePosition(idx) {
  let col, row

  if (idx >= 0 && idx <= 9) {
    // 底边：tile 0 在右下角(col=10,row=10)，tile 9 在左下角(col=0,row=10)
    col = 10 - idx
    row = 10
  } else if (idx >= 10 && idx <= 19) {
    // 左边：tile 10 在左下角(col=0,row=10)，tile 19 在左上角(col=0,row=0)
    col = 0
    row = 10 - (idx - 10)
  } else if (idx >= 20 && idx <= 29) {
    // 顶边：tile 20 在左上角(col=0,row=0)，tile 29 在右上角(col=10,row=0)
    col = idx - 20
    row = 0
  } else {
    // 右边：tile 30 在右上角(col=10,row=0)，tile 39 在右下角(col=10,row=9)
    col = 10
    row = idx - 29
  }

  // 计算像素位置
  let left, top
  const isCorner = [0, 10, 20, 30].includes(idx)
  const size = isCorner ? CORNER_SIZE : TILE_SIZE

  // 累计位置
  if (col === 0) {
    left = 0
  } else if (col === 10) {
    left = TILE_SIZE * 9 + CORNER_SIZE
  } else {
    left = CORNER_SIZE + (col - 1) * TILE_SIZE
  }

  if (row === 0) {
    top = 0
  } else if (row === 10) {
    top = TILE_SIZE * 9 + CORNER_SIZE
  } else {
    top = CORNER_SIZE + (row - 1) * TILE_SIZE
  }

  return {
    position: 'absolute',
    left: left + 'px',
    top: top + 'px',
    width: size + 'px',
    height: size + 'px'
  }
}

function onTileClick(tile) {
  emit('tile-click', tile)
}
</script>

<style scoped>
.board {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.board-grid {
  position: relative;
  width: 970px;
  height: 970px;
  background: #e8dcc8;
  border: 3px solid #8B7355;
  border-radius: 4px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.board-center {
  position: absolute;
  left: 100px;
  top: 100px;
  width: 770px;
  height: 770px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f0e8 0%, #ede4d4 100%);
  border: 1px solid #c9b99a;
}
</style>
