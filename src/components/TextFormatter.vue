<template>
  <div class="text-formatter">
    <div class="form-group">
      <label for="inputText">输入文本</label>
      <textarea 
        id="inputText" 
        v-model="inputText" 
        placeholder="在此输入文本..." 
        rows="6"
      ></textarea>
    </div>
    
    <div class="btn-group">
      <button class="btn btn-primary" @click="toUpperCase">
        <i>🔠</i> 转大写
      </button>
      <button class="btn btn-primary" @click="toLowerCase">
        <i>🔡</i> 转小写
      </button>
      <button class="btn btn-primary" @click="capitalize">
        <i>🏛️</i> 首字母大写
      </button>
      <button class="btn btn-success" @click="copyToClipboard">
        <i>📋</i> 复制结果
      </button>
      <button class="btn btn-danger" @click="clearText">
        <i>🗑️</i> 清空
      </button>
    </div>
    
    <div class="form-group">
      <label for="outputText">格式化结果</label>
      <textarea 
        id="outputText" 
        v-model="outputText" 
        placeholder="格式化结果将显示在这里..." 
        rows="6"
        readonly
      ></textarea>
    </div>
    
    <div class="status" :style="{ borderLeftColor: status.isError ? '#e74c3c' : '#3498db' }">
      <i>{{ status.isError ? '❌' : 'ℹ️' }}</i>
      <span>{{ status.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';


const inputText = ref('');
const outputText = ref('');
const status = reactive({
  message: '输入文本并选择格式操作',
  isError: false
});

const updateStatus = (message, isError = false) => {
  status.message = message;
  status.isError = isError;
};

const toUpperCase = () => {
  if (!inputText.value.trim()) {
    updateStatus('请输入文本内容', true);
    return;
  }
  
  outputText.value = inputText.value.toUpperCase();
  updateStatus('已转换为大写');
};

const toLowerCase = () => {
  if (!inputText.value.trim()) {
    updateStatus('请输入文本内容', true);
    return;
  }
  
  outputText.value = inputText.value.toLowerCase();
  updateStatus('已转换为小写');
};

const capitalize = () => {
  if (!inputText.value.trim()) {
    updateStatus('请输入文本内容', true);
    return;
  }
  
  outputText.value = inputText.value
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
  
  updateStatus('已转换为首字母大写');
};

const copyToClipboard = () => {
  if (!outputText.value.trim()) {
    updateStatus('没有内容可复制', true);
    return;
  }
  
  navigator.clipboard.writeText(outputText.value)
    .then(() => {
      updateStatus('已复制到剪贴板');
    })
    .catch(() => {
      updateStatus('复制失败', true);
    });
};

const clearText = () => {
  inputText.value = '';
  outputText.value = '';
  updateStatus('已清空所有内容');
};
</script>

<style scoped>
.text-formatter {
  width: 100%;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.3s;
}

textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.btn-group {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
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
  box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3);
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(52, 152, 219, 0.4);
}

.btn-success {
  background: #2ecc71;
  color: white;
  box-shadow: 0 4px 10px rgba(46, 204, 113, 0.3);
}

.btn-success:hover {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(46, 204, 113, 0.4);
}

.btn-danger {
  background: #e74c3c;
  color: white;
  box-shadow: 0 4px 10px rgba(231, 76, 60, 0.3);
}

.btn-danger:hover {
  background: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(231, 76, 60, 0.4);
}

.btn i {
  margin-right: 8px;
  font-size: 1.2rem;
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
  .btn-group {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>