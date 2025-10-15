import fs from 'fs'
import path from 'path'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0",
    https: {
      key: fs.readFileSync(path.resolve(__dirname, 'localhost-key.pem')),
      cert: fs.readFileSync(path.resolve(__dirname, 'localhost.pem'))
    },
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
