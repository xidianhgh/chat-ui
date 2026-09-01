// 道具系统
import { ITEM_NAMES } from './constants.js'

// 获取道具
export function addItem(player, itemType) {
  if (!player.items) {
    player.items = []
  }
  player.items.push(itemType)
  console.log(`[道具] ${player.name} 获得 ${ITEM_NAMES[itemType] || itemType}，当前道具:`, [...player.items])
}

// 使用道具
export function useItem(player, itemType) {
  if (!player.items) return false
  const idx = player.items.indexOf(itemType)
  if (idx === -1) return false
  player.items = player.items.filter((_, i) => i !== idx)
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
