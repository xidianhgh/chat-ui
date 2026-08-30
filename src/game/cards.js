// 机会与命运卡片

const CHANCE_CARDS = [
  { text: '银行发放红利，获得 500 元', effect: { type: 'money', amount: 500 } },
  { text: '罚款 200 元', effect: { type: 'money', amount: -200 } },
  { text: '前进到起点', effect: { type: 'move_to', position: 0 } },
  { text: '前进到银杏街(21)，若经过起点获得 2000 元', effect: { type: 'move_to', position: 21 } },
  { text: '入狱！直接前往监狱', effect: { type: 'go_to_jail' } },
  { text: '获得免费出狱卡', effect: { type: 'get_item', item: 'jail_free' } },
  { text: '房屋维修费：每栋房 250 元，每座酒店 1000 元', effect: { type: 'repair', house: 250, hotel: 1000 } },
  { text: '被选为选美冠军，获得 1000 元', effect: { type: 'money', amount: 1000 } },
  { text: '获得遥控骰子道具', effect: { type: 'get_item', item: 'dice_control' } },
  { text: '后退 3 格', effect: { type: 'move_back', steps: 3 } },
  { text: '获得免租牌道具', effect: { type: 'get_item', item: 'free_rent' } },
  { text: '股票分红，获得 300 元', effect: { type: 'money', amount: 300 } },
  { text: '医疗费用，支付 500 元', effect: { type: 'money', amount: -500 } },
  { text: '前进到东站(15)', effect: { type: 'move_to', position: 15 } },
  { text: '获得护身符道具', effect: { type: 'get_item', item: 'shield' } },
  { text: '生日！每位其他玩家给你 200 元', effect: { type: 'birthday', amount: 200 } }
]

const DESTINY_CARDS = [
  { text: '遗产继承，获得 1000 元', effect: { type: 'money', amount: 1000 } },
  { text: '缴纳学费 500 元', effect: { type: 'money', amount: -500 } },
  { text: '前进到免费停车', effect: { type: 'move_to', position: 20 } },
  { text: '入狱！直接前往监狱', effect: { type: 'go_to_jail' } },
  { text: '获得免费出狱卡', effect: { type: 'get_item', item: 'jail_free' } },
  { text: '获得路障道具', effect: { type: 'get_item', item: 'barrier' } },
  { text: '房屋维修费：每栋房 100 元，每座酒店 500 元', effect: { type: 'repair', house: 100, hotel: 500 } },
  { text: '彩票中奖，获得 800 元', effect: { type: 'money', amount: 800 } },
  { text: '获得转移卡道具', effect: { type: 'get_item', item: 'teleport' } },
  { text: '前进到玉兰路(39)', effect: { type: 'move_to', position: 39 } },
  { text: '交通罚款 300 元', effect: { type: 'money', amount: -300 } },
  { text: '银行利息，获得 200 元', effect: { type: 'money', amount: 200 } },
  { text: '后退 5 格', effect: { type: 'move_back', steps: 5 } },
  { text: '获得遥控骰子道具', effect: { type: 'get_item', item: 'dice_control' } },
  { text: '慈善捐款，支付 1000 元', effect: { type: 'money', amount: -1000 } },
  { text: '生日快乐！每位其他玩家给你 300 元', effect: { type: 'birthday', amount: 300 } }
]

// 洗牌
function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

export function createCardDecks() {
  return {
    chance: shuffle(CHANCE_CARDS),
    destiny: shuffle(DESTINY_CARDS),
    chanceIndex: 0,
    destinyIndex: 0
  }
}

export function drawCard(decks, type) {
  if (type === 'chance') {
    const card = decks.chance[decks.chanceIndex % decks.chance.length]
    decks.chanceIndex++
    return card
  } else {
    const card = decks.destiny[decks.destinyIndex % decks.destiny.length]
    decks.destinyIndex++
    return card
  }
}
