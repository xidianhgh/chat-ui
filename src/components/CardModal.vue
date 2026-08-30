<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('confirm')">
    <div class="modal-card card-modal">
      <div class="card-type" :class="type">{{ type === 'chance' ? '机会' : '命运' }}</div>
      <div class="card-icon">{{ type === 'chance' ? '❓' : '🌟' }}</div>
      <div class="card-text">{{ card?.text }}</div>
      <button class="btn-confirm" @click="$emit('confirm')">确定</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: Boolean,
  card: Object,
  type: String // 'chance' or 'destiny'
})

defineEmits(['confirm'])
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.card-modal {
  background: #fff;
  border-radius: 16px;
  padding: 30px;
  min-width: 280px;
  text-align: center;
  box-shadow: 0 16px 48px rgba(0,0,0,0.3);
  animation: cardFlip 0.4s ease;
}

@keyframes cardFlip {
  from { transform: rotateY(90deg) scale(0.5); opacity: 0; }
  to { transform: rotateY(0) scale(1); opacity: 1; }
}

.card-type {
  display: inline-block;
  padding: 4px 16px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
  color: #fff;
  margin-bottom: 16px;
}

.card-type.chance { background: #3498db; }
.card-type.destiny { background: #9b59b6; }

.card-icon {
  font-size: 3em;
  margin: 10px 0;
}

.card-text {
  font-size: 1.1em;
  color: #333;
  margin: 16px 0;
  line-height: 1.5;
}

.btn-confirm {
  padding: 10px 40px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  font-size: 1em;
  margin-top: 10px;
}

.btn-confirm:hover { opacity: 0.9; }
</style>
