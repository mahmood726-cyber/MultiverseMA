// node --test truth-recovery/test-truth-recovery.mjs
// Measured invariants for the MultiverseMA spec-collapse yardstick. Seeded; no
// hand-entered numbers.
import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { generate, makeRng } from './dgp-mv.mjs';
import { runCell } from './harness.mjs';

describe('multiverse DGP', () => {
  it('is reproducible for a fixed seed', () => {
    const a = generate(0, 40, 0.1, makeRng(7));
    const b = generate(0, 40, 0.1, makeRng(7));
    assert.deepEqual(a.specs, b.specs);
  });
});

describe('Truth-recovery (measured)', () => {
  it('naive IV-RE pooling manufactures false robustness under the null (spec-collapse)', () => {
    const r = runCell(0.0, 40, 0.20, 3000, makeRng(20260613));
    assert.ok(r.ivreRobust > 0.35,
      `naive IV-RE false-robustness ${r.ivreRobust} not inflated (spec-collapse not reproduced)`);
  });

  it('the shipped weighted-likelihood (mixture-prediction) interval has ZERO power -- it calls every multiverse fragile', () => {
    const rNull = runCell(0.0, 40, 0.10, 3000, makeRng(1));
    const rEff = runCell(0.15, 40, 0.10, 3000, makeRng(2));
    assert.ok(rNull.wlRobust < 0.01, `WL null robustness ${rNull.wlRobust}`);
    assert.ok(rEff.wlRobust < 0.05, `WL power under a true effect ${rEff.wlRobust} -- should be ~0 (over-conservative)`);
  });

  it('the proposed mean-CI (mean +/- z*sqrt(total/n)) controls false-robustness AND keeps power', () => {
    const rNull = runCell(0.0, 40, 0.20, 3000, makeRng(3));
    const rEff = runCell(0.15, 40, 0.20, 3000, makeRng(4));
    assert.ok(rNull.meanRobust <= 0.06, `proposed false-robustness ${rNull.meanRobust} not controlled`);
    assert.ok(rEff.meanRobust > 0.9, `proposed power ${rEff.meanRobust} too low`);
    // and it is dramatically better calibrated than naive under the null
    assert.ok(rNull.meanRobust < rNull.ivreRobust - 0.3,
      `proposed ${rNull.meanRobust} not much better than naive ${rNull.ivreRobust}`);
  });
});
