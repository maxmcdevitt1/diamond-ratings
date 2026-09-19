<div align="center">

<img src="banner.svg">

[![Status](https://img.shields.io/badge/status-in%20development-6E7681?style=for-the-badge&labelColor=24292F)](#project-status)
[![Python](https://img.shields.io/badge/python-6E7681?style=for-the-badge&logo=python&logoColor=white)](#install)
[![GitHub](https://img.shields.io/badge/maxmcdevitt1%2Fdiamond--ratings-00852E?style=for-the-badge&labelColor=24292F)](https://github.com/maxmcdevitt1/diamond-ratings)

[How it Works](#how-it-works) · [Data](#data)· [Credits](#credits)

</div>

# Let's Rate the Diamond

**Diamond Ratings** is a Python project for turning baseball performance into **player ratings**.

The current focus is pitching: fastball velocity, pitch movement, whiff rate, and wOBA allowed, with OpenCommand and FanGraphs data available for the next stages. The long-term goal is to combine player ratings into **team ratings**, then use them to predict games and seasons.

## Project status

> [!NOTE]
> This project is in development. Individual pitcher metrics are implemented; a complete player rating, hitter ratings, and team predictions are still being built.

| Area | Current state |
|---|---|
| Data loading | Statcast downloads and local Parquet/CSV readers |
| Pitcher attributes | Velocity, movement, whiff rate, and wOBA calculations |
| Command & WAR | Source data and initial functions; integration is unfinished |
| Hitter ratings | Starter modules and batting datasets |
| Team ratings & predictions | Planned |

## How it Works

### Summary

- Load pitch-level Statcast data and season-level supporting datasets.
- Measure pitcher attributes against the season's comparison group.
- Convert selected attributes into percentile scores.
- Develop a combined rating that weights recent performance more heavily.
- Extend the model to hitters, rosters, and team predictions.

The last two stages are the project direction, described in [objective.txt](objective.txt).

### Install

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/maxmcdevitt1/diamond-ratings.git
cd diamond-ratings
python -m venv .venv
source .venv/bin/activate
python -m pip install pandas numpy pybaseball pyarrow
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

### Load pitching data

Run this from the repository root:

```bash
python -c "from src import data_loader; data_loader.get_all_pitchers()"
```

The loader requests **2021–2026** Statcast data, using March 27 through October 1 for each year. It saves one Parquet file per year in `data/pitching_data/` and skips files already present.

> The first run downloads multiple seasons and can take a while. The fixed date windows may omit games outside those dates, and an existing file is not automatically refreshed as a season progresses.

### Explore a pitcher

After generating the season files, run this in a Python session or notebook from the repository root:

```python
from src import data_loader, pitcher_attributes, pitcher_rating

season = data_loader.get_season_pitching(2025)

# Percentile score for the current whiff-rate implementation.
print(pitcher_rating.whiff(season, "Chris", "Sale"))

# Season-weighted wOBA allowed and its percentile score.
woba = pitcher_attributes.calculate_woba(2025, season)
print(woba.loc[
    woba["player_name"].eq("Sale, Chris"),
    ["player_name", "wOBA", "wOBA_score"],
])
```

`main.py` currently downloads missing season files and initializes Chris Sale's `Player` objects for 2024–2026. It does not yet print or export a finished rating.

### Pipeline

```text
Statcast                     OpenCommand           FanGraphs
   │                              │                    │
   ▼                              ▼                    ▼
Season Parquet files         Command CSVs          Pitching CSVs
   │                              │                    │
   ▼                              └─────────┬──────────┘
Velocity · Movement · Whiff · wOBA          │
   │                                      │
   ▼                                      ▼
Attribute percentiles          Command / WAR integration
   │                                  (in progress)
   └──────────────────┬───────────────────┘
                      ▼
            Combined player ratings
                    (planned)
                      │
                      ▼
       Team ratings → Game / season predictions
                    (planned)
```

| File | Role |
|---|---|
| [src/data_loader.py](src/data_loader.py) | Download Statcast data, look up player IDs, and read local datasets |
| [src/pitcher_attributes.py](src/pitcher_attributes.py) | Calculate pitcher attributes and supporting metrics |
| [src/pitcher_rating.py](src/pitcher_rating.py) | Player wrapper, percentile scores, and rating experiments |
| [src/woba_weights.py](src/woba_weights.py) | Season-specific wOBA weights |
| [src/batter_attributes.py](src/batter_attributes.py) / [src/batter_rating.py](src/batter_rating.py) | Hitter rating scaffolding |
| [lab.ipynb](lab.ipynb) | Exploratory notebook |

## Data

### Layout

The repository includes command, FanGraphs pitching, and batting CSVs. Statcast Parquet files are generated locally.

| Path | Seasons | Contents |
|---|---|---|
| `data/pitching_data/<year>.parquet` | 2021–2026 requested by the loader | Downloaded pitch-level Statcast records |
| `data/pitching_data/<year>command.csv` | 2024–2026 included | OpenCommand command scores |
| `data/fangraphs/fg_pitching_<year>.csv` | 2020–2026 included | FanGraphs pitching statistics |
| `data/batting_data/<year>_batting.csv` | 2021–2026 included | Batting datasets |

**Player matching:** Statcast calculations commonly group by `player_name` in `Last, First` format. Player lookup returns an MLBAM ID; the FanGraphs lookup uses `xMLBAMID`. Command integration uses its own `pitcher` field.

The hitting loader currently points to `data/pitching_data/stats.csv`, which is not included. Connecting it to the batting datasets is part of the unfinished hitter workflow.

## Topics

### What goes into a pitcher rating?

| Attribute | Current calculation |
|---|---|
| **Velocity** | Median fastball velocity across four-seamers (`FF`), sinkers (`SI`), and cutters (`FC`), compared with the season's pooled fastball median |
| **Movement** | Induced movement magnitude from `pfx_x` and `pfx_z`, converted to inches and compared within pitch categories |
| **Whiff** | Misses divided by swings using the event groups defined in `get_whif()`, then ranked by percentile |
| **wOBA allowed** | Weighted plate-appearance outcomes using that season's weights; lower wOBA earns a higher percentile |
| **Command** | Initial use of OpenCommand's `inferred_in` for `ALL` pitches with at least 200 observations; integration is in progress |
| **WAR** | Initial FanGraphs lookup; scoring is in progress |

The movement score weights category percentiles **50% breaking**, **30% offspeed**, and **20% fastball**. Its current implementation expects the pitcher to have all three categories.

### How should I read the scores?

Percentiles describe a player's position within the data being ranked. They are relative to that comparison group and are not a validated forecast of future performance.

The scoring system is still being standardized. Some rating experiments remap a percentile to a **50–100** scale with `50 + percentile / 2`, while other functions return a **0–100** percentile. There is no final combined score yet.


See [objective.txt](objective.txt) for the original goals and [todo](todo) for current development notes.

## Credits

- [pybaseball](https://github.com/jldbc/pybaseball) — Statcast access and player ID lookup.
- [FanGraphs](https://www.fangraphs.com/) — supporting pitching statistics.
- [OpenCommand](https://github.com/tomdoyo/open-command) by [tomdoyo](https://github.com/tomdoyo) — command data and inspiration for this README's layout.

OpenCommand's upstream code and data are released under [CC BY-NC-SA 4.0](https://github.com/tomdoyo/open-command/blob/main/LICENSE).
