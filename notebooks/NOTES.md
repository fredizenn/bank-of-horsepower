# BOH-1: Data audit notes

## Scope
- Unit of analysis: one row per **team per season** (team-season).
- Tables kept: `constructor_finances` (team-seasons) and `f1_business` (one row per season).
- 17 seasons: 2010–2026.

## Q1. Grain and teams per season
- `constructor_finances`: one row per (team_name, season). Verified: 0 duplicate (team, season) pairs.
- Teams per season in the data: 9 (2010–2015), 10 (2016–2026). The change in 2016 is Haas joining, which matches reality.
- Missing values: only `cost_cap_limit_usd_m` has any (104). All are in 2010–2020 (9×6 + 10×5 = 104 rows), because the cost cap was introduced in 2021. These are structural (no cap existed), not lost data (source: https://www.formula1.com/en/latest/article/explained-what-is-the-f1-cost-cap-and-why-has-it-gone-up.2tYtDIe5SbE5utjThctBT3).

## Q2. Joins and tables used
- `f1_business` → `constructor_finances` on `season`: many-to-one (one F1-wide row per season). Verified: `season` is unique in `f1_business` (17 rows, 17 seasons, 0 duplicates).
- `race_results` joins `circuit_economics` on (season, grand_prix), and `driver_standings` on (season, driver_name).
- None of those three tables has a team column, and nothing maps drivers to teams, so there is no join path to team-seasons. Excluded.
- `driver_standings` only lists the top 6–8 drivers per season (one row per driver per season), not the full grid.
- A season-only join to race-level tables would be many-to-many (17–24 races per team-season in full seasons; 2026 has 8 so far) and inflate the row count.

## Q3. Checks against the real world
**Finding 1: survivorship bias.** The real grid had 10–12 teams per season (12 in 2010–2012, 11 in 2013–2014, 10 in 2015, 11 in 2016, 10 in 2017–2025, 11 in 2026). The dataset has 9–10. Missing: teams that went out of business (HRT, Virgin/Marussia/Manor, Lotus Racing/Caterham), plus Cadillac (2026). Low-budget teams that failed are therefore absent, so any money-versus-success relationship is measured only among survivors. Source: (https://www.nss-sports.com/en/long-form/46688/forgotten-f1-teams-formula-1-history).

**Finding 2: wrong champion labels.** 7 seasons have no champion flagged: 2010, 2011, 2012, 2013, 2022, 2023, 2026.
- 2010–2013 and 2022–2023: the actual champion was Red Bull Racing (source: TODO). That team is in the dataset, and its rows are labelled 0 ("did not win"). These are **wrong labels**, not missing values: the data teaches a model that the champion lost.
- 2026: the season is not finished (as of Oct 2026), so its label is **unknown**, not 0.
- Labels that were present (2014–2021 Mercedes, 2024–2025 McLaren) match the real record.
- Fix (next ticket): correct the six wrong seasons from a cited source, and store 2026 as missing (NaN) so it is never used as a training example. 2026 can later be a prediction target.

**Finding 3: team names are backdated to current names.**
- Aston Martin was Force India from 2008-2018, and then Racing Point in 2019-2020, before rebranding to Aston Martin in 2021 (source: https://www.espn.com/f1/story/_/id/30667786/rebranded-aston-martin-f1-team-signs-title-sponsor)
- In the dataset, every season uses "Aston Martin", including 2010–2020 when the team raced under other names. The name is consistent, but it is today's name applied backwards, not the historical one.
- The same applies to other teams: Alpine (Renault, then Lotus F1, then Renault again), RB (Toro Rosso, then AlphaTauri), and Stake (Sauber) (Alfa Romeo in 2019–2023). Source: TODO.
- "Stake (Sauber)" in 2026 is out of date: that team became Audi in 2026.

**Finding 4: `race_results` contains impossible entries.** Example: the 2010 Bahrain GP lists Lewis Hamilton as winner (it was Fernando Alonso) and Oscar Piastri on the podium (he debuted in 2023). The table is excluded, so this does not affect the analysis, but it shows the race-level data is not reliable.

## Q4. Measured vs estimated columns
Three categories: **measured** (reported by an official body), **estimated** (press or analyst figures, or modelled), and **derived** (computed from other columns or from dates). Evidence below comes from checks on the data itself.

**`constructor_finances`**
| Column | Type | Evidence |
|---|---|---|
| `season`, `team_name`, `country_iso3` | measured (identifiers) | Team names are backdated, see Finding 3. |
| `operating_budget_usd_m` | estimated | Teams do not publish budgets in a standard form, and F1 does not publish them. Values look like press estimates. |
| `sponsorship_revenue_usd_m` | estimated | Same as above. |
| `prize_money_usd_m` | estimated | F1 does not officially publish prize money per team; press figures are leaks or estimates. |
| `total_revenue_usd_m` | derived | Equals sponsorship + prize money to within 0.1 on every row. It excludes owner funding, which is why many teams' revenue is below their budget (e.g. Mercedes 2010: 198.8 revenue vs 270.0 budget). |
| `in_cost_cap_era` | derived | 1 from 2021 onwards. |
| `cost_cap_limit_usd_m` | measured (FIA regulation) | 145 (2021), 140 (2022), 135 (2023–2025) match the base cap. **2026 = 130 looks wrong**: the 2026 cap was raised to about $215m with a wider scope (verify, source: TODO). Budgets far above the cap are expected, because the cap excludes driver salaries, the top three staff and marketing. |
| `is_constructors_champion` | measured | 6 seasons wrong and 2026 unknown, see Finding 2. |
| All 2026 rows | estimated | The season was not finished when the data was built, so 2026 finances can only be projections. |

**`f1_business`**
| Column | Type | Evidence |
|---|---|---|
| `total_revenue_usd_m` | measured (2017+, Liberty Media filings) / partly estimated (before 2017, when F1 was privately held) | 2019 = 2,022 matches the reported figure. **2020 = 766 is inconsistent**: its four components sum to 1,179, close to the real 2020 revenue of about $1.15bn. 2026 is a projection. |
| `race_promotion_fees_usd_m`, `broadcast_media_usd_m`, `sponsorship_usd_m`, `other_revenue_usd_m` | estimated (modelled) | They are a fixed 36% / 34% / 16% / 14% split of the total in every season except 2020. Real shares change from year to year, so these were generated from the total, not reported. They add no information beyond `total_revenue_usd_m`. |
| `is_liberty_media_era` | derived | 1 from 2017, when Liberty completed the takeover. Correct. |
| `drive_to_survive_viewers_m_est` | estimated | Named `_est`; Netflix does not publish viewing figures. 2019 is 0 even though season 1 came out in March 2019. Pre-2019 zeros are structural (the show did not exist). |
| `us_avg_race_viewers_m` | estimated before 2021, plausibly measured from 2021 | Exactly 0.55 in 2010–2018 and 2020, which is a placeholder, not a measurement. 2021–2023 (0.95, 1.21, 1.11) look like published US TV ratings (verify, source: TODO). 2026 is a projection. |
| `global_avg_race_viewers_m` | estimated (interpolated) | Rises by exactly 1.5 every year (2010–2019 and 2022–2026). Real audience figures do not grow in a straight line. |

**Implications**
- Most numeric features are estimates, so treat small differences between teams as noise, not signal.
- Use `total_revenue_usd_m` from `f1_business`, not its four components: they carry no extra information.
- Fix or drop 2020 `total_revenue_usd_m` before use, and decide whether 2020 (COVID season) belongs in training at all.
- Do not use the viewer columns before 2021 as if they were measurements.

## Q5. Leakage
Rule: a feature leaks if its value would not be known at the moment the prediction is made.

**Target A: next-season team revenue (predict season t+1 in about March of t+1, before it starts).**
- Why March: F1's full-year total for season t (`f1_business.total_revenue_usd_m`) is only reported in February of t+1. Predicting at the end of season t would mean that figure is not yet known and would leak. Predicting after February makes it a valid feature.
- Season-t team columns (`total_revenue_usd_m`, `sponsorship_revenue_usd_m`, `prize_money_usd_m`, `operating_budget_usd_m`) are treated as known by then, so they do **not** leak. Season-t revenue is likely the strongest feature. Caveat: teams' official accounts come out later than March, so these columns stand in for the press estimates available at that time (see Q4).
- Any season-t+1 value leaks, e.g. t+1 prize money or sponsorship, which are parts of the target itself.
- Redundancy (not leakage): `sponsorship_revenue_usd_m + prize_money_usd_m = total_revenue_usd_m` (verified to within 0.1 rounding on all rows). Keep either the total or its two parts, not all three, to avoid duplicated information.

**Target B: constructors' champion in season t (predict before season t starts).**
- All season-t finance columns leak: they are reported after the season, and revenue partly reflects that season's results (prize money, performance bonuses in sponsorship). Use season t−1 values instead (lagged features).
- `is_constructors_champion` from earlier seasons is fine as a lagged feature (e.g. "won last year").
- Open question: does `prize_money_usd_m` in season t reflect the t or t−1 finishing position? (In reality F1 pays based on the previous season's finish.) The data alone does not settle it, so treat it as season-t information to be safe.

**`f1_business` timing:** `total_revenue_usd_m` is reported quarterly, and the full-season total is reported in February of the following year. This is what sets the prediction time for Target A. For Target B (predicting before season t starts), the season t−1 total is already known, so lag `f1_business` by one season.