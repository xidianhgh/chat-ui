<template>
  <div class="item-bar">
    <div v-if="!items || items.length === 0" class="empty">无道具</div>
    <div v-for="(item, idx) in items" :key="idx" class="item-chip" :title="getItemName(item)" @click="$emit('use-item', item)">
      {{ getItemIcon(item) }}
      <span class="item-label">{{ getItemName(item) }}</span>
    </div>
  </div>
</template>

<script setup>
import { ITEM_NAMES } from '../game/constants.js'

defineProps({
  items: Array
})

defineEmits(['use-item'])

function getItemName(type) {
  return ITEM_NAMES[type] || type
}

function getItemIcon(type) {
  const icons = {
    dice_control: '🎲',
    barrier: '🚧',
    teleport: '🌀',
    free_rent: '🎫',
    shield: '🛡️'
  }
  return icons[type] || '📦'
}
</script>

<style scoped>
.item-bar {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.empty {
  font-size: 0.8em;
  color: rgba(255,255,255,0.4);
}

.item-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8em;
  color: #fff;
}

.item-chip:hover {
  background: rgba(255,255,255,0.2);
  transform: scale(1.05);
}

.item-label {
  font-size: 0.75em;
}
</style>
