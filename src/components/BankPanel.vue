<template>
  <div v-if="show" class="panel-overlay" @click.self="$emit('close')">
    <div class="panel-card bank-panel">
      <div class="panel-header">
        <h3>🏦 银行</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <div class="bank-info">
        <div class="bank-row">
          <span>存款余额</span>
          <span class="amount deposit">{{ player?.bankDeposit || 0 }} 元</span>
        </div>
        <div class="bank-row">
          <span>贷款余额</span>
          <span class="amount loan">{{ player?.bankLoan || 0 }} 元</span>
        </div>
        <div class="bank-row">
          <span>现金</span>
          <span class="amount cash">{{ player?.money || 0 }} 元</span>
        </div>
      </div>

      <div class="bank-tabs">
        <button :class="{ active: tab === 'deposit' }" @click="tab = 'deposit'">存取款</button>
        <button :class="{ active: tab === 'mortgage' }" @click="tab = 'mortgage'">抵押</button>
        <button :class="{ active: tab === 'loan' }" @click="tab = 'loan'">贷款</button>
      </div>

      <div v-if="tab === 'deposit'" class="bank-section">
        <div class="input-row">
          <input v-model.number="depositAmount" type="number" placeholder="金额" min="0" />
          <button class="btn-action" @click="onDeposit" :disabled="!depositAmount">存款</button>
          <button class="btn-action secondary" @click="onWithdraw" :disabled="!depositAmount">取款</button>
        </div>
      </div>

      <div v-if="tab === 'mortgage'" class="bank-section">
        <div v-if="mortgageableProperties.length === 0" class="empty-msg">没有可抵押的地产</div>
        <div v-for="idx in mortgageableProperties" :key="idx" class="mortgage-row">
          <span>{{ tileName(idx) }}</span>
          <button class="btn-action small" @click="onMortgage(idx)">抵押 (+{{ mortgageValue(idx) }})</button>
        </div>
        <div v-for="idx in mortgagedProperties" :key="'m'+idx" class="mortgage-row unmortgage">
          <span>{{ tileName(idx) }}</span>
          <button class="btn-action small secondary" @click="onUnmortgage(idx)">赎回 (-{{ unmortgageValue(idx) }})</button>
        </div>
      </div>

      <div v-if="tab === 'loan'" class="bank-section">
        <div class="input-row">
          <input v-model.number="loanAmount" type="number" placeholder="金额" min="0" />
          <button class="btn-action" @click="onLoan" :disabled="!loanAmount">贷款</button>
          <button class="btn-action secondary" @click="onRepay" :disabled="!loanAmount">还款</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { BOARD } from '../game/constants.js'
import { deposit, withdraw, mortgageProperty, unmortgageProperty, takeLoan, repayLoan } from '../game/bank.js'

const props = defineProps({
  show: Boolean,
  player: Object
})

const emit = defineEmits(['close', 'action'])

const tab = ref('deposit')
const depositAmount = ref(0)
const loanAmount = ref(0)

const mortgageableProperties = computed(() => {
  if (!props.player) return []
  return props.player.properties.filter(i => !props.player.mortgaged?.includes(i) && BOARD[i].price)
})

const mortgagedProperties = computed(() => {
  return props.player?.mortgaged || []
})

function tileName(idx) { return BOARD[idx]?.name || '' }
function mortgageValue(idx) { return Math.floor(BOARD[idx].price * 0.5) }
function unmortgageValue(idx) { return Math.floor(BOARD[idx].price * 0.55) }

function onDeposit() {
  if (deposit(props.player, depositAmount.value)) {
    depositAmount.value = 0
    emit('action')
  }
}

function onWithdraw() {
  if (withdraw(props.player, depositAmount.value)) {
    depositAmount.value = 0
    emit('action')
  }
}

function onMortgage(idx) {
  mortgageProperty(props.player, idx)
  emit('action')
}

function onUnmortgage(idx) {
  unmortgageProperty(props.player, idx)
  emit('action')
}

function onLoan() {
  takeLoan(props.player, loanAmount.value)
  loanAmount.value = 0
  emit('action')
}

function onRepay() {
  repayLoan(props.player, loanAmount.value)
  loanAmount.value = 0
  emit('action')
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
  min-width: 380px;
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
}

.bank-info {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 16px;
}

.bank-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 0.9em;
  color: #555;
}

.amount { font-weight: 700; }
.amount.deposit { color: #3498db; }
.amount.loan { color: #e74c3c; }
.amount.cash { color: #2ecc71; }

.bank-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
}

.bank-tabs button {
  flex: 1;
  padding: 8px;
  border: 2px solid #eee;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-weight: 600;
  color: #666;
  font-size: 0.85em;
}

.bank-tabs button.active {
  border-color: #3498db;
  color: #3498db;
  background: #ebf5fb;
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.input-row input {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #eee;
  border-radius: 8px;
  font-size: 0.95em;
}

.btn-action {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: #3498db;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.85em;
  white-space: nowrap;
}

.btn-action.secondary {
  background: #95a5a6;
}

.btn-action.small {
  padding: 4px 10px;
  font-size: 0.8em;
}

.btn-action:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.mortgage-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.9em;
}

.unmortgage { opacity: 0.7; }

.empty-msg {
  text-align: center;
  color: #999;
  padding: 20px;
}
</style>
