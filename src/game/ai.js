// AI 决策逻辑
import { BOARD, TILE_TYPES } from './constants.js'
import { buyStock, sellStock } from './stock.js'
import { deposit } from './bank.js'
import { addLog, ownsFullGroup } from './gameState.js'

const delay = ms => new Promise(r => setTimeout(r, ms))

// AI 购买决策
export function aiDecideBuy(state, player, tile) {
  const buyThreshold = tile.price * 1.5
  if (player.money > buyThreshold || (tile.group && ownsFullGroup(player, tile.group))) {
    doBuyProperty(state, player, tile)
  } else if (player.money > tile.price * 0.8) {
    // 70% 概率购买
    if (Math.random() < 0.7) {
      doBuyProperty(state, player, tile)
    } else {
      addLog(state, `${player.name} 决定不买 ${tile.name}`, player.color)
    }
  } else {
    addLog(state, `${player.name} 资金不足，放弃购买 ${tile.name}`, player.color)
  }
}

// AI 执行购买（内联逻辑，避免循环依赖）
function doBuyProperty(state, player, tile) {
  if (player.money < tile.price) return
  player.money -= tile.price
  player.properties = [...player.properties, tile.id]
  addLog(state, `${player.name} 购买了 ${tile.name}，花费 ${tile.price} 元`, player.color)
}

// AI 自由操作阶段
export async function aiFreeActions(state, player) {
  // 1. 尝试建房
  await aiTryBuild(state, player)
  await delay(300)

  // 2. 尝试买股票
  await aiTryStocks(state, player)
  await delay(300)

  // 3. 尝试存款
  aiTryDeposit(player)
}

// AI 建房决策
async function aiTryBuild(state, player) {
  for (const tileIdx of player.properties) {
    const tile = BOARD[tileIdx]
    if (tile.type !== TILE_TYPES.PROPERTY || !tile.buildCost) continue
    if (!ownsFullGroup(player, tile.group)) continue

    const current = player.buildings[tileIdx] || 0
    if (current >= 5) continue

    // 保留至少 2000 元现金
    if (player.money - tile.buildCost > 2000) {
      // 内联建房逻辑，避免循环依赖
      player.buildings = { ...player.buildings, [tileIdx]: current + 1 }
      player.money -= tile.buildCost
      const label = current + 1 === 5 ? '酒店' : `${current + 1}栋房子`
      addLog(state, `${player.name} 在 ${tile.name} 建造了${label}，花费 ${tile.buildCost} 元`, player.color)
    }
  }
}

// AI 股票决策
async function aiTryStocks(state, player) {
  if (player.money < 1000) return

  // 简单策略：低价买入，高价卖出
  for (const stock of state.stocks) {
    const owned = player.stocks[stock.id] || 0
    const avgCost = stock.history[0] // 简化：用初始价作为参考

    if (stock.price < avgCost * 0.9 && player.money > 2000) {
      // 低价买入
      const shares = Math.min(5, Math.floor(player.money * 0.1 / stock.price))
      if (shares > 0) {
        buyStock(player, stock, shares)
        addLog(state, `${player.name} 买入 ${stock.name} ${shares}股`, player.color)
      }
    } else if (stock.price > avgCost * 1.3 && owned > 0) {
      // 高价卖出
      sellStock(player, stock, owned)
      addLog(state, `${player.name} 卖出 ${stock.name} ${owned}股`, player.color)
    }
  }
}

// AI 存款决策
function aiTryDeposit(player) {
  if (player.money > 5000 && !player.bankLoan) {
    const depositAmount = Math.floor(player.money * 0.3)
    deposit(player, depositAmount)
  }
}
