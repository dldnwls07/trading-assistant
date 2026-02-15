import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';
// 브라우저에서는 환경변수 접근이 제한적일 수 있어 우선 기본값을 사용합니다.
// 실제 배포 시에는 빌드 타임 환경변수(VITE_ / REACT_APP_)로 관리하는 것이 권장됩니다.
const API_KEY = "trading-assistant-secret-2024";

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
    }
});

export default api;
