import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0"
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
