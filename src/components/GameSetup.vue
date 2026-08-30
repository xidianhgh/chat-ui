<template>
  <div class="game-setup">
    <div class="setup-card">
      <h1>🎲 大富翁</h1>
      <p class="subtitle">经典棋盘策略游戏</p>

      <div class="setup-section">
        <label>人类玩家</label>
        <div class="player-select">
          <button v-for="n in 4" :key="'h'+n" :class="{ active: humanCount === n }" @click="humanCount = n">{{ n }}</button>
        </div>
      </div>

      <div class="setup-section">
        <label>AI 电脑</label>
        <div class="player-select">
          <button v-for="n in 3" :key="'a'+n" :class="{ active: aiCount === n }" @click="aiCount = n">{{ n }}</button>
        </div>
      </div>

      <div class="setup-info">
        <span>总玩家：{{ humanCount + aiCount }}</span>
        <span v-if="humanCount + aiCount < 2" class="warning">至少需要2名玩家</span>
        <span v-if="humanCount + aiCount > 4" class="warning">最多4名玩家</span>
      </div>

      <div class="player-preview">
        <div v-for="i in humanCount + aiCount" :key="i" class="player-chip"
             :style="{ background: colors[i-1] }">
          {{ names[i-1] }}
          <span v-if="i > humanCount" class="ai-tag">AI</span>
        </div>
      </div>

      <button class="start-btn" :disabled="humanCount + aiCount < 2 || humanCount + aiCount > 4" @click="$emit('start', humanCount, aiCount)">
        开始游戏
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { PLAYER_COLORS, PLAYER_NAMES } from '../game/constants.js'

defineEmits(['start'])

const humanCount = ref(1)
const aiCount = ref(2)
const colors = PLAYER_COLORS
const names = PLAYER_NAMES
</script>

<style scoped>
.game-setup {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

.setup-card {
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  color: #fff;
  min-width: 380px;
}

.setup-card h1 {
  font-size: 2.5em;
  margin-bottom: 5px;
}

.subtitle {
  color: rgba(255,255,255,0.6);
  margin-bottom: 30px;
}

.setup-section {
  margin: 20px 0;
}

.setup-section label {
  display: block;
  margin-bottom: 10px;
  font-size: 0.95em;
  color: rgba(255,255,255,0.8);
}

.player-select button {
  width: 48px;
  height: 48px;
  margin: 0 6px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  color: #fff;
  font-size: 1.2em;
  cursor: pointer;
  transition: all 0.2s;
}

.player-select button.active {
  background: rgba(255,255,255,0.2);
  border-color: #e74c3c;
  box-shadow: 0 0 12px rgba(231,76,60,0.4);
}

.player-select button:hover {
  background: rgba(255,255,255,0.15);
}

.setup-info {
  margin: 15px 0;
  font-size: 0.9em;
  color: rgba(255,255,255,0.7);
}

.warning {
  color: #e74c3c;
  margin-left: 10px;
}

.player-preview {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.player-chip {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 600;
  color: #fff;
}

.ai-tag {
  font-size: 0.7em;
  background: rgba(0,0,0,0.3);
  padding: 1px 6px;
  border-radius: 8px;
  margin-left: 4px;
}

.start-btn {
  margin-top: 20px;
  padding: 14px 50px;
  font-size: 1.1em;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: #fff;
  cursor: pointer;
  transition: all 0.3s;
}

.start-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(231,76,60,0.4);
}

.start-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
