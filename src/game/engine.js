// 游戏核心引擎
import { BOARD, TILE_TYPES, START_SALARY, JAIL_FINE, GROUP_TILES, RAILROADS, getRailroadRent, getUtilityRent } from './constants.js'
import { rollDice, rollFixed } from './dice.js'
import { drawCard } from './cards.js'
import { fluctuateStock } from './stock.js'
import { applyDepositInterest } from './bank.js'
import { addItem, hasItem, useItem } from './items.js'
import { addLog, getCurrentPlayer, calcNetWorth, ownsFullGroup, checkBankruptcy } from './gameState.js'
import { aiFreeActions, aiDecideBuy } from './ai.js'

const delay = ms => new Promise(r => setTimeout(r, ms))

// 开始游戏
export function startGame(state) {
  state.phase = 'playing'
  state.currentPlayerIndex = 0
  state.turnCount = 1
  addLog(state, '游戏开始！')
}

// 移动玩家
function movePlayer(state, player, steps) {
  const oldPos = player.position
  const newPos = (oldPos + steps) % 40
  // 经过起点获得工资
  if (newPos < oldPos && steps > 0) {
    player.money += START_SALARY
    addLog(state, `${player.name} 经过起点，获得 ${START_SALARY} 元`)
  }
  player.position = newPos
}

// 移动到指定位置
function moveToPosition(state, player, position) {
  const oldPos = player.position
  if (position < oldPos) {
    player.money += START_SALARY
    addLog(state, `${player.name} 经过起点，获得 ${START_SALARY} 元`)
  }
  player.position = position
}

// 计算租金
function calcRent(state, tileIndex, diceTotal) {
  const tile = BOARD[tileIndex]
  const owner = state.players.find(p => p.properties.includes(tileIndex))
  if (!owner || owner.bankrupt) return { amount: 0, to: null }

  // 抵押中的地产不收租
  if (owner.mortgaged && owner.mortgaged.includes(tileIndex)) return { amount: 0, to: null }

  if (tile.type === TILE_TYPES.RAILROAD) {
    const count = RAILROADS.filter(r => owner.properties.includes(r)).length
    return { amount: getRailroadRent(count), to: owner }
  }

  if (tile.type === TILE_TYPES.UTILITY) {
    const utilTiles = BOARD.reduce((a, t, i) => {
      if (t.type === TILE_TYPES.UTILITY) a.push(i)
      return a
    }, [])
    const count = utilTiles.filter(u => owner.properties.includes(u)).length
    return { amount: getUtilityRent(count, diceTotal), to: owner }
  }

  if (tile.type === TILE_TYPES.PROPERTY) {
    const building = owner.buildings[tileIndex] || 0
    let rent
    if (building >= 5) {
      // 酒店：4栋租金的双倍
      rent = tile.rent[4] * 2
    } else {
      rent = tile.rent[building]
      // 空地且拥有全套：双倍租金
      if (building === 0 && ownsFullGroup(owner, tile.group)) {
        rent *= 2
      }
    }
    return { amount: rent, to: owner }
  }

  return { amount: 0, to: null }
}

// 处理格子事件
async function handleTileEvent(state, player, diceTotal) {
  const tile = BOARD[player.position]

  switch (tile.type) {
    case TILE_TYPES.GO:
      addLog(state, `${player.name} 到达起点`)
      break

    case TILE_TYPES.PROPERTY:
    case TILE_TYPES.RAILROAD:
    case TILE_TYPES.UTILITY: {
      const owner = state.players.find(p => p.properties.includes(player.position))
      if (!owner) {
        // 无主地产 - 可以购买
        if (player.money >= tile.price) {
          state.pendingProperty = { tileIndex: player.position, tile }
          if (player.isAI) {
            // AI 自动决定是否购买
            await delay(500)
            aiDecideBuy(state, player, tile)
          } else {
            state.showPropertyModal = true
            state.needAction = 'buy_property'
          }
        } else {
          addLog(state, `${player.name} 资金不足，无法购买 ${tile.name}`)
        }
      } else if (owner.id !== player.id && !owner.bankrupt) {
        // 支付租金
        const { amount, to } = calcRent(state, player.position, diceTotal)
        if (amount > 0) {
          // 检查免租牌
          if (hasItem(player, 'free_rent')) {
            useItem(player, 'free_rent')
            addLog(state, `${player.name} 使用免租牌，免交 ${amount} 元租金`)
          } else {
            player.money -= amount
            to.money += amount
            addLog(state, `${player.name} 向 ${to.name} 支付 ${tile.name} 租金 ${amount} 元`)
          }
        }
      }
      break
    }

    case TILE_TYPES.CHANCE: {
      const card = drawCard(state.cardDecks, 'chance')
      addLog(state, `${player.name} 抽到机会卡：${card.text}`)
      state.pendingCard = card
      if (player.isAI) {
        await delay(500)
        await applyCardEffect(state, player, card, diceTotal)
      } else {
        state.showCardModal = true
        state.needAction = 'card'
      }
      break
    }

    case TILE_TYPES.DESTINY: {
      const card = drawCard(state.cardDecks, 'destiny')
      addLog(state, `${player.name} 抽到命运卡：${card.text}`)
      state.pendingCard = card
      if (player.isAI) {
        await delay(500)
        await applyCardEffect(state, player, card, diceTotal)
      } else {
        state.showCardModal = true
        state.needAction = 'card'
      }
      break
    }

    case TILE_TYPES.TAX:
      player.money -= tile.amount
      addLog(state, `${player.name} 缴纳税款 ${tile.amount} 元`)
      break

    case TILE_TYPES.GO_TO_JAIL:
      sendToJail(state, player)
      break

    case TILE_TYPES.JAIL:
      addLog(state, `${player.name} 探访监狱`)
      break

    case TILE_TYPES.FREE_PARKING:
      addLog(state, `${player.name} 免费停车，休息一下`)
      break
  }
}

// 送入监狱
function sendToJail(state, player) {
  player.position = 10
  player.inJail = true
  player.jailTurns = 0
  addLog(state, `${player.name} 被送进监狱！`)
}

// 应用卡片效果
async function applyCardEffect(state, player, card, diceTotal) {
  const eff = card.effect
  switch (eff.type) {
    case 'money':
      player.money += eff.amount
      if (eff.amount > 0) {
        addLog(state, `${player.name} 获得 ${eff.amount} 元`)
      } else {
        addLog(state, `${player.name} 支付 ${Math.abs(eff.amount)} 元`)
      }
      break

    case 'move_to':
      state.movingPlayerId = player.id
      moveToPosition(state, player, eff.position)
      addLog(state, `${player.name} 移动到 ${BOARD[eff.position].name}`)
      await delay(600)
      state.movingPlayerId = null
      await handleTileEvent(state, player, diceTotal)
      break

    case 'move_back':
      state.movingPlayerId = player.id
      player.position = (player.position - eff.steps + 40) % 40
      addLog(state, `${player.name} 后退 ${eff.steps} 格到 ${BOARD[player.position].name}`)
      await delay(600)
      state.movingPlayerId = null
      await handleTileEvent(state, player, diceTotal)
      break

    case 'go_to_jail':
      state.movingPlayerId = player.id
      sendToJail(state, player)
      await delay(600)
      state.movingPlayerId = null
      break

    case 'get_item':
      if (eff.item === 'jail_free') {
        player.jailFreeCards = (player.jailFreeCards || 0) + 1
        addLog(state, `${player.name} 获得免费出狱卡`)
      } else {
        addItem(player, eff.item)
        addLog(state, `${player.name} 获得道具`)
      }
      break

    case 'repair': {
      let cost = 0
      for (const tileIdx of player.properties) {
        const b = player.buildings[tileIdx] || 0
        if (b === 5) cost += eff.hotel
        else cost += b * eff.house
      }
      if (cost > 0) {
        player.money -= cost
        addLog(state, `${player.name} 支付维修费 ${cost} 元`)
      }
      break
    }

    case 'birthday': {
      let total = 0
      for (const p of state.players) {
        if (p.id !== player.id && !p.bankrupt) {
          p.money -= eff.amount
          total += eff.amount
        }
      }
      player.money += total
      addLog(state, `${player.name} 过生日，收到 ${total} 元`)
      break
    }
  }
}

// 购买地产
export function buyProperty(state, player, tile) {
  if (player.money < tile.price) return false
  player.money -= tile.price
  // 使用数组替换而非 push，确保 Vue 响应式检测到变化
  player.properties = [...player.properties, tile.id]
  addLog(state, `${player.name} 购买了 ${tile.name}，花费 ${tile.price} 元`)
  return true
}

// 建房
export function buildHouse(state, player, tileIndex) {
  const tile = BOARD[tileIndex]
  if (!tile.buildCost) return false
  if (player.money < tile.buildCost) return false
  if (!ownsFullGroup(player, tile.group)) return false
  const current = player.buildings[tileIndex] || 0
  if (current >= 5) return false
  // 均匀建房规则简化：允许直接建
  // 使用对象替换而非直接赋值，确保 Vue 响应式检测到变化
  player.buildings = { ...player.buildings, [tileIndex]: current + 1 }
  player.money -= tile.buildCost
  const label = current + 1 === 5 ? '酒店' : `${current + 1}栋房子`
  addLog(state, `${player.name} 在 ${tile.name} 建造了${label}，花费 ${tile.buildCost} 元`)
  return true
}

// 处理监狱回合
async function handleJailTurn(state, player, diceResult) {
  // 尝试使用免费出狱卡
  if (player.jailFreeCards > 0) {
    player.jailFreeCards--
    player.inJail = false
    player.jailTurns = 0
    addLog(state, `${player.name} 使用免费出狱卡`)
    return false // 不消耗骰子
  }

  // 掷骰子判断是否出狱
  if (diceResult.isDouble) {
    player.inJail = false
    player.jailTurns = 0
    addLog(state, `${player.name} 掷出双数，成功出狱！`)
    return false // 使用本次骰子移动
  }

  player.jailTurns++
  if (player.jailTurns >= 3) {
    // 第三次必须出狱，交罚款
    player.money -= JAIL_FINE
    player.inJail = false
    player.jailTurns = 0
    addLog(state, `${player.name} 缴纳 ${JAIL_FINE} 元罚款出狱`)
    return false
  }

  addLog(state, `${player.name} 在监狱中 (第${player.jailTurns}回合)`)
  return true // 跳过本回合
}

// 执行一个玩家的回合
export async function executeTurn(state) {
  const player = getCurrentPlayer(state)
  console.log(`[引擎] executeTurn 开始, 玩家: ${player.name}, 破产: ${player.bankrupt}`)
  if (player.bankrupt) {
    nextPlayer(state)
    return
  }

  state.animating = true
  addLog(state, `--- ${player.name} 的回合 (第${state.turnCount}轮) ---`)

  // 存款利息
  const interest = applyDepositInterest(player)
  if (interest > 0) {
    addLog(state, `${player.name} 获得存款利息 ${interest} 元`)
  }

  // 监狱处理
  let diceResult
  if (player.inJail) {
    diceResult = rollDice()
    state.currentDice = diceResult
    addLog(state, `${player.name} 掷出 [${diceResult.d1}+${diceResult.d2}=${diceResult.total}]`)

    const skipTurn = await handleJailTurn(state, player, diceResult)
    if (skipTurn) {
      // 继续坐牢，跳过本回合
      state.animating = false
      await delay(800)
      nextPlayer(state)
      return
    }
    // 出狱了：如果是掷双数出狱，用当前骰子移动；否则需要重新掷骰子
    if (!diceResult.isDouble) {
      // 用卡或罚款出狱，重新掷骰子
      diceResult = rollDice()
      state.currentDice = diceResult
      addLog(state, `${player.name} 掷出 [${diceResult.d1}+${diceResult.d2}=${diceResult.total}]`)
    }
    // 如果是双数出狱，diceResult 已经是出狱时的骰子，直接用它移动
  } else {
    // 正常掷骰子
    if (state.showDiceControl) {
      diceResult = state.currentDice || rollDice()
      state.showDiceControl = false
    } else {
      diceResult = rollDice()
    }
    state.currentDice = diceResult
    addLog(state, `${player.name} 掷出 [${diceResult.d1}+${diceResult.d2}=${diceResult.total}]`)
  }

  // 移动
  state.movingPlayerId = player.id
  await movePlayer(state, player, diceResult.total)
  addLog(state, `${player.name} 移动到 ${BOARD[player.position].name}`)

  await delay(600)
  state.movingPlayerId = null

  // 处理格子事件
  await handleTileEvent(state, player, diceResult.total)

  // 如果需要等待人类操作（购买地产弹窗等），暂停回合并返回
  // 操作完成后由 App.vue 调用 finishTurnProcessing 继续
  if (state.needAction) {
    console.log(`[引擎] 等待人类操作, needAction=${state.needAction}`)
    state.animating = false
    return
  }

  console.log(`[引擎] 调用 finishTurnProcessing`)
  await finishTurnProcessing(state, player, diceResult)
  console.log(`[引擎] finishTurnProcessing 完成`)
}

// 回合结束处理：破产检查、股票波动、AI操作、双数判定、切换玩家
export async function finishTurnProcessing(state, player, diceResult) {
  // 检查破产
  calcNetWorth(player, state.stocks, state.players)
  if (player.money < 0 && player.netWorth < 0) {
    player.bankrupt = true
    addLog(state, `${player.name} 破产了！`)
    const alive = state.players.filter(p => !p.bankrupt)
    if (alive.length === 1) {
      state.winner = alive[0]
      state.phase = 'ended'
      addLog(state, `游戏结束！${alive[0].name} 获胜！`)
      state.animating = false
      return
    }
  }

  // 股票波动
  state.stocks = fluctuateStock(state.stocks)

  state.animating = false

  // AI 自由操作阶段
  if (player.isAI && !player.bankrupt && state.phase === 'playing') {
    await delay(300)
    await aiFreeActions(state, player)
  }

  await delay(500)
  nextPlayer(state)
}

// 切换到下一个玩家
function nextPlayer(state) {
  let next = (state.currentPlayerIndex + 1) % state.players.length
  let safety = 0
  while (state.players[next].bankrupt && safety < state.players.length) {
    next = (next + 1) % state.players.length
    safety++
  }
  if (next <= state.currentPlayerIndex) {
    state.turnCount++
  }
  state.currentPlayerIndex = next
  state.currentDice = null
  state.needAction = null
}

// 确认卡片效果
export async function confirmCard(state) {
  const player = getCurrentPlayer(state)
  const previousAction = state.needAction
  if (state.pendingCard) {
    await applyCardEffect(state, player, state.pendingCard, state.currentDice?.total || 0)
  }
  state.showCardModal = false
  state.pendingCard = null
  // 仅当 needAction 未被卡片效果改变时才清除
  // （卡片可能导致移动到新格子并触发购买弹窗，此时 needAction 已被更新）
  if (state.needAction === previousAction) {
    state.needAction = null
  }
}

// 结束回合
export function endTurn(state) {
  const player = getCurrentPlayer(state)
  calcNetWorth(player, state.stocks, state.players)

  nextPlayer(state)
}
