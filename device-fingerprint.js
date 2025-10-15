/**
 * 设备指纹生成器 - 跨域名一致的硬件机器码
 * 
 * 特点：
 * 1. 不依赖 localStorage（避免跨域问题）
 * 2. 基于硬件特征生成（同一设备生成相同ID）
 * 3. 跨域名一致（阿里云和Vercel生成相同机器码）
 * 4. 高准确性（结合多种硬件特征）
 */

function generateDeviceId() {
    // 🔑 基于硬件特征生成唯一机器码（跨域名一致）
    // 不使用 localStorage，每次都重新计算，确保跨域名时生成相同的ID
    
    try {
        // Canvas指纹
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillText('Device fingerprint', 2, 2);
        const canvasData = canvas.toDataURL();
        
        // WebGL指纹
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        let webglVendor = '';
        let webglRenderer = '';
        if (gl) {
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            if (debugInfo) {
                webglVendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                webglRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            }
        }
        
        // 收集硬件特征（这些特征在同一设备上是稳定的）
        const fingerprint = [
            // 浏览器信息
            navigator.userAgent,
            navigator.language,
            navigator.languages ? navigator.languages.join(',') : '',
            navigator.platform,
            
            // 屏幕信息
            screen.width + 'x' + screen.height,
            screen.colorDepth,
            screen.pixelDepth,
            window.devicePixelRatio || 1,
            
            // 时区
            new Date().getTimezoneOffset(),
            Intl.DateTimeFormat().resolvedOptions().timeZone,
            
            // 硬件信息
            navigator.hardwareConcurrency || 0,
            navigator.maxTouchPoints || 0,
            
            // Canvas指纹
            canvasData,
            
            // WebGL指纹
            webglVendor,
            webglRenderer,
            
            // 其他特征
            navigator.cookieEnabled,
            navigator.doNotTrack || 'unknown'
        ].join('|');
        
        // 使用SHA-256风格的哈希函数
        let hash = 0;
        for (let i = 0; i < fingerprint.length; i++) {
            const char = fingerprint.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // 转换为32位整数
        }
        
        // 生成唯一ID（36进制，更短更易读）
        const deviceId = Math.abs(hash).toString(36);
        
        // 📝 调试日志（生产环境可删除）
        if (typeof console !== 'undefined' && console.log) {
            console.log('🔑 机器码生成成功:', deviceId.substring(0, 8) + '...');
            console.log('📊 硬件特征:', {
                ua: navigator.userAgent.substring(0, 50) + '...',
                screen: screen.width + 'x' + screen.height,
                platform: navigator.platform,
                cores: navigator.hardwareConcurrency,
                webgl: webglRenderer || '不可用'
            });
        }
        
        return deviceId;
        
    } catch (error) {
        // 降级方案：如果指纹生成失败，使用基础特征
        if (typeof console !== 'undefined' && console.error) {
            console.error('机器码生成失败，使用降级方案:', error);
        }
        
        const fallback = [
            navigator.userAgent,
            screen.width + 'x' + screen.height,
            navigator.platform
        ].join('|');
        
        let hash = 0;
        for (let i = 0; i < fallback.length; i++) {
            hash = ((hash << 5) - hash) + fallback.charCodeAt(i);
            hash = hash & hash;
        }
        
        return 'fb_' + Math.abs(hash).toString(36); // fb = fallback
    }
}

/**
 * 获取设备详细信息（用于调试）
 */
function getDeviceInfo() {
    return {
        deviceId: generateDeviceId(),
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        screenResolution: `${screen.width}x${screen.height}`,
        colorDepth: screen.colorDepth,
        pixelRatio: window.devicePixelRatio || 1,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        timezoneOffset: new Date().getTimezoneOffset(),
        hardwareConcurrency: navigator.hardwareConcurrency || 0,
        maxTouchPoints: navigator.maxTouchPoints || 0,
        cookieEnabled: navigator.cookieEnabled
    };
}

// 导出函数（如果使用模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { generateDeviceId, getDeviceInfo };
}

