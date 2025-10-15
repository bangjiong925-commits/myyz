// 密钥管理系统前端更新脚本
// 此文件包含需要添加到 key_management.html 的代码片段

/*
 * ========== 添加到 <script> 标签开头 ==========
 */

// 管理员密钥管理
const AdminKeyManager = {
    // 从localStorage获取管理员密钥
    get() {
        return localStorage.getItem('adminKey') || '';
    },
    
    // 保存管理员密钥
    set(key) {
        if (key && key.trim()) {
            localStorage.setItem('adminKey', key.trim());
            console.log('✅ 管理员密钥已保存');
            return true;
        }
        return false;
    },
    
    // 清除管理员密钥
    clear() {
        localStorage.removeItem('adminKey');
        console.log('🗑️ 管理员密钥已清除');
    },
    
    // 检查是否已设置
    isSet() {
        const key = this.get();
        return key && key.length > 0;
    },
    
    // 提示输入管理员密钥
    prompt() {
        const key = window.prompt('请输入管理员密钥（用于访问密钥管理功能）:');
        if (key && key.trim()) {
            this.set(key);
            return true;
        }
        return false;
    }
};

// 修改 API_BASE 获取函数
function getApiBase() {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:3002/api/admin';  // ← 改为 /api/admin
    }
    
    if (hostname === '47.242.214.89') {
        return '/api/admin';  // ← 改为 /api/admin
    }
    
    if (hostname.includes('vercel.app')) {
        return '/api/admin';  // ← 改为 /api/admin（Vercel也需要代理这个）
    }
    
    return `${protocol}//${hostname}/api/admin`;
}

// 创建带管理员密钥的 fetch 函数
async function authFetch(url, options = {}) {
    // 检查管理员密钥
    if (!AdminKeyManager.isSet()) {
        if (!AdminKeyManager.prompt()) {
            throw new Error('需要管理员密钥才能访问此功能');
        }
    }
    
    // 添加管理员密钥到请求头
    const headers = {
        ...options.headers,
        'X-Admin-Key': AdminKeyManager.get()
    };
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    // 如果返回403，说明密钥无效
    if (response.status === 403) {
        AdminKeyManager.clear();
        alert('管理员密钥无效，请重新输入');
        if (AdminKeyManager.prompt()) {
            // 重试
            return authFetch(url, options);
        }
        throw new Error('管理员密钥无效');
    }
    
    return response;
}

/*
 * ========== 修改所有 fetch 调用 ==========
 * 将所有对管理API的 fetch 调用改为 authFetch
 */

// 示例1：加载密钥列表
async function loadKeys() {
    try {
        const response = await authFetch(`${API_BASE}/keys?page=${currentPage}&limit=${pageSize}`);
        // ... 其余代码不变
    } catch (error) {
        console.error('加载密钥失败:', error);
    }
}

// 示例2：创建密钥
async function createKey(data) {
    try {
        const response = await authFetch(`${API_BASE}/keys`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        // ... 其余代码不变
    } catch (error) {
        console.error('创建密钥失败:', error);
    }
}

// 示例3：删除密钥
async function deleteKey(key) {
    try {
        const response = await authFetch(`${API_BASE}/keys/${encodeURIComponent(key)}`, {
            method: 'DELETE'
        });
        // ... 其余代码不变
    } catch (error) {
        console.error('删除密钥失败:', error);
    }
}

/*
 * ========== 添加管理员设置界面 ==========
 */

// HTML 添加到页面顶部
const adminSettingsHTML = `
<div style="position: fixed; top: 10px; right: 10px; z-index: 9999;">
    <button onclick="showAdminSettings()" style="
        background: #667eea;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
    ">
        🔑 管理员设置
    </button>
</div>

<div id="adminSettingsModal" style="
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 10000;
    justify-content: center;
    align-items: center;
" onclick="closeAdminSettings(event)">
    <div style="
        background: white;
        padding: 30px;
        border-radius: 12px;
        max-width: 500px;
        width: 90%;
    " onclick="event.stopPropagation()">
        <h2>🔑 管理员设置</h2>
        <div style="margin: 20px 0;">
            <label style="display: block; margin-bottom: 10px; font-weight: bold;">
                管理员密钥
            </label>
            <input type="password" id="adminKeyInput" placeholder="请输入管理员密钥" style="
                width: 100%;
                padding: 12px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                font-size: 16px;
            ">
            <div style="color: #666; font-size: 13px; margin-top: 5px;">
                此密钥仅保存在本地浏览器，不会上传到服务器
            </div>
        </div>
        <div style="margin-top: 20px;">
            <button onclick="saveAdminKey()" style="
                background: #10b981;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                margin-right: 10px;
            ">保存密钥</button>
            <button onclick="clearAdminKey()" style="
                background: #ef4444;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
            ">清除密钥</button>
        </div>
        <div id="adminKeyStatus" style="margin-top: 15px; padding: 10px; border-radius: 5px;"></div>
    </div>
</div>
`;

function showAdminSettings() {
    const modal = document.getElementById('adminSettingsModal');
    modal.style.display = 'flex';
    
    const input = document.getElementById('adminKeyInput');
    input.value = AdminKeyManager.get();
    
    updateAdminKeyStatus();
}

function closeAdminSettings(event) {
    if (event.target.id === 'adminSettingsModal') {
        document.getElementById('adminSettingsModal').style.display = 'none';
    }
}

function saveAdminKey() {
    const input = document.getElementById('adminKeyInput');
    const key = input.value.trim();
    
    if (AdminKeyManager.set(key)) {
        updateAdminKeyStatus('success', '✅ 管理员密钥已保存');
    } else {
        updateAdminKeyStatus('error', '❌ 请输入有效的密钥');
    }
}

function clearAdminKey() {
    if (confirm('确定要清除管理员密钥吗？清除后将无法访问管理功能。')) {
        AdminKeyManager.clear();
        document.getElementById('adminKeyInput').value = '';
        updateAdminKeyStatus('warning', '⚠️ 管理员密钥已清除');
    }
}

function updateAdminKeyStatus(type = 'info', message = '') {
    const statusDiv = document.getElementById('adminKeyStatus');
    const colors = {
        success: '#ecfdf5',
        error: '#fef2f2',
        warning: '#fff3cd',
        info: '#f0f9ff'
    };
    
    if (message) {
        statusDiv.style.background = colors[type];
        statusDiv.textContent = message;
    } else {
        if (AdminKeyManager.isSet()) {
            statusDiv.style.background = colors.success;
            statusDiv.textContent = '✅ 管理员密钥已设置';
        } else {
            statusDiv.style.background = colors.warning;
            statusDiv.textContent = '⚠️ 未设置管理员密钥';
        }
    }
}

/*
 * ========== 初始化 ==========
 */

// 页面加载时添加管理员设置按钮
window.addEventListener('DOMContentLoaded', () => {
    // 添加管理员设置界面
    document.body.insertAdjacentHTML('beforeend', adminSettingsHTML);
    
    // 如果未设置管理员密钥，提示用户
    if (!AdminKeyManager.isSet()) {
        setTimeout(() => {
            if (confirm('检测到您还没有设置管理员密钥。\n\n管理员密钥用于保护密钥管理功能，防止未授权访问。\n\n是否现在设置？')) {
                showAdminSettings();
            }
        }, 1000);
    }
});

// 导出给window使用
window.AdminKeyManager = AdminKeyManager;
window.authFetch = authFetch;

