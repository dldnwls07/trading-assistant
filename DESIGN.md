# Design System: Trading Assistant Pro (Stitch Standard)
**Project ID:** Stitch-Analysis-17457833442335774981

## 1. Visual Theme & Atmosphere
**Deep Minimalist FinTech.** The atmosphere is characterized by absolute depth using a Zinc-950 (`#09090B`) core background. It utilizes high-contrast glassmorphism to separate functional modules from the dark canvas. The aesthetic is clean, sharp, and utilitarian, avoiding unnecessary gradients or decorative clutter in favor of crisp typography and vibrant semantic indicators.

## 2. Color Palette & Roles
*   **Golden Accent (#FACC15):** The primary focus color. Used for active states, primary buttons, and critical data points. Matches Tailwind `yellow-400`.
*   **Deep Core Background (#09090B):** The foundational dark tone. Matches Tailwind `zinc-950`.
*   **Glass Surface (rgba(255, 255, 255, 0.05)):** The background for all cards and interactive panels.
*   **Crystal Border (rgba(255, 255, 255, 0.1)):** The razor-sharp edge for all glass elements.
*   **Growth Green (#34D399):** Positive signals and price action. Matches Tailwind `emerald-400`.
*   **Signal Rose (#FB7185):** Negative signals and price action. Matches Tailwind `rose-400`.
*   **Muted Zinc (#71717a):** Secondary text and labels. Matches Tailwind `zinc-400`.

## 3. Typography Rules
*   **Typeface:** `Inter` or `Geist` for a clean, professional sans-serif look. `JetBrains Mono` for all price data, tickers, and algorithmic values to ensure numeric clarity.
*   **Weight Usage:** `font-black` (900) for tickers and primary headers. `font-medium` (500) for body text.
*   **Layout:** Tracking-tight for large price displays, tracking-widest for small meta-labels.

## 4. Component Stylings
*   **Glass Panels:** `bg-white/5 backdrop-blur-md border border-white/10 rounded-xl`. No heavy shadows; depth is created through blur and subtle borders.
*   **Primary Buttons:** `bg-yellow-400 text-black font-bold px-6 py-2 rounded-lg`. Hover state uses `bg-yellow-500` with explicit `transition-colors`.
*   **Information Priority:** 
    - **Tier 1:** Ticker, Current Price, AI Sentiment (High contrast, Accent colors).
    - **Tier 2:** Charts, Primary Signals (Full width/High visibility).
    - **Tier 3:** Order book data, checklists, timelines (Muted text, smaller containers).

## 5. Layout Principles & Motion
*   **Grid:** Strict 16px (gap-4) or 24px (gap-6) spacing.
*   **Performance:** ZERO use of `transition-all`. Every interactive element must specify its transition property (e.g., `transition-colors`, `transition-transform`).
*   **Motion:** Spring-based entrance animations using `framer-motion` for a responsive, tactile feel.

