# 号码交集功能整合到做号拼接页面 - 实施方案

## 📋 需求说明

将号码交集功能整合到做号拼接页面中，实现：
1. 在结果显示区域上方添加**模式切换**：拼接模式 ↔️ 交集模式
2. 交集模式下：
   - 显示模块选择器（选择2个模块进行交集）
   - 显示容错设置
   - 不需要粘贴框，直接从下面8个做号模块中提取数据
   - 自动识别相同星级的号码进行交集
3. 简化操作：选择模块 → 设置容错 → 点击"做号"按钮

## 🎨 UI设计

### 修改位置：做号拼接页面结果显示区域上方

```
┌─────────────────────────────────────────────────────┐
│  【拼接】 【交集】  ← 模式切换按钮                    │
├─────────────────────────────────────────────────────┤
│  拼接模式：                                          │
│  └─ 显示现有的"做号"、"复制"、"验证"按钮             │
│                                                      │
│  交集模式：                                          │
│  ┌─ 模块选择 ─────────────────────────────┐         │
│  │ 选择模块A: [下拉选择 1-8] (X注 Y星)     │         │
│  │ 选择模块B: [下拉选择 1-8] (X注 Y星)     │         │
│  └──────────────────────────────────────┘         │
│  ┌─ 容错设置 ─────────────────────────────┐         │
│  │ [0] [1] [2] [3] [4] [5] [6] [7] [8]   │         │
│  └──────────────────────────────────────┘         │
│  [做号] [复制]                                       │
└─────────────────────────────────────────────────────┘
```

## 🔧 技术实现

### 1. HTML结构修改

在做号拼接页面结果显示区域上方添加：

```html
<!-- 模式切换区域 -->
<div class="mode-selector bg-white rounded-lg shadow-sm p-4 mb-4">
  <div class="flex gap-2 mb-3">
    <button id="concatModeBtn" class="mode-btn active">
      <span class="icon">🔗</span> 拼接模式
    </button>
    <button id="intersectionModeBtn" class="mode-btn">
      <span class="icon">⚡</span> 交集模式
    </button>
  </div>
  
  <!-- 交集模式配置区域（默认隐藏） -->
  <div id="intersectionConfig" class="hidden">
    <!-- 模块选择 -->
    <div class="flex gap-4 mb-3">
      <div class="flex-1">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          模块A
        </label>
        <select id="moduleASelect" class="w-full px-3 py-2 border border-gray-300 rounded-md">
          <option value="">请选择模块</option>
          <option value="1">模块1 (0注)</option>
          <option value="2">模块2 (0注)</option>
          <!-- ... 其他模块 ... -->
        </select>
      </div>
      <div class="flex-1">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          模块B
        </label>
        <select id="moduleBSelect" class="w-full px-3 py-2 border border-gray-300 rounded-md">
          <option value="">请选择模块</option>
          <option value="1">模块1 (0注)</option>
          <option value="2">模块2 (0注)</option>
          <!-- ... 其他模块 ... -->
        </select>
      </div>
    </div>
    
    <!-- 容错设置 -->
    <div class="mb-3">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        容错设置
      </label>
      <div class="flex gap-2">
        <button class="tolerance-btn" data-tolerance="0">0</button>
        <button class="tolerance-btn" data-tolerance="1">1</button>
        <button class="tolerance-btn" data-tolerance="2">2</button>
        <button class="tolerance-btn" data-tolerance="3">3</button>
        <button class="tolerance-btn" data-tolerance="4">4</button>
        <button class="tolerance-btn" data-tolerance="5">5</button>
        <button class="tolerance-btn" data-tolerance="6">6</button>
        <button class="tolerance-btn" data-tolerance="7">7</button>
        <button class="tolerance-btn" data-tolerance="8">8</button>
      </div>
    </div>
  </div>
</div>
```

### 2. CSS样式

```css
.mode-selector {
  border: 2px solid #e5e7eb;
}

.mode-btn {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  color: #6b7280;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.mode-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.mode-btn.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-color: #3b82f6;
}

.mode-btn .icon {
  font-size: 1.25rem;
}
```

### 3. JavaScript逻辑

```javascript
// 模式切换
let currentMode = 'concat'; // 'concat' | 'intersection'

document.getElementById('concatModeBtn').addEventListener('click', () => {
  currentMode = 'concat';
  updateModeUI();
});

document.getElementById('intersectionModeBtn').addEventListener('click', () => {
  currentMode = 'intersection';
  updateModeUI();
});

function updateModeUI() {
  const concatBtn = document.getElementById('concatModeBtn');
  const intersectionBtn = document.getElementById('intersectionModeBtn');
  const intersectionConfig = document.getElementById('intersectionConfig');
  
  if (currentMode === 'concat') {
    concatBtn.classList.add('active');
    intersectionBtn.classList.remove('active');
    intersectionConfig.classList.add('hidden');
  } else {
    concatBtn.classList.remove('active');
    intersectionBtn.classList.add('active');
    intersectionConfig.classList.remove('hidden');
  }
}

// 更新模块选择器的显示（注数和星级）
function updateModuleSelectors() {
  const selects = [
    document.getElementById('moduleASelect'),
    document.getElementById('moduleBSelect')
  ];
  
  selects.forEach(select => {
    for (let i = 1; i <= 8; i++) {
      const textarea = document.querySelector(`textarea[data-module="${i}"]`);
      const lines = textarea.value.trim().split('\n').filter(line => line.trim());
      const count = lines.length;
      
      // 检测星级
      let star = 0;
      if (lines.length > 0) {
        const firstLine = lines[0].trim();
        const numbers = firstLine.split(/[,，\s]+/).filter(n => n);
        star = numbers.length;
      }
      
      const option = select.querySelector(`option[value="${i}"]`);
      option.textContent = `模块${i} (${count}注 ${star}星)`;
    }
  });
}

// 执行交集计算
function performIntersection() {
  const moduleA = document.getElementById('moduleASelect').value;
  const moduleB = document.getElementById('moduleBSelect').value;
  
  if (!moduleA || !moduleB) {
    alert('请选择两个模块');
    return;
  }
  
  if (moduleA === moduleB) {
    alert('请选择不同的模块');
    return;
  }
  
  // 获取选中的容错值
  const toleranceBtn = document.querySelector('.tolerance-btn.bg-blue-500');
  const tolerance = toleranceBtn ? parseInt(toleranceBtn.dataset.tolerance) : 0;
  
  // 获取模块数据
  const dataA = getModuleData(moduleA);
  const dataB = getModuleData(moduleB);
  
  if (dataA.star !== dataB.star) {
    alert(`两个模块的星级不同！\n模块${moduleA}: ${dataA.star}星\n模块${moduleB}: ${dataB.star}星\n\n请选择相同星级的模块`);
    return;
  }
  
  // 执行交集计算
  const result = calculateIntersection(dataA.numbers, dataB.numbers, tolerance, dataA.star);
  
  // 显示结果
  displayIntersectionResult(result);
}

function getModuleData(moduleNum) {
  const textarea = document.querySelector(`textarea[data-module="${moduleNum}"]`);
  const lines = textarea.value.trim().split('\n').filter(line => line.trim());
  
  const numbers = lines.map(line => {
    return line.trim().split(/[,，\s]+/).filter(n => n).map(n => n.padStart(2, '0'));
  });
  
  const star = numbers.length > 0 ? numbers[0].length : 0;
  
  return { numbers, star };
}

function calculateIntersection(numbersA, numbersB, tolerance, star) {
  const result = [];
  
  numbersA.forEach(numA => {
    numbersB.forEach(numB => {
      const sameCount = numA.filter(n => numB.includes(n)).length;
      const diffCount = star - sameCount;
      
      if (diffCount <= tolerance) {
        // 合并两个号码，去重
        const combined = [...new Set([...numA, ...numB])].sort();
        result.push({
          numbers: combined,
          sameCount: sameCount,
          diffCount: diffCount
        });
      }
    });
  });
  
  return result;
}

function displayIntersectionResult(result) {
  const resultDisplay = document.getElementById('resultDisplay');
  const resultCount = document.getElementById('resultCount');
  
  const resultText = result.map(item => item.numbers.join(',')).join('\n');
  resultDisplay.value = resultText;
  resultCount.textContent = `共${result.length}注`;
}
```

## 📝 实施步骤

1. ✅ 在做号拼接页面添加模式切换UI
2. ✅ 添加交集模式配置区域（模块选择+容错设置）
3. ✅ 实现模式切换逻辑
4. ✅ 实现模块数据读取功能
5. ✅ 实现星级检测和验证
6. ✅ 实现交集计算算法（带容错）
7. ✅ 实现结果显示
8. ✅ 添加"做号"按钮事件绑定

## 🎯 优势

- ✅ 无需粘贴数据，直接从做号模块选择
- ✅ 自动检测星级是否匹配
- ✅ 支持容错筛选
- ✅ 界面统一，操作流畅
- ✅ 一键切换拼接/交集模式

---

**创建时间**: 2025-10-18
**状态**: 待实施

