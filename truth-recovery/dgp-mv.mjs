// ============================================================
// dgp-mv.mjs -- Known-truth DGP for MULTIVERSE meta-analysis robustness.
//
// A multiverse runs the same data through many analytical specifications and
// summarises the cloud. MultiverseMA already ships the spec-collapse correction
// (specCollapseAggregates): a naive inverse-variance pool across specifications
// treats analyses of the SAME data as independent studies and manufactures false
// robustness, whereas a weighted-likelihood mixture interval accounts for the
// between-specification spread. This DGP checks that directly against a known
// truth: under a true NULL effect, how often does each summary declare the
// multiverse "robust" (CI excludes 0)? A calibrated summary should do so ~5% of
// the time; the naive pool should far exceed that.
//
// Model: m specifications of the same underlying truth mu.
//   theta_i = mu + tauSpec * b_i + se_i * e_i ,  b_i,e_i ~ N(0,1),
//   se_i ~ log-uniform[seLo,seHi].  tauSpec = between-specification spread
//   induced by analytical choices. Each spec reports (theta_i, se_i).
//
// Seeded -> reproducible. Standalone.
// ============================================================

export function makeRng(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function randn(rng) {
  let u1 = rng(), u2 = rng();
  if (u1 < 1e-12) u1 = 1e-12;
  return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
}
function drawSe(rng, lo, hi) {
  const a = Math.log(lo), b = Math.log(hi);
  return Math.exp(a + (b - a) * rng());
}

// One multiverse: m specifications estimating the same truth mu.
export function generate(mu, m, tauSpec, rng, { seLo = 0.06, seHi = 0.20 } = {}) {
  const specs = [];
  for (let i = 0; i < m; i++) {
    const se = drawSe(rng, seLo, seHi);
    const theta = mu + tauSpec * randn(rng) + se * randn(rng);
    specs.push({ theta, se });
  }
  return { specs, mu };
}
