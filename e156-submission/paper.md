Mahmood Ahmad
Tahir Heart Institute
author@example.com

MultiverseMA: Browser-Based Multiverse Meta-Analysis Engine

Can a browser-based multiverse engine systematically enumerate all defensible analytic specifications and reveal whether meta-analytic conclusions are robust or fragile? Three built-in datasets were analyzed: BCG vaccine (13 studies), aspirin-stroke (6 studies), and omega-3 cardiovascular mortality (8 studies), spanning diverse clinical domains. MultiverseMA, a single-file HTML application of 2,430 lines, generates the full Cartesian product across seven decision dimensions including estimator choice, CI method, outlier handling, and publication bias adjustment. The BCG dataset yielded a median log-RR of -0.633 (95% CI -0.97 to -0.30) with 100% significance concordance across all 48 specifications. The aspirin-stroke dataset revealed fragility, with significance flipping under alternative estimator and inclusion choices, while omega-3 showed high between-specification heterogeneity. This tool is the first browser-based multiverse meta-analysis engine, validated by 33 Selenium tests, enabling transparent robustness assessment without software installation or programming. A limitation is that the engine currently supports univariate pairwise meta-analysis only and does not incorporate network or diagnostic accuracy models.

Outside Notes

Type: methods
Primary estimand: Specification concordance
App: MultiverseMA v1.0
Data: BCG vaccine, aspirin-stroke, omega-3 (built-in datasets)
Code: https://github.com/mahmood726-cyber/MultiverseMA
Version: 1.0
Validation: DRAFT

References

1. Walsh M, Srinathan SK, McAuley DF, et al. The statistical significance of randomized controlled trial results is frequently fragile: a case for a Fragility Index. J Clin Epidemiol. 2014;67(6):622-628.
2. Atal I, Porcher R, Boutron I, Ravaud P. The statistical significance of meta-analyses is frequently fragile: definition of a fragility index for meta-analyses. J Clin Epidemiol. 2019;111:32-40.
3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.

AI Disclosure

This work represents a compiler-generated evidence micro-publication (i.e., a structured, pipeline-based synthesis output). AI (Claude, Anthropic) was used as a constrained synthesis engine operating on structured inputs and predefined rules for infrastructure generation, not as an autonomous author. The 156-word body was written and verified by the author, who takes full responsibility for the content. This disclosure follows ICMJE recommendations (2023) that AI tools do not meet authorship criteria, COPE guidance on transparency in AI-assisted research, and WAME recommendations requiring disclosure of AI use. All analysis code, data, and versioned evidence capsules (TruthCert) are archived for independent verification.
