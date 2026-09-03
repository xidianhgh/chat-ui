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
        <div class="win-condition">
          <div class="wc-title">🏆 胜负条件</div>
          <div class="wc-line">所有其他玩家破产后，最后存活的玩家获胜</div>
          <div class="wc-line">所有人类玩家破产时，净资产最高的 AI 获胜</div>
          <div class="wc-line">或 净资产率先达到目标值的玩家获胜（人类与 AI 均适用）</div>
          <div v-if="targetNetWorth > 0" class="wc-line wc-goal">🎯 净资产目标：{{ targetNetWorth }} 元</div>
          <div class="wc-sub">破产 = 现金为负 且 净资产为负</div>
          <div class="wc-sub">净资产 = 现金 + 存款 + 地产 + 股票 − 贷款</div>
        </div>
        <slot></slot>
      </div>

      <!-- 格子详情弹窗 -->
      <transition name="fade">
        <div v-if="selectedTile" class="tile-info-overlay" @click.self="selectedTile = null">
          <div class="tile-info-popup">
            <button class="close-btn" @click="selectedTile = null">✕</button>

            <!-- 颜色条 -->
            <div v-if="selectedTile.tile.group" class="info-color-bar" :style="{ background: groupColor(selectedTile.tile) }"></div>

            <div class="info-header">
              <span class="info-icon">{{ tileIcon(selectedTile.tile) }}</span>
              <span class="info-name">{{ selectedTile.tile.name }}</span>
            </div>

            <div class="info-body">
              <!-- 地产类 -->
              <template v-if="selectedTile.tile.type === 'property'">
                <div class="info-row"><span>价格</span><span>{{ selectedTile.tile.price }} 元</span></div>
                <div class="info-row"><span>建房费用</span><span>{{ selectedTile.tile.buildCost }} 元/栋</span></div>
                <div class="info-section">
                  <div class="section-title">租金表</div>
                  <div class="info-row"><span>空地</span><span>{{ selectedTile.tile.rent[0] }} 元</span></div>
                  <div class="info-row"><span>1栋</span><span>{{ selectedTile.tile.rent[1] }} 元</span></div>
                  <div class="info-row"><span>2栋</span><span>{{ selectedTile.tile.rent[2] }} 元</span></div>
                  <div class="info-row"><span>3栋</span><span>{{ selectedTile.tile.rent[3] }} 元</span></div>
                  <div class="info-row"><span>4栋</span><span>{{ selectedTile.tile.rent[4] }} 元</span></div>
                  <div class="info-row highlight"><span>酒店</span><span>{{ selectedTile.tile.rent[4] * 2 }} 元</span></div>
                </div>
                <div v-if="selectedTile.owner" class="info-row">
                  <span>所有者</span>
                  <span :style="{ color: selectedTile.owner.color }">{{ selectedTile.owner.name }}</span>
                </div>
                <div v-if="selectedTile.building > 0" class="info-row">
                  <span>建筑</span>
                  <span>{{ selectedTile.building === 5 ? '酒店' : selectedTile.building + '栋房子' }}</span>
                </div>
                <div v-if="selectedTile.mortgaged" class="info-row warn"><span>已抵押</span></div>
              </template>

              <!-- 火车站 -->
              <template v-else-if="selectedTile.tile.type === 'railroad'">
                <div class="info-row"><span>价格</span><span>{{ selectedTile.tile.price }} 元</span></div>
                <div class="info-section">
                  <div class="section-title">租金表</div>
                  <div class="info-row"><span>拥有1座</span><span>250 元</span></div>
                  <div class="info-row"><span>拥有2座</span><span>500 元</span></div>
                  <div class="info-row"><span>拥有3座</span><span>1000 元</span></div>
                  <div class="info-row"><span>拥有4座</span><span>2000 元</span></div>
                </div>
                <div v-if="selectedTile.owner" class="info-row">
                  <span>所有者</span>
                  <span :style="{ color: selectedTile.owner.color }">{{ selectedTile.owner.name }}</span>
                </div>
              </template>

              <!-- 公共事业 -->
              <template v-else-if="selectedTile.tile.type === 'utility'">
                <div class="info-row"><span>价格</span><span>{{ selectedTile.tile.price }} 元</span></div>
                <div class="info-section">
                  <div class="section-title">租金规则</div>
                  <div class="info-row"><span>拥有1座</span><span>骰子点数 × 40</span></div>
                  <div class="info-row"><span>拥有2座</span><span>骰子点数 × 100</span></div>
                </div>
                <div v-if="selectedTile.owner" class="info-row">
                  <span>所有者</span>
                  <span :style="{ color: selectedTile.owner.color }">{{ selectedTile.owner.name }}</span>
                </div>
              </template>

              <!-- 税收 -->
              <template v-else-if="selectedTile.tile.type === 'tax'">
                <div class="info-row"><span>税款</span><span>{{ selectedTile.tile.amount }} 元</span></div>
              </template>

              <!-- 入狱格 -->
              <template v-else-if="selectedTile.tile.type === 'go_to_jail'">
                <div class="info-desc">落在该格立即被送入监狱，直接传送，不经过起点，不获得 2000 元。</div>
                <div class="info-section">
                  <div class="section-title">出狱方式</div>
                  <div class="info-row"><span>掷出双数</span><span>立即出狱并用该骰移动</span></div>
                  <div class="info-row"><span>使用出狱卡</span><span>免费出狱并重新掷骰</span></div>
                  <div class="info-row highlight"><span>坐满3回合</span><span>缴纳 500 元罚款出狱</span></div>
                </div>
                <div class="info-desc" style="font-size:12px;color:#999;margin-top:4px;">坐牢期间无法移动、购买地产或收租</div>
              </template>

              <!-- 机会格 -->
              <template v-else-if="selectedTile.tile.type === 'chance'">
                <div class="info-desc">落在该格需翻开一张机会卡，按卡片指示执行。</div>
                <div class="info-section">
                  <div class="section-title">可能的结果</div>
                  <div class="info-row"><span>💰 获得/支付金钱</span><span>200~1000 元</span></div>
                  <div class="info-row"><span>🚶 前进到指定位置</span><span>起点/银杏街/西站</span></div>
                  <div class="info-row"><span>🔙 后退 3 格</span><span>触发落点事件</span></div>
                  <div class="info-row"><span>👮 直接入狱</span><span>传送到监狱</span></div>
                  <div class="info-row"><span>🎁 获得道具</span><span>出狱卡/骰子/免租/护身符</span></div>
                  <div class="info-row"><span>🔧 房屋维修</span><span>每栋 250 / 酒店 1000</span></div>
                  <div class="info-row"><span>🎂 过生日</span><span>其他玩家各付 200 元</span></div>
                </div>
              </template>

              <!-- 命运格 -->
              <template v-else-if="selectedTile.tile.type === 'destiny'">
                <div class="info-desc">落在该格需翻开一张命运卡，按卡片指示执行。</div>
                <div class="info-section">
                  <div class="section-title">可能的结果</div>
                  <div class="info-row"><span>💰 获得/支付金钱</span><span>200~1000 元</span></div>
                  <div class="info-row"><span>🚶 前进到指定位置</span><span>免费停车/玉兰路</span></div>
                  <div class="info-row"><span>🔙 后退 5 格</span><span>触发落点事件</span></div>
                  <div class="info-row"><span>👮 直接入狱</span><span>传送到监狱</span></div>
                  <div class="info-row"><span>🎁 获得道具</span><span>出狱卡/骰子/路障/转移卡</span></div>
                  <div class="info-row"><span>🔧 房屋维修</span><span>每栋 100 / 酒店 500</span></div>
                  <div class="info-row"><span>🎂 过生日</span><span>其他玩家各付 300 元</span></div>
                </div>
              </template>

              <!-- 其他特殊格子 -->
              <template v-else>
                <div class="info-desc">{{ tileDescription(selectedTile.tile) }}</div>
              </template>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { BOARD, TILE_TYPES, COLOR_GROUPS } from '../game/constants.js'
import Tile from './Tile.vue'

const props = defineProps({
  players: Array,
  movingPlayerId: { type: Number, default: null },
  targetNetWorth: { type: Number, default: 0 }
})

const emit = defineEmits(['tile-click'])

const selectedTile = ref(null)

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
const TILE_SIZE = 85
const CORNER_SIZE = 100

function getTilePosition(idx) {
  let col, row

  if (idx >= 0 && idx <= 9) {
    col = 10 - idx
    row = 10
  } else if (idx >= 10 && idx <= 19) {
    col = 0
    row = 10 - (idx - 10)
  } else if (idx >= 20 && idx <= 29) {
    col = idx - 20
    row = 0
  } else {
    col = 10
    row = idx - 29
  }

  let left, top
  const isCorner = [0, 10, 20, 30].includes(idx)
  const size = isCorner ? CORNER_SIZE : TILE_SIZE

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

function onTileClick(tileIndex) {
  const tile = BOARD[tileIndex]
  if (!tile) return

  const owner = ownersMap.value[tileIndex] || null
  const building = owner?.buildings?.[tileIndex] || 0
  const mortgaged = owner?.mortgaged?.includes(tileIndex) || false

  selectedTile.value = { tile, tileIndex, owner, building, mortgaged }
  emit('tile-click', tile)
}

function groupColor(tile) {
  return COLOR_GROUPS[tile.group] || '#999'
}

function tileIcon(tile) {
  switch (tile.type) {
    case TILE_TYPES.GO: return '🚀'
    case TILE_TYPES.JAIL: return '🔒'
    case TILE_TYPES.FREE_PARKING: return '🅿️'
    case TILE_TYPES.GO_TO_JAIL: return '👮'
    case TILE_TYPES.CHANCE: return '❓'
    case TILE_TYPES.DESTINY: return '🌟'
    case TILE_TYPES.TAX: return '💰'
    case TILE_TYPES.RAILROAD: return '🚂'
    case TILE_TYPES.UTILITY: return tile.name.includes('电力') ? '💡' : '💧'
    default: return '🏠'
  }
}

function tileDescription(tile) {
  switch (tile.type) {
    case TILE_TYPES.GO: return '经过或停留此处可获得 2000 元'
    case TILE_TYPES.JAIL: return '探访监狱，只是来看看朋友'
    case TILE_TYPES.FREE_PARKING: return '免费停车，休息一下'
    case TILE_TYPES.GO_TO_JAIL: return '直接入狱！不要经过起点'
    case TILE_TYPES.CHANCE: return '翻开一张机会卡'
    case TILE_TYPES.DESTINY: return '翻开一张命运卡'
    default: return ''
  }
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
  background: linear-gradient(135deg, #1a2a4a 0%, #0f1d36 100%);
  border: 1px solid #2c4a7c;
}

/* 胜负条件 */
.win-condition {
  position: absolute;
  top: 16px;
  left: 20px;
  text-align: left;
  z-index: 1;
}

.wc-title {
  font-size: 15px;
  font-weight: 700;
  color: #f1c40f;
  margin-bottom: 6px;
  text-shadow: 0 1px 4px rgba(0,0,0,0.4);
}

.wc-line {
  font-size: 13px;
  color: #f1c40f;
  font-weight: 600;
  line-height: 1.5;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.wc-sub {
  font-size: 11px;
  color: rgba(241, 196, 15, 0.65);
  line-height: 1.5;
  margin-top: 2px;
}

/* 净资产目标（只读展示） */
.wc-goal {
  color: #2ecc71;
  margin-top: 4px;
}

/* 详情弹窗 */
.tile-info-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tile-info-popup {
  position: relative;
  background: #fff;
  border-radius: 16px;
  padding: 0;
  min-width: 280px;
  max-width: 320px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.3);
  overflow: hidden;
  animation: popup-in 0.25s ease-out;
}

@keyframes popup-in {
  from { transform: scale(0.85); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.close-btn {
  position: absolute;
  top: 8px;
  right: 10px;
  background: none;
  border: none;
  font-size: 16px;
  color: #999;
  cursor: pointer;
  z-index: 10;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(0,0,0,0.08);
  color: #333;
}

.info-color-bar {
  height: 8px;
  width: 100%;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px 10px;
  border-bottom: 1px solid #eee;
}

.info-icon {
  font-size: 28px;
}

.info-name {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.info-body {
  padding: 12px 20px 18px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  font-size: 14px;
  color: #555;
}

.info-row span:first-child {
  color: #888;
}

.info-row.highlight {
  font-weight: 700;
  color: #e74c3c;
}

.info-row.highlight span {
  color: #e74c3c;
}

.info-row.warn {
  color: #e74c3c;
  font-weight: 600;
}

.info-section {
  margin: 8px 0;
  padding: 8px 0;
  border-top: 1px dashed #eee;
  border-bottom: 1px dashed #eee;
}

.section-title {
  font-size: 12px;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.info-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  text-align: center;
  padding: 8px 0;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
