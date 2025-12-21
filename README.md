# fxpipeline

A modular foreign-exchange research pipeline for building, labeling, and testing machine-learning-based trading signals.

## Project Structure

```bash
fxpipeline
├── core           # Core data classes
├── ingestion      # Data loaders (yfinance, AlphaVantage, Polygon)
├── preprocessing  # Feature engineering, z-score windows, indicators
├── backtest       # Validation
└── utils          # Shared helpers
```
