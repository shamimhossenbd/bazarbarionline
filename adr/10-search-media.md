# ADR-10: MySQL FULLTEXT and WebP media

- **Status:** Proposed — not started
- **Date:** 2026-11-19
- **Spec section:** 5

## Context

Shared hosting has no search service. Phase 0 found images stored on the `public` disk without conversion and no search index.

## Decision

MVP search uses a MySQL FULLTEXT index on product name and tags, plus category and brand filters. Uploaded product images are converted to WebP in three sizes (thumbnail, card, full) on the public disk; private vendor documents use a private disk served through signed URLs. Revisit Meilisearch or a CDN when the catalogue or traffic outgrows this.

## Consequences

- Bangla search quality depends on MySQL's tokenizer; test with real Bangla product names (consider `ngram` parser).
- Image conversion needs GD or Imagick on the host (verify in cPanel).

## Alternatives rejected

- An external search service at launch: cost and hosting complexity.
