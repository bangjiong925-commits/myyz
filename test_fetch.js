const puppeteer = require('puppeteer');
const fs = require('fs');

async function fetchTaiwanPK10Data() {
  let browser = null;
  
  try {
    // 检查当前是否在台湾PK10开奖时间段内
    const now = new Date();
    const taiwanTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Taipei"}));
    const currentHour = taiwanTime.getHours();
    
    console.log(`当前台湾时间: ${taiwanTime.getHours()}:${taiwanTime.getMinutes().toString().padStart(2, '0')}`);
    
    if (currentHour < 9 || currentHour >= 24) {
      console.log(`不在开奖时间段内（09:00-23:59），生成模拟数据用于测试`);
      
      // 生成模拟数据用于测试
      const mockNumbers = Array.from({length: 10}, (_, i) => i + 1).sort(() => Math.random() - 0.5);
      const mockPeriod = '114047' + String(Math.floor(Math.random() * 1000)).padStart(3, '0');
      
      return {
        period: mockPeriod,
        numbers: mockNumbers,
        time: taiwanTime.toLocaleTimeString('zh-CN', { hour12: false }),
        timestamp: new Date().toISOString(),
        isMock: true
      };
    }
    
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
    
    console.log('正在访问台湾PK10网站...');
    await page.goto('https://www.twpk10.com/', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // 等待数据加载
    await page.waitForTimeout(3000);
    
    // 提取最新开奖数据
    const latestData = await page.evaluate(() => {
      // 查找最新期数和开奖号码
      const periodElement = document.querySelector('.period, .issue, [class*="period"], [class*="issue"]');
      const numbersElements = document.querySelectorAll('.number, .ball, [class*="number"], [class*="ball"]');
      
      if (!periodElement || numbersElements.length === 0) {
        return null;
      }
      
      const period = periodElement.textContent.trim();
      const numbers = Array.from(numbersElements).slice(0, 10).map(el => parseInt(el.textContent.trim()));
      
      return {
        period,
        numbers,
        time: new Date().toLocaleTimeString('zh-CN', { timeZone: 'Asia/Taipei', hour12: false }),
        timestamp: new Date().toISOString()
      };
    });
    
    if (latestData && latestData.numbers.length === 10) {
      console.log('成功获取数据:', latestData);
      return latestData;
    } else {
      console.log('未能获取有效数据');
      return null;
    }
    
  } catch (error) {
    console.error('抓取数据时出错:', error.message);
    return null;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// 执行数据抓取
fetchTaiwanPK10Data().then(data => {
  if (data) {
    console.log('\n=== 抓取结果 ===');
    console.log('期数:', data.period);
    console.log('号码:', data.numbers.join(' '));
    console.log('时间:', data.time);
    console.log('时间戳:', data.timestamp);
    if (data.isMock) {
      console.log('注意: 这是模拟数据（非开奖时间）');
    }
    
    // 更新最新数据文件
    const latestData = {
      time: data.time,
      period: data.period,
      numbers: data.numbers,
      numbersString: data.numbers.join(' '),
      timestamp: data.timestamp,
      source: data.isMock ? 'mock_data' : 'taiwan_pk10',
      type: 'pk10'
    };
    
    fs.writeFileSync('taiwan_pk10_latest_test.json', JSON.stringify(latestData, null, 2));
    console.log('\n测试数据已保存到 taiwan_pk10_latest_test.json');
    
  } else {
    console.log('未获取到有效数据');
  }
}).catch(error => {
  console.error('脚本执行出错:', error);
  process.exit(1);
});