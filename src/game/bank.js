// 银行系统逻辑
import { BANK_DEPOSIT_RATE, BANK_MORTGAGE_RATE, BANK_MORTGAGE_REPAY_RATE, BOARD } from './constants.js'

// 存款利息
export function applyDepositInterest(player) {
  if (player.bankDeposit > 0) {
    const interest = Math.floor(player.bankDeposit * BANK_DEPOSIT_RATE)
    player.bankDeposit += interest
    return interest
  }
  return 0
}

// 存款
export function deposit(player, amount) {
  if (player.money < amount || amount <= 0) return false
  player.money -= amount
  player.bankDeposit = (player.bankDeposit || 0) + amount
  return true
}

// 取款
export function withdraw(player, amount) {
  if (player.bankDeposit < amount || amount <= 0) return false
  player.bankDeposit -= amount
  player.money += amount
  return true
}

// 抵押地产
export function mortgageProperty(player, tileIndex) {
  const tile = BOARD[tileIndex]
  if (!tile.price) return false
  if (player.properties.indexOf(tileIndex) === -1) return false
  const mortgageValue = Math.floor(tile.price * BANK_MORTGAGE_RATE)
  player.money += mortgageValue
  player.mortgaged = player.mortgaged || []
  player.mortgaged = [...player.mortgaged, tileIndex]
  return mortgageValue
}

// 赎回地产
export function unmortgageProperty(player, tileIndex) {
  if (!player.mortgaged || player.mortgaged.indexOf(tileIndex) === -1) return false
  const tile = BOARD[tileIndex]
  const repayValue = Math.floor(tile.price * BANK_MORTGAGE_REPAY_RATE)
  if (player.money < repayValue) return false
  player.money -= repayValue
  player.mortgaged = player.mortgaged.filter(i => i !== tileIndex)
  return true
}

// 贷款
export function takeLoan(player, amount) {
  player.bankLoan = (player.bankLoan || 0) + amount
  player.money += amount
  return true
}

// 还款
export function repayLoan(player, amount) {
  const repay = Math.min(amount, player.bankLoan || 0, player.money)
  if (repay <= 0) return false
  player.money -= repay
  player.bankLoan -= repay
  return true
}
