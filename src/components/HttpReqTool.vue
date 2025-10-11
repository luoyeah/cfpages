<template>
  <div class="http-request-tool">
    <div class="tool-header">
      <h2 class="card-title">HTTP 请求调试工具</h2>
      <p class="tool-description">发送 HTTP 请求并查看响应结果</p>
    </div>

    <div class="request-section">
      <div class="form-group">
        <div class="method-url">
          <select v-model="request.method" class="method-select">
            <option v-for="method in httpMethods" :key="method" :value="method">
              {{ method }}
            </option>
          </select>
          <input 
            v-model="request.url" 
            type="text" 
            placeholder="输入请求URL (例如: https://api.example.com/data)" 
            class="url-input"
          />
          <button class="btn btn-primary" @click="sendRequest">
            <i>🚀</i> 发送请求
          </button>
        </div>
      </div>

      <div class="form-group">
        <div class="section-header">
          <h3>请求头</h3>
          <button class="btn btn-small" @click="addHeader">
            <i>➕</i> 添加
          </button>
        </div>
        <div class="headers-container">
          <div v-for="(header, index) in request.headers" :key="index" class="header-row">
            <input 
              v-model="header.key" 
              type="text" 
              placeholder="Header 名称" 
              class="header-input"
            />
            <input 
              v-model="header.value" 
              type="text" 
              placeholder="Header 值" 
              class="header-input"
            />
            <button class="btn btn-small btn-danger" @click="removeHeader(index)">
              <i>🗑️</i>
            </button>
          </div>
        </div>
      </div>

      <div class="form-group">
        <div class="section-header">
          <h3>请求体</h3>
          <div class="content-type">
            <label>Content-Type:</label>
            <select v-model="request.contentType" class="content-type-select">
              <option value="application/json">application/json</option>
              <option value="application/x-www-form-urlencoded">x-www-form-urlencoded</option>
              <option value="text/plain">text/plain</option>
              <option value="multipart/form-data">multipart/form-data</option>
            </select>
          </div>
        </div>
        <textarea 
          v-model="request.body" 
          placeholder="输入请求体内容 (JSON, form data等)" 
          class="body-textarea"
          rows="8"
        ></textarea>
      </div>
    </div>

    <div class="response-section">
      <div class="section-header">
        <h3>响应结果</h3>
        <div class="response-status">
          <span v-if="response.status" class="status-code" :class="statusClass">
            {{ response.status }} {{ response.statusText }}
          </span>
          <span v-if="response.time" class="response-time">
            耗时: {{ response.time }}ms
          </span>
        </div>
      </div>

      <div class="tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'body' }" 
          @click="activeTab = 'body'"
        >
          响应体
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'headers' }" 
          @click="activeTab = 'headers'"
        >
          响应头
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'request' }" 
          @click="activeTab = 'request'"
        >
          原始请求
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'body'" class="response-body">
          <pre v-if="isJsonResponse" class="json-response">{{ formattedResponse }}</pre>
          <pre v-else class="text-response">{{ response.body }}</pre>
        </div>

        <div v-if="activeTab === 'headers'" class="response-headers">
          <div v-for="(value, key) in response.headers" :key="key" class="header-row">
            <span class="header-key">{{ key }}:</span>
            <span class="header-value">{{ value }}</span>
          </div>
        </div>

        <div v-if="activeTab === 'request'" class="raw-request">
          <pre>{{ rawRequest }}</pre>
        </div>
      </div>
    </div>

    <div class="status" :style="{ borderLeftColor: status.isError ? '#e74c3c' : '#3498db' }">
      <i>{{ status.isError ? '❌' : 'ℹ️' }}</i>
      <span>{{ status.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';

// HTTP 方法列表
const httpMethods = ref(['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']);

// 请求数据
const request = reactive({
  method: 'GET',
  url: '',
  headers: [
    { key: 'Accept', value: 'application/json' },
    { key: 'Content-Type', value: 'application/json' }
  ],
  contentType: 'application/json',
  body: ''
});

// 响应数据
const response = reactive({
  status: null,
  statusText: '',
  headers: {},
  body: '',
  time: null
});

// 状态信息
const status = reactive({
  message: '准备就绪，输入URL并发送请求',
  isError: false
});

// 活动标签页
const activeTab = ref('body');

// 更新状态信息
const updateStatus = (message, isError = false) => {
  status.message = message;
  status.isError = isError;
};

// 添加请求头
const addHeader = () => {
  request.headers.push({ key: '', value: '' });
};

// 移除请求头
const removeHeader = (index) => {
  request.headers.splice(index, 1);
};

// 检查是否是JSON响应
const isJsonResponse = computed(() => {
  const contentType = response.headers['content-type'] || '';
  return contentType.includes('application/json');
});

// 格式化JSON响应
const formattedResponse = computed(() => {
  if (!response.body) return '';
  
  try {
    if (isJsonResponse.value) {
      return JSON.stringify(JSON.parse(response.body), null, 2);
    }
    return response.body;
  } catch (e) {
    return response.body;
  }
});

// 根据状态码设置样式类
const statusClass = computed(() => {
  if (!response.status) return '';
  
  if (response.status >= 200 && response.status < 300) {
    return 'status-success';
  } else if (response.status >= 400 && response.status < 500) {
    return 'status-client-error';
  } else if (response.status >= 500) {
    return 'status-server-error';
  }
  return '';
});

// 原始请求信息
const rawRequest = computed(() => {
  let raw = `${request.method} ${request.url}\n`;
  
  // 添加请求头
  raw += 'Headers:\n';
  request.headers.forEach(header => {
    if (header.key && header.value) {
      raw += `  ${header.key}: ${header.value}\n`;
    }
  });
  
  // 添加请求体
  if (request.body) {
    raw += '\nBody:\n';
    try {
      // 尝试格式化JSON
      const parsed = JSON.parse(request.body);
      raw += JSON.stringify(parsed, null, 2);
    } catch (e) {
      raw += request.body;
    }
  }
  
  return raw;
});

// 发送HTTP请求
const sendRequest = async () => {
  // 验证URL
  if (!request.url) {
    updateStatus('请输入请求URL', true);
    return;
  }
  
  try {
    updateStatus('正在发送请求...');
    
    // 准备请求头
    const headers = {};
    request.headers.forEach(header => {
      if (header.key && header.value) {
        headers[header.key] = header.value;
      }
    });
    
    // 更新Content-Type
    if (request.contentType) {
      headers['Content-Type'] = request.contentType;
    }
    
    // 准备请求选项
    const options = {
      method: request.method,
      headers: headers
    };
    
    // 添加请求体（GET和HEAD请求不能有body）
    if (request.body && request.method !== 'GET' && request.method !== 'HEAD') {
      options.body = request.body;
    }
    
    // 记录开始时间
    const startTime = Date.now();
    
    // 发送请求
    const res = await fetch(request.url, options);
    
    // 记录响应时间
    response.time = Date.now() - startTime;
    
    // 获取响应头
    const responseHeaders = {};
    res.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });
    
    // 获取响应体
    const body = await res.text();
    
    // 更新响应数据
    response.status = res.status;
    response.statusText = res.statusText;
    response.headers = responseHeaders;
    response.body = body;
    
    updateStatus(`请求成功完成 (${res.status} ${res.statusText})`);
  } catch (error) {
    console.error('请求失败:', error);
    
    // 更新响应数据
    response.status = 0;
    response.statusText = 'Network Error';
    response.headers = {};
    response.body = error.message;
    response.time = null;
    
    updateStatus(`请求失败: ${error.message}`, true);
  }
};
</script>

<style scoped>
.http-request-tool {
  width: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.tool-header {
  margin-bottom: 20px;
}

.card-title {
  color: #3498db;
  font-size: 1.4rem;
  margin-bottom: 5px;
}

.tool-description {
  color: #7f8c8d;
  font-size: 1rem;
}

.request-section, .response-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin: 0;
}

.method-url {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.method-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 1rem;
  width: 120px;
}

.url-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-small {
  padding: 6px 12px;
  font-size: 0.9rem;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.headers-container {
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 10px;
}

.header-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.header-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.content-type {
  display: flex;
  align-items: center;
  gap: 10px;
}

.content-type-select {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 0.9rem;
}

.body-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9rem;
  resize: vertical;
}

.response-status {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-code {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

.status-success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-client-error {
  background-color: #ffebee;
  color: #c62828;
}

.status-server-error {
  background-color: #fff3e0;
  color: #e65100;
}

.response-time {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 15px;
}

.tab-btn {
  padding: 8px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.tab-btn.active {
  border-bottom: 3px solid #3498db;
  color: #3498db;
  font-weight: 600;
}

.tab-content {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 15px;
  min-height: 200px;
  max-height: 400px;
  overflow: auto;
}

.response-body, .response-headers, .raw-request {
  font-family: monospace;
  font-size: 0.9rem;
  white-space: pre-wrap;
  word-break: break-all;
}

.json-response {
  color: #2c3e50;
  line-height: 1.5;
}

.text-response {
  color: #2c3e50;
  line-height: 1.5;
}

.header-row {
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.header-key {
  font-weight: 600;
  color: #2c3e50;
  min-width: 200px;
}

.header-value {
  color: #7f8c8d;
}

.status {
  margin-top: 20px;
  padding: 15px;
  border-radius: 8px;
  background: #f8f9fa;
  border-left: 4px solid #3498db;
  display: flex;
  align-items: center;
}

.status i {
  margin-right: 10px;
  font-size: 1.2rem;
  color: #3498db;
}

@media (max-width: 768px) {
  .method-url {
    flex-direction: column;
  }
  
  .method-select, .url-input, .btn {
    width: 100%;
  }
  
  .header-row {
    flex-direction: column;
    gap: 5px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .content-type {
    width: 100%;
    justify-content: space-between;
  }
}
</style>