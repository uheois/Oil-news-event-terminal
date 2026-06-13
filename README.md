# Oil Event Intelligence Terminal

A personal event-driven intelligence system for oil, energy, geopolitics, and macroeconomic news.(draft)

The system continuously collects headlines, clusters similar stories into events, and tracks market reactions in:

- WTI Crude Oil
- Brent Crude Oil
- USD/KRW

## Features

- Automated news collection via GitHub Actions
- Event clustering from multiple sources
- Candidate / Confirmed / Strong event detection
- Event strength scoring
- Historical event database
- Price reaction tracking

## News Sources

- Reuters Energy
- Reuters World
- Reuters Markets
- Yahoo Finance
- Investing.com
- EIA
- IEA
- OPEC

## Event Levels

- Candidate
- Confirmed
- Strong
- Research Candidate

## Market Reaction Windows

- T-30m
- T-10m
- T-1m
- T0
- T+1m
- T+10m
- T+30m
- T+1h
- T+2h
- T+3h
- T+6h
- T+12h

## Database

- news_headlines
- events
- price_reactions

## Automation

GitHub Actions runs every 5 minutes and updates the event database automatically.

## Status

Work in progress.

Current focus:

- Event detection quality
- High-impact news recognition
- Price reaction analytics
- Dashboard visualization
