# 号码交集功能 - 简化自动方案

## 🎯 核心逻辑

**自动交集**：无需选择模块，系统自动：
1. 扫描8个做号模块
2. 按星级分组（2星、3星、4星、5星）
3. 对**相同星级**的所有模块进行交集
4. 用户只需设置容错，点击"做号"

## 📐 UI设计（简化版）

```
做号拼接页面
├─ 【模式切换】
│   [🔗 拼接] [⚡ 交集] ← 切换按钮
│
├─ 交集配置区域（仅交集模式显示）
│   ├─ 📊 自动检测到的模块：
│   │   • 5星: 模块1(10注), 模块3(8注), 模块5(12注)
│   │   • 3星: 模块2(15注), 模块4(20注)
│   │
│   └─ 容错设置: [0] [1] [2] [3] [4] [5] [6] [7] [8]
│
├─ 结果显示区域
│   └─ [做号] [复制] [验证]
│
└─ 8个做号模块
```

## 🔧 工作流程

```
用户在模块1放了10注5星号码
用户在模块2放了15注3星号码  
用户在模块3放了8注5星号码
用户在模块4放了20注3星号码
用户在模块5放了12注5星号码

↓ 点击"交集"模式

系统自动分析：
  5星组: 模块1(10注) + 模块3(8注) + 模块5(12注)
  3星组: 模块2(15注) + 模块4(20注)

↓ 用户设置容错: 2

↓ 点击"做号"

系统执行：
  1. 对5星组进行交集（模块1 ∩ 模块3 ∩ 模块5）
  2. 对3星组进行交集（模块2 ∩ 模块4）
  3. 合并所有交集结果

↓ 显示结果

结果展示：
  5星交集: 45注
  3星交集: 120注
  ─────────
  总计: 165注
```

## 💻 核心代码逻辑

```javascript
// 1. 扫描并分组模块
function scanAndGroupModules() {
  const groups = {}; // { '5': [模块数据], '3': [模块数据] }
  
  for (let i = 1; i <= 8; i++) {
    const textarea = document.querySelector(`textarea[data-module="${i}"]`);
    const lines = textarea.value.trim().split('\n').filter(line => line.trim());
    
    if (lines.length === 0) continue; // 跳过空模块
    
    // 解析第一行确定星级
    const firstLine = lines[0].trim();
    const numbers = firstLine.split(/[,，\s]+/).filter(n => n);
    const star = numbers.length;
    
    // 解析所有号码
    const allNumbers = lines.map(line => {
      return line.trim().split(/[,，\s]+/)
        .filter(n => n)
        .map(n => n.padStart(2, '0'));
    });
    
    // 按星级分组
    if (!groups[star]) groups[star] = [];
    groups[star].push({
      moduleNum: i,
      star: star,
      count: lines.length,
      numbers: allNumbers
    });
  }
  
  return groups;
}

// 2. 显示检测到的模块信息
function displayDetectedModules(groups) {
  let html = '<div class="mb-3"><h4 class="font-medium mb-2">📊 自动检测到的模块：</h4>';
  
  if (Object.keys(groups).length === 0) {
    html += '<p class="text-gray-500">暂无数据，请在下方模块中输入号码</p>';
  } else {
    Object.keys(groups).sort((a, b) => b - a).forEach(star => {
      const modules = groups[star];
      const moduleInfo = modules.map(m => 
        `模块${m.moduleNum}(${m.count}注)`
      ).join(', ');
      
      html += `<div class="mb-1">
        <span class="font-semibold text-blue-600">${star}星:</span> 
        ${moduleInfo}
        <span class="text-gray-500 text-sm">→ 将进行${modules.length}模块交集</span>
      </div>`;
    });
  }
  
  html += '</div>';
  document.getElementById('detectedModulesInfo').innerHTML = html;
}

// 3. 执行多模块交集
function performMultiModuleIntersection(modules, tolerance) {
  if (modules.length === 0) return [];
  if (modules.length === 1) return modules[0].numbers; // 只有一个模块，直接返回
  
  // 从第一个模块开始，逐个与后续模块求交集
  let result = modules[0].numbers;
  
  for (let i = 1; i < modules.length; i++) {
    result = intersectTwoGroups(result, modules[i].numbers, tolerance, modules[0].star);
  }
  
  return result;
}

// 4. 两组号码求交集（带容错）
function intersectTwoGroups(groupA, groupB, tolerance, star) {
  const result = [];
  
  groupA.forEach(numA => {
    groupB.forEach(numB => {
      // 计算相同数字个数
      const sameCount = numA.filter(n => numB.includes(n)).length;
      const diffCount = star - sameCount;
      
      // 如果差异在容错范围内
      if (diffCount <= tolerance) {
        // 合并两个号码，去重并排序
        const combined = [...new Set([...numA, ...numB])].sort();
        result.push(combined);
      }
    });
  });
  
  // 去重（相同的组合只保留一个）
  const uniqueResult = [];
  const seen = new Set();
  
  result.forEach(nums => {
    const key = nums.join(',');
    if (!seen.has(key)) {
      seen.add(key);
      uniqueResult.push(nums);
    }
  });
  
  return uniqueResult;
}

// 5. 主执行函数
function executeAutoIntersection() {
  // 获取容错值
  const toleranceBtn = document.querySelector('.tolerance-btn.bg-blue-500');
  const tolerance = toleranceBtn ? parseInt(toleranceBtn.dataset.tolerance) : 0;
  
  // 扫描并分组
  const groups = scanAndGroupModules();
  
  if (Object.keys(groups).length === 0) {
    alert('❌ 没有检测到任何模块数据\n请在下方模块中输入号码后再试');
    return;
  }
  
  // 对每个星级组执行交集
  let allResults = [];
  let resultSummary = [];
  
  Object.keys(groups).forEach(star => {
    const modules = groups[star];
    
    if (modules.length < 2) {
      // 少于2个模块，无法交集，直接跳过或返回原数据
      console.log(`${star}星只有1个模块，跳过交集`);
      return;
    }
    
    console.log(`开始处理${star}星交集，共${modules.length}个模块`);
    const intersectionResult = performMultiModuleIntersection(modules, tolerance);
    
    if (intersectionResult.length > 0) {
      allResults.push(...intersectionResult);
      resultSummary.push(`${star}星: ${intersectionResult.length}注`);
    }
  });
  
  // 显示结果
  if (allResults.length === 0) {
    alert('❌ 交集结果为空\n\n可能原因：\n1. 各模块号码差异过大\n2. 容错值设置过小\n\n建议：增加容错值再试');
    return;
  }
  
  const resultText = allResults.map(nums => nums.join(',')).join('\n');
  document.getElementById('resultDisplay').value = resultText;
  document.getElementById('resultCount').textContent = 
    `共${allResults.length}注 (${resultSummary.join(' | ')})`;
  
  console.log('✅ 交集完成:', resultSummary.join(', '));
}
```

## 🎨 简化的HTML

```html
<!-- 模式切换 -->
<div class="mode-selector mb-4">
  <div class="flex gap-2">
    <button id="concatModeBtn" class="mode-btn active">
      <span>🔗</span> 拼接模式
    </button>
    <button id="intersectionModeBtn" class="mode-btn">
      <span>⚡</span> 交集模式
    </button>
  </div>
</div>

<!-- 交集配置（默认隐藏） -->
<div id="intersectionConfig" class="hidden bg-blue-50 rounded-lg p-4 mb-4">
  <!-- 自动检测信息 -->
  <div id="detectedModulesInfo"></div>
  
  <!-- 容错设置 -->
  <div>
    <label class="block text-sm font-medium mb-2">容错设置</label>
    <div class="flex gap-2">
      <button class="tolerance-btn bg-blue-500 text-white" data-tolerance="0">0</button>
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
```

## ✅ 优势

1. **完全自动化** - 无需手动选择模块
2. **智能分组** - 自动按星级分类
3. **批量处理** - 同时处理多个星级组
4. **操作简单** - 只需切换模式 → 设置容错 → 做号
5. **清晰反馈** - 实时显示检测到的模块信息

## 📝 用户操作流程

```
1. 在模块1-8中输入做号结果
   ↓
2. 点击"交集"模式
   ↓
3. 查看自动检测到的模块分组
   ↓
4. 调整容错值（默认0）
   ↓
5. 点击"做号"按钮
   ↓
6. 查看交集结果
```

---

**更新时间**: 2025-10-18 02:00
**状态**: 简化方案 - 待实施

