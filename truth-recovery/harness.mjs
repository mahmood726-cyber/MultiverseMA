// ============================================================
// harness.mjs -- Truth-recovery yardstick for MultiverseMA.
//
// Uses the app's OWN specCollapseAggregates (engine.mjs, verbatim) to measure,
// against a known truth, the FALSE-ROBUSTNESS rate of the two multiverse
// summaries: the naive inverse-variance pool vs the weighted-likelihood mixture.
// Under a true null a calibrated summary should call the multiverse "robust"
// (CI excludes 0) ~5% of the time; under a true effect it should keep power.
//
// Truth-first: every number printed comes from seeded simulation here.
// Run:  node truth-recovery/harness.mjs --reps 4000
// ============================================================

import { specCollapseAggregates } from './engine.mjs';
import { generate, makeRng } from './dgp-mv.mjs';

const BASE_SEED = 20260613;

const Z = 1.959963984540054;

// Proposed calibrated CI for the MEAN, built from the engine's OWN within/between
// components (which specCollapseAggregates already computes but does not use for
// its interval): SE_mean = sqrt(total / n), total = within + between. Unlike the
// mixture PREDICTION interval the app ships, this shrinks with the number of
// specifications, so it keeps power.
function calibratedMeanCI(a) {
  const se = Math.sqrt(a.wl.total / a.n);
  const lo = a.wl.theta - Z * se, hi = a.wl.theta + Z * se;
  return { lo, hi, sig: (lo > 0 || hi < 0) };
}

export function runCell(mu, m, tauSpec, reps, rng) {
  let ivreRobust = 0, wlRobust = 0, meanRobust = 0, widthRatioSum = 0, n = 0;
  for (let r = 0; r < reps; r++) {
    const { specs } = generate(mu, m, tauSpec, rng);
    const a = specCollapseAggregates(specs);
    if (!a) continue;
    n++;
    if (a.ivre.sig) ivreRobust++;
    if (a.wl.sig) wlRobust++;
    if (calibratedMeanCI(a).sig) meanRobust++;
    widthRatioSum += a.widthRatio;
  }
  return {
    ivreRobust: +(ivreRobust / n).toFixed(4),   // P(declared robust)
    wlRobust: +(wlRobust / n).toFixed(4),
    meanRobust: +(meanRobust / n).toFixed(4),
    widthRatio: +(widthRatioSum / n).toFixed(3), // naive width / mixture-prediction width
  };
}

const isMain = process.argv[1]?.endsWith('harness.mjs');
if (isMain) {
  const i = process.argv.indexOf('--reps');
  const reps = i >= 0 ? Number(process.argv[i + 1]) : 4000;
  const t0 = Date.now();
  const rng = makeRng(BASE_SEED);
  console.log(`\n# Truth-recovery yardstick -- MultiverseMA (spec-collapse aggregator)`);
  console.log(`reps=${reps}/cell  m=40 specs  seed=${BASE_SEED}\n`);
  console.log('## FALSE-ROBUSTNESS under a TRUE NULL (mu=0) -- "robust" rate should be ~0.05\n');
  console.log('tauSpec   naive-IVRE   shipped-WL(mixture)   proposed mean-CI');
  for (const tau of [0.0, 0.05, 0.10, 0.20]) {
    const r = runCell(0.0, 40, tau, reps, rng);
    console.log(String(tau).padEnd(9),
      String(r.ivreRobust).padStart(10), String(r.wlRobust).padStart(19), String(r.meanRobust).padStart(18));
  }
  console.log('\n## POWER under a TRUE effect (mu=0.15) -- should detect when real\n');
  console.log('tauSpec   naive-IVRE   shipped-WL(mixture)   proposed mean-CI');
  for (const tau of [0.05, 0.10, 0.20]) {
    const r = runCell(0.15, 40, tau, reps, rng);
    console.log(String(tau).padEnd(9),
      String(r.ivreRobust).padStart(10), String(r.wlRobust).padStart(19), String(r.meanRobust).padStart(18));
  }
  console.log(`\n("robust" = the aggregate 95% CI excludes 0. Under the null this is a FALSE-positive robustness call.)`);
  console.log(`(${(Date.now() - t0) / 1000}s)`);
}
