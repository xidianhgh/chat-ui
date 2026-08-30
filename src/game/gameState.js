// 游戏状态管理
import { reactive } from 'vue'
import { INITIAL_MONEY, PLAYER_COLORS, PLAYER_NAMES, BOARD } from './constants.js'
import { createCardDecks } from './cards.js'
import { initStocks } from './stock.js'

export function createGameState() {
  return reactive({
    phase: 'setup', // setup, playing, ended
    players: [],
    currentPlayerIndex: 0,
    turnCount: 0,
    stocks: [],
    cardDecks: createCardDecks(),
    logs: [],
    // 当前回合状态
    currentDice: null,
    doublesCount: 0,
    needAction: null, // null, 'buy_property', 'card', 'jail', 'pay_rent'
    pendingProperty: null,
    pendingCard: null,
    // 弹窗控制
    showPropertyModal: false,
    showCardModal: false,
    showStockPanel: false,
    showBankPanel: false,
    showDiceControl: false,
    // 动画
    animating: false,
    // 游戏结果
    winner: null
  })
}

export function initPlayers(humanCount, aiCount) {
  const total = humanCount + aiCount
  const players = []
  for (let i = 0; i < total; i++) {
    players.push({
      id: i,
      name: PLAYER_NAMES[i],
      color: PLAYER_COLORS[i],
      money: INITIAL_MONEY,
      position: 0,
      properties: [],
      buildings: {}, // tileIndex -> building count (1-4=houses, 5=hotel)
      isAI: i >= humanCount,
      inJail: false,
      jailTurns: 0,
      jailFreeCards: 0,
      items: [],
      stocks: {},
      bankDeposit: 0,
      bankLoan: 0,
      mortgaged: [],
      bankrupt: false,
      netWorth: INITIAL_MONEY
    })
  }
  return players
}

export function addLog(state, message) {
  const time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  state.logs.unshift({ time, message })
  if (state.logs.length > 200) state.logs.pop()
}

export function getCurrentPlayer(state) {
  return state.players[state.currentPlayerIndex]
}

// 计算玩家净资产
export function calcNetWorth(player, stocks, allPlayers) {
  let worth = player.money + (player.bankDeposit || 0)
  // 地产价值
  for (const tileIdx of player.properties) {
    const tile = BOARD[tileIdx]
    if (tile.price) {
      worth += tile.price
      const building = player.buildings[tileIdx] || 0
      if (building > 0) {
        worth += (tile.buildCost || 0) * building
      }
    }
  }
  // 股票价值
  if (player.stocks) {
    for (const [id, shares] of Object.entries(player.stocks)) {
      worth += stocks[id].price * shares
    }
  }
  // 减去贷款
  worth -= (player.bankLoan || 0)
  player.netWorth = Math.round(worth)
  return player.netWorth
}

// 检查玩家是否拥有同色全套
export function ownsFullGroup(player, group) {
  const groupTiles = BOARD.reduce((arr, t, i) => {
    if (t.type === 'property' && t.group === group) arr.push(i)
    return arr
  }, [])
  return groupTiles.every(i => player.properties.includes(i))
}

// 检查破产
export function checkBankruptcy(player) {
  return player.money <= 0 && player.netWorth <= 0
}
