# Multiverse Meta-Analysis Engine — Implementation Plan

## Vision
The world's first browser-based Multiverse Meta-Analysis engine. Researchers define their analytic choices (which studies, which estimator, which effect measure, outlier rules, subgroup definitions) and the engine systematically runs ALL defensible combinations, producing a specification curve that reveals how robust — or fragile — the meta-analytic conclusion truly is.

**No browser tool exists.** The only related tools are `specr` (R, single-dataset) and SMART (registration-only, no execution). This fills a massive gap.

## Why Build First
- Leverages ALL existing statistical engines (DL, REML, PM, ML, PL, HKSJ, etc.)
- Clearest architecture (define → enumerate → run → visualize)
- Fastest path to working MVP
- Broadest audience (every meta-analyst faces the "garden of forking paths")
- Naturally integrates with TruthCert (proof that ALL specifications were explored)

## Architecture

### Single-file HTML app (`multiverse-ma.html`)
- Target: ~15K-25K lines (mature)
- Seeded PRNG (xoshiro128**) for reproducibility
- WebR validation tier (optional)
- Dark/light theme, WCAG AA accessible

### Core Modules

#### 1. Data Input Module
- CSV/JSON import (drag-and-drop, fuzzy header matching)
- Manual entry table
- Fields: study, yi (effect), vi (variance), sei (SE), ni (sample size), moderators
- RIS/BibTeX metadata import for study labels
- Example datasets (built-in: BCG vaccine, Cochrane exemplars)

#### 2. Decision Space Definition Module
**The heart of the tool.** Users define "forking paths" — each a dimension of the multiverse:

| Decision Dimension | Example Choices |
|---|---|
| **Study inclusion** | All studies, exclude high-RoB, exclude outliers (±2SD, ±3SD, GOSH), exclude small (n<50) |
| **Effect measure** | OR, RR, HR, MD, SMD (Hedges' g, Cohen's d) |
| **Heterogeneity estimator** | DL, REML, ML, PM, HS, HO, SJ, EB, PL |
| **CI method** | Wald, HKSJ, t-distribution, Profile Likelihood |
| **Outlier handling** | None, studentized residuals >2, Cook's D, leave-one-out influence |
| **Publication bias adjustment** | None, trim-and-fill, PET-PEESE, Copas selection |
| **Subgroup scope** | All, by risk of bias, by region, by dose, by follow-up duration |
| **Correlation structure** | Independent, correlated (rho=0.5, 0.7, 0.9) for multi-outcome |
| **Knob: one-study-removed** | Include full set vs each leave-one-out variant |
| **Custom** | User-defined binary/categorical choices |

- Each dimension: checkbox list of options to include in the multiverse
- Combinatorial count displayed live: "This multiverse has 2,304 specifications"
- Warning thresholds: >10,000 specs → suggest pruning; >50,000 → require confirmation

#### 3. Multiverse Execution Engine
- Enumerate all combinations (Cartesian product of checked options)
- For each specification:
  - Filter studies per inclusion rule
  - Compute effect size (convert if needed)
  - Estimate tau² with chosen estimator
  - Compute pooled effect + CI + PI
  - Record: specification ID, pooled effect, CI, p-value, tau², I², k (studies), estimator, decisions
- **Performance**: Web Worker for parallel execution
  - Target: 1,000 specs in <5 seconds
  - Progress bar with cancellation
- **Deterministic**: seeded PRNG, sorted specification order

#### 4. Specification Curve Visualization (Primary Output)
**Top panel**: Sorted point estimates with CIs
- X-axis: specification rank (sorted by effect size)
- Y-axis: pooled effect (log-scale for ratios)
- Color: significance (p < 0.05 green, p ≥ 0.05 red)
- Horizontal reference line at null (0 or 1)
- Median effect line + IQR band

**Bottom panel**: Decision matrix (dot plot)
- Each row = one decision dimension
- Each column = one specification (aligned with top panel)
- Filled dot = that option was active for this specification
- Reveals which decisions drive variation

**Interactive**: Click any specification to see full details (forest plot, funnel, etc.)

#### 5. Robustness Metrics Dashboard
- **Specification count**: total, significant (p<0.05), non-significant
- **Median effect [IQR]**: across all specifications
- **Concordance rate**: % of specs agreeing on direction
- **Fragility spectrum**: which decisions cause the most variation (ANOVA decomposition)
- **Vibration of Effects (VoE)** ratio: max/min absolute effect
- **Specification p-curve**: distribution of p-values across multiverse
- **Inferential agreement**: % significant at α=0.05, 0.01, 0.001

#### 6. Influence Decomposition
- For each decision dimension: how much variance in pooled effect does it explain?
- Partial eta² or similar decomposition
- Tornado/waterfall chart: most influential decisions ranked
- Interaction detection: do two decisions together shift conclusions more than either alone?

#### 7. Reporting & Export
- **Specification curve plot** (SVG, PNG, PDF)
- **Results table** (CSV: all specifications with full parameter details)
- **Summary report** (auto-generated Methods & Results text)
- **R code export** (`specr` equivalent script)
- **TruthCert bundle**: SHA-256 hash of data + all specifications + results

#### 8. Built-in Datasets & Tutorial
- 3-5 classic datasets with known multiverse sensitivity
- Guided walkthrough: "Your First Multiverse Analysis"
- Tooltips explaining each decision dimension

## Key Algorithms

### Specification Enumeration
```
decisions = [
  { name: "inclusion", options: ["all", "no_high_rob", "no_outliers"] },
  { name: "estimator", options: ["DL", "REML", "PM"] },
  { name: "ci_method", options: ["Wald", "HKSJ"] },
  ...
]
specs = cartesianProduct(decisions.map(d => d.options))
// Each spec is a unique combination of one option per dimension
```

### Fragility Decomposition (ANOVA-style)
- Run one-way ANOVA of pooled effects by each decision dimension
- Partial eta² = SS_dimension / SS_total
- Rank dimensions by influence
- Two-way interactions for top-3 influential dimensions

### Vibration of Effects
- VoE ratio = |max(effect)| / |min(effect)| (on natural scale)
- VoE Janus plot: effect size vs -log10(p) for all specifications

## Implementation Phases

### Phase 1: Core Engine (MVP)
- Data input (CSV + manual)
- 4 decision dimensions (inclusion, estimator, CI method, outlier)
- Specification curve plot (static SVG)
- Basic metrics (median, concordance, count)
- 1 built-in dataset
- **Target: ~5K lines**

### Phase 2: Full Multiverse
- All 10 decision dimensions
- Web Worker parallelism
- Interactive specification curve (click-to-inspect)
- Decision matrix dot plot
- Influence decomposition (tornado chart)
- VoE Janus plot
- **Target: ~12K lines**

### Phase 3: Publication-Ready
- Auto-generated methods/results text
- R code export
- TruthCert bundle
- 3+ built-in datasets + tutorial
- WebR validation tier
- Dark mode, accessibility, PDF export
- **Target: ~18K-22K lines**

### Phase 4: Review & Paper
- Multi-persona review (3+ rounds)
- PLOS ONE / Research Synthesis Methods manuscript
- Selenium test suite (200+ tests)

## Testing Strategy
- Unit: each estimator produces correct results (cross-validated vs metafor)
- Integration: specification enumeration × execution pipeline
- Property: more restrictive inclusion → fewer studies in each spec
- Regression: built-in datasets produce known specification curves
- Performance: 1,000 specs completes in <10 seconds
- Edge cases: k=1 study specs, all-excluded specs, zero-heterogeneity

## Key References
- Voracek et al. (2019) Specification-curve meta-analysis. Zeitschrift fur Psychologie.
- Del Giudice & Gangestad (2021) Multiverse meta-analysis.
- Simonsohn et al. (2020) Specification curve analysis.
- SMART tool (2025) Royal Society Open Science.
- Steegen et al. (2016) Multiverse analysis. Perspectives on Psych Science.

## Success Criteria
- [ ] 1,000+ specifications execute in <10 seconds
- [ ] Specification curve + decision matrix render correctly
- [ ] Influence decomposition identifies the most variable decision
- [ ] 200+ Selenium tests pass
- [ ] R parity for individual specification results
- [ ] TruthCert bundle validates
- [ ] Publishable paper with real-world example demonstrating fragility detection
