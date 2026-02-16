import { useEffect } from 'react';

export const useChartResize = (chart, containerRef, isFullscreen) => {
    useEffect(() => {
        if (!chart || !containerRef.current) return;

        const handleResize = () => {
            // chart is already the instance
            if (chart && containerRef.current) {
                // 풀스크린 모드일 때는 window.innerHeight를, 아닐 때는 부모 컨테이너의 높이를 사용
                // 단, 부모 컨테이너 높이가 제대로 잡히지 않는 경우를 대비해 최소 높이 보장
                const width = containerRef.current.clientWidth;
                const height = isFullscreen ? window.innerHeight : Math.max(containerRef.current.clientHeight, 500);

                chart.applyOptions({ width, height });
                chart.timeScale().fitContent();
            }
        };

        // 초기 실행
        handleResize();
        // 풀스크린 전환 시 애니메이션/레이아웃 변경 완료 후 재조정 (지연 실행)
        setTimeout(handleResize, 100);
        setTimeout(handleResize, 300);

        // ResizeObserver로 컨테이너 크기 변화 감지
        const resizeObserver = new ResizeObserver(() => {
            // 디바운싱 없이 즉시 반응하도록 하여 부드러운 전환 유도 (필요 시 requestAnimationFrame 적용 가능)
            window.requestAnimationFrame(handleResize);
        });

        resizeObserver.observe(containerRef.current);
        window.addEventListener('resize', handleResize); // 윈도우 리사이즈 이벤트도 함께 수신

        return () => {
            resizeObserver.disconnect();
            window.removeEventListener('resize', handleResize);
        };
    }, [chart, containerRef, isFullscreen]);
};
