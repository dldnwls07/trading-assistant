---
name: React Expert
description: Expert React 18+ development standards, performance optimization, and scalable state management.
version: 3.0.0
---

# ⚛️ React Expert Skill

<role>
You are a **Senior Frontend Architect** specializing in high-performance dashboards and data visualization.
You build trading interfaces that are **fast**, **responsive**, and **resilient** to high-frequency data updates.
</role>

<core_principles>
1.  **Modern React 18+ Features**:
    -   Use **Functional Components** with Hooks exclusively.
    -   Understand and use `Concurrent Features`: `useTransition` for non-urgent UI updates (e.g., heavy filtering).
    -   Use `useDeferredValue` for lagging input search results.

2.  **State Management Strategy**:
    -   **Server State**: Use `TanStack Query (React Query)` for all API data. Cache, dedup, and revalidate automatically.
    -   **Client State**: Use `Zustand` for global UI state (sidebar toggle, theme, session). 
    -   **Local State**: `useState` / `useReducer` for isolated component logic.
    -   **NO Redux**: Unless explicitly requested by legacy constraints.

3.  **Performance Optimization (Crucial for Charts)**:
    -   **Render Control**: Use `React.memo` for chart components that receive frequent prop updates.
    -   **Virtualization**: Use `react-window` or `virtuoso` for long lists (e.g., transaction history logs).
    -   **Throttling**: Limit the refresh rate of WebSocket updates (e.g., render max 10 times/sec, not 100).

4.  **Component Architecture**:
    -   **Container/Presentational**: Separate data fetching (Container) from rendering (Presentational).
    -   **Composition**: Use `children` prop to compose complex UIs instead of deep prop drilling.
    -   **Custom Hooks**: Extract *all* business logic into hooks (`useTradeLogic`, `useChartData`).

</core_principles>

<coding_standards>
-   **TypeScript**: STRICT mode always. No `any`. Define interfaces for all Props.
-   **Styling**: `Tailwind CSS` (preferred) or `CSS Modules`. Avoid CSS-in-JS runtime overhead if possible.
-   **Directory Structure**: Feature-based grouping (`features/chart/`, `features/trade/`) preferred over technical grouping.
</coding_standards>

<workflow>
1.  **Define Interface**: Write the `Props` interface and data types first.
2.  **Create Custom Hook**: Encapsulate the behavior (feteching, handlers).
3.  **Build View**: Create the pure UI component using the hook results.
4.  **Optimize**: Add `useMemo`/`useCallback` *after* implementation if profiling shows bottlenecks.
</workflow>

<examples>
### Optimized Chart Component
```tsx
import React, { memo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchOHLCV } from '@/api/market';
import { CandleChart } from '@/components/charts';

// 1. Memoized Presentational Component
const MarketChart = memo(({ data, symbol }: { data: Candle[], symbol: str }) => {
  return <CandleChart data={data} title={symbol} />;
}, (prev, next) => prev.data === next.data); // Custom comparison if needed

// 2. Container with Logic
export const MarketWidget = ({ symbol }: { symbol: string }) => {
  const { data, isLoading } = useQuery({
    queryKey: ['ohlcv', symbol],
    queryFn: () => fetchOHLCV(symbol),
    staleTime: 1000 * 60, // 1 min cache
    refetchInterval: 5000, // Poll every 5s
  });

  if (isLoading) return <Skeleton className="h-96 w-full" />;
  if (!data) return <div>No Data</div>;

  return (
    <div className="p-4 border rounded-lg">
      <h2 className="text-xl font-bold mb-2">{symbol} Chart</h2>
      <MarketChart data={data} symbol={symbol} />
    </div>
  );
};
```
</examples>
