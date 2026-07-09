━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROBLEM:          Existing FII/DII dashboard shows only cash segment data with no interpretation layer, no sector breakdown, no alerts, and no monthly aggregates.
CUSTOMER:         Indian retail traders and investors who track institutional flows for swing trades and portfolio positioning.
MARKET:           ~20M+ active retail demat accounts in India. FII/DII tracking tools exist but are scattered across 8+ paid/free tools
                  (Trendlyne paid, ScanX free but tables-only, Groww/5paisa basic tables, TradersCockpit registration-walled, OptionX paid).
COMPETITION:      Trendlyne (most complete, paid), ScanX (free tables, no charts), 5paisa/Groww (free basic), TradersCockpit (registration),
                  OptionX (paid, options-focused), Strike (paid, RRG/heatmaps), StockeZee (FII buying stocks screener).
TECHNOLOGY:       Python 3.12 + Streamlit + SQLite + Plotly + yfinance + nsepython. LLM for AI interpretation. Telegram cron for alerts.
BUSINESS:         Free open-source (AGPL). Paid users get AI interpretation + Telegram alerts. Free users get sector breakdown + F&O data.
MOATS:            Zero moat for standalone FII/DII. Slight moat when integrated with user's other tools (Portfolio Risk Scanner,
                  Sentiment Analyzer) to provide institutional context alongside personal portfolio risk.
RISKS:            LLM API costs for AI summary. NSE API changes breaking F&O data fetch. No retention if user doesn't check daily.
VALIDATION:       External research completed (Reddit, competitor websites, YouTube). Six features ranked by user demand vs. effort.
RECOMMENDATION:   Build — 4 features are quick wins (<50 lines each). Sector breakdown and F&O are medium effort (<200 lines).
PRIORITY:         7.5/10 — incremental value for an existing live app. No new users without these but current users benefit.
NEXT ACTIONS:     1) AI summary  2) Monthly rollup  3) Telegram alerts  4) F&O tab  5) Sector breakdown
SOURCES CITED:
  - Trendlyne FII/DII: trendlyne.com/macro-data/fii-dii/latest/
  - ScanX FII/DII: scanx.trade/insight/fii-dii-data (cash table since 2014)
  - 5paisa FII/DII: 5paisa.com/share-market-today/fii-dii-data (cash+F&O+SEBI tables)
  - TradersCockpit FII/DII: traderscockpit.com (10+ year historical, Nifty overlay)
  - OptionX FII/DII: optionx.trade/blogs/how-to-read-fii-dii-data-options-trading (AI-powered analysis)
  - Groww FII/DII: groww.in/fii-dii-data (basic educational page)
  - Strike Money: strike.money (RRG heatmaps, paid)
  - StockeZee: stockezee.com/fii-buying-stocks (FII buying stock screener)
  - Reddit: r/IndianStreetBets "FII/DII data is free and most retail traders completely ignore it"
  - Reddit: r/IndianStockMarket multiple threads — users mainly confused about interpretation, not access
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
