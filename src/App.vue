<template>
  <div class="app">
    <!-- 音乐控制 - 全局显示 -->
    <MusicControl />

    <!-- 游戏设置阶段 -->
    <GameSetup v-if="state.phase === 'setup'" @start="onGameStart" />

    <!-- 游戏进行中 -->
    <div v-else class="game-layout">
      <!-- 左侧：玩家面板 -->
      <div class="sidebar-left">
        <PlayerPanel :players="state.players" :currentPlayerId="currentPlayer?.id" />
        <ItemBar :items="currentPlayer?.items || []" @use-item="onUseItem" />
      </div>

      <!-- 中间：棋盘 -->
      <div class="main-area">
        <Board :players="state.players" :movingPlayerId="state.movingPlayerId"
               :targetNetWorth="state.targetNetWorth">
          <!-- 中心控制区 -->
          <div class="center-controls">
            <div class="turn-info">
              <span>第 {{ state.turnCount }} 轮</span>
              <span v-if="currentPlayer" :style="{ color: currentPlayer.color }">
                {{ currentPlayer.name }} 的回合
              </span>
            </div>

            <DiceView
              :d1="state.currentDice?.d1 || 1"
              :d2="state.currentDice?.d2 || 1"
              :total="state.currentDice?.total || 0"
              :rolling="state.animating"
            />

            <div class="action-buttons">
              <button v-if="canRollDice" class="btn-roll" @click="onRollDice" :disabled="state.animating">
                🎲 掷骰子
              </button>
              <button v-if="canEndTurn" class="btn-end" @click="onEndTurn">
                结束回合
              </button>
            </div>

            <div class="action-buttons secondary">
              <button class="btn-sm" data-tooltip="买卖4家公司的股票，赚取差价。股价实时波动，可低买高卖。" @click="state.showStockPanel = true" :disabled="!isHumanTurn">📈 股票</button>
              <button class="btn-sm" data-tooltip="存款获得2%利息，货款需要3%利息，抵押地产获得半价资金，赎回需付抵押价+10%利息。" @click="state.showBankPanel = true" :disabled="!isHumanTurn">🏦 银行</button>
              <button class="btn-sm" data-tooltip="集齐同色全套地产后，可在此套地产上建房（最多酒店），建筑越多租金越高。" @click="onBuildMode" :disabled="!isHumanTurn">🏠 建房</button>
            </div>

            <!-- 建房模式 -->
            <div v-if="buildMode" class="build-panel">
              <div class="build-title">点击棋盘上的地产建房</div>
              <div v-for="idx in buildableTiles" :key="idx" class="build-option" @click="onBuild(idx)">
                {{ tileName(idx) }} ({{ buildingCount(idx) }}/5) - {{ buildCost(idx) }}元
              </div>
              <button class="btn-sm" @click="buildMode = false">取消</button>
            </div>

            <!-- 游戏结束 -->
            <div v-if="state.phase === 'ended'" class="game-over">
              <div class="winner-text">🏆 {{ state.winner?.name }} 获胜！</div>
              <button class="btn-roll" @click="resetGame">重新开始</button>
            </div>
          </div>
        </Board>
      </div>

      <!-- 右侧：游戏日志 -->
      <div class="sidebar-right">
        <GameLog :logs="state.logs" />
      </div>
    </div>

    <!-- 弹窗 -->
    <PropertyModal
      :show="state.showPropertyModal"
      :tile="state.pendingProperty?.tile"
      @buy="onBuyProperty"
      @close="onSkipBuy"
    />

    <CardModal
      :show="state.showCardModal"
      :card="state.pendingCard"
      :type="getCardType()"
      @confirm="onConfirmCard"
    />

    <StockPanel
      :show="state.showStockPanel"
      :stocks="state.stocks"
      :player="currentPlayer"
      @close="state.showStockPanel = false"
      @buy-stock="onBuyStock"
      @sell-stock="onSellStock"
    />

    <BankPanel
      :show="state.showBankPanel"
      :player="currentPlayer"
      @close="state.showBankPanel = false"
      @action="onBankAction"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { BOARD, TILE_TYPES } from './game/constants.js'
import { createGameState, initPlayers, addLog, getCurrentPlayer, calcNetWorth, ownsFullGroup } from './game/gameState.js'
import { rollDice, rollFixed } from './game/dice.js'
import { startGame, executeTurn, buyProperty, buildHouse, confirmCard, endTurn, finishTurnProcessing } from './game/engine.js'
import { initStocks, buyStock, sellStock } from './game/stock.js'
import { useItem, hasItem } from './game/items.js'

import GameSetup from './components/GameSetup.vue'
import Board from './components/Board.vue'
import PlayerPanel from './components/PlayerPanel.vue'
import DiceView from './components/DiceView.vue'
import PropertyModal from './components/PropertyModal.vue'
import CardModal from './components/CardModal.vue'
import StockPanel from './components/StockPanel.vue'
import BankPanel from './components/BankPanel.vue'
import ItemBar from './components/ItemBar.vue'
import GameLog from './components/GameLog.vue'
import MusicControl from './components/MusicControl.vue'
import { initMusic } from './game/music.js'

const state = createGameState()
const buildMode = ref(false)

// 初始化音乐系统
initMusic()

const currentPlayer = computed(() => getCurrentPlayer(state))
const isHumanTurn = computed(() => currentPlayer.value && !currentPlayer.value.isAI && !currentPlayer.value.bankrupt)
const canRollDice = computed(() => {
  if (state.phase !== 'playing' || state.animating) return false
  if (!currentPlayer.value || currentPlayer.value.bankrupt) return false
  if (state.needAction) return false
  return true
})
const canEndTurn = computed(() => {
  if (state.phase !== 'playing') return false
  if (!currentPlayer.value) return false
  if (state.needAction) return false
  if (state.animating) return false
  // 掷过骰子后才能结束
  return state.currentDice !== null
})

// 游戏开始
async function onGameStart(humanCount, aiCount, targetNetWorth) {
  state.players = initPlayers(humanCount, aiCount)
  state.stocks = initStocks()
  state.targetNetWorth = targetNetWorth > 0 ? targetNetWorth : 0
  startGame(state)
  // 开始第一个玩家的回合
  await nextTick()
  processCurrentTurn()
}

// 处理当前玩家回合
async function processCurrentTurn() {
  if (state.phase !== 'playing') return
  const player = getCurrentPlayer(state)
  if (!player || player.bankrupt) return

  if (player.isAI) {
    try {
      await delay(800)
      await executeTurn(state)
      await nextTick()
      if (state.phase === 'playing') {
        await delay(500)
        processCurrentTurn()
      }
    } catch (e) {
      console.error('AI 回合执行出错:', e)
      state.animating = false
      state.needAction = null
      const next = (state.currentPlayerIndex + 1) % state.players.length
      state.currentPlayerIndex = next
      state.currentDice = null
      if (state.phase === 'playing') {
        processCurrentTurn()
      }
    }
  }
}

// 掷骰子
async function onRollDice() {
  if (!canRollDice.value) return
  const player = currentPlayer.value
  if (!player || player.isAI) return

  state.animating = true
  await delay(500)
  state.animating = false

  try {
    // 执行回合（内部已包含 finishTurnProcessing：破产检查、股票波动、双数判定、切换玩家）
    await executeTurn(state)
  } catch (e) {
    console.error('回合执行出错:', e)
    state.animating = false
    state.needAction = null
  }

  // 如果需要等待人类操作（购买地产弹窗等），等待用户操作
  if (state.needAction) return

  if (state.phase === 'playing') {
    await delay(500)
    processCurrentTurn()
  }
}

// 购买地产
async function onBuyProperty() {
  const player = getCurrentPlayer(state)
  const diceResult = state.currentDice
  if (state.pendingProperty) {
    buyProperty(state, player, state.pendingProperty.tile)
  }
  state.showPropertyModal = false
  state.pendingProperty = null
  state.needAction = null
  // 继续回合结束处理（破产检查、股票波动、双数判定等）
  if (diceResult && state.phase === 'playing') {
    await finishTurnProcessing(state, player, diceResult)
  }
  // 启动下一个玩家的回合（因为 needAction 导致 onRollDice 提前返回，它无法调用 processCurrentTurn）
  if (state.phase === 'playing') {
    await delay(500)
    processCurrentTurn()
  }
}

// 放弃购买
async function onSkipBuy() {
  const player = getCurrentPlayer(state)
  const diceResult = state.currentDice
  state.showPropertyModal = false
  state.pendingProperty = null
  state.needAction = null
  addLog(state, `${player.name} 放弃购买`, player.color)
  if (diceResult && state.phase === 'playing') {
    await finishTurnProcessing(state, player, diceResult)
  }
  // 启动下一个玩家的回合
  if (state.phase === 'playing') {
    await delay(500)
    processCurrentTurn()
  }
}

// 确认卡片
async function onConfirmCard() {
  await confirmCard(state)
  // 卡片可能导致移动和新事件（如购买地产弹窗），检查是否又需要操作
  if (state.needAction) return
  // 卡片效果完成后，继续回合结束处理
  const player = currentPlayer.value
  const diceResult = state.currentDice
  if (player && diceResult && state.phase === 'playing') {
    await finishTurnProcessing(state, player, diceResult)
  }
  // 启动下一个玩家的回合
  if (state.phase === 'playing') {
    await delay(500)
    processCurrentTurn()
  }
}

// 结束回合
function onEndTurn() {
  if (!canEndTurn.value) return
  buildMode.value = false
  endTurn(state)
  // 处理下一个玩家
  nextTick(() => processCurrentTurn())
}

// 股票操作
function onBuyStock(stock) {
  const player = getCurrentPlayer(state)
  if (buyStock(player, stock, 1)) {
    addLog(state, `${player.name} 买入 ${stock.name} 1股 @${stock.price}`, player.color)
  }
}

function onSellStock(stock) {
  const player = getCurrentPlayer(state)
  if (sellStock(player, stock, 1)) {
    addLog(state, `${player.name} 卖出 ${stock.name} 1股 @${stock.price}`, player.color)
  }
}

// 银行操作
function onBankAction() {
  const player = getCurrentPlayer(state)
  console.log('[银行操作] 计算前:', { money: player.money, bankLoan: player.bankLoan, netWorth: player.netWorth })
  calcNetWorth(player, state.stocks, state.players)
  console.log('[银行操作] 计算后:', { netWorth: player.netWorth })
}

// 使用道具
function onUseItem(itemType) {
  const player = getCurrentPlayer(state)
  if (!player || player.isAI) return

  if (itemType === 'dice_control') {
    // 遥控骰子 - 弹出选择
    const val = prompt('输入骰子点数 (2-12):')
    const num = parseInt(val)
    if (num >= 2 && num <= 12) {
      useItem(player, 'dice_control')
      state.currentDice = rollFixed(num)
      addLog(state, `${player.name} 使用遥控骰子，掷出 ${num}`, player.color)
    }
  }
}

// 建房模式
function onBuildMode() {
  buildMode.value = !buildMode.value
}

const buildableTiles = computed(() => {
  const player = currentPlayer.value
  if (!player) return []
  return player.properties.filter(idx => {
    const tile = BOARD[idx]
    if (tile.type !== TILE_TYPES.PROPERTY || !tile.buildCost) return false
    if (!ownsFullGroup(player, tile.group)) return false
    const current = player.buildings[idx] || 0
    return current < 5 && player.money >= tile.buildCost
  })
})

function onBuild(idx) {
  const player = getCurrentPlayer(state)
  buildHouse(state, player, idx)
}

function tileName(idx) { return BOARD[idx]?.name || '' }
function buildingCount(idx) { return currentPlayer.value?.buildings?.[idx] || 0 }
function buildCost(idx) { return BOARD[idx]?.buildCost || 0 }

function getCardType() {
  // 判断当前卡片类型
  const tile = BOARD[currentPlayer.value?.position]
  if (tile?.type === TILE_TYPES.CHANCE) return 'chance'
  return 'destiny'
}

// 重置游戏
function resetGame() {
  const humanCount = state.players.filter(p => !p.isAI).length
  const aiCount = state.players.filter(p => p.isAI).length
  const targetNetWorth = state.targetNetWorth
  const newState = createGameState()
  Object.assign(state, newState)
  state.targetNetWorth = targetNetWorth
  state.players = initPlayers(humanCount, aiCount)
  state.stocks = initStocks()
  startGame(state)
  nextTick(() => processCurrentTurn())
}

const delay = ms => new Promise(r => setTimeout(r, ms))
</script>

<style scoped>
.app {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.game-layout {
  display: flex;
  height: 100%;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

.sidebar-left {
  width: 220px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  background: rgba(0,0,0,0.2);
}

.main-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.sidebar-right {
  width: 240px;
  padding: 12px;
  background: rgba(0,0,0,0.2);
  overflow-y: auto;
}

.center-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
}

.turn-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 0.9em;
  color: rgba(255,255,255,0.7);
}

.turn-info span:last-child {
  font-weight: 700;
  font-size: 1.1em;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons.secondary {
  gap: 6px;
}

.btn-roll {
  padding: 12px 32px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: #fff;
  font-weight: 700;
  font-size: 1.05em;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(231,76,60,0.3);
}

.btn-roll:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(231,76,60,0.4);
}

.btn-roll:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-end {
  padding: 12px 24px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.btn-end:hover {
  background: rgba(255,255,255,0.15);
}

.btn-sm {
  padding: 6px 14px;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.8);
  font-size: 0.8em;
  cursor: pointer;
}

.btn-sm:hover:not(:disabled) {
  background: rgba(255,255,255,0.15);
}

.btn-sm:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* 悬浮提示 */
.btn-sm[data-tooltip] {
  position: relative;
}

.btn-sm[data-tooltip]::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.85);
  color: #fff;
  font-size: 12px;
  line-height: 1.5;
  padding: 8px 12px;
  border-radius: 8px;
  white-space: normal;
  width: 200px;
  text-align: center;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.btn-sm[data-tooltip]:hover::after {
  opacity: 1;
}

.build-panel {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 10px;
  max-height: 200px;
  overflow-y: auto;
  width: 100%;
}

.build-title {
  font-size: 0.85em;
  color: rgba(255,255,255,0.6);
  margin-bottom: 8px;
}

.build-option {
  padding: 6px 10px;
  background: rgba(255,255,255,0.05);
  border-radius: 6px;
  margin-bottom: 4px;
  font-size: 0.8em;
  cursor: pointer;
  color: rgba(255,255,255,0.8);
}

.build-option:hover {
  background: rgba(255,255,255,0.15);
}

.game-over {
  text-align: center;
  animation: pulse 1.5s infinite;
}

.winner-text {
  font-size: 1.5em;
  font-weight: 700;
  color: #f1c40f;
  margin-bottom: 12px;
}
</style>
