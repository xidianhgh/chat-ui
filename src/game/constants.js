// 大富翁游戏常量定义

// 玩家颜色
export const PLAYER_COLORS = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
export const PLAYER_NAMES = ['红方', '蓝方', '绿方', '橙方']

// 初始资金
export const INITIAL_MONEY = 15000
export const START_SALARY = 2000
export const JAIL_FINE = 500

// 地图格子类型
export const TILE_TYPES = {
  GO: 'go',             // 起点
  PROPERTY: 'property', // 地产
  CHANCE: 'chance',     // 机会
  DESTINY: 'destiny',   // 命运
  TAX: 'tax',           // 税收
  JAIL: 'jail',         // 监狱/探访
  FREE_PARKING: 'free_parking', // 免费停车
  GO_TO_JAIL: 'go_to_jail',     // 入狱
  RAILROAD: 'railroad', // 火车站
  UTILITY: 'utility'    // 公共事业
}

// 地产颜色分组
export const COLOR_GROUPS = {
  BROWN: '#8B4513',
  LIGHT_BLUE: '#87CEEB',
  PINK: '#FF69B4',
  ORANGE: '#FF8C00',
  RED: '#FF0000',
  YELLOW: '#FFD700',
  GREEN: '#228B22',
  DARK_BLUE: '#00008B'
}

// 40格地图数据
export const BOARD = [
  // 底边 (右→左): 0-9
  { id: 0, name: '起点', type: TILE_TYPES.GO },
  { id: 1, name: '老街', type: TILE_TYPES.PROPERTY, group: 'BROWN', price: 600, rent: [30, 150, 450, 900, 1200], buildCost: 500 },
  { id: 2, name: '命运', type: TILE_TYPES.DESTINY },
  { id: 3, name: '小巷', type: TILE_TYPES.PROPERTY, group: 'BROWN', price: 800, rent: [40, 200, 600, 1200, 1600], buildCost: 500 },
  { id: 4, name: '所得税', type: TILE_TYPES.TAX, amount: 2000 },
  { id: 5, name: '南站', type: TILE_TYPES.RAILROAD, price: 2000 },
  { id: 6, name: '码头路', type: TILE_TYPES.PROPERTY, group: 'LIGHT_BLUE', price: 1000, rent: [60, 300, 900, 1800, 2400], buildCost: 600 },
  { id: 7, name: '机会', type: TILE_TYPES.CHANCE },
  { id: 8, name: '港口路', type: TILE_TYPES.PROPERTY, group: 'LIGHT_BLUE', price: 1200, rent: [70, 350, 1050, 2100, 2800], buildCost: 600 },
  { id: 9, name: '海滨道', type: TILE_TYPES.PROPERTY, group: 'LIGHT_BLUE', price: 1400, rent: [80, 400, 1200, 2400, 3200], buildCost: 600 },

  // 左边 (下→上): 10-19
  { id: 10, name: '监狱', type: TILE_TYPES.JAIL },
  { id: 11, name: '教堂街', type: TILE_TYPES.PROPERTY, group: 'PINK', price: 1600, rent: [90, 450, 1350, 2700, 3600], buildCost: 800 },
  { id: 12, name: '电力公司', type: TILE_TYPES.UTILITY, price: 1500 },
  { id: 13, name: '花园路', type: TILE_TYPES.PROPERTY, group: 'PINK', price: 1800, rent: [100, 500, 1500, 3000, 4000], buildCost: 800 },
  { id: 14, name: '公园大道', type: TILE_TYPES.PROPERTY, group: 'PINK', price: 2000, rent: [110, 550, 1650, 3300, 4400], buildCost: 800 },
  { id: 15, name: '东站', type: TILE_TYPES.RAILROAD, price: 2000 },
  { id: 16, name: '玫瑰街', type: TILE_TYPES.PROPERTY, group: 'ORANGE', price: 2200, rent: [120, 600, 1800, 3600, 4800], buildCost: 1000 },
  { id: 17, name: '命运', type: TILE_TYPES.DESTINY },
  { id: 18, name: '百合路', type: TILE_TYPES.PROPERTY, group: 'ORANGE', price: 2400, rent: [130, 650, 1950, 3900, 5200], buildCost: 1000 },
  { id: 19, name: '丁香道', type: TILE_TYPES.PROPERTY, group: 'ORANGE', price: 2600, rent: [140, 700, 2100, 4200, 5600], buildCost: 1000 },

  // 顶边 (左→右): 20-29
  { id: 20, name: '免费停车', type: TILE_TYPES.FREE_PARKING },
  { id: 21, name: '银杏街', type: TILE_TYPES.PROPERTY, group: 'RED', price: 2800, rent: [150, 750, 2250, 4500, 6000], buildCost: 1200 },
  { id: 22, name: '机会', type: TILE_TYPES.CHANCE },
  { id: 23, name: '梧桐路', type: TILE_TYPES.PROPERTY, group: 'RED', price: 3000, rent: [160, 800, 2400, 4800, 6400], buildCost: 1200 },
  { id: 24, name: '枫林道', type: TILE_TYPES.PROPERTY, group: 'RED', price: 3200, rent: [170, 850, 2550, 5100, 6800], buildCost: 1200 },
  { id: 25, name: '北站', type: TILE_TYPES.RAILROAD, price: 2000 },
  { id: 26, name: '桂花巷', type: TILE_TYPES.PROPERTY, group: 'YELLOW', price: 3400, rent: [180, 900, 2700, 5400, 7200], buildCost: 1400 },
  { id: 27, name: '梅花路', type: TILE_TYPES.PROPERTY, group: 'YELLOW', price: 3600, rent: [190, 950, 2850, 5700, 7600], buildCost: 1400 },
  { id: 28, name: '自来水', type: TILE_TYPES.UTILITY, price: 1500 },
  { id: 29, name: '兰花道', type: TILE_TYPES.PROPERTY, group: 'YELLOW', price: 3800, rent: [200, 1000, 3000, 6000, 8000], buildCost: 1400 },

  // 右边 (上→下): 30-39
  { id: 30, name: '入狱', type: TILE_TYPES.GO_TO_JAIL },
  { id: 31, name: '牡丹街', type: TILE_TYPES.PROPERTY, group: 'GREEN', price: 4000, rent: [220, 1100, 3300, 6600, 8800], buildCost: 1600 },
  { id: 32, name: '芍药路', type: TILE_TYPES.PROPERTY, group: 'GREEN', price: 4200, rent: [240, 1200, 3600, 7200, 9600], buildCost: 1600 },
  { id: 33, name: '命运', type: TILE_TYPES.DESTINY },
  { id: 34, name: '紫荆道', type: TILE_TYPES.PROPERTY, group: 'GREEN', price: 4400, rent: [260, 1300, 3900, 7800, 10400], buildCost: 1600 },
  { id: 35, name: '西站', type: TILE_TYPES.RAILROAD, price: 2000 },
  { id: 36, name: '机会', type: TILE_TYPES.CHANCE },
  { id: 37, name: '海棠街', type: TILE_TYPES.PROPERTY, group: 'DARK_BLUE', price: 4600, rent: [280, 1400, 4200, 8400, 11200], buildCost: 2000 },
  { id: 38, name: '奢侈税', type: TILE_TYPES.TAX, amount: 1000 },
  { id: 39, name: '玉兰路', type: TILE_TYPES.PROPERTY, group: 'DARK_BLUE', price: 5000, rent: [300, 1500, 4500, 9000, 12000], buildCost: 2000 }
]

// 颜色分组包含的格子ID
export const GROUP_TILES = {}
BOARD.forEach((tile, i) => {
  if (tile.type === TILE_TYPES.PROPERTY && tile.group) {
    if (!GROUP_TILES[tile.group]) GROUP_TILES[tile.group] = []
    GROUP_TILES[tile.group].push(i)
  }
})

// 火车站格子ID
export const RAILROADS = BOARD.reduce((arr, t, i) => {
  if (t.type === TILE_TYPES.RAILROAD) arr.push(i)
  return arr
}, [])

// 租金计算 - 火车站
export function getRailroadRent(ownerTileCount) {
  return [250, 500, 1000, 2000][ownerTileCount - 1] || 250
}

// 租金计算 - 公共事业
export function getUtilityRent(ownerUtilityCount, diceTotal) {
  return ownerUtilityCount === 2 ? diceTotal * 100 : diceTotal * 40
}

// 建房数量对应的图标
export const HOUSE_ICONS = ['□', '🏠', '🏠🏠', '🏠🏠🏠', '🏠🏠🏠🏠', '🏨']

// 股票初始数据
export const INITIAL_STOCKS = [
  { id: 0, name: '地产股份', symbol: 'DC', price: 100, history: [100] },
  { id: 1, name: '科技股份', symbol: 'KJ', price: 120, history: [120] },
  { id: 2, name: '医药股份', symbol: 'YY', price: 80, history: [80] },
  { id: 3, name: '能源股份', symbol: 'NY', price: 150, history: [150] }
]

// 道具定义
export const ITEM_TYPES = {
  DICE_CONTROL: 'dice_control',   // 遥控骰子
  BARRIER: 'barrier',             // 路障
  TELEPORT: 'teleport',           // 转移卡
  FREE_RENT: 'free_rent',         // 免租牌
  SHIELD: 'shield'                // 护身符
}

export const ITEM_NAMES = {
  dice_control: '遥控骰子',
  barrier: '路障',
  teleport: '转移卡',
  free_rent: '免租牌',
  shield: '护身符'
}

// 银行利率
export const BANK_DEPOSIT_RATE = 0.05
export const BANK_MORTGAGE_RATE = 0.5  // 抵押获得地产价格的一半
export const BANK_MORTGAGE_REPAY_RATE = 0.55 // 赎回需付抵押价+10%利息
