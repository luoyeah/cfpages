<template>
  <div class="location-recorder">
    <div class="btn-group">
      <button class="btn btn-primary" @click="handleRecord">
        <i>⏱️</i> 记录当前时间和位置
      </button>
      <button class="btn btn-success" @click="handleExport">
        <i>📥</i> 导出为CSV文件
      </button>
    </div>

    <div class="status" :style="{ borderLeftColor: status.isError ? '#e74c3c' : '#3498db' }">
      <i>{{ status.isError ? '❌' : 'ℹ️' }}</i>
      <span>{{ status.message }}</span>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>序号</th>
            <th>记录时间</th>
            <th>日期</th>
            <th>经度</th>
            <th>纬度</th>
            <th>精确度</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="records.length === 0" class="empty-row">
            <td colspan="6">暂无记录数据</td>
          </tr>
          <tr v-for="(record, index) in records" :key="record.id">
            <td>{{ index + 1 }}</td>
            <td>{{ record.time }}</td>
            <td>{{ record.date }}</td>
            <td :class="{ 'loading-text': record.loading, 'error-text': record.error }">
              <span v-if="record.loading" class="loading-spinner"></span>
              {{ record.loading ? '获取中...' : (record.error || record.longitude.toFixed(6)) }}
            </td>
            <td :class="{ 'loading-text': record.loading, 'error-text': record.error }">
              <span v-if="record.loading" class="loading-spinner"></span>
              {{ record.loading ? '获取中...' : (record.error || record.latitude.toFixed(6)) }}
            </td>
            <td :class="{ 'loading-text': record.loading, 'error-text': record.error }">
              <span v-if="record.loading" class="loading-spinner"></span>
              {{ record.loading ? '获取中...' : (record.error || Math.round(record.accuracy) + ' 米') }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';


// 响应式数据
const records = ref([]);
const status = reactive({
  message: '准备就绪，点击上方按钮开始记录',
  isError: false
});

// 更新状态信息
const updateStatus = (message, isError = false) => {
  status.message = message;
  status.isError = isError;
};

// 获取当前位置
const getCurrentLocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject("您的浏览器不支持地理位置功能");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      position => {
        resolve({
          longitude: position.coords.longitude,
          latitude: position.coords.latitude,
          accuracy: position.coords.accuracy
        });
      },
      error => {
        let errorMessage;
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = "用户拒绝了地理位置请求";
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = "位置信息不可用";
            break;
          case error.TIMEOUT:
            errorMessage = "获取位置超时";
            break;
          default:
            errorMessage = "发生未知错误";
        }
        reject(errorMessage);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  });
};

// 格式化日期和时间
const formatDateTime = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');

  return {
    time: `${hours}:${minutes}:${seconds}`,
    date: `${year}-${month}-${day}`
  };
};

// 处理记录事件
const handleRecord = async () => {
  // 获取当前时间
  const now = new Date();
  const { time, date } = formatDateTime(now);
  
  // 创建新记录（带加载状态）
  const newRecord = {
    id: Date.now(),
    time,
    date,
    longitude: 0,
    latitude: 0,
    accuracy: 0,
    loading: true,
    error: null
  };
  
  // 添加到记录列表
  records.value.unshift(newRecord);
  updateStatus("正在获取位置信息...");
  
  try {
    // 异步获取位置信息
    const location = await getCurrentLocation();
    
    // 更新记录
    newRecord.longitude = location.longitude;
    newRecord.latitude = location.latitude;
    newRecord.accuracy = location.accuracy;
    newRecord.loading = false;
    
    updateStatus(`记录成功！位置：经度 ${location.longitude.toFixed(6)}, 纬度 ${location.latitude.toFixed(6)}`);
  } catch (error) {
    // 更新记录错误信息
    newRecord.error = error;
    newRecord.loading = false;
    updateStatus(error, true);
  }
};

// 处理导出事件
const handleExport = () => {
  // 过滤掉正在加载的记录
  const validRecords = records.value.filter(r => !r.loading);
  
  // 检查是否有数据
  if (validRecords.length === 0) {
    updateStatus("没有数据可导出", true);
    return;
  }

  // 创建CSV内容
  let csvContent = "序号,记录时间,日期,经度,纬度,精确度(米)\n";

  validRecords.forEach((record, index) => {
    const rowData = [
      index + 1,
      record.time,
      record.date,
      record.error ? record.error : record.longitude.toFixed(6),
      record.error ? record.error : record.latitude.toFixed(6),
      record.error ? record.error : Math.round(record.accuracy)
    ];
    
    csvContent += rowData.map(data => {
      if (data.toString().includes(',')) {
        return `"${data}"`;
      }
      return data;
    }).join(',') + '\n';
  });

  // 创建下载链接
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  const now = new Date();
  const timestamp = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}`;

  link.setAttribute('href', url);
  link.setAttribute('download', `位置记录_${timestamp}.csv`);
  link.style.visibility = 'hidden';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  updateStatus(`数据已导出为CSV文件 (${validRecords.length} 条记录)`);
};
</script>

<style scoped>
.location-recorder {
  width: 100%;
}

.btn-group {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.btn {
  padding: 12px 25px;
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

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

th,
td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #f8f9fa;
  color: #2c3e50;
  font-weight: 600;
}

tr:hover {
  background-color: #f8f9fa;
}

.empty-row {
  text-align: center;
  padding: 30px;
  color: #7f8c8d;
  font-style: italic;
}

@media (max-width: 768px) {
  .btn-group {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  th,
  td {
    padding: 10px 8px;
    font-size: 0.9rem;
  }
}

/* 新增样式 */
.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 3px solid rgba(52, 152, 219, 0.3);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #7f8c8d;
  font-style: italic;
}

.error-text {
  color: #e74c3c;
  font-weight: 500;
}
</style>