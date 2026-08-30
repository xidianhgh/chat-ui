<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <h3>购买地产</h3>
      <div v-if="tile" class="property-info">
        <div class="property-color" :style="{ background: groupColor }"></div>
        <div class="property-name">{{ tile.name }}</div>
        <div class="property-details">
          <div class="detail-row">
            <span>价格</span>
            <span class="price">{{ tile.price }} 元</span>
          </div>
          <div v-if="tile.rent" class="detail-row">
            <span>空地租金</span>
            <span>{{ tile.rent[0] }} 元</span>
          </div>
          <div v-if="tile.rent" class="rent-table">
            <div class="detail-row"><span>1栋房子</span><span>{{ tile.rent[1] }} 元</span></div>
            <div class="detail-row"><span>2栋房子</span><span>{{ tile.rent[2] }} 元</span></div>
            <div class="detail-row"><span>3栋房子</span><span>{{ tile.rent[3] }} 元</span></div>
            <div class="detail-row"><span>4栋房子</span><span>{{ tile.rent[4] }} 元</span></div>
            <div class="detail-row"><span>酒店</span><span>{{ Math.floor(tile.rent[4] * 1.2) }} 元</span></div>
          </div>
          <div v-if="tile.buildCost" class="detail-row">
            <span>建房费用</span>
            <span>{{ tile.buildCost }} 元/栋</span>
          </div>
        </div>
      </div>
      <div class="modal-actions">
        <button class="btn-buy" @click="$emit('buy')">购买</button>
        <button class="btn-skip" @click="$emit('close')">放弃</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { COLOR_GROUPS } from '../game/constants.js'

const props = defineProps({
  show: Boolean,
  tile: Object
})

defineEmits(['buy', 'close'])

const groupColor = computed(() => COLOR_GROUPS[props.tile?.group] || '#999')
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

.modal-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  min-width: 300px;
  box-shadow: 0 16px 48px rgba(0,0,0,0.3);
}

.modal-card h3 {
  margin: 0 0 16px;
  color: #333;
}

.property-color {
  height: 8px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.property-name {
  font-size: 1.3em;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 0.9em;
  color: #555;
}

.price {
  font-weight: 700;
  color: #e74c3c;
}

.rent-table {
  border-top: 1px solid #eee;
  margin-top: 4px;
  padding-top: 4px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-buy {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  font-size: 1em;
}

.btn-skip {
  flex: 1;
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 10px;
  background: #fff;
  color: #666;
  font-weight: 600;
  cursor: pointer;
  font-size: 1em;
}

.btn-buy:hover { opacity: 0.9; }
.btn-skip:hover { background: #f5f5f5; }
</style>
