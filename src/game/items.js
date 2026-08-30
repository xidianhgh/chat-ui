// 道具系统
import { ITEM_NAMES } from './constants.js'

// 获取道具
export function addItem(player, itemType) {
  player.items = player.items || []
  player.items.push(itemType)
}

// 使用道具
export function useItem(player, itemType) {
  if (!player.items) return false
  const idx = player.items.indexOf(itemType)
  if (idx === -1) return false
  player.items.splice(idx, 1)
  return true
}

// 检查是否有某道具
export function hasItem(player, itemType) {
  return player.items && player.items.indexOf(itemType) !== -1
}

// 获取道具中文名
export function getItemName(itemType) {
  return ITEM_NAMES[itemType] || itemType
}
