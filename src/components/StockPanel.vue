<template>
  <div v-if="show" class="panel-overlay" @click.self="$emit('close')">
    <div class="panel-card stock-panel">
      <div class="panel-header">
        <h3>📈 股票交易所</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      <div class="stock-list">
        <div v-for="stock in stocks" :key="stock.id" class="stock-row">
          <div class="stock-info">
            <div class="stock-name">{{ stock.name }}</div>
            <div class="stock-symbol">{{ stock.symbol }}</div>
          </div>
          <div class="stock-price" :class="priceClass(stock)">
            {{ stock.price }}
            <span class="price-change">{{ priceChange(stock) }}</span>
          </div>
          <div class="stock-owned">
            持有: {{ player?.stocks?.[stock.id] || 0 }}股
          </div>
          <div class="stock-actions">
            <button class="btn-buy-s" @click="onBuy(stock)" :disabled="!canBuy(stock)">买</button>
            <button class="btn-sell-s" @click="onSell(stock)" :disabled="!canSell(stock)">卖</button>
          </div>
        </div>
      </div>
      <div class="stock-footer">
        <span>现金: {{ player?.money || 0 }} 元</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  show: Boolean,
  stocks: Array,
  player: Object
})

const emit = defineEmits(['close', 'buy-stock', 'sell-stock'])

function priceClass(stock) {
  if (stock.history.length < 2) return ''
  const prev = stock.history[stock.history.length - 2]
  return stock.price >= prev ? 'up' : 'down'
}

function priceChange(stock) {
  if (stock.history.length < 2) return ''
  const prev = stock.history[stock.history.length - 2]
  const diff = stock.price - prev
  return diff >= 0 ? `+${diff}` : `${diff}`
}

function canBuy(stock) {
  return props.player && props.player.money >= stock.price
}

function canSell(stock) {
  return props.player?.stocks?.[stock.id] > 0
}

function onBuy(stock) {
  emit('buy-stock', stock)
}

function onSell(stock) {
  emit('sell-stock', stock)
}
</script>

<style scoped>
.panel-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.panel-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  min-width: 400px;
  box-shadow: 0 16px 48px rgba(0,0,0,0.3);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-header h3 { margin: 0; color: #333; }

.close-btn {
  background: none;
  border: none;
  font-size: 1.2em;
  cursor: pointer;
  color: #999;
  padding: 4px 8px;
}

.stock-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.stock-info { flex: 1; }
.stock-name { font-weight: 600; color: #333; font-size: 0.95em; }
.stock-symbol { font-size: 0.75em; color: #999; }

.stock-price {
  font-weight: 700;
  font-size: 1.1em;
  min-width: 60px;
  text-align: right;
}
.stock-price.up { color: #e74c3c; }
.stock-price.down { color: #2ecc71; }
.price-change { font-size: 0.7em; }

.stock-owned {
  font-size: 0.8em;
  color: #666;
  min-width: 70px;
}

.stock-actions {
  display: flex;
  gap: 4px;
}

.btn-buy-s, .btn-sell-s {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  font-size: 0.85em;
}

.btn-buy-s { background: #e74c3c; color: #fff; }
.btn-sell-s { background: #2ecc71; color: #fff; }
.btn-buy-s:disabled, .btn-sell-s:disabled { opacity: 0.3; cursor: not-allowed; }

.stock-footer {
  margin-top: 12px;
  text-align: right;
  color: #666;
  font-size: 0.9em;
}
</style>
