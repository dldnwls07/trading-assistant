import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  build: {
    // Node v24 환경에서 Rollup 크래시를 방지하기 위해 설정을 간소화합니다.
    minify: false,
    sourcemap: false,
    chunkSizeWarningLimit: 2000,
    rollupOptions: {
      maxParallelFileOps: 1, // 파일 처리 병렬도를 낮춰 메모리/스레드 이슈 방지
    }
  }
})
