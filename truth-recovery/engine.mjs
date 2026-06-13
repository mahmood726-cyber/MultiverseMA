// engine.mjs -- spec-collapse aggregator EXTRACTED VERBATIM from multiverse-ma.html
// (normalCDF + specCollapseAggregates). The SAME math the app ships is measured.

function normalCDF(x) {
  // Abramowitz & Stegun approximation 26.2.17
  if (x === 0) return 0.5;
  const sign = x < 0 ? -1 : 1;
  x = Math.abs(x);
  const t = 1 / (1 + 0.2316419 * x);
  const d = 0.3989422804014327 * Math.exp(-0.5 * x * x);
  const p = d * t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
  return sign < 0 ? p : 1 - p;
}

function specCollapseAggregates(specs) {
  const n = specs.length;
  if (n === 0) return null;
  const thetas = specs.map(s => s.theta);
  const vars = specs.map(s => s.se * s.se);
  const sds = vars.map(v => Math.sqrt(v));
  // (1) naive IV-RE pool across specs -- the cardinal sin
  let sInv = 0, sNum = 0;
  for (let i = 0; i < n; i++) { const inv = 1 / vars[i]; sInv += inv; sNum += thetas[i] * inv; }
  const ivreTheta = sNum / sInv, ivreVar = 1 / sInv;
  const ivreHalf = 1.959963984540054 * Math.sqrt(ivreVar);
  const ivre = { theta: ivreTheta, lo: ivreTheta - ivreHalf, hi: ivreTheta + ivreHalf };
  ivre.sig = (ivre.lo > 0 || ivre.hi < 0);
  // (2) weighted-likelihood Gaussian mixture, uniform weights
  const mean = thetas.reduce((a, b) => a + b, 0) / n;
  let within = 0, between = 0;
  for (let i = 0; i < n; i++) { within += vars[i] / n; between += ((thetas[i] - mean) ** 2) / n; }
  const mixCdf = x => { let s = 0; for (let i = 0; i < n; i++) s += normalCDF((x - thetas[i]) / sds[i]); return s / n; };
  const loB = Math.min(...thetas.map((t, i) => t - 6 * sds[i]));
  const hiB = Math.max(...thetas.map((t, i) => t + 6 * sds[i]));
  const invert = p => { let a = loB, b = hiB; for (let it = 0; it < 200; it++) { const m = (a + b) / 2; if (mixCdf(m) < p) a = m; else b = m; } return (a + b) / 2; };
  const wl = { theta: mean, lo: invert(0.025), hi: invert(0.975), within, between, total: within + between };
  wl.sig = (wl.lo > 0 || wl.hi < 0);
  return { ivre, wl, widthRatio: (ivre.hi - ivre.lo) / (wl.hi - wl.lo), n };
}


export { specCollapseAggregates, normalCDF };
