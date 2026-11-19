# ADR-07: Next.js with a Node runtime

- **Status:** Proposed — **blocked** on cPanel Node.js support
- **Date:** 2026-11-19
- **Spec section:** 5

## Context

The storefront needs server rendering for SEO, and the App Router needs a Node runtime for SSR, metadata and rewrites. `next.config.ts` has no `output` setting today and relies on rewrites to Laravel.

## Decision

Build with `output: 'standalone'` and run it through cPanel "Setup Node.js App" if the plan supports it. If not, host the frontend on Vercel or a small VPS and keep the API on cPanel. The rewrites keep cookies same-origin either way.

## Consequences

- The owner must confirm Node.js support (audit §6 Q1).
- Moving to Vercel changes only env values and the rewrite destination.

## Alternatives rejected

- Static export (`output: 'export'`): loses SSR, rewrites and per-request metadata.
