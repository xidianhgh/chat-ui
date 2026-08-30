// 股票市场逻辑
import { INITIAL_STOCKS } from './constants.js'

export function initStocks() {
  return INITIAL_STOCKS.map(s => ({
    ...s,
    price: s.price,
    history: [...s.history]
  }))
}

// 股价波动
export function fluctuateStock(stocks) {
  return stocks.map(s => {
    const change = (Math.random() - 0.45) * 10 // 略微上涨倾向
    const newPrice = Math.max(10, Math.round(s.price + change))
    return {
      ...s,
      price: newPrice,
      history: [...s.history, newPrice]
    }
  })
}

// 购买股票
export function buyStock(player, stock, shares) {
  const cost = stock.price * shares
  if (player.money < cost) return false
  player.money -= cost
  if (!player.stocks) player.stocks = {}
  player.stocks[stock.id] = (player.stocks[stock.id] || 0) + shares
  return true
}

// 卖出股票
export function sellStock(player, stock, shares) {
  if (!player.stocks || !player.stocks[stock.id] || player.stocks[stock.id] < shares) return false
  const income = stock.price * shares
  player.money += income
  player.stocks[stock.id] -= shares
  if (player.stocks[stock.id] === 0) delete player.stocks[stock.id]
  return true
}

// 计算股票资产总值
export function getStockValue(player, stocks) {
  if (!player.stocks) return 0
  let total = 0
  for (const [id, shares] of Object.entries(player.stocks)) {
    total += stocks[id].price * shares
  }
  return total
}
