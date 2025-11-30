import fs from 'fs'
import path from 'path'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0",
        // 添加代理配置
    proxy: {
      // 匹配所有以 /api 開頭的請求
      '/api': {
        // 目標伺服器地址
        target: 'http://localhost:9001',
        // 改變源頭 (Origin)，確保請求頭中的 Host 設置為目標 URL
        changeOrigin: true,
        // 可選：如果您希望後端接收的路徑不包含 /api 前綴，可以取消註釋以下行
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
    },
    // https: {
    //   key: fs.readFileSync(path.resolve(__dirname, 'localhost-key.pem')),
    //   cert: fs.readFileSync(path.resolve(__dirname, 'localhost.pem'))
    // },
  },
  build: {
    rollupOptions: {
      input: 'main.html' // 你的自定义入口文件
    },
    outDir: 'dist',
    assetsDir: 'assets',
  },

  base: ''
})
