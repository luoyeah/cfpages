<template>
  <div class="container">
    <header>
      <h1>在线工具集</h1>
      <p class="subtitle">一站式解决您的日常需求</p>
    </header>

    <main>
      <!-- 工具选择视图 -->
      <div v-if="!selectedTool" class="tools-grid">
        <div 
          v-for="tool in tools" 
          :key="tool.name"
          class="tool-card"
          @click="selectTool(tool)"
        >
          <div class="card">
            <div class="tool-icon">
              {{ tool.icon }}
            </div>
            <h3 class="tool-title">{{ tool.title }}</h3>
            <p class="tool-desc">{{ tool.description }}</p>
          </div>
        </div>
      </div>

      <!-- 工具详情视图 -->
      <div v-if="selectedTool" class="tool-container">
        <div class="card">
          <div class="tool-header">
            <button class="back-btn" @click="deselectTool">
              &larr; 返回工具列表
            </button>
            <h2 class="card-title">
              {{ selectedTool.title }}
            </h2>
            <p class="tool-description">{{ selectedTool.description }}</p>
          </div>
          
          <component :is="selectedTool.component" />
        </div>
      </div>
    </main>

    <footer>
      <p>在线工具集 &copy; {{ new Date().getFullYear() }} | 所有工具均在浏览器本地运行</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, shallowRef } from 'vue';

// 手动导入工具组件
import LocationRecorder from './components/LocationRecorder.vue';
import HttpReqTool from './components/HttpReqTool.vue';
import TextFormatter from './components/TextFormatter.vue';
// 在这里添加更多工具组件...

// 工具列表
const tools = [
  {
    name: 'LocationRecorder',
    title: '定位记录工具',
    description: '记录您的位置和时间信息，支持导出为CSV文件',
    icon: '📍',
    component: LocationRecorder
  },  
  {
    name: 'HttpReqTool',
    title: 'http请求调试',
    description: 'http请求调试',
    icon: '',
    component: HttpReqTool
  },
  {
    name: 'TextFormatter',
    title: '文本格式化工具',
    description: '转换文本大小写、首字母大写等格式',
    icon: '📝',
    component: TextFormatter
  },
  // 在这里添加更多工具...
];

// 响应式数据
const selectedTool = shallowRef(null);

// 选择工具
const selectTool = (tool) => {
  selectedTool.value = tool;
};

// 取消选择工具
const deselectTool = () => {
  selectedTool.value = null;
};
</script>

<style scoped>
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin: 30px 0;
}

h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 10px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.tool-card {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.tool-card:hover {
  transform: translateY(-5px);
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  padding: 25px;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.tool-card:hover .card {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  background: #f8f9fa;
}

.tool-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
  text-align: center;
}

.tool-title {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 10px;
  text-align: center;
}

.tool-desc {
  color: #7f8c8d;
  font-size: 0.9rem;
  text-align: center;
  line-height: 1.5;
  flex-grow: 1;
}

.tool-container {
  margin-top: 30px;
}

.tool-header {
  margin-bottom: 20px;
}

.back-btn {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 8px 15px;
  font-size: 0.9rem;
  cursor: pointer;
  margin-bottom: 15px;
  color: #3498db;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
}

.back-btn:hover {
  background: #e3f2fd;
  border-color: #3498db;
}

.back-btn i {
  margin-right: 5px;
}

.card-title {
  color: #3498db;
  font-size: 1.4rem;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.tool-description {
  color: #7f8c8d;
  margin-bottom: 20px;
  line-height: 1.6;
}

footer {
  text-align: center;
  margin-top: 40px;
  color: #7f8c8d;
  font-size: 0.9rem;
  padding: 20px;
}

@media (max-width: 768px) {
  .tools-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
  
  .card {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .tools-grid {
    grid-template-columns: 1fr;
  }
  
  h1 {
    font-size: 2rem;
  }
}
</style>