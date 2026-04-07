Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

MultiverseMA: Browser-Based Multiverse Meta-Analysis Engine

Can a browser-based multiverse engine systematically enumerate all defensible analytic specifications and quantify how robust a meta-analytic conclusion truly is? Five built-in datasets were analyzed: BCG vaccine (13 studies), aspirin-stroke (8 studies), omega-3 cardiovascular mortality (7 studies), IV magnesium in AMI (10 studies), and antenatal corticosteroids (12 studies). MultiverseMA, a single-file HTML application of 4,540 lines, generates the full Cartesian product across nine decision dimensions — including ten tau-squared estimators, four CI methods, five effect measures, and four publication bias adjustments — with TruthCert SHA-256 audit trails. The BCG dataset yielded a median log-RR of -0.633 (95% CI -0.97 to -0.30) with 100% significance concordance across all specifications. Aspirin-stroke revealed fragility at 62% concordance, while magnesium showed the ISIS-4 mega-trial dominance effect. This is the first browser-based multiverse meta-analysis engine, validated by 81 Selenium tests with WebR cross-validation, enabling transparent robustness assessment without installation. A limitation is that the engine supports univariate pairwise meta-analysis only.

Outside Notes

Type: methods
Primary estimand: Specification concordance
App: MultiverseMA v2.0
Data: BCG vaccine, aspirin-stroke, omega-3, magnesium AMI, corticosteroids (built-in)
Code: https://github.com/mahmood726-cyber/MultiverseMA
Version: 2.0
Validation: PASS (81/81 tests, WebR, 3-round review clean)

References

1. Voracek M, Kossmeier M, Tran US. Which data to meta-analyze, and how? Specification-curve and multiverse-analysis approaches. Zeitschrift fur Psychologie. 2019;227(1):64-82.
2. Simonsohn U, Simmons JP, Nelson LD. Specification curve analysis. Nature Human Behaviour. 2020;4:1208-1214.
3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.
