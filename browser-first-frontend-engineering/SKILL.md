---
name: browser-first-frontend-engineering
description: "Browser-first frontend engineering skill for building, reviewing, and optimizing web applications from browser internals: rendering pipelines, JavaScript runtime behavior, networking, memory, event loops, Core Web Vitals, accessibility, and user-perceived responsiveness. Use when diagnosing or improving frontend performance, stability, observability, accessibility, UI responsiveness, or framework code that must map cleanly to browser execution."
metadata:
  short-description: Browser-first frontend engineering
---

# Browser-First Frontend Engineering Skill

## Purpose

This skill guides the agent to build, review, and optimize frontend applications by reasoning from browser internals, rendering pipelines, JavaScript runtime behavior, networking, memory, event loops, and user-perceived responsiveness, rather than only following framework conventions or language-level style rules.

The goal is to produce frontend code that is fast, stable, observable, accessible, and mechanically sympathetic to how browsers actually execute, render, schedule, and deliver user interfaces.

## Core Principle

Do not optimize for framework elegance first.

Optimize for the browser execution path:

1. URL navigation and document loading
2. DNS/TCP/TLS/HTTP negotiation
3. HTML parsing and preload scanning
4. CSSOM construction
5. JavaScript parsing, compilation, and execution
6. DOM mutation and style recalculation
7. Layout, paint, compositing, and GPU upload
8. Event loop scheduling and task queues
9. User input latency and main-thread availability
10. Memory allocation, garbage collection, and detached DOM cleanup
11. Cache behavior across browser, CDN, service worker, and application state
12. Accessibility tree generation and semantic interaction behavior

Framework best practices are secondary unless they preserve or improve the above properties.

## Mental Model

A browser is not a template renderer.

A browser is a constrained, multi-stage runtime:

```text
Network -> Parser -> DOM/CSSOM -> JS Runtime -> Style -> Layout -> Paint -> Composite -> Display
                                      ^                                  |
                                      |                                  v
                              Event Loop <- Input <- User <- Frame Budget
```

Frontend performance is primarily governed by:

- How soon useful bytes arrive
- How quickly the browser can parse and discover resources
- How little JavaScript blocks the main thread
- How predictable style and layout work are
- How little unnecessary DOM and memory churn exists
- How efficiently the page reaches first useful render
- How consistently it stays responsive after load

## When To Use This Skill

Use this skill when the task involves:

- Frontend performance optimization
- Browser rendering issues
- Slow first load or slow route transition
- High JavaScript bundle size
- Layout thrashing
- Animation jank
- Input delay
- Hydration delay
- Memory leaks
- Excessive re-rendering
- Asset loading strategy
- SPA/SSR/SSG/ISR architecture
- CDN/browser cache behavior
- Service worker behavior
- CSS architecture and rendering cost
- DOM-heavy UI
- WebSocket/SSE/streaming UI
- Mobile web performance
- Accessibility and semantic correctness
- Debugging production frontend latency
- Choosing between React, Vue, Svelte, Astro, Solid, Qwik, vanilla, Web Components, or server-first rendering

## Non-Goals

This skill does not blindly enforce:

- Framework idioms
- Code style rules
- Component purity as an absolute principle
- Single-page application architecture by default
- Client-side rendering by default
- State management libraries by default
- Animation libraries by default
- CSS-in-JS by default
- Large design-system abstraction by default

These may be valid, but only when they do not damage browser-level execution properties.

## Required Analysis Flow

When reviewing or optimizing frontend code, use this order:

1. Identify user-visible symptom
2. Map symptom to browser subsystem
3. Locate hot path or blocking path
4. Separate load-time cost from runtime cost
5. Separate CPU, network, memory, rendering, and framework costs
6. Propose concrete changes
7. Define measurement method
8. Explain tradeoffs

## Diagnosis Categories

### 1. Load Path Analysis

Inspect the initial page load path.

Ask:

- What is the first HTML response time?
- Is the page server-rendered, statically rendered, or client-rendered?
- Are critical resources discoverable early?
- Is CSS render-blocking?
- Is JavaScript blocking parsing or rendering?
- Are fonts blocking text rendering?
- Are images delaying LCP?
- Is hydration blocking interaction?
- Is there too much code before first useful render?

Prefer:

- Server-rendered or static HTML for content-first pages
- Critical CSS or minimal render-blocking CSS
- Early discovery of important resources
- `defer` or module scripts for non-critical JS
- Route-level code splitting
- Image dimension hints
- Proper `preload`, `preconnect`, and `fetchpriority` where justified
- CDN caching for immutable assets
- HTML streaming where useful

Avoid:

- Blank screen until JavaScript loads
- Large client bundle for mostly static content
- Late-discovered hero images
- Blocking third-party scripts
- Runtime configuration fetches that block render
- Waterfall chains created by JavaScript-discovered resources

### 2. Critical Rendering Path

Understand the browser's rendering sequence:

```text
HTML -> DOM
CSS -> CSSOM
DOM + CSSOM -> Render Tree
Render Tree -> Layout
Layout -> Paint
Paint -> Composite
```

Optimization targets:

- Reduce blocking CSS
- Reduce DOM size
- Reduce CSS selector complexity in large documents
- Avoid forced synchronous layout
- Avoid repeated style invalidation
- Promote only appropriate layers
- Keep animations on compositor-friendly properties

Prefer animating:

- `transform`
- `opacity`

Avoid animating hot-path layout properties:

- `width`
- `height`
- `top`
- `left`
- `margin`
- `padding`
- `border-width`
- `font-size`

These may trigger layout and paint work.

### 3. JavaScript Main Thread Analysis

The browser main thread is a scarce scheduling resource.

Inspect:

- Long tasks over 50 ms
- Large synchronous loops
- JSON parsing cost
- Hydration cost
- Framework render cost
- Event handler cost
- Third-party script cost
- Large object creation
- Repeated serialization/deserialization
- Excessive promise/microtask churn
- Blocking work inside input handlers

Prefer:

- Less JavaScript by default
- Server-side work when possible
- Lazy loading non-critical code
- Web Workers for CPU-heavy tasks
- Incremental work scheduling
- Virtualization for huge lists
- Batching state updates
- Avoiding unnecessary reactive dependencies
- Precomputed data shapes

Avoid:

- Heavy computation during initial load
- Large framework runtime for simple pages
- Re-rendering large subtrees for small state changes
- Putting everything in global reactive state
- Running analytics/experiments before critical render
- Parsing large JSON blobs on the main thread

### 4. Event Loop and Scheduling

Browser scheduling matters.

Know the basic queues:

```text
Macrotask queue: setTimeout, setInterval, events, network callbacks
Microtask queue: Promise.then, queueMicrotask, mutation observers
Animation frame: requestAnimationFrame
Idle periods: requestIdleCallback, scheduler APIs where available
```

Guidelines:

- Use `requestAnimationFrame` for visual updates
- Use debouncing/throttling for high-frequency events
- Avoid unbounded microtask chains
- Split long CPU work into chunks
- Keep input handlers short
- Defer non-critical work after first interaction readiness
- Do not block the main thread with synchronous storage or large parsing

High-frequency events requiring care:

- `scroll`
- `resize`
- `mousemove`
- `pointermove`
- `input`
- `dragover`

Prefer:

- Passive event listeners for scroll/touch where possible
- Event delegation for many similar elements
- `IntersectionObserver` instead of scroll polling
- `ResizeObserver` instead of resize polling
- CSS-based state where possible

### 5. Layout Thrashing and Forced Reflow

A forced synchronous layout happens when code writes layout-affecting styles and then immediately reads layout information.

Danger pattern:

```js
el.style.width = '200px';
const width = el.offsetWidth;
```

Layout-reading APIs include:

- `offsetWidth`, `offsetHeight`
- `clientWidth`, `clientHeight`
- `scrollWidth`, `scrollHeight`
- `getBoundingClientRect()`
- `getComputedStyle()`

Prefer:

- Batch DOM reads before writes
- Use `requestAnimationFrame` for coordinated visual writes
- Use CSS classes instead of repeated inline writes
- Avoid measuring inside loops
- Cache measurements when valid
- Use containment where appropriate

Useful CSS containment:

```css
.component {
  contain: layout paint;
}
```

Use carefully. Containment can change layout semantics.

### 6. DOM Size and Shape

The DOM is not free.

Inspect:

- Total node count
- Depth of nested elements
- Number of interactive elements
- Large tables/lists
- Hidden but mounted UI
- Offscreen panels still participating in layout
- Detached nodes retained by JavaScript references

Prefer:

- Smaller DOM
- List virtualization
- Pagination or progressive rendering
- Semantic elements instead of div soup
- Unmount hidden heavy panels
- Use CSS containment for isolated regions
- Avoid deeply nested component wrappers

Avoid:

- Rendering thousands of nodes for a visible subset
- Keeping modal trees mounted forever if heavy
- Framework wrappers that multiply DOM depth
- Recreating large DOM subtrees for minor updates

### 7. CSS Performance and Architecture

CSS can be a performance system, not just presentation.

Inspect:

- Global selector blast radius
- Expensive selectors in huge DOMs
- Frequent class toggles near document root
- CSS-in-JS runtime injection cost
- Unused CSS
- Large design-system CSS bundles
- Dynamic style recalculation

Prefer:

- Scoped styles
- Low-specificity selectors
- Class-based styling
- Static extraction where possible
- CSS variables for theming
- Avoiding runtime style generation in hot paths
- `content-visibility` for large offscreen sections where appropriate

Potentially useful:

```css
.offscreen-section {
  content-visibility: auto;
  contain-intrinsic-size: 800px;
}
```

Use when it improves rendering without harming accessibility or layout expectations.

### 8. Animation and Compositing

Smooth animation requires respecting frame budgets.

At 60 FPS, each frame has roughly 16.67 ms.
At 120 FPS, each frame has roughly 8.33 ms.

That budget includes input, JavaScript, style, layout, paint, composite, and browser overhead.

Prefer:

- CSS transitions for simple animations
- `transform` and `opacity`
- `requestAnimationFrame` for JS-driven visual updates
- Short-lived layer promotion
- Reducing paint area

Avoid:

- Animating layout properties
- Animating large blurred shadows
- Too many fixed/sticky elements
- Excessive `will-change`
- Canvas redraw of huge regions every frame unless necessary
- JS animation libraries for trivial effects

Use `will-change` only when justified:

```css
.card-entering {
  will-change: transform, opacity;
}
```

Remove or scope it after animation if possible. Too many layers increase memory and compositing cost.

### 9. Images, Fonts, and Media

Images and fonts often dominate frontend performance.

Inspect:

- LCP element type
- Image dimensions
- Image format
- Responsive image candidates
- Lazy loading strategy
- Font loading behavior
- Video autoplay or preload behavior

Prefer:

- Correct intrinsic image dimensions
- `srcset` and `sizes`
- Modern formats such as AVIF/WebP where supported by the target environment
- Lazy loading below-the-fold images
- Eager loading or high fetch priority for the LCP image when appropriate
- Font subsetting
- `font-display: swap` or an intentionally selected font strategy
- Avoiding icon font for large icon sets when SVG works better

Avoid:

- Huge original images scaled down by CSS
- Lazy loading the hero image
- Layout shift from missing image dimensions
- Blocking text rendering on slow font downloads
- Multiple font families and weights without need

Example:

```html
<img
  src="/hero-1280.webp"
  srcset="/hero-640.webp 640w, /hero-1280.webp 1280w, /hero-1920.webp 1920w"
  sizes="100vw"
  width="1280"
  height="720"
  fetchpriority="high"
  alt="..."
>
```

### 10. Network and Resource Loading

Frontend performance starts before JavaScript runs.

Inspect:

- TTFB
- Redirect chains
- DNS lookup cost
- TLS negotiation
- HTTP protocol version
- CDN cache hit ratio
- Compression
- Cache-Control headers
- Resource waterfall
- API request fan-out
- Third-party domains

Prefer:

- Fewer critical origins
- CDN edge caching
- Immutable hashed assets
- Brotli or gzip compression for text assets
- HTTP/2 or HTTP/3 where appropriate
- Server-side aggregation for chatty APIs
- Avoiding request waterfalls
- Early hints or preload only when truly useful

Cache headers for hashed assets:

```http
Cache-Control: public, max-age=31536000, immutable
```

Cache headers for HTML:

```http
Cache-Control: no-cache
```

Or use a deliberate CDN strategy such as short TTL plus stale-while-revalidate.

Avoid:

- Per-component API request waterfalls
- Client-side fetching that blocks render unnecessarily
- Multiple redirects before HTML
- Uncompressed JS/CSS/JSON
- Loading large third-party SDKs before critical render

### 11. Framework Runtime Analysis

Frameworks are scheduling and diffing systems. They are not free.

Analyze:

- Render frequency
- Render scope
- State granularity
- Component tree depth
- Hydration cost
- Client bundle size
- Runtime dependency count
- Suspense/loading boundaries
- Memoization correctness
- Signal/reactivity dependency precision

#### React

Check:

- Unnecessary parent re-renders
- Expensive context updates
- Overuse or misuse of `useEffect`
- Derived state stored unnecessarily
- Large hydration roots
- Memoization around stable props
- List keys
- Server Components suitability
- Client component boundary size

Prefer:

- Smaller client boundaries
- Server Components for non-interactive parts where available
- Local state over global state when possible
- Stable references where they prevent real re-render cost
- Route-level and component-level code splitting

Avoid:

- Putting frequently changing state in broad context
- Recomputing derived data each render without need
- Large client-only trees for static content
- Fetching the same data in many components

#### Vue

Check:

- Reactive object breadth
- Deep watchers
- Computed invalidation scope
- Large reactive arrays
- Unnecessary component updates
- Hydration cost in Nuxt apps

Prefer:

- Shallow refs for large immutable data
- Computed values for derived state
- Narrow reactive dependencies
- Async components where useful

Avoid:

- Watching huge objects deeply
- Making static config reactive
- Mutating large reactive structures frequently

#### Svelte / SvelteKit

Check:

- Compile-time output size
- Reactive statement invalidation
- Store subscription scope
- SSR vs CSR choice
- Load function waterfall
- Hydration cost

Prefer:

- Server-first data loading
- Minimal client JavaScript
- Narrow stores
- Static extraction when possible

Avoid:

- Global stores for every UI state
- Browser-only code in server paths
- Over-hydrating static sections

#### Astro

Check:

- Island hydration strategy
- Client directives
- Static vs server output
- Cross-island duplication
- Asset discovery

Prefer:

- No JS by default
- Hydrate only interactive islands
- Use `client:visible`, `client:idle`, or explicit hydration intentionally

Avoid:

- Hydrating entire pages as islands
- Multiple framework runtimes for small interactions

### 12. State Management

State management is a performance and correctness problem.

Classify state:

- Server cache state
- URL state
- Form state
- Local UI state
- Global application state
- Derived state
- Ephemeral animation state

Guidelines:

- Keep state as close as possible to where it is used
- Do not globalize local state
- Do not duplicate server cache into global stores unnecessarily
- Store canonical data, compute derived views
- Use URL state for shareable navigation state
- Avoid reactive updates that invalidate large UI regions
- Normalize large datasets when needed

Avoid:

- One global store for everything
- Storing both source data and derived data without invalidation discipline
- Deeply reactive massive objects
- Re-rendering whole pages for minor state changes

### 13. Memory and Garbage Collection

Frontend memory leaks degrade long-lived sessions.

Inspect:

- Detached DOM nodes
- Unremoved event listeners
- Timers not cleared
- Large caches without eviction
- Retained closures
- WebSocket/SSE subscriptions not closed
- Observers not disconnected
- Global arrays/maps growing forever
- Canvas/WebGL resources not released

Cleanup targets:

```js
clearInterval(timerId);
controller.abort();
observer.disconnect();
socket.close();
map.clear();
```

Prefer:

- Explicit lifecycle cleanup
- AbortController for cancelable async work
- Bounded caches
- WeakMap where appropriate
- Component unmount cleanup
- Object URL revocation

Remember:

```js
URL.revokeObjectURL(url);
```

### 14. Accessibility as Browser Semantics

Accessibility is not just compliance. It is part of browser semantics.

Inspect:

- Correct semantic elements
- Keyboard navigation
- Focus management
- Accessible names
- ARIA only when native semantics are insufficient
- Screen reader behavior
- Color contrast
- Reduced motion support
- Form labels and validation messages

Prefer:

- Native elements first
- Buttons for actions
- Links for navigation
- Real inputs for forms
- Proper headings
- Logical tab order
- `aria-live` only when justified

Avoid:

- Clickable divs
- Removing outlines without replacement
- Trapping focus accidentally
- ARIA that contradicts native semantics
- Motion that ignores `prefers-reduced-motion`

Example:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
  }
}
```

Use broad reduced-motion rules carefully in component libraries; avoid breaking essential state transitions.

### 15. Security and Browser Boundaries

Browser-first engineering includes respecting security boundaries.

Inspect:

- XSS risks
- Unsafe HTML injection
- CSP strategy
- SameSite cookies
- CORS policy
- CSRF protection
- Token storage
- iframe sandboxing
- postMessage origin validation
- Dependency supply chain

Prefer:

- HttpOnly Secure SameSite cookies for sensitive session tokens
- Strict output encoding
- Avoiding `dangerouslySetInnerHTML` unless sanitized
- CSP with nonces/hashes where practical
- Origin checks for `postMessage`
- Minimal third-party script permissions

Avoid:

- Storing long-lived sensitive tokens in localStorage
- Wildcard CORS with credentials
- Blindly trusting query strings or hash fragments
- Injecting unsanitized markdown/HTML

## Measurement Requirement

Never claim a frontend performance improvement without defining how to measure it.

Use the right tool for the layer:

### Browser DevTools

- Performance panel
- Network panel
- Coverage panel
- Memory panel
- Rendering tools
- Lighthouse
- Core Web Vitals diagnostics

### Field Metrics

- LCP: Largest Contentful Paint
- INP: Interaction to Next Paint
- CLS: Cumulative Layout Shift
- TTFB: Time to First Byte
- FCP: First Contentful Paint
- Long tasks
- JS error rate
- Hydration time
- Route transition time

### Lab and CI Tools

- WebPageTest
- Lighthouse CI
- Playwright traces
- Chrome User Experience Report when available
- Bundle analyzer
- Source map explorer
- Framework profiler
- RUM instrumentation

### Runtime Inspection

- `performance.mark()` / `performance.measure()`
- PerformanceObserver
- Long Tasks API
- Resource Timing API
- Navigation Timing API
- User Timing API

Example:

```js
performance.mark('search-start');
await runSearch();
performance.mark('search-end');
performance.measure('search', 'search-start', 'search-end');
```

## Optimization Priority Order

Use this order unless evidence suggests otherwise:

1. Remove unnecessary work
2. Reduce JavaScript shipped to the browser
3. Reduce critical request waterfalls
4. Improve server/CDN/cache behavior
5. Improve LCP resource discovery and delivery
6. Reduce hydration and main-thread blocking
7. Reduce DOM size and layout cost
8. Fix layout shifts
9. Optimize images and fonts
10. Reduce re-renders and reactive invalidation
11. Move CPU-heavy work to workers or server
12. Tune animations and compositing
13. Fix memory leaks
14. Add targeted micro-optimizations only after measurement

## Common Anti-Patterns

### Architecture Anti-Patterns

- SPA by default for content-heavy pages
- Client-side rendering for static or mostly static content
- Shipping admin-dashboard architecture to a landing page
- Global state for local UI
- Framework runtime for tiny interactions
- Multiple frontend frameworks on one page without reason
- Component abstraction that creates excessive DOM depth

### Loading Anti-Patterns

- Hero image discovered only after JavaScript runs
- Critical CSS hidden inside late-loaded JS
- Blocking analytics before first render
- Huge vendor bundle shared by every route
- No cache headers for hashed assets
- Fonts blocking text rendering
- Large JSON embedded in HTML without need

### Runtime Anti-Patterns

- Measuring and mutating layout in the same loop
- Rendering thousands of rows without virtualization
- Deep watchers on large objects
- Broad context/store updates for tiny state changes
- Input handlers doing network, parsing, and rendering synchronously
- Unbounded timers, observers, and subscriptions
- Microtask loops that starve rendering

### Rendering Anti-Patterns

- Animating width/height/top/left on many elements
- Excessive box-shadow/blur filters in scrolling areas
- Permanent `will-change` everywhere
- Large fixed backgrounds repainted during scroll
- Huge DOM kept hidden but mounted

### Security Anti-Patterns

- `innerHTML` with unsanitized content
- Long-lived tokens in localStorage
- Wildcard CORS with credentials
- Trusting postMessage without origin checks
- Third-party scripts with unlimited page access

## Output Format

When analyzing frontend code or architecture, respond using this structure:

```markdown
## Browser-Level Diagnosis

### User-Visible Symptom
...

### Likely Browser Subsystem
...

### Root Cause Hypothesis
...

### Evidence To Check
...

### Concrete Optimization Plan
1. ...
2. ...
3. ...

### Measurement Plan
- Before metric:
- After metric:
- Tool:
- Success threshold:

### Tradeoffs
...
```

## Code Review Checklist

When reviewing frontend code, check:

- Does this code run during initial load?
- Does this code run per render?
- Does this code run per input event?
- Does this code allocate frequently?
- Does this code trigger layout reads after writes?
- Does this code create network waterfalls?
- Does this code increase bundle size?
- Does this code increase hydration scope?
- Does this code retain memory after unmount?
- Does this code harm keyboard or screen reader behavior?
- Does this code depend on browser-only APIs in server paths?
- Does this code create security exposure?

## Framework Selection Heuristics

Choose frontend architecture by browser cost, not fashion.

### Prefer Static/Server-First Rendering When

- Content is public or cacheable
- SEO matters
- Interaction is limited
- First load speed is critical
- Page content can be generated ahead of time
- Most UI does not require client state

### Prefer SPA/Heavy Client Runtime When

- The app is highly interactive
- Offline-like behavior matters
- Client-side state is central
- Transitions are frequent and data reuse is high
- The app behaves more like a workstation than a document

### Prefer Islands Architecture When

- Most content is static
- Only specific regions are interactive
- You want minimal JavaScript by default
- Multiple teams own separate interactive widgets

### Prefer Web Workers When

- CPU work blocks input
- Large parsing/transforming is needed
- Search/filtering over large local datasets is needed
- Compression, diffing, or rendering preparation is expensive

### Prefer Server Aggregation When

- Client performs many dependent API calls
- Mobile latency is high
- Request fan-out creates waterfalls
- Data can be joined near the database or service layer

## Golden Rules

1. First make the browser do less work.
2. Then make unavoidable work happen earlier, later, smaller, or off the main thread.
3. Do not ship JavaScript unless the browser must execute it.
4. Do not hydrate what does not need interaction.
5. Do not measure performance only in local development.
6. Do not treat framework rules as more fundamental than rendering, scheduling, memory, and network reality.
7. Fast frontend is not just fast JavaScript. It is fast discovery, fast rendering, fast interaction, stable layout, bounded memory, and safe semantics.

## Short Operating Doctrine

A good frontend engineer does not merely write components.

A good frontend engineer shapes the browser's workload:

```text
Fewer bytes.
Earlier discovery.
Less JavaScript.
Smaller DOM.
Predictable layout.
Compositor-friendly motion.
Bounded memory.
Short input path.
Measured reality.
```

The framework is the steering wheel.
The browser is the chassis.
The network is the road.
The user feels the whole machine.
