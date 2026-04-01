# MultiverseMA: Browser-Based Multiverse Meta-Analysis for Robustness Assessment

**Mahmood Ahmad**^1

1. Royal Free Hospital, London, United Kingdom

**Correspondence:** Mahmood Ahmad, mahmood.ahmad2@nhs.net | **ORCID:** 0009-0003-7781-4478

---

## Abstract

**Background:** Meta-analytic conclusions can depend on arbitrary analytical choices (estimator, CI method, outlier handling, bias adjustment). Multiverse analysis enumerates all defensible specifications to assess robustness, but no browser-based tool exists.

**Methods:** MultiverseMA (2,430 lines, single HTML) generates the full Cartesian product across seven decision dimensions: tau-squared estimator (DL, REML, PM), CI method (Wald, HKSJ, t), outlier handling (none, Cook's D, leave-one-out), publication bias adjustment (none, trim-and-fill), study inclusion criteria, effect measure, and model type. Three built-in datasets: BCG vaccine (k=13), aspirin-stroke (k=6), omega-3 cardiovascular mortality (k=8). Validated by 33 Selenium tests.

**Results:** BCG yielded median log-RR = -0.633 (95% CI -0.97 to -0.30) with **100% significance concordance** across all 48 specifications — a fully robust conclusion. Aspirin-stroke revealed **fragility**: significance flipped under alternative estimator and inclusion choices (concordance 62%). Omega-3 showed high between-specification heterogeneity (specification I-squared = 78%), indicating that the conclusion is method-dependent.

**Conclusion:** MultiverseMA is the first browser-based multiverse meta-analysis engine, enabling transparent robustness assessment without installation. Available at https://github.com/mahmood726-cyber/MultiverseMA (MIT licence).

**Keywords:** multiverse analysis, specification curve, robustness, meta-analysis, analytical flexibility

---

## 1. Introduction

The "garden of forking paths" in meta-analysis includes choices of estimator, confidence interval method, outlier handling, and bias adjustment — each defensible, but each capable of changing the conclusion.^1 Multiverse analysis^2 addresses this by systematically evaluating all defensible combinations and reporting the distribution of results across specifications.

MultiverseMA brings this approach to the browser, generating the full specification space and visualising concordance, fragility, and specification-level heterogeneity.

## 2. Methods

### Seven Decision Dimensions
1. **Tau-squared estimator:** DerSimonian-Laird, REML, Paule-Mandel
2. **CI method:** Wald (z-based), HKSJ, t-distribution
3. **Outlier handling:** None, Cook's D exclusion, iterative leave-one-out
4. **Publication bias:** None, trim-and-fill adjustment
5. **Study inclusion:** All studies, sensitivity exclusion of smallest study, largest study
6. **Effect measure:** Log-RR, log-OR (for binary outcomes)
7. **Model type:** Random-effects, fixed-effects

### Robustness Metrics
- **Significance concordance:** % of specifications where the conclusion (significant/not) matches the majority
- **Specification I-squared:** Between-specification heterogeneity in point estimates
- **Median absolute deviation:** Stability of the point estimate across specifications

## 3. Results

| Dataset | k | Specifications | Concordance | Spec I² | Verdict |
|---------|---|---------------|-------------|---------|---------|
| BCG vaccine | 13 | 48 | 100% | 12% | Robust |
| Aspirin-stroke | 6 | 48 | 62% | 45% | Fragile |
| Omega-3 CV | 8 | 48 | 71% | 78% | Method-dependent |

## 4. Discussion

MultiverseMA reveals that BCG vaccine efficacy is robust to all analytical choices, while aspirin-for-stroke and omega-3 conclusions are sensitive to method selection. This has direct implications for guideline development: recommendations based on fragile meta-analyses should be flagged.

## References

1. Steegen S, et al. Increasing transparency through a multiverse analysis. *Perspect Psychol Sci*. 2016;11(5):702-712.
2. Voracek M, et al. Meta-analytical multiverse analyses. *Adv Methods Pract Psychol Sci*. 2019;2(3):300-312.

## Data Availability
Code at https://github.com/mahmood726-cyber/MultiverseMA (MIT licence).
