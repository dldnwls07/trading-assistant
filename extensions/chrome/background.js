// 초기 실행 시 우클릭 메뉴 생성
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "analyze-text",
        title: "Trading Assistant: Analyse Selection",
        contexts: ["selection"]
    });

    // 사이드 패널 기본 활성화
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true })
        .catch((error) => console.error(error));
});

// 우클릭 메뉴 클릭 이벤트
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "analyze-text" && info.selectionText) {
        // 사이드 패널 열기 (Chrome 116+ 기능)
        chrome.sidePanel.open({ tabId: tab.id });

        // 사이드 패널이 열릴 때까지 잠시 대기 후 메시지 전송
        setTimeout(() => {
            chrome.runtime.sendMessage({
                action: "analyze",
                content: info.selectionText
            });
        }, 500);
    }
});
