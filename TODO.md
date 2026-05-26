# Fix Horizontal Scroll Issue - Plan & Tracking

## Problem
The UI has unwanted horizontal scrolling. Content exceeds viewport width, causing horizontal scrollbars to appear.

## Root Cause
Multiple CSS files (`nav.css`, `dashboard.css`, `login.css`, `pg-specification.css`, `pgs.css`, `terms&conditions.css`) do not restrict horizontal overflow on `html`/`body` elements.

## Progress

### Step 1: Add `overflow-x: hidden` to prevent horizontal scroll
Edit the following CSS files to add `overflow-x: hidden` on `html` and/or `body`:

1. [x] **PgFinder/static/css/nav.css** — Added to `html` and `body` rules
2. [x] **PgFinder/static/css/dashboard.css** — Added `html, body { overflow-x: hidden; }`
3. [x] **PgFinder/static/css/login.css** — Added to existing `body, html` rule
4. [x] **PgFinder/static/css/pg-specification.css** — Added to `body` and `html`
5. [x] **PgFinder/static/css/pgs.css** — Added `html, body { overflow-x: hidden; }`
6. [x] **PgFinder/static/css/terms&conditions.css** — Added to `body`

### Step 2: Mirror edits to static/css/ directory
Repeat same edits for:
- `static/css/nav.css`
- `static/css/dashboard.css`
