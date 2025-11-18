# fxpipeline

A modular foreign-exchange research pipeline for building, labeling, and testing machine-learning-based trading signals.

## Project Structure

fxpipeline
├── core           # Core data classes
├── ingestion      # Data loaders (yfinance, AlphaVantage, Polygon)
├── preprocessing  # Feature engineering, z-score windows, indicators
├── strategy       # Trading strategy, models (unfinished)
├── backtest       # Walk forward validation (unfinished)
└── utils          # Shared helpers
