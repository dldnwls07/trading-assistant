const API_URL = "http://127.0.0.1:8000";

// --- Utility Functions ---
function formatText(text) {
    if (!text) return "";
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
}

function addMessage(sender, html, isLoading = false) {
    const container = document.getElementById("chat-container");
    const div = document.createElement("div");

    if (sender === "System") div.className = "message system";
    else div.className = `message ${sender.toLowerCase()}`;

    if (isLoading) {
        div.id = `loading-${Date.now()}`;
        div.classList.add("loading");
    }

    div.innerHTML = html;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div.id;
}

function removeMessage(id) {
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.remove();
}

// 오인 방지 블랙리스트
const BLOCKLIST = [
    "THE", "AND", "FOR", "NEW", "NOW", "USA", "CEO", "CFO", "ETF", "USD", "KRW",
    "KOSPI", "KOSDAQ", "URL", "HTTP", "HTTPS", "WWW", "COM", "NET", "ORG",
    "HTML", "CSS", "API", "APP", "WEB", "SITE", "PAGE", "MENU", "HOME",
    "LOGIN", "SIGN", "OUT", "TOP", "BOT", "NAV", "BAR", "TAB", "IMG", "DIV",
    "SPAN", "LOG", "KEY", "ID", "PW", "FAQ", "QNA", "ASK", "AI", "LLM", "GPT",
    "PRICE", "CHART", "DATA", "INFO", "NEWS", "NULL", "NONE", "NAN", "WIKI"
];

// --- Main Event Landscape ---

document.addEventListener("DOMContentLoaded", () => {
    addMessage("System", `
        <div style="text-align:center; padding:10px 0;">
            <h3>📊 Trading Assistant</h3>
            <p style="color:#64748b; font-size:0.9rem;">
                현재 증권/금융 페이지를 분석합니다.
            </p>
            <button id="analyzePageBtn" style="width:100%; border-radius:12px; background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; padding:10px; margin-top:10px; cursor:pointer; font-weight:600;">
                📸 현재 화면 읽기
            </button>
        </div>
    `);

    // Context Menu Handler
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.action === "analyze") {
            handlePageAnalysis(request.content);
        }
    });

    // UI Event Listeners
    const sendBtn = document.getElementById("sendBtn");
    const userInput = document.getElementById("userInput");

    if (sendBtn) sendBtn.addEventListener("click", handleUserAction);
    if (userInput) userInput.addEventListener("keypress", (e) => { if (e.key === "Enter") handleUserAction(); });

    document.addEventListener("click", (e) => {
        if (e.target && e.target.id === "analyzePageBtn") handlePageAnalysis();
    });

    async function handleUserAction() {
        const userText = userInput.value.trim();
        if (!userText) return;

        addMessage("User", userText, false);
        userInput.value = "";

        if (userText.includes("화면") || userText.includes("페이지") || userText.includes("여기")) {
            handlePageAnalysis(userText);
            return;
        }

        const ticker = await detectTicker(userText);
        if (ticker) await processStockAnalysis(ticker, userText);
        else await processAIRequest(userText);
    }
});

// --- Core Logic: Screen Scraping (Restricted) ---

async function scrapeScreenData() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return null;

    const injectionResults = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            // [보안 필터] 금융 사이트인지 엄격히 검사
            const url = window.location.href.toLowerCase();
            const title = document.title.toLowerCase();

            // 1. 도메인 화이트리스트
            const validDomains = [
                "finance", "stock", "invest", "trading", "crypto", "upbit", "bithumb", "coin", "koreaex",
                "naver.com", "daum.net", "yahoo", "google.com/finance", "tossinvest", "bloomberg",
                "cnbc", "wsj", "reuters", "hankyung", "mk.co.kr", "sedaily", "alpha"
            ];

            // 2. 키워드 검사 (도메인이 달라도 제목에 '증권' 등 있으면 OK)
            const validKeywords = ["증권", "주식", "금융", "투자", "stock", "market", "finance", "korea exchange"];

            const isFinancialSite = validDomains.some(d => url.includes(d)) ||
                validKeywords.some(w => title.includes(w));

            if (!isFinancialSite) {
                return { isFinancial: false }; // 금융 사이트 아님
            }

            // --- 스크래핑 시작 ---
            const bodyText = document.body.innerText;
            const keywords = ["이동평균", "볼린저", "MACD", "RSI", "스토캐스틱", "거래량", "PER", "PBR", "시가총액", "Volume", "Market Cap"];
            let foundIndicators = [];

            keywords.forEach(kw => {
                // 키워드 주변 30글자 내의 숫자/특수문자 추출
                const regex = new RegExp(`${kw}.{0,30}?([0-9,.]+%?)`, 'gi');
                const matches = bodyText.match(regex);
                if (matches) {
                    foundIndicators.push(matches[0].replace(/\s+/g, ' '));
                }
            });

            return {
                isFinancial: true,
                title: document.title,
                url: window.location.href,
                indicators: foundIndicators.join(", "),
                fullText: bodyText.substring(0, 800)
            };
        }
    });

    return injectionResults[0].result;
}

// --- Core Logic: Ticker Detection ---

async function detectTicker(text) {
    if (!text) return null;

    if (text.includes("isFinancial: false")) return null;

    const parenMatch = text.match(/\(([A-Z]{2,5}|[0-9]{6}(\.[A-Z]{2})?)\)/);
    if (parenMatch) {
        const candidate = parenMatch[1].replace(/\.[A-Z]{2}$/, '');
        if (!BLOCKLIST.includes(candidate)) return candidate;
    }

    const urlMatch = text.match(/\/quote\/([A-Z]{1,5})/);
    if (urlMatch && !BLOCKLIST.includes(urlMatch[1])) return urlMatch[1];

    const krMatch = text.match(/\b([0-9]{6})\b/);
    if (krMatch) return krMatch[1];

    const matches = text.matchAll(/\b([A-Z]{2,5})\b/g);
    for (const match of matches) {
        const candidate = match[1];
        if (!BLOCKLIST.includes(candidate)) return candidate;
    }

    return null;
}

// --- Core Logic: Page Analysis (Hybrid) ---

async function handlePageAnalysis(userQuery = "") {
    const loadingId = addMessage("AI", "👁️ 금융 데이터 스캔 중...", true);

    // 1. 화면 스크래핑
    const screenData = await scrapeScreenData();

    if (!screenData || screenData.isFinancial === false) {
        removeMessage(loadingId);
        addMessage("AI", "🚫 <strong>금융/투자 사이트가 아닙니다.</strong><br>증권사 홈페이지나 금융 뉴스에서 실행해주세요.");
        return;
    }

    try {
        const combinedText = `Title: ${screenData.title}, Text: ${screenData.fullText}`;
        const ticker = await detectTicker(combinedText);

        removeMessage(loadingId);

        if (ticker) {
            addMessage("AI", `🔍 <strong>${ticker}</strong> 감지됨!`);
            await processStockAnalysis(ticker, userQuery || "현재 화면 데이터를 바탕으로 분석해줘", screenData);
        } else {
            addMessage("AI", `📄 종목 미감지 (화면 분석 모드)`);
            const prompt = `
            [화면 데이터 직접 분석]
            제목: ${screenData.title}
            감지된 지표: ${screenData.indicators}
            내용 요약: ${screenData.fullText}
            질문: "${userQuery}"
            
            위 정보를 바탕으로 주식 투자 관점에서 분석하세요. 
            화면에 보이는 보조지표(RSI, 볼린저 등)가 있다면 적극적으로 해석하세요.
            `;
            await processAIRequest(prompt);
        }

    } catch (e) {
        removeMessage(loadingId);
        addMessage("AI", "❌ 분석 실패");
    }
}

// --- Core Logic: Stock Analysis (Hybrid Data Source) ---

async function processStockAnalysis(ticker, userQuestion, screenData = null) {
    const loadingId = addMessage("AI", `⏳ <strong>${ticker}</strong> 데이터 통합 중...`, true);

    try {
        let apiData = {};
        try {
            const res = await fetch(`${API_URL}/analyze/${ticker}`);
            apiData = await res.json();
        } catch (e) {
            console.log("API Fetch Failed - Using Screen Data Only");
        }

        removeMessage(loadingId);

        const indicatorsFromScreen = screenData?.indicators || "화면에서 감지된 지표 없음";
        const currentPrice = apiData.current_price ? `$${Number(apiData.current_price).toLocaleString()}` : "화면 참고 필요";

        if (apiData.ticker) {
            renderStockCard(apiData);
        } else {
            addMessage("System", `<div class="message system">⚠️ API 데이터 연동 실패. 화면 데이터로 분석합니다.</div>`);
        }

        const loadingAI = addMessage("AI", "🧠 하이브리드 분석 중...", true);

        const injectedContext = `
        [긴급 분석 요청: ${ticker}]
        당신은 실시간 트레이딩 룸의 수석 분석가입니다.
        API 데이터와 **현재 사용자가 보고 있는 화면 데이터(Screen Data)**를 모두 종합하여 분석하세요.
        
        [API 데이터 (과거/지연될 수 있음)]
        - 현재가: ${currentPrice}
        - AI 점수: ${apiData.final_score || 'N/A'}/100
        - 신호: ${apiData.signal || 'N/A'}
        - 기술적 지표(API): RSI=${apiData.technical_analysis?.rsi?.toFixed(2) || '-'}, MACD=${apiData.technical_analysis?.macd || '-'}
        
        [★ 화면 데이터 (실시간/사용자 관찰 중)]
        - 페이지 제목: ${screenData?.title || 'N/A'}
        - **감지된 지표 텍스트**: ${indicatorsFromScreen}
        - 페이지 텍스트 요약: ${screenData?.fullText?.substring(0, 200) || 'N/A'}...
        
        [지시사항]
        1. API 데이터가 비어있다면(N/A), **화면 데이터**를 최우선 근거로 삼으세요.
        2. 화면 내용에 "볼린저 밴드", "이동평균선" 등의 단어가 보이면 그 맥락을 파악하여 설명하세요.
        3. 구체적인 매수/매도 타이밍을 질문받았다면, "제공된 정보 내에서 판단컨대..." 라고 전제하고 의견을 내세요.
        `;

        const fullMessage = `${injectedContext}\n\n[사용자 질문]\n"${userQuestion}"`;

        const chatRes = await fetch(`${API_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: fullMessage })
        });
        const chatData = await chatRes.json();

        removeMessage(loadingAI);
        addMessage("AI", formatText(chatData.response));

    } catch (e) {
        removeMessage(loadingId);
        if (e.name === 'AbortError') {
            console.log("Request aborted");
            return;
        }
        addMessage("AI", "❌ 서버 통신 오류");
        console.error(e);
    }
}

async function processAIRequest(text) {
    const loadingId = addMessage("AI", "💬 ...", true);
    try {
        const res = await fetch(`${API_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        removeMessage(loadingId);
        addMessage("AI", formatText(data.response));
    } catch (e) {
        removeMessage(loadingId);
        addMessage("AI", "❌ AI 서버 응답 없음");
    }
}

// --- UI Rendering ---

function renderStockCard(data) {
    const change = data.daily_analysis?.change_percent || 0;
    const isUp = change >= 0;
    const colorClass = isUp ? "color:#dc2626" : "color:#2563eb";
    const sign = isUp ? "+" : "";

    // 안전한 점수 계산
    const score = data.final_score || 50;
    const scoreColor = score >= 70 ? "#16a34a" : score >= 40 ? "#ca8a04" : "#dc2626";
    const scoreWidth = Math.min(Math.max(score, 0), 100);

    const priceDisplay = data.current_price ? `$${Number(data.current_price).toLocaleString()}` : "Check Price...";

    const html = `
        <div class="stock-card" style="border-left: 4px solid ${scoreColor}; padding: 12px; background:white; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:10px; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong style="font-size:1.1rem; color:#1e293b;">${data.ticker}</strong>
                    <div style="font-size:0.75rem; color:#64748b;">${data.display_name || ''}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.2rem; font-weight:800; color:#0f172a;">${priceDisplay}</div>
                    <div style="font-size:0.9rem; font-weight:600; ${colorClass}">${sign}${change.toFixed(2)}%</div>
                </div>
            </div>

            <div style="margin: 12px 0;">
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#475569; margin-bottom:4px;">
                    <span>AI Confidence</span>
                    <strong style="color:${scoreColor}">${score}</strong>
                </div>
                <div style="background:#e2e8f0; height:6px; border-radius:3px; overflow:hidden;">
                    <div style="background:${scoreColor}; width:${scoreWidth}%; height:100%;"></div>
                </div>
            </div>
            
            <div style="display:flex; gap:6px;">
                <span style="background:${data.signal.includes('BUY') ? '#dcfce7' : '#fee2e2'}; color:${data.signal.includes('BUY') ? '#166534' : '#991b1b'}; padding:4px 8px; border-radius:4px; font-size:0.75rem; font-weight:bold;">
                    ${data.signal}
                </span>
                <span style="background:#f1f5f9; color:#475569; padding:4px 8px; border-radius:4px; font-size:0.75rem;">
                    RSI ${data.technical_analysis?.rsi?.toFixed(1) || '-'}
                </span>
            </div>
        </div>
    `;
    addMessage("System", html);
}
