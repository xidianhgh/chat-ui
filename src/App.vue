<template>
  <div class="app">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-icon">🧈</span>
          <span class="logo-text">豆腐</span>
        </div>
      </div>
      <button class="new-chat-btn" @click="startNewChat">
        <span>+</span> 新建对话
      </button>
      <div class="chat-list">
        <div
          v-for="(chat, index) in chatHistory"
          :key="chat.id"
          class="chat-list-item"
          :class="{ active: currentChatId === chat.id }"
          @click="switchChat(chat.id)"
        >
          <span class="chat-title">{{ chat.title }}</span>
          <button class="delete-btn" @click.stop="deleteChat(chat.id)">×</button>
        </div>
      </div>
    </aside>

    <!-- 主聊天区域 -->
    <main class="chat-main">
      <div class="chat-header">
        <h2>{{ currentChat?.title || '新对话' }}</h2>
      </div>

      <div class="messages-container" ref="messagesContainer">
        <!-- 欢迎界面 -->
        <div v-if="!currentChat || currentChat.messages.length === 0" class="welcome">
          <div class="welcome-icon">🧈</div>
          <h1>你好，我是豆腐</h1>
          <p>你的 AI 聊天助手，有什么可以帮你的吗？</p>
          <div class="suggestions">
            <div class="suggestion-card" v-for="s in suggestions" :key="s" @click="useSuggestion(s)">
              {{ s }}
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-else class="messages">
          <div
            v-for="msg in currentChat.messages"
            :key="msg.id"
            class="message"
            :class="msg.role"
          >
            <div class="avatar">
              <span v-if="msg.role === 'user'">👤</span>
              <span v-else>🧈</span>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(msg.content)"></div>
              <div v-if="msg.loading" class="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-wrapper">
          <textarea
            ref="inputRef"
            v-model="inputText"
            placeholder="给豆腐发送消息..."
            @keydown.enter.exact.prevent="sendMessage"
            @input="autoResize"
            rows="1"
            :disabled="isStreaming"
          ></textarea>
          <button
            class="send-btn"
            @click="sendMessage"
            :disabled="!inputText.trim() || isStreaming"
          >
            <svg v-if="!isStreaming" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
            <div v-else class="stop-icon">⬛</div>
          </button>
        </div>
        <p class="input-hint">按 Enter 发送，Shift + Enter 换行</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'

const suggestions = [
  '帮我写一段Python快速排序',
  '解释一下什么是机器学习',
  '今天适合出去运动吗？',
  '推荐几本好看的小说'
]

const inputText = ref('')
const isStreaming = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)
let abortController = null

// 聊天历史
const chatHistory = ref([
  {
    id: 'default',
    title: '新对话',
    messages: []
  }
])
const currentChatId = ref('default')

const currentChat = computed(() => {
  return chatHistory.value.find(c => c.id === currentChatId.value)
})

let msgIdCounter = 0
function genMsgId() {
  return 'msg_' + (++msgIdCounter)
}

let chatIdCounter = 1
function genChatId() {
  return 'chat_' + (++chatIdCounter)
}

function startNewChat() {
  const newChat = {
    id: genChatId(),
    title: '新对话',
    messages: []
  }
  chatHistory.value.unshift(newChat)
  currentChatId.value = newChat.id
}

function switchChat(id) {
  currentChatId.value = id
}

function deleteChat(id) {
  const idx = chatHistory.value.findIndex(c => c.id === id)
  if (idx > -1) {
    chatHistory.value.splice(idx, 1)
    if (currentChatId.value === id) {
      currentChatId.value = chatHistory.value[0]?.id || null
      if (!currentChatId.value) {
        startNewChat()
      }
    }
  }
}

function useSuggestion(text) {
  inputText.value = text
  sendMessage()
}

function autoResize() {
  const el = inputRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function formatMessage(content) {
  if (!content) return ''
  // 简单的 markdown 处理：代码块、加粗、换行
  let html = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // 代码块
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code class="lang-$1">$2</code></pre>')
  // 行内代码
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  // 加粗
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // 换行
  html = html.replace(/\n/g, '<br>')
  
  return html
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isStreaming.value) return

  // 确保有当前对话
  if (!currentChat.value) {
    startNewChat()
  }

  // 更新对话标题（如果是第一条消息）
  if (currentChat.value.messages.length === 0) {
    currentChat.value.title = text.slice(0, 20) + (text.length > 20 ? '...' : '')
  }

  // 添加用户消息
  currentChat.value.messages.push({
    id: genMsgId(),
    role: 'user',
    content: text
  })

  inputText.value = ''
  autoResize()
  scrollToBottom()

  // 添加 AI 消息（加载中）
  const aiMsg = {
    id: genMsgId(),
    role: 'assistant',
    content: '',
    loading: true
  }
  currentChat.value.messages.push(aiMsg)
  scrollToBottom()

  // 使用响应式代理引用，确保 Vue 能检测到 content 变化
  const aiMsgProxy = currentChat.value.messages[currentChat.value.messages.length - 1]

  isStreaming.value = true
  abortController = new AbortController()

  try {
    // 使用 XHR + onprogress 实现流式显示，兼容性优于 fetch ReadableStream
    const streamResult = await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('POST', 'http://localhost:9999/ai/stream-chat')
      xhr.setRequestHeader('Content-Type', 'application/json')

      abortController.signal.addEventListener('abort', () => xhr.abort())

      let lastIndex = 0
      let sseBuffer = ''

      function processChunk(text) {
        sseBuffer += text
        const lines = sseBuffer.split(/\r?\n/)
        sseBuffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data:')) {
            const data = line.slice(5)
            if (data.trim() === '') {
              // 空 data: 行解析为换行符
              if (aiMsgProxy.content.length > 0) {
                aiMsgProxy.content += '\n'
              }
            } else {
              parseSSEData(data.trim())
            }
          } else if (line.trim()) {
            aiMsgProxy.content += line
          }
        }
        scrollToBottom()
      }

      function parseSSEData(raw) {
        if (raw === '[DONE]') return
        try {
          const parsed = JSON.parse(raw)
          if (typeof parsed === 'string') {
            aiMsgProxy.content += parsed
          } else if (parsed.content) {
            aiMsgProxy.content += parsed.content
          } else if (parsed.choices?.[0]?.delta?.content) {
            aiMsgProxy.content += parsed.choices[0].delta.content
          } else if (parsed.data) {
            aiMsgProxy.content += parsed.data
          }
        } catch {
          // 非 JSON，直接作为纯文本追加
          aiMsgProxy.content += raw
        }
      }

      xhr.onprogress = () => {
        const newText = xhr.responseText.substring(lastIndex)
        lastIndex = xhr.responseText.length
        if (newText) {
          aiMsgProxy.loading = false
          processChunk(newText)
        }
      }

      xhr.onload = () => {
        // 处理剩余 buffer
        if (sseBuffer.trim()) {
          if (sseBuffer.startsWith('data:')) {
            const data = sseBuffer.slice(5)
            if (data.trim() !== '') {
              parseSSEData(data.trim())
            }
          } else {
            aiMsgProxy.content += sseBuffer
          }
        }
        resolve()
      }

      xhr.onerror = () => reject(new Error('网络请求失败'))
      xhr.onabort = () => reject(new DOMException('已取消', 'AbortError'))

      xhr.send(JSON.stringify({ msg: text }))
    })

    // 如果内容为空，显示错误提示
    if (!aiMsgProxy.content) {
      aiMsgProxy.content = '抱歉，没有收到有效回复。'
    }
  } catch (error) {
    aiMsgProxy.loading = false
    if (error.name === 'AbortError' || error.message === '已取消') {
      aiMsgProxy.content += '\n\n[已停止生成]'
    } else {
      aiMsgProxy.content = `请求失败: ${error.message}`
    }
  } finally {
    isStreaming.value = false
    abortController = null
    scrollToBottom()
  }
}

onMounted(() => {
  inputRef.value?.focus()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', sans-serif;
  background: #f5f5f5;
  color: #333;
}

.app {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  background: #1a1a2e;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 16px;
  flex-shrink: 0;
}

.sidebar-header {
  margin-bottom: 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  margin-bottom: 16px;
}

.new-chat-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 13px;
}

.chat-list-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.chat-list-item.active {
  background: rgba(102, 126, 234, 0.3);
}

.chat-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.delete-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  font-size: 18px;
  padding: 0 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.chat-list-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #ff4757;
}

/* 主聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  min-width: 0;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
  background: #fff;
}

.chat-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 欢迎界面 */
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 40px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.welcome h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.welcome p {
  font-size: 16px;
  color: #666;
  margin-bottom: 32px;
}

.suggestions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-width: 600px;
  width: 100%;
}

.suggestion-card {
  padding: 16px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  color: #495057;
  transition: all 0.2s;
  text-align: left;
}

.suggestion-card:hover {
  background: #e9ecef;
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 消息列表 */
.messages {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  background: #f0f0f0;
}

.message.user .avatar {
  background: #e3f2fd;
}

.message-content {
  max-width: 70%;
  min-width: 0;
}

.message-text {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

.message.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-top-right-radius: 4px;
}

.message.assistant .message-text {
  background: #f1f3f5;
  color: #333;
  border-top-left-radius: 4px;
}

.message-text pre {
  background: #282c34;
  color: #abb2bf;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
  font-size: 13px;
}

.message-text code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.message-text pre code {
  background: none;
  padding: 0;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

/* 输入区域 */
.input-area {
  padding: 16px 24px 24px;
  background: #fff;
  border-top: 1px solid #eee;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  max-width: 800px;
  margin: 0 auto;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 16px;
  padding: 12px 16px;
  transition: border-color 0.2s;
}

.input-wrapper:focus-within {
  border-color: #667eea;
  background: #fff;
}

textarea {
  flex: 1;
  border: none;
  background: none;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  outline: none;
  font-family: inherit;
  max-height: 200px;
}

textarea::placeholder {
  color: #adb5bd;
}

textarea:disabled {
  opacity: 0.6;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stop-icon {
  font-size: 10px;
}

.input-hint {
  text-align: center;
  font-size: 12px;
  color: #adb5bd;
  margin-top: 8px;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .suggestions {
    grid-template-columns: 1fr;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style>
