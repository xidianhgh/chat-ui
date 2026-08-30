// 骰子逻辑
export function rollDice() {
  const d1 = Math.floor(Math.random() * 6) + 1
  const d2 = Math.floor(Math.random() * 6) + 1
  return { d1, d2, total: d1 + d2, isDouble: d1 === d2 }
}

export function rollFixed(total) {
  const d1 = Math.max(1, Math.min(6, Math.floor(total / 2)))
  const d2 = total - d1
  return { d1, d2, total, isDouble: d1 === d2 }
}
