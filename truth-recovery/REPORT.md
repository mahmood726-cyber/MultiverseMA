# Truth-recovery yardstick — MultiverseMA (spec-collapse aggregator)

**Verdict: VALIDATION of the problem + an OVER-CORRECTION bug in the fix + a proven
minimal repair. The naive pool manufactures false robustness; the shipped
"calibrated" interval over-corrects to ZERO power; a one-line change using
quantities the engine already computes fixes both.**

## Method
MultiverseMA ships `specCollapseAggregates`, which contrasts a naive
inverse-variance pool across specifications (flagged anti-conservative) with a
"weighted-likelihood" interval (offered as the calibrated alternative). The
harness injects a known truth — `m=40` specifications estimating the same effect
`mu`, with between-specification spread `tauSpec` — and measures how often each
summary declares the multiverse "robust" (aggregate 95% CI excludes 0). Under a
true null that rate should be ~0.05; under a true effect it should stay high
(power). Engine used **verbatim**. 4000 reps/cell.

## Results

### False-robustness under a true NULL (mu=0) — should be ~0.05
| tauSpec | naive IV-RE | shipped WL (mixture) | proposed mean-CI |
|--------:|------------:|---------------------:|-----------------:|
| 0.00 | 0.050 | 0.000 | 0.006 |
| 0.05 | 0.099 | 0.000 | 0.008 |
| 0.10 | 0.223 | 0.000 | 0.015 |
| 0.20 | **0.458** | 0.000 | 0.033 |

### Power under a true effect (mu=0.15) — should detect it
| tauSpec | naive IV-RE | shipped WL (mixture) | proposed mean-CI |
|--------:|------------:|---------------------:|-----------------:|
| 0.05 | 1.000 | **0.000** | 1.000 |
| 0.10 | 1.000 | **0.000** | 0.9998 |
| 0.20 | 0.998 | **0.000** | 0.962 |

## Findings (all measured)
1. **VALIDATION — naive IV-RE manufactures false robustness.** Under the null with
   real between-specification spread, inverse-variance pooling declares the
   multiverse "robust" up to 46% of the time (vs the nominal 5%). This reproduces
   the spec-collapse-atlas result (~40.8% false robustness) at the tool level.
2. **OVER-CORRECTION BUG in the shipped fix.** The weighted-likelihood interval is
   built from the **mixture *prediction* quantiles** (`invert(0.025/0.975)` of the
   1/n·ΣN(θ_i, se_i²) mixture) — a prediction interval for where a *single* new
   specification would land, not a confidence interval for the effect. It does not
   shrink with the number of specifications, so it is enormously wide and has
   **zero power**: it calls *every* multiverse "fragile," including a genuine,
   consistent real effect (mu=0.15 → robust rate 0.000). The app's "calibrated"
   verdict is therefore uninformative — it always says fragile.
3. **PROVEN minimal fix.** `specCollapseAggregates` already computes `within`,
   `between`, and `total` but never uses them for the interval. Building the CI for
   the **mean** as `mean ± z·√(total/n)` (total = within + between) controls
   false-robustness (≤ 0.033 across all spread levels under the null) **and**
   retains power (0.962–1.000 under a true effect). It is mildly conservative at
   `tauSpec=0` (0.006) — honest, and on the safe side. This is a one-line change
   reusing existing computed quantities.

## Recommendation
Replace `wl.lo/hi` (mixture-prediction quantiles) with the mean CI
`wl.theta ± 1.96·√(wl.total / n)` for the robustness *verdict*, OR clearly relabel
the current interval a **prediction interval** ("where a new specification would
land") rather than a robustness CI — otherwise the tool reports every result as
fragile and the spec-collapse banner never confirms robustness.

## What did NOT transfer
NPE/conformal machinery is estimator-of-μ specific; this is the multiverse
robustness-vs-truth diagnostic (same family as MAFI / spec-collapse-atlas), so the
known-truth false-robustness harness transferred. No runtime dependency added;
engine unchanged.

## Reproduce
```
node truth-recovery/harness.mjs --reps 4000
node --test truth-recovery/test-truth-recovery.mjs
```
