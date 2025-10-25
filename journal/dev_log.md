# Development Log


## 📅 2025-10-20 — Polygon Forex Data Sketch

### ✅ What I did
- Created `ForexPriceRequest` and `ForexPrice` dataclasses.
- Wrote `get_polygon_forex_price()` to fetch & clean daily candles.
- Implemented save/load functions to `.polygon_cache`.

### 💡 What I learned
- Polygon’s free tier allows only past 2 years — enforced `datetime.now() - 730 days`.
- API returns clean data but needs minor cleanup (`timestamp`, `transactions`, etc.)
- Using `dataclass` for request/response helps modularity.

### 🧠 Ideas / Next
- Wrap this into a `PolygonExtractor` class (interface-aligned with `ForexExtractor`).
- Add `is_stale()` logic based on file date or request range.
- Could integrate with `load_data(req, source, cache)` pattern from previous chat.
- Maybe test multiple tickers in batch.

### 💭 Side notes
- One Pomodoro >> 3 months of wandering.
- This is the start of the "Stable Data Feeder" arc.


## 2025-10-25 - Light Review

### What I reviewed
- Pandas Data Reader is not the best choice, I should probably write my own MacroDataLoader
- Should nuke the old v3 folder


---

## Ideas

- Kalman filiter as MA, its Std. as Band
- Maybe make Indicator class
