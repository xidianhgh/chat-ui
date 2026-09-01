<template>
  <div class="player-panel">
    <div v-for="player in players" :key="player.id"
         class="player-card" :class="{ active: player.id === currentPlayerId, bankrupt: player.bankrupt }">
      <div class="player-header" :style="{ borderLeftColor: player.color }">
        <div class="player-avatar" :style="{ '--token-color': player.color }">
          <div class="avatar-head"></div>
          <div class="avatar-base"></div>
        </div>
        <div class="player-info">
          <div class="player-name">
            {{ player.name }}
            <span v-if="player.isAI" class="ai-badge">AI</span>
            <span v-if="player.bankrupt" class="bankrupt-badge">破产</span>
          </div>
          <div class="player-money">{{ player.money }} 元</div>
        </div>
      </div>
      <div class="player-stats">
        <div class="stat clickable" @click="toggleProperties(player.id)">
          <span class="stat-label">地产</span>
          <span class="stat-value">{{ player.properties.length }} <span v-if="player.properties.length" class="toggle-hint">{{ expanded[player.id] ? '▲' : '▼' }}</span></span>
        </div>
        <div class="stat">
          <span class="stat-label">净资产</span>
          <span class="stat-value">{{ player.netWorth }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">存款</span>
          <span class="stat-value">{{ player.bankDeposit || 0 }}</span>
        </div>
        <div class="stat" v-if="player.bankLoan">
          <span class="stat-label">贷款</span>
          <span class="stat-value loan-value">{{ player.bankLoan }}</span>
        </div>
      </div>
      <!-- 地产列表 -->
      <div v-if="expanded[player.id] && player.properties.length" class="property-list">
        <div v-for="tileIdx in player.properties" :key="tileIdx" class="property-item">
          <span class="property-dot" :style="{ background: getPropertyColor(tileIdx) }"></span>
          <span class="property-name">{{ BOARD[tileIdx].name }}</span>
          <span v-if="player.buildings[tileIdx]" class="property-building">{{ getBuildingLabel(player.buildings[tileIdx]) }}</span>
          <span v-if="player.mortgaged && player.mortgaged.includes(tileIdx)" class="property-mortgaged">抵押</span>
        </div>
      </div>
      <div v-if="player.inJail" class="jail-indicator">🔒 监狱中 ({{ player.jailTurns }}/3)</div>
      <div v-if="player.items && player.items.length" class="items-indicator clickable" @click="toggleItems(player.id)">
        🎒 {{ player.items.length }}个道具 <span class="toggle-hint">{{ itemsExpanded[player.id] ? '▲' : '▼' }}</span>
      </div>
      <div v-if="itemsExpanded[player.id] && player.items && player.items.length" class="item-list">
        <div v-for="(item, idx) in player.items" :key="idx" class="item-item">
          <span class="item-icon">{{ getItemIcon(item) }}</span>
          <span class="item-name">{{ getItemLabel(item) }}</span>
        </div>
      </div>
      <div v-if="player.jailFreeCards && player.jailFreeCards > 0" class="jailfree-indicator">
        🗝️ 免费出狱卡 ×{{ player.jailFreeCards }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { BOARD, COLOR_GROUPS, ITEM_NAMES } from '../game/constants.js'

defineProps({
  players: Array,
  currentPlayerId: Number
})

const expanded = reactive({})
const itemsExpanded = reactive({})

function toggleProperties(playerId) {
  expanded[playerId] = !expanded[playerId]
}

function toggleItems(playerId) {
  itemsExpanded[playerId] = !itemsExpanded[playerId]
}

function getItemLabel(itemType) {
  return ITEM_NAMES[itemType] || itemType
}

function getPropertyColor(tileIdx) {
  const tile = BOARD[tileIdx]
  return COLOR_GROUPS[tile.group] || '#999'
}

function getBuildingLabel(level) {
  if (level === 5) return '🏨'
  return '🏠'.repeat(level)
}

const ITEM_ICONS = {
  dice_control: '🎲',
  barrier: '🚧',
  teleport: '🌀',
  free_rent: '🆓',
  shield: '🛡️'
}

function getItemIcon(itemType) {
  return ITEM_ICONS[itemType] || '📦'
}
</script>

<style scoped>
.player-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.player-card {
  background: rgba(255,255,255,0.08);
  border-radius: 10px;
  padding: 10px;
  transition: all 0.3s;
}

.player-card.active {
  background: rgba(255,255,255,0.15);
  box-shadow: 0 0 12px rgba(255,255,255,0.1);
}

.player-card.bankrupt {
  opacity: 0.4;
}

.player-header {
  display: flex;
  align-items: center;
  gap: 10px;
  border-left: 3px solid;
  padding-left: 8px;
}

.player-avatar {
  width: 36px;
  height: 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
}

.avatar-head {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--token-color);
  border: 1.5px solid rgba(0,0,0,0.2);
  box-shadow: inset 0 -2px 3px rgba(0,0,0,0.2), inset 0 2px 3px rgba(255,255,255,0.3);
  z-index: 1;
}

.avatar-base {
  width: 24px;
  height: 12px;
  background: var(--token-color);
  border: 1.5px solid rgba(0,0,0,0.2);
  border-radius: 4px 4px 6px 6px;
  margin-top: -4px;
  box-shadow: inset 0 -2px 3px rgba(0,0,0,0.15);
}

.player-name {
  font-weight: 600;
  color: #fff;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.ai-badge {
  font-size: 9px;
  background: rgba(255,255,255,0.2);
  padding: 1px 5px;
  border-radius: 6px;
}

.bankrupt-badge {
  font-size: 9px;
  background: #e74c3c;
  padding: 1px 5px;
  border-radius: 6px;
}

.player-money {
  color: #2ecc71;
  font-size: 14px;
  font-weight: 700;
}

.player-stats {
  display: flex;
  gap: 12px;
  margin-top: 6px;
  padding-left: 42px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 9px;
  color: rgba(255,255,255,0.5);
}

.stat-value {
  font-size: 12px;
  color: rgba(255,255,255,0.8);
  font-weight: 600;
}

.stat.clickable {
  cursor: pointer;
}

.stat.clickable:hover .stat-value {
  color: #fff;
}

.toggle-hint {
  font-size: 8px;
  opacity: 0.6;
}

.property-list {
  margin-top: 6px;
  padding-left: 42px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.property-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  color: rgba(255,255,255,0.75);
}

.property-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.property-name {
  flex: 1;
}

.property-building {
  font-size: 9px;
}

.property-mortgaged {
  font-size: 8px;
  color: #e74c3c;
  background: rgba(231,76,60,0.15);
  padding: 0 4px;
  border-radius: 3px;
}

.jail-indicator {
  font-size: 11px;
  color: #e74c3c;
  margin-top: 4px;
  padding-left: 42px;
}

.items-indicator {
  font-size: 11px;
  color: #f39c12;
  margin-top: 2px;
  padding-left: 42px;
}

.items-indicator.clickable {
  cursor: pointer;
}

.items-indicator.clickable:hover {
  color: #f1c40f;
}

.item-list {
  margin-top: 4px;
  padding-left: 42px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  animation: fadeIn 0.2s ease;
}

.item-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  color: rgba(255,255,255,0.75);
}

.item-icon {
  font-size: 11px;
}

.item-name {
  color: #f39c12;
}

.jailfree-indicator {
  font-size: 11px;
  color: #e67e22;
  margin-top: 2px;
  padding-left: 42px;
}
</style>
