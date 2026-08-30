<template>
  <div class="game-log">
    <div class="log-title">游戏日志</div>
    <div class="log-list" ref="logList">
      <div v-for="(log, idx) in logs" :key="idx" class="log-entry">
        <span class="log-time">{{ log.time }}</span>
        <span class="log-msg">{{ log.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  logs: Array
})
</script>

<style scoped>
.game-log {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.log-title {
  font-weight: 700;
  color: #fff;
  font-size: 0.9em;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.log-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.log-list::-webkit-scrollbar {
  width: 4px;
}

.log-list::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.2);
  border-radius: 2px;
}

.log-entry {
  display: flex;
  gap: 6px;
  padding: 3px 0;
  font-size: 0.75em;
  line-height: 1.4;
}

.log-time {
  color: rgba(255,255,255,0.3);
  white-space: nowrap;
  flex-shrink: 0;
}

.log-msg {
  color: rgba(255,255,255,0.8);
}
</style>
