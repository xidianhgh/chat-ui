<template>
  <div class="player-panel">
    <div v-for="player in players" :key="player.id"
         class="player-card" :class="{ active: player.id === currentPlayerId, bankrupt: player.bankrupt }">
      <div class="player-header" :style="{ borderLeftColor: player.color }">
        <div class="player-avatar" :style="{ background: player.color }">
          {{ player.name[0] }}
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
        <div class="stat">
          <span class="stat-label">地产</span>
          <span class="stat-value">{{ player.properties.length }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">净资产</span>
          <span class="stat-value">{{ player.netWorth }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">存款</span>
          <span class="stat-value">{{ player.bankDeposit || 0 }}</span>
        </div>
      </div>
      <div v-if="player.inJail" class="jail-indicator">🔒 监狱中 ({{ player.jailTurns }}/3)</div>
      <div v-if="player.items && player.items.length" class="items-indicator">
        🎒 {{ player.items.length }}个道具
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  players: Array,
  currentPlayerId: Number
})
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
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #fff;
  font-size: 14px;
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
</style>
