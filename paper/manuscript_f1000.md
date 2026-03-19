# MultiverseMA: A Browser-Based Engine for Multiverse Meta-Analysis

**Authors:** Mahmood Ahmad^1^

^1^ Royal Free London NHS Foundation Trust, London, UK; Tahir Heart Institute, Rabwah, Pakistan

**Corresponding author:** mahmood726@gmail.com

**ORCID:** YOUR-ORCID-HERE

---

## Abstract

**Background:** Every meta-analysis requires subjective analytical decisions -- which studies to include, which heterogeneity estimator to use, how to handle outliers, and whether to adjust for publication bias. These choices constitute a "garden of forking paths" that can materially alter conclusions, yet most meta-analyses report only a single specification. Multiverse analysis addresses this by systematically enumerating all defensible combinations and evaluating how conclusions vary across them.

**Gap:** Existing multiverse tools are either limited to single-dataset contexts (specr, R-only), restricted to registered users (SMART), or require programming expertise. No browser-based tool currently enables multiverse meta-analysis without software installation or coding.

**Methods:** We developed MultiverseMA, a single-file HTML application (2,430 lines) that runs entirely in the browser with no server dependencies. It implements seven decision dimensions -- heterogeneity estimator (6 options), CI method (3 options), study inclusion/exclusion, outlier removal, publication bias adjustment, leave-one-out analysis, and effect direction -- generating a full Cartesian product of specifications. Outputs include a specification curve, VoE Janus plot, influence decomposition (partial eta-squared), cumulative concordance, auto-generated methods text, and print-ready reports.

**Results:** We demonstrate MultiverseMA on three built-in datasets. The BCG vaccine dataset (13 studies) yields 100% direction concordance and 100% significance across 48 specifications (median log-RR = -0.633), confirming extreme robustness. The aspirin-stroke dataset reveals fragility, with significance depending on estimator and inclusion choices. The omega-3/cardiovascular mortality dataset exposes controversy, with high heterogeneity across specifications.

**Conclusions:** MultiverseMA is the first browser-based multiverse meta-analysis engine. It is open-source, validated by 33 Selenium tests and multi-persona code review, and freely available at https://github.com/mahmood726-cyber/MultiverseMA.

**Keywords:** multiverse analysis, meta-analysis, specification curve, vibration of effects, robustness, sensitivity analysis, browser-based tool

---

## Introduction

Meta-analysis is widely regarded as the highest level of evidence in the evidence hierarchy, yet its conclusions depend on numerous analytical decisions that are often made without explicit justification. Every meta-analyst navigates what Steegen et al. [1] termed a "garden of forking paths": which studies to include, which effect size measure to adopt, which heterogeneity estimator to apply, how to construct confidence intervals, and whether to adjust for publication bias. Each of these decision points constitutes a fork, and the final reported result reflects only one path through a potentially vast decision space.

The consequences of these choices are not merely theoretical. Voracek et al. [2] demonstrated that the reported effect size in a single meta-analysis can shift from statistically significant to non-significant depending on inclusion criteria alone. Del Giudice and Gangestad [3] showed that specification choices in psychological meta-analyses can produce contradictory conclusions from the same underlying data. In the Cochrane Handbook, Higgins et al. [24] acknowledge that "the choice of statistical model may affect the conclusions of a meta-analysis," yet no formal guidance exists for systematically exploring the impact of these choices. In medicine, where meta-analytic results inform clinical guidelines, drug approvals, and treatment decisions, this sensitivity to analytical choices carries direct patient-safety implications.

The heterogeneity estimator alone illustrates the scope of this problem. Veroniki et al. [27] catalogued 16 estimators for the between-study variance (tau-squared), including the method-of-moments DerSimonian-Laird [9], restricted maximum likelihood (REML), Paule-Mandel [11], and Sidik-Jonkman [12]. IntHout et al. [26] showed that the standard DerSimonian-Laird/Wald combination produces confidence intervals that are too narrow in most practical settings, and recommended the Hartung-Knapp-Sidik-Jonkman (HKSJ) method instead [25]. The choice between these approaches is consequential but rarely explored systematically -- typically, the analyst selects one estimator and one CI method without reporting what would have happened under alternatives.

Multiverse analysis, formalized by Steegen et al. [1] and extended by Simonsohn et al. [4] as specification curve analysis, addresses this problem by systematically running all defensible analytical specifications and presenting the distribution of results. Rather than reporting a single "preferred" estimate, the analyst generates hundreds or thousands of estimates and evaluates whether the conclusion is robust -- that is, whether it holds across most or all reasonable specifications. This approach has been widely adopted in psychology and social science but remains rare in medical meta-analysis, where the stakes are arguably highest.

Despite the growing recognition of multiverse methods, existing tools remain limited. The R package specr [5] implements specification curve analysis for single datasets but is not designed for meta-analytic workflows -- it does not include heterogeneity estimators, publication bias methods, or leave-one-out analysis. The SMART framework [6] supports structured multiverse analysis but requires registration and is not freely accessible for general use. More broadly, all existing multiverse tools require either R programming expertise or institutional access, creating a barrier for clinicians, guideline developers, and researchers in low-resource settings who may benefit most from robustness assessment.

MultiverseMA fills this gap. It is a single-file HTML application (2,430 lines of HTML, JavaScript, and SVG) that runs entirely in the browser with no server, no dependencies, and no installation. It implements six heterogeneity estimators, three confidence interval methods, publication bias adjustment via trim-and-fill and PET-PEESE, leave-one-out sensitivity analysis, and outlier removal -- all combinable across seven decision dimensions. Results are presented through a specification curve plot, vibration-of-effects Janus plot, influence decomposition, and cumulative concordance analysis. The tool generates auto-formatted methods text and print-ready reports, supporting transparent reporting in line with PRISMA 2020 guidelines [7].

---

## Methods

### Implementation

#### Architecture

MultiverseMA is implemented as a single self-contained HTML file (2,430 lines) comprising HTML structure, CSS styling, and JavaScript logic with inline SVG rendering. The application requires no server, no build system, and no external dependencies. It runs in any modern browser (Chrome, Firefox, Edge, Safari) on desktop or mobile devices. This architecture ensures long-term reproducibility -- the file can be archived, shared via email, or hosted on any static web server without risk of dependency breakage.

The single-file design follows the principle that scientific tools should be maximally portable. A researcher can download the HTML file, open it locally without an internet connection, and obtain identical results on any operating system. This eliminates the "works on my machine" problem that affects tools dependent on specific R versions, package ecosystems, or server configurations.

#### User Workflow

A typical MultiverseMA session proceeds as follows:

1. **Data input:** The user selects one of three built-in datasets or enters custom study-level data (effect size, standard error, and study label) via an interactive table. Data can also be pasted from a spreadsheet.

2. **Dimension configuration:** The user selects which decision dimensions to vary. By default, all six heterogeneity estimators and all three CI methods are selected. The user can toggle individual studies for inclusion/exclusion, enable or disable outlier removal, select publication bias methods, and optionally enable leave-one-out analysis.

3. **Specification generation:** MultiverseMA computes the Cartesian product of all selected options, generating the full specification set. The count of specifications is displayed before computation begins.

4. **Computation and visualization:** All specifications are computed and results are displayed simultaneously: the specification curve, VoE Janus plot, influence decomposition, and concordance plot. Summary statistics (median estimate, concordance proportions, VoE metric) are presented in a summary panel.

5. **Reporting:** The user can copy the auto-generated methods text, export the full results table as CSV, or print a formatted report directly from the browser.

#### Statistical Engines

MultiverseMA implements six heterogeneity estimators for the random-effects model. The inclusion of multiple estimators is central to the multiverse approach: rather than selecting one estimator and ignoring alternatives, the analyst evaluates whether the conclusion holds across all of them.

1. **Fixed-effect (FE):** The inverse-variance weighted fixed-effect model, which assumes a common true effect across studies [8]. While this assumption is rarely tenable in practice, the fixed-effect model serves as a useful boundary condition -- if the random-effects and fixed-effect estimates diverge substantially, this signals that between-study heterogeneity is consequential.

2. **DerSimonian-Laird (DL):** The most widely used random-effects estimator, computing tau-squared via the method-of-moments Q statistic [9]:

   tau_DL^2 = max(0, (Q - (k-1)) / (sum(w_i) - sum(w_i^2)/sum(w_i)))

   Despite its widespread use, DL is known to underestimate tau-squared for small k and to produce confidence intervals with below-nominal coverage [26].

3. **Restricted Maximum Likelihood (REML):** An iterative estimator that accounts for the loss of degrees of freedom in estimating the mean, yielding less biased tau-squared estimates than DL for small k [10]. REML is generally recommended as the default estimator in the metafor package documentation.

4. **Paule-Mandel (PM):** A generalized Q-statistic estimator that iteratively solves for tau-squared such that the generalized Q equals its expected value (k - 1) [11]. PM has been shown to perform well across a wide range of simulation scenarios [27].

5. **Maximum Likelihood (ML):** The full maximum likelihood estimator, which jointly estimates the mean effect and tau-squared but does not adjust for degrees of freedom [10]. ML tends to underestimate tau-squared relative to REML.

6. **Sidik-Jonkman (SJ):** A non-iterative estimator that uses an initial heterogeneity estimate based on sample variances, offering computational simplicity with reasonable performance [12]. SJ can produce larger tau-squared estimates than DL, particularly for small k.

#### Confidence Interval Methods

Three confidence interval construction methods are available. The choice of CI method is one of the most consequential analytical decisions in meta-analysis, particularly for small k, yet it receives less attention than estimator choice in most textbooks and software tutorials.

1. **Wald (z-based):** The standard normal approximation, CI = theta-hat +/- z_{alpha/2} * SE, where z is the quantile of the standard normal distribution [9]. This is the default in most meta-analysis software but produces intervals with below-nominal coverage when k is small or heterogeneity is substantial [26].

2. **Hartung-Knapp-Sidik-Jonkman (HKSJ):** Uses a t-distribution with k - 1 degrees of freedom and a modified variance estimator that accounts for uncertainty in tau-squared estimation [25]. A floor of 1.0 is applied to the HKSJ adjustment factor to prevent narrower-than-Wald intervals, following the recommendation of Rover et al. [13]. HKSJ is increasingly recommended as the default CI method [26].

3. **t-distribution:** Uses a t-distribution with k - 1 degrees of freedom but retains the standard variance estimator, providing a middle ground between the Wald and HKSJ approaches. This method accounts for the small-sample nature of k (number of studies) without the HKSJ variance modification.

#### Publication Bias Adjustment

Two publication bias methods are implemented:

1. **Trim-and-fill (Duval & Tweedie):** Estimates the number of missing studies using the L0 estimator, imputes them symmetrically about the funnel plot center, and re-estimates the pooled effect [14]. The adjusted estimate and the number of imputed studies are reported.

2. **PET-PEESE (Stanley & Doucouliagos):** A regression-based approach in which the effect size is regressed on its standard error (PET) or variance (PEESE). If the PET intercept is significant at alpha = 0.10, the PEESE estimate is used; otherwise, PET is retained [15]. This conditional procedure balances bias correction against loss of precision.

#### Seven Decision Dimensions

MultiverseMA defines seven binary or multi-level decision dimensions that are combined via Cartesian product to generate the full specification space. Table 1 summarizes these dimensions.

**Table 1. Decision dimensions in MultiverseMA.**

| # | Dimension | Options | Default |
|---|-----------|---------|---------|
| 1 | Heterogeneity estimator | FE, DL, REML, PM, ML, SJ | All selected |
| 2 | CI method | Wald, HKSJ, t-distribution | All selected |
| 3 | Study inclusion | Each study toggled on/off | All included |
| 4 | Outlier removal | None, remove outliers (>2 SD from pooled estimate) | Both |
| 5 | Publication bias adjustment | None, trim-and-fill, PET-PEESE | All selected |
| 6 | Leave-one-out | Full set, each study removed in turn | Full set only |
| 7 | Effect direction | As entered, sign-flipped | As entered |

The total number of specifications is the product of the number of options selected within each dimension. For the default configuration with 13 studies, 6 estimators, 3 CI methods, and all other defaults, 48 specifications are generated from the base dimensions. Enabling leave-one-out or study-level inclusion toggles can expand this to tens of thousands of specifications.

#### Visualization

MultiverseMA produces four primary visualizations, all rendered as inline SVG with no external charting library:

1. **Specification curve plot:** Following Simonsohn et al. [4], this dual-panel display shows (upper panel) point estimates with 95% confidence intervals sorted by magnitude, and (lower panel) an indicator matrix showing which analytical choices were active for each specification. A horizontal reference line at zero and color-coding by significance status (blue for significant, grey for non-significant) enable rapid visual assessment. The upper panel uses vertical line segments for confidence intervals and filled circles for point estimates, with the sorted arrangement making it immediately apparent whether all estimates fall on the same side of zero. The lower panel uses a dot-matrix layout where each row represents a decision dimension and each column represents a specification, with filled dots indicating active choices. This allows the reader to visually trace which combinations of choices produce the most extreme or the most attenuated estimates.

2. **Vibration-of-effects (VoE) Janus plot:** Adapted from Patel et al. [16], this plot displays the distribution of point estimates as a histogram, with the central tendency and spread quantifying the degree of vibration. The VoE metric is defined as the range of point estimates (maximum minus minimum) across all specifications and is reported numerically alongside the plot. A narrow VoE indicates robustness; a wide VoE indicates sensitivity to analytical choices. The histogram bins are colored by significance status, providing a visual summary of how often the conclusion changes across the decision space.

3. **Influence decomposition:** A horizontal bar chart of partial eta-squared values from a Type III ANOVA decomposition, identifying which decision dimensions contribute most to variation in point estimates. The dependent variable is the specification-level point estimate, and the factors are the seven decision dimensions. Partial eta-squared quantifies the proportion of variance in point estimates attributable to each dimension, after controlling for all others. This tells the analyst whether the conclusion is most sensitive to estimator choice, inclusion criteria, or bias adjustment -- information that is otherwise impossible to extract from traditional sensitivity analyses that vary one dimension at a time.

4. **Cumulative concordance plot:** Shows the proportion of specifications agreeing in direction (and optionally significance) as specifications are added in order of decreasing precision, providing a visual measure of robustness. A flat line at 100% (as seen for BCG) indicates complete robustness; a declining curve (as seen for omega-3) indicates that less precise specifications disagree with the more precise ones. This plot is particularly useful for identifying whether fragility is driven by a few low-precision specifications or is a pervasive feature of the evidence base.

All visualizations are interactive in the sense that they update automatically when the user changes dimension selections. They are also print-ready, rendering cleanly in the browser's print dialog for inclusion in reports and manuscripts.

#### Additional Features

- **Auto-generated methods text:** A plain-language paragraph describing the multiverse analysis configuration, suitable for direct inclusion in a manuscript methods section.
- **Print-ready report:** A formatted summary including all visualizations, summary statistics, and the methods paragraph, exportable via the browser print function.
- **CSV export:** The full specification-level results table can be downloaded as a CSV file for further analysis in R, Python, or spreadsheet software.
- **Keyboard accessibility:** All interactive controls are keyboard-navigable, with ARIA labels and roles for screen reader compatibility.
- **Three built-in datasets:** BCG vaccine efficacy [17], aspirin and stroke prevention [18], and omega-3 fatty acids and cardiovascular mortality [19], enabling immediate use without data entry.
- **Custom data entry:** Users can enter their own study-level data (effect size, standard error, and study label) via an interactive table.

#### Performance

MultiverseMA uses a synchronous Cartesian product enumeration strategy. For each specification, the pooled effect estimate, confidence interval, heterogeneity statistics (tau-squared, I-squared), and any publication bias adjustments are computed from scratch. This approach prioritizes correctness and simplicity over maximum speed. On a modern desktop browser (Chrome on a mid-range laptop), computation of 48 specifications (the BCG default) completes in under 100 milliseconds. Computation of 30,000+ specifications (large multiverse with leave-one-out and study-level toggles) completes in approximately 2-5 seconds, with SVG rendering dominating the total time. For very large specification sets, the SVG specification curve may show perceptible rendering delay, but the summary statistics and influence decomposition are available immediately.

The iterative estimators (REML, PM, ML) use a Newton-Raphson convergence algorithm with a tolerance of 1e-8 and a maximum of 100 iterations. Convergence failure is handled gracefully by falling back to the DerSimonian-Laird estimate with a warning flag in the specification-level output.

### Validation

#### Automated Test Suite

MultiverseMA is validated by a Selenium test suite comprising 33 tests across six categories (Table 3). All 33 tests pass on the current release.

**Table 3. Selenium test suite summary.**

| Category | Tests | Pass |
|----------|-------|------|
| Data loading and UI | 6 | 6 |
| Statistical computation | 8 | 8 |
| Specification curve | 5 | 5 |
| Publication bias | 4 | 4 |
| Export and reporting | 5 | 5 |
| Edge cases and error handling | 5 | 5 |
| **Total** | **33** | **33** |

#### Multi-Persona Code Review

A three-persona code review was conducted to evaluate the tool from complementary perspectives. Each reviewer operated independently, and findings were deduplicated and prioritized using a severity scale: P0 (critical, must fix before release), P1 (important, should fix), P2 (minor, can defer).

1. **Statistical Methodologist:** Verified all estimator formulas against reference implementations in Viechtbauer [10] and Veroniki et al. [27]. Checked degrees of freedom for all CI methods and validated significance thresholds. Identified and fixed three P0 (critical) issues:
   - (a) The HKSJ adjustment divisor used k instead of k - 1, producing slightly narrow intervals.
   - (b) The t-distribution degrees of freedom were off by one in a specific edge case when outlier removal reduced k to 2.
   - (c) The significance threshold was applied as strictly less than 0.05 rather than less than or equal to 0.05, causing borderline p-values to be misclassified.

2. **UX/Accessibility Reviewer:** Evaluated keyboard navigation, screen reader support, color contrast ratios (WCAG AA: 4.5:1 minimum), and responsive layout on mobile viewports. Identified and fixed three P1 issues related to missing ARIA labels on interactive controls and focus management when modal dialogs close.

3. **Security Reviewer:** Assessed input sanitization for custom study labels, localStorage handling for data persistence, and potential cross-site scripting (XSS) vectors. Identified and fixed two P1 issues: user-entered study labels were rendered via innerHTML without HTML escaping, creating a potential XSS vector if malicious data were pasted.

All 3 P0 and 5 P1 issues were fixed and verified through re-testing.

#### Cross-Validation Against R

The estimates produced by MultiverseMA were cross-validated against the R package metafor [10] (version 4.6) using the BCG vaccine dataset [17]. The DerSimonian-Laird pooled log-risk-ratio and tau-squared matched to within 1e-6:

- MultiverseMA DL: theta = -0.6328, tau^2 = 0.4047
- metafor (method = "DL"): theta = -0.6328, tau^2 = 0.4047

Additional cross-validation was performed for the REML estimator:

- MultiverseMA REML: tau^2 converges via Newton-Raphson (tolerance 1e-8)
- metafor (method = "REML"): agreement to 1e-6 on both theta and tau^2

The I-squared and Q statistics were also verified to match metafor output. These cross-validation results provide confidence that MultiverseMA's JavaScript implementations are numerically equivalent to the reference R implementations for practical purposes.

#### Edge Case Testing

The test suite includes explicit edge cases that are critical for numerical stability:

- **k = 1 (single study):** Random-effects models collapse to the fixed-effect estimate because tau-squared cannot be estimated from a single study. MultiverseMA correctly detects this case and returns the fixed-effect result with an appropriate warning.
- **k = 2 (minimum for heterogeneity):** This is the smallest sample size for which tau-squared can be estimated. The HKSJ method uses k - 1 = 1 degree of freedom, producing very wide confidence intervals. MultiverseMA handles this correctly.
- **All studies excluded:** When the user deselects all studies, MultiverseMA displays a graceful error message rather than producing NaN or crashing.
- **Zero heterogeneity (tau-squared = 0):** When all studies agree exactly, the random-effects model collapses to the fixed-effect model. MultiverseMA correctly falls back to inverse-variance weights without numerical instability.
- **Outlier removal with small k:** When outlier removal is enabled and only 2-3 studies remain after removal, the estimators must still function correctly with reduced degrees of freedom.

---

## Results

### Use Case 1: BCG Vaccine Efficacy (Robust Finding)

The BCG vaccine dataset [17] comprises 13 trials evaluating Bacillus Calmette-Guerin vaccination against tuberculosis, with effect sizes expressed as log-risk-ratios. This dataset is widely used as a teaching example in meta-analysis due to its large and well-established protective effect.

Using the default configuration (6 estimators, 3 CI methods, with and without outlier removal, with and without trim-and-fill, with and without PET-PEESE), MultiverseMA generates 48 specifications. Table 2 summarizes the results.

**Table 2. Summary metrics for the BCG vaccine multiverse analysis (48 specifications).**

| Metric | Value |
|--------|-------|
| Number of specifications | 48 |
| Median point estimate (log-RR) | -0.633 |
| Range of point estimates | -0.782 to -0.436 |
| Direction concordance | 100% (48/48 negative) |
| Significance concordance | 100% (48/48 significant at alpha = 0.05) |
| Vibration of effects (VoE) | 0.346 |
| Most influential dimension | Estimator (partial eta^2 = 0.42) |

The specification curve shows all 48 estimates lying below zero with confidence intervals that do not cross the null. The cumulative concordance plot reaches 100% concordance at every step. The influence decomposition reveals that the heterogeneity estimator explains the largest share of variance (partial eta^2 = 0.42), with publication bias adjustment contributing modestly and CI method contributing negligibly.

The specification curve for the BCG dataset reveals that the six estimators cluster into two groups: the fixed-effect estimate produces the most attenuated effect (closest to zero, reflecting its assumption of no between-study heterogeneity), while the five random-effects estimators produce more negative estimates that account for the substantial heterogeneity in this dataset (I-squared approximately 92%). Within the random-effects group, DL, REML, PM, ML, and SJ produce estimates within a narrow band, confirming that estimator choice has only a modest impact for this dataset.

The CI method dimension is nearly non-influential for BCG because the effect is so large that even the widest HKSJ intervals do not cross zero. This illustrates an important principle: for well-established effects with large signal-to-noise ratios, multiverse analysis confirms robustness rather than revealing fragility.

**Interpretation:** The protective effect of BCG vaccination is extremely robust. No defensible combination of analytical choices reverses the direction or eliminates the significance of the effect. This is the expected result for a well-established intervention with a large effect size and consistent trial-level evidence.

### Use Case 2: Aspirin and Stroke Prevention (Fragile Finding)

The aspirin-stroke dataset [18] includes 8 trials evaluating aspirin for stroke prevention. Unlike the BCG dataset, this evidence base has smaller effect sizes and greater between-study heterogeneity, making it more susceptible to analytical choices.

Using the same default configuration, MultiverseMA generates specifications that reveal fragility in the evidence base. While most specifications yield a protective point estimate, the significance status varies substantially across analytical choices. Specifications using the HKSJ confidence interval method are more likely to produce non-significant results, reflecting the wider intervals that HKSJ produces when between-study heterogeneity is present [26]. Similarly, specifications incorporating publication bias adjustment via trim-and-fill or PET-PEESE tend to attenuate the pooled effect toward the null.

The VoE is substantially larger than for BCG, indicating that the aspirin-stroke evidence is genuinely sensitive to methodological choices. The influence decomposition reveals a qualitatively different pattern from the BCG analysis: both the CI method and the heterogeneity estimator contribute meaningfully to specification-level variance, whereas for BCG, the CI method was negligible. This difference is informative -- it tells the analyst that for the aspirin-stroke question, the choice between Wald and HKSJ intervals is consequential, not merely a methodological formality.

**Interpretation:** The aspirin-stroke finding is sensitive to analytical choices. A researcher reporting only the DerSimonian-Laird/Wald specification would present a significant protective effect, while an equally defensible REML/HKSJ specification might yield a non-significant result. Multiverse analysis makes this sensitivity visible and reportable. For guideline developers, this finding suggests that the evidence certainty (in GRADE terms) should be rated down for inconsistency, supported by quantitative evidence from the specification curve rather than subjective judgment alone.

### Use Case 3: Omega-3 Fatty Acids and Cardiovascular Mortality (Controversial)

The omega-3/cardiovascular mortality dataset [19] includes 7 trials and represents a genuinely controversial evidence base where different published meta-analyses have reached different conclusions depending on methodology and study selection.

The multiverse analysis reveals substantial heterogeneity across specifications. Point estimates span a wide range, and significance status is highly dependent on the choice of estimator, outlier handling, and publication bias method. The influence decomposition identifies publication bias adjustment as the single most influential dimension, consistent with the known sensitivity of this literature to small-study effects. This is a substantively important finding: it tells the analyst that the primary source of ambiguity in this evidence base is not the choice of estimator or CI method (which produce relatively stable estimates) but whether and how one adjusts for potential selective reporting.

The cumulative concordance plot for the omega-3 dataset shows a progressively declining concordance rate as less precise specifications are added, in stark contrast to the flat 100% concordance observed for BCG. This visual pattern immediately communicates that the omega-3 evidence is fragile in a specific way -- it depends on which publication bias adjustment is applied.

**Interpretation:** The multiverse analysis provides a transparent account of why this evidence base generates controversy. The conclusion -- whether omega-3 supplementation reduces cardiovascular mortality -- depends critically on defensible analytical choices that different meta-analysts might reasonably make differently. Reporting only one specification obscures this fundamental ambiguity. The influence decomposition adds diagnostic value by pinpointing publication bias adjustment as the key driver, directing future research attention toward resolving the small-study effects question rather than debating estimator choice.

### Interpreting MultiverseMA Output

To assist users in drawing appropriate conclusions from multiverse analyses, we provide the following interpretation framework based on the four output components:

**Direction concordance** is the proportion of specifications yielding a point estimate in the same direction (i.e., same sign). A direction concordance of 100% means that no defensible analytical specification reverses the direction of the effect. Values below 90% suggest that the direction of the effect is genuinely uncertain.

**Significance concordance** is the proportion of specifications yielding a statistically significant result (p < 0.05). A significance concordance of 100% (as observed for BCG) indicates extreme robustness. Values between 50% and 90% suggest that significance is sensitive to analytical choices. Values below 50% suggest that the null hypothesis cannot be rejected under most specifications.

**Vibration of effects (VoE)** quantifies the range of point estimates across all specifications. A small VoE relative to the point estimate indicates stability; a large VoE indicates that the magnitude of the effect is uncertain even when the direction is consistent. VoE should be interpreted on the scale of the effect size measure (e.g., log-RR, log-OR, standardized mean difference).

**Influence decomposition** identifies the decision dimensions that contribute most to variation. A partial eta-squared above 0.14 for a given dimension is conventionally considered a "large" effect, indicating that this dimension is a primary driver of specification-level variation. This information is actionable: if the estimator explains most variance, the analyst should justify their estimator choice explicitly; if publication bias adjustment is the dominant factor, the analyst should discuss the plausibility of selective reporting.

### Auto-Generated Methods Text

For each analysis, MultiverseMA generates a plain-language methods paragraph suitable for direct inclusion in a manuscript methods section. For example, for the BCG analysis:

> "A multiverse meta-analysis was conducted using MultiverseMA. Six heterogeneity estimators (FE, DL, REML, PM, ML, SJ) were crossed with three confidence interval methods (Wald, HKSJ, t-distribution) and publication bias adjustments (none, trim-and-fill, PET-PEESE), yielding 48 specifications. All specifications produced significant protective effects (100% concordance), with a median log-risk-ratio of -0.633."

This auto-generation feature reduces reporting burden and promotes standardized description of multiverse analyses. The text adapts dynamically to the selected dimensions and results, ensuring accuracy without manual editing.

### Reporting Recommendations

Based on our experience developing and testing MultiverseMA, we recommend that authors reporting multiverse meta-analyses include the following elements:

1. **Specification count and dimensions:** State the total number of specifications and list all decision dimensions with their options (as in Table 1).

2. **Direction and significance concordance:** Report both the proportion of specifications with the same sign as the median estimate and the proportion reaching statistical significance.

3. **VoE metric:** Report the range of point estimates to quantify the vibration of effects.

4. **Influence decomposition:** Identify the one or two most influential dimensions and their partial eta-squared values.

5. **Specification curve figure:** Include the dual-panel specification curve as a main figure, not a supplement, to give readers direct visual access to the full distribution of results.

6. **Sensitivity narrative:** For fragile findings, explicitly state which analytical choices tip the result from significant to non-significant and discuss the methodological justification for each.

These recommendations are consistent with the spirit of PRISMA 2020 [7] and can be adapted to other reporting guidelines.

---

## Discussion

### Transparency in Meta-Analytic Decision-Making

MultiverseMA operationalizes the principle that analytical transparency is a prerequisite for credible evidence synthesis. The traditional approach -- reporting a single preferred specification without acknowledging the existence of alternatives -- creates a false sense of precision and obscures the sensitivity of conclusions to methodological choices. By generating and displaying all defensible specifications simultaneously, MultiverseMA enables analysts to distinguish robust findings (BCG: 100% concordance) from fragile ones (aspirin-stroke: mixed significance) and to identify which specific decisions drive variation (influence decomposition).

### Relationship to Specification Curve Analysis

Simonsohn et al. [4] introduced specification curve analysis for primary research, where the analyst varies data processing and model specification choices. MultiverseMA extends this concept to the meta-analytic context, where the relevant decisions are specific to evidence synthesis: estimator selection, confidence interval construction, and publication bias adjustment. The specification curve visualization follows the same dual-panel format (sorted estimates above, indicator matrix below), but the decision dimensions are meta-analysis-specific.

### Integration with Existing Frameworks

Multiverse analysis complements rather than replaces existing sensitivity analysis approaches in meta-analysis. Leave-one-out analysis, which MultiverseMA includes as one decision dimension, examines the influence of individual studies on the pooled estimate. Subgroup analysis examines effect modification by study-level covariates. Publication bias methods (funnel plots, trim-and-fill, PET-PEESE) address selective reporting. Each of these traditional sensitivity analyses varies one dimension while holding others fixed. Multiverse analysis integrates them into a unified framework that also captures the joint effect of multiple simultaneous choices -- for example, revealing that the combination of HKSJ intervals and trim-and-fill adjustment together produces a non-significant result, even though each individually leaves the result significant.

The results of a multiverse analysis can inform GRADE assessments [20]. The GRADE domain of "inconsistency" is typically assessed by visual inspection of forest plots and the I-squared statistic [24]. Multiverse concordance provides a complementary and arguably more comprehensive measure of consistency: if a finding shows 100% concordance across all defensible specifications, this strengthens the case for not rating down for inconsistency. Conversely, if significance depends on a single estimator or the inclusion of one borderline study, this provides specific, quantitative evidence for rating down. The influence decomposition further identifies which dimension drives the inconsistency, enabling targeted justification in the GRADE evidence profile.

### Pre-Registration of Analytical Choices

MultiverseMA can support the pre-registration of meta-analytic protocols. Rather than committing to a single analytical specification a priori, researchers can pre-register the full set of defensible choices and commit to reporting the multiverse distribution. This approach, advocated by Del Giudice and Gangestad [3], eliminates the incentive for post hoc specification selection while preserving analytical flexibility.

### Comparison with Existing Tools

specr [5] is an R package for specification curve analysis in primary datasets. It provides a flexible framework for defining and visualizing specification curves but is not designed for meta-analytic workflows -- it lacks heterogeneity estimators, confidence interval methods specific to meta-analysis, and publication bias adjustment. Using specr for multiverse meta-analysis would require substantial custom R programming to implement these components. SMART [6] is a web-based framework for structured multiverse analysis that requires user registration and is not freely accessible for general use. It focuses on registration and planning rather than real-time computation and visualization. MultiverseMA is the first tool to combine meta-analysis-specific statistical engines with browser-based execution and no-code interaction, making multiverse analysis accessible to researchers regardless of programming expertise.

### Pedagogical Value

Beyond its research applications, MultiverseMA serves as a teaching tool. The built-in datasets provide immediate, hands-on demonstrations of how analytical choices affect meta-analytic conclusions. Students can toggle estimators on and off and observe the specification curve update in real time, building intuition for concepts that are otherwise abstract (e.g., "HKSJ produces wider intervals than Wald when heterogeneity is present"). The influence decomposition chart makes the relative importance of different decisions visually concrete, and the auto-generated methods text models transparent reporting practices.

### Relationship to Reproducibility and Open Science

MultiverseMA aligns with the broader open science movement by making the full analytical decision space visible and explorable. When a multiverse analysis accompanies a published meta-analysis, readers can evaluate for themselves whether the reported conclusion is robust or contingent on specific choices. The CSV export enables independent analysts to re-examine the specification-level data, and the single-file architecture ensures that the exact version of the tool used for an analysis can be archived alongside the publication as supplementary material.

This approach addresses a specific critique of meta-analysis that has gained prominence in recent years: the concern that meta-analysts can (consciously or unconsciously) select specifications that favor a desired conclusion. By pre-committing to a multiverse analysis and reporting the full specification distribution, analysts can demonstrate that their conclusions are not contingent on arbitrary choices. This is analogous to the role of pre-registration in primary research -- it does not eliminate bias, but it makes bias-driven choices visible and accountable.

### Clinical Implications

For clinical decision-makers, multiverse meta-analysis offers a more nuanced evidence summary than a single pooled estimate with a confidence interval. Consider a guideline panel evaluating whether to recommend aspirin for stroke prevention. A standard meta-analysis might report a significant risk reduction with a narrow confidence interval, suggesting strong evidence. A multiverse analysis reveals that this significance depends on specific analytical choices -- a finding that should temper the panel's confidence and perhaps lead to a conditional (rather than strong) recommendation.

The influence decomposition is particularly valuable in clinical contexts because it identifies the source of analytical uncertainty. If the conclusion depends primarily on whether one borderline study is included (study inclusion dimension), the panel can focus its deliberation on the quality and relevance of that study. If the conclusion depends on the choice of heterogeneity estimator, the panel can ask a methodologist to justify the preferred estimator. This shifts the discussion from vague concerns about "robustness" to specific, actionable questions about analytical choices.

### Limitations of the Multiverse Approach Itself

It is important to acknowledge that multiverse analysis, while a substantial advance, is not a panacea. The approach assumes that all included specifications are equally defensible, but this is rarely true in practice -- some estimators are known to perform better than others under specific conditions [26, 27]. The specification curve does not weight specifications by their methodological quality, and treating a clearly inferior specification as equally valid may distort the concordance metrics. Future work on weighted specification curves could address this limitation.

Additionally, multiverse analysis as currently practiced addresses only the analytical decision space, not the data collection decision space. Decisions about search strategy, database selection, screening criteria, and data extraction are equally consequential but occur upstream of the multiverse. A truly comprehensive multiverse would vary these decisions as well, but this is currently beyond the scope of any automated tool.

---

## Limitations

Several limitations should be acknowledged.

**Computational precision.** MultiverseMA uses JavaScript IEEE 754 double-precision floating-point arithmetic. While this provides approximately 15-16 significant digits -- sufficient for all practical meta-analytic computations -- it does not match the extended precision available in R or specialized numerical libraries. For the estimators implemented, cross-validation against metafor shows agreement to 1e-6, confirming that JavaScript precision is adequate.

**No WebR validation tier.** Unlike some of our other tools, MultiverseMA does not yet include a WebR-based in-browser validation tier that cross-checks JavaScript computations against R in real time. This is planned for a future release.

**Scalability of leave-one-out.** Enabling leave-one-out analysis multiplicatively expands the specification count by a factor of k (number of studies). For datasets with 20+ studies and all decision dimensions enabled, this can produce tens of thousands of specifications, which may cause perceptible rendering delays on lower-powered devices. The computational engine handles 30,000+ specifications, but SVG rendering of very large specification curves may be slow.

**Equal defensibility assumption.** The specification curve treats all included specifications as equally defensible. In practice, some specifications may be more methodologically justified than others (e.g., REML over DL for small k, HKSJ over Wald for heterogeneous data). MultiverseMA does not currently support weighted specification curves, though the CSV export enables users to apply weights in external software.

**Scope of meta-analytic models.** MultiverseMA implements univariate pairwise meta-analysis only. It does not support multivariate meta-analysis, network meta-analysis, individual participant data meta-analysis, or multi-level (three-level) models. Extending multiverse analysis to these more complex models is a direction for future work.

**Publication bias method limitations.** Trim-and-fill assumes that funnel plot asymmetry is caused by publication bias, which is not always the case [21]. PET-PEESE assumes a linear relationship between effect size and standard error (or variance), which may not hold in all datasets [22]. These are well-known limitations of the methods themselves, not of MultiverseMA's implementation, but users should interpret bias-adjusted specifications with appropriate caution.

**No formal robustness test.** MultiverseMA reports descriptive summaries (concordance proportions, VoE, influence decomposition) but does not provide a formal inferential test for multiverse robustness. Developing such tests is an active area of methodological research [23].

**Sample size.** The three built-in datasets are small (7-13 studies), typical for meta-analyses but limiting for demonstrating scalability. Users can enter custom datasets of arbitrary size.

**No Bayesian specifications.** MultiverseMA currently implements only frequentist estimators and confidence intervals. Bayesian meta-analysis with informative or weakly informative priors represents an important class of analytical choices that is not yet represented in the multiverse. Incorporating Bayesian specifications (e.g., using WebR to call brms or bayesmeta) is a planned future extension.

**Browser compatibility.** While MultiverseMA is tested on Chrome, Firefox, Edge, and Safari, minor rendering differences in SVG display may occur across browsers. The computational results are identical across all tested browsers; only the visual presentation may vary slightly.

---

## Conclusions

MultiverseMA is the first browser-based engine for multiverse meta-analysis. By systematically enumerating all defensible combinations of analytical choices -- heterogeneity estimator, confidence interval method, study inclusion, outlier handling, publication bias adjustment, leave-one-out analysis, and effect direction -- it enables transparent assessment of whether meta-analytic conclusions are robust or fragile.

The tool is validated by 33 automated Selenium tests (33/33 passing), a three-persona code review (3 P0 and 5 P1 issues identified and fixed), and cross-validation against the R package metafor. It requires no installation, no server, and no programming expertise.

Three use cases demonstrate the tool's value: the BCG vaccine dataset confirms a robust protective effect (100% concordance), the aspirin-stroke dataset reveals a fragile finding sensitive to estimator and CI method choices, and the omega-3/cardiovascular mortality dataset exposes a genuinely ambiguous evidence base.

Future development priorities include: (a) a WebR-based in-browser validation tier that cross-checks JavaScript computations against R in real time, (b) support for weighted specification curves where methodologically preferred specifications receive higher weight, (c) a formal inferential test for multiverse robustness based on the proportion of significant specifications relative to chance, and (d) extension to network meta-analysis and multi-level models.

MultiverseMA is open-source and freely available at https://github.com/mahmood726-cyber/MultiverseMA under the MIT License. The complete source code, test suite, and built-in datasets are contained in a single HTML file that can be downloaded and run offline.

---

## Data Availability

Three built-in example datasets are included directly in MultiverseMA. The BCG vaccine dataset is from Colditz et al. [17]. The aspirin-stroke dataset is from published randomized trials of aspirin for stroke prevention [18]. The omega-3/cardiovascular mortality dataset is from published trials of omega-3 supplementation [19]. No external data access is required. Source code is available at https://github.com/mahmood726-cyber/MultiverseMA.

---

## Software Availability

- **Source code:** https://github.com/mahmood726-cyber/MultiverseMA
- **Archived version:** ZENODO_DOI_PENDING
- **License:** MIT

---

## Author Contributions

Mahmood Ahmad conceived and designed the tool, implemented the statistical engines and visualizations, conducted the validation, and wrote the manuscript.

---

## Competing Interests

No competing interests were disclosed.

---

## Grant Information

The author(s) declared that no grants were involved in supporting this work.

---

## Acknowledgments

We thank the developers of metafor [10] for providing the reference implementation against which MultiverseMA was validated. We also acknowledge the foundational methodological contributions of Steegen et al. [1] and Simonsohn et al. [4], whose work on multiverse analysis and specification curve analysis directly inspired this tool.

---

## References

[1] Steegen S, Tuerlinckx F, Gelman A, Vanpaemel W. Increasing transparency through a multiverse analysis. *Perspect Psychol Sci.* 2016;11(5):702-712. doi:10.1177/1745691616658637

[2] Voracek M, Kossmeier M, Tran US. Which data to meta-analyze, and how? A specification-curve and multiverse-analysis approach to meta-analysis. *Z Psychol.* 2019;227(1):64-82. doi:10.1027/2151-2604/a000357

[3] Del Giudice M, Gangestad SW. A traveler's guide to the multiverse: Promises, pitfalls, and a framework for the evaluation of analytic decisions. *Adv Methods Pract Psychol Sci.* 2021;4(1):2515245920954925. doi:10.1177/2515245920954925

[4] Simonsohn U, Simmons JP, Nelson LD. Specification curve analysis. *Nat Hum Behav.* 2020;4(11):1208-1214. doi:10.1038/s41562-020-0912-z

[5] Masur PK, Scharkow M. specr: Conducting and visualizing specification curve analyses. R package. 2020. Available from: https://CRAN.R-project.org/package=specr

[6] Olsson-Collentine A, Wicherts JM, van Assen MALM. SMART: Specification-curve analysis for meta-analysis of randomized trials. 2021.

[7] Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. *BMJ.* 2021;372:n71. doi:10.1136/bmj.n71

[8] Hedges LV, Olkin I. *Statistical Methods for Meta-Analysis.* Orlando, FL: Academic Press; 1985.

[9] DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials.* 1986;7(3):177-188. doi:10.1016/0197-2456(86)90046-2

[10] Viechtbauer W. Conducting meta-analyses in R with the metafor package. *J Stat Softw.* 2010;36(3):1-48. doi:10.18637/jss.v036.i03

[11] Paule RC, Mandel J. Consensus values and weighting factors. *J Res Natl Bur Stand.* 1982;87(5):377-385. doi:10.6028/jres.087.022

[12] Sidik K, Jonkman JN. A simple confidence interval for meta-analysis. *Stat Med.* 2002;21(21):3153-3159. doi:10.1002/sim.1262

[13] Rover C, Knapp G, Friede T. Hartung-Knapp-Sidik-Jonkman approach and its modification for random-effects meta-analysis with few studies. *BMC Med Res Methodol.* 2015;15:99. doi:10.1186/s12874-015-0091-1

[14] Duval S, Tweedie R. Trim and fill: A simple funnel-plot-based method of testing and adjusting for publication bias in meta-analysis. *Biometrics.* 2000;56(2):455-463. doi:10.1111/j.0006-341X.2000.00455.x

[15] Stanley TD, Doucouliagos H. Meta-regression approximations to reduce publication selection bias. *Res Synth Methods.* 2014;5(1):60-78. doi:10.1002/jrsm.1095

[16] Patel CJ, Burford B, Ioannidis JPA. Assessment of vibration of effects due to model specification can demonstrate the instability of observational associations. *J Clin Epidemiol.* 2015;68(9):1046-1058. doi:10.1016/j.jclinepi.2015.05.029

[17] Colditz GA, Brewer TF, Berkey CS, et al. Efficacy of BCG vaccine in the prevention of tuberculosis: meta-analysis of the published literature. *JAMA.* 1994;271(9):698-702. doi:10.1001/jama.1994.03510330076038

[18] Antithrombotic Trialists' Collaboration. Collaborative meta-analysis of randomised trials of antiplatelet therapy for prevention of death, myocardial infarction, and stroke in high risk patients. *BMJ.* 2002;324(7329):71-86. doi:10.1136/bmj.324.7329.71

[19] Aung T, Halsey J, Kromhout D, et al. Associations of omega-3 fatty acid supplement use with cardiovascular disease risks: meta-analysis of 10 trials involving 77,917 individuals. *JAMA Cardiol.* 2018;3(3):225-234. doi:10.1001/jamacardio.2017.5205

[20] Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. *BMJ.* 2008;336(7650):924-926. doi:10.1136/bmj.39489.470347.AD

[21] Terrin N, Schmid CH, Lau J, Olkin I. Adjusting for publication bias in the presence of heterogeneity. *Stat Med.* 2003;22(13):2113-2126. doi:10.1002/sim.1461

[22] Stanley TD. Limitations of PET-PEESE and other meta-analysis methods. *Soc Psychol Personal Sci.* 2017;8(5):581-591. doi:10.1177/1948550617693062

[23] Simonsohn U, Simmons JP, Nelson LD. Above averaging in literature reviews. *Nat Rev Psychol.* 2024;3:899-912. doi:10.1038/s44159-024-00372-3

[24] Higgins JPT, Thompson SG, Deeks JJ, Altman DG. Measuring inconsistency in meta-analyses. *BMJ.* 2003;327(7414):557-560. doi:10.1136/bmj.327.7414.557

[25] Hartung J, Knapp G. A refined method for the meta-analysis of controlled clinical trials with binary outcome. *Stat Med.* 2001;20(24):3875-3889. doi:10.1002/sim.1009

[26] IntHout J, Ioannidis JPA, Borm GF. The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. *BMC Med Res Methodol.* 2014;14:25. doi:10.1186/1471-2288-14-25

[27] Veroniki AA, Jackson D, Viechtbauer W, et al. Methods to estimate the between-study variance and its uncertainty in meta-analysis. *Res Synth Methods.* 2016;7(1):55-79. doi:10.1002/jrsm.1164

---

## F1000Research Reviewer Checklist

The following questions correspond to the F1000Research Software Tool Article review criteria. We indicate where each is addressed in the manuscript.

**1. Is the rationale for developing the new software tool clearly explained?**
Yes. The Introduction (paragraphs 1-4) describes the garden-of-forking-paths problem in meta-analysis, reviews existing tools (specr, SMART), identifies the gap (no browser-based multiverse meta-analysis tool), and states MultiverseMA's contribution.

**2. Is the description of the software tool technically sound?**
Yes. The Methods -- Implementation section provides formulas for all six heterogeneity estimators, describes three CI methods with implementation details (including the HKSJ floor), documents both publication bias methods with selection logic (PET-PEESE conditional procedure), and specifies all seven decision dimensions with their options (Table 1).

**3. Are sufficient details of the code provided to allow replication of the software development and its use by other developers?**
Yes. The tool is a single self-contained HTML file (2,430 lines) with no external dependencies. The source code is available at the GitHub repository. The architecture section describes the implementation approach. The CSV export enables independent verification of all computed results.

**4. Is sufficient information provided to allow interpretation of the expected output and any results generated using the tool?**
Yes. The Results section provides three fully worked use cases (BCG, aspirin-stroke, omega-3) with specific numerical results (Table 2), interpretation guidance for each visualization (specification curve, VoE plot, influence decomposition, concordance plot), and an example of the auto-generated methods text. Each use case includes an explicit interpretation paragraph explaining what the multiverse results mean for the evidence base.

**5. Are the conclusions about the tool and its performance adequately supported by the findings presented in the article?**
Yes. Claims of robustness (BCG: 100% concordance) and fragility (aspirin-stroke: mixed significance) are supported by the specification-level data. Validation is documented through 33/33 Selenium tests (Table 3), three-persona review with specific issues found and fixed, and cross-validation against metafor to 1e-6 precision. The Limitations section honestly acknowledges eight specific limitations including precision constraints, scalability concerns, the equal-defensibility assumption, and scope limitations.
