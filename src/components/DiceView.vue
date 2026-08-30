<template>
  <div class="dice-container">
    <div class="dice" :class="{ rolling: rolling }">
      <div class="die die1">{{ rolling ? '?' : d1 }}</div>
      <div class="die die2">{{ rolling ? '?' : d2 }}</div>
    </div>
    <div v-if="total" class="dice-total">{{ total }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  d1: { type: Number, default: 1 },
  d2: { type: Number, default: 1 },
  total: { type: Number, default: 0 },
  rolling: { type: Boolean, default: false }
})
</script>

<style scoped>
.dice-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dice {
  display: flex;
  gap: 8px;
}

.die {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 8px;
  font-size: 1.3em;
  font-weight: 700;
  color: #333;
  box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
  transition: transform 0.3s;
}

.dice.rolling .die {
  animation: diceShake 0.1s infinite alternate;
}

@keyframes diceShake {
  from { transform: rotate(-10deg) scale(1.1); }
  to { transform: rotate(10deg) scale(0.9); }
}

.dice-total {
  font-size: 1.2em;
  font-weight: 700;
  color: #e74c3c;
  min-width: 30px;
}
</style>
