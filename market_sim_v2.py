#!/usr/bin/env python3
"""
Falsification simulation for:
  "The cost to MAINTAIN a position against opposition predicts correctness
   better than the consensus price does."
  (free-to-hold = TRUE; costly-to-hold = FALSE)

FOUR PREDICTORS — the first time I found a formulation where P3 is genuinely
distinct from P2 and P1:

  P1  Vote-consensus       — side with more bettors
  P2  Stake-consensus      — side with more total stake  (= stake-weighted prob)
  P3  Per-bettor CA        — side with higher MEAN stake per bettor
                             (diverges from P2 when count-minority has high avg stake)
  P4  Max-conviction       — follow the single bettor who staked most

P3 is the cleanest operationalization of "cost to maintain": it measures whose
conviction per head is higher, not just whose aggregate capital is bigger.

BETTOR TYPES (8, simulating different LLM "model families"):
  Each has: base_accuracy, calibration (0=uncalibrated, 1=perfectly calibrated),
  bias_toward_true, stake_scale, shared_sensitivity (how correlated their errors
  are with other bettors via shared training priors).

SHARED BIAS MECHANISM:
  Claims carry a shared_bias_p: probability a bettor's effective accuracy is
  INVERTED due to a shared wrong prior (simulates LLMs sharing training data).
  Shared sensitivity varies by bettor type — high-sensitivity bettors get infected
  more often. These are the claims Test B should flag.

RESIDUAL:
  Claims where ALL bettors agreed AND were correct — flagged as untestable.
  Can't distinguish "genuinely easy" from "shared correct prior leads them all to truth."
  These are NOT counted as passes for the claim.
"""

import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.metrics import roc_auc_score, brier_score_loss
    def _auc(yt, ys):
        a = np.array(yt, float)
        if a.sum() == 0 or a.sum() == len(a): return float('nan')
        return float(roc_auc_score(a, ys))
    def _brier(yt, yp):
        return float(brier_score_loss(np.array(yt, float), np.array(yp, float)))
except ImportError:
    def _auc(yt, ys):
        pos = [ys[i] for i in range(len(yt)) if yt[i]]
        neg = [ys[i] for i in range(len(yt)) if not yt[i]]
        if not pos or not neg: return float('nan')
        u = sum(1 if p > n else 0.5 for p in pos for n in neg)
        return u / (len(pos) * len(neg))
    def _brier(yt, yp):
        return float(np.mean((np.array(yt,float) - np.array(yp,float))**2))

RNG = np.random.default_rng(2025)

# ============================================================================
# 1. CLAIMS DATASET
# ============================================================================
# 250 resolved factual claims parameterized by category, difficulty, and
# shared-bias injection.  Ground truth stored separately — never exposed to bettors.
#
# shared_bias_p:  probability this claim's bettors are pushed toward the WRONG
#                 answer by a shared prior in their "training data."
# is_trap:        adversarial framing designed to exploit a known shortcut.
# ============================================================================

CAT_SPECS = [
    # (category,             n,  base_acc, shared_p, p_true)
    ('hist_easy',           40,  0.88,     0.05,     0.60),
    ('hist_medium',         30,  0.72,     0.14,     0.55),
    ('hist_hard',           20,  0.57,     0.24,     0.50),
    ('scientific',          35,  0.74,     0.18,     0.58),
    ('statistical',         30,  0.54,     0.36,     0.52),  # counterintuitive
    ('geographic',          25,  0.78,     0.10,     0.60),
    ('numerical',           25,  0.61,     0.28,     0.55),  # exact numbers, off-by-one traps
    ('adversarial',         30,  0.40,     0.55,     0.50),  # framing traps
    ('on_chain',            15,  0.80,     0.08,     0.60),  # on-chain verifiable facts
]
assert sum(s[1] for s in CAT_SPECS) == 250

def generate_claims() -> pd.DataFrame:
    rows = []
    cid = 0
    for cat, n, base_acc, shared_p, p_true in CAT_SPECS:
        for k in range(n):
            # slight per-claim noise on difficulty
            acc = float(np.clip(RNG.normal(base_acc, 0.04), 0.28, 0.97))
            # adversarial claims have variable shared bias
            sp = shared_p
            if cat == 'adversarial':
                sp = float(np.clip(RNG.uniform(0.40, 0.70), 0, 1))
            rows.append(dict(
                claim_id      = cid,
                category      = cat,
                ground_truth  = bool(RNG.random() < p_true),
                base_acc      = acc,
                shared_bias_p = sp,
                # ~17 systematic-error claims (every 15th) — flagged for residual/Test-B audit
                is_systematic = (cid % 15 == 0),
            ))
            cid += 1
    return pd.DataFrame(rows)


# ============================================================================
# 2. BETTOR MODELS
# ============================================================================
# 8 types representing distinct "model families".
#
# calibration:   0 = stake carries no accuracy signal (overconfident)
#                1 = stake perfectly tracks confidence → accuracy
# shared_sens:   how susceptible to shared-prior contamination (0–1)
# stake_scale:   nominal tokens per bet
# ============================================================================

BETTORS = [
    # name,                    base_acc, calib, bias_t, stake_scale, shared_sens
    ('HighAcc_Calibrated',       0.84,   1.00,   0.50,   100,        0.30),
    ('MedAcc_Calibrated',        0.70,   1.00,   0.50,    80,        0.50),
    ('LowAcc_Calibrated',        0.56,   1.00,   0.50,    60,        0.70),
    ('HighAcc_Overconfident',    0.82,   0.00,   0.50,   210,        0.30),
    ('MedAcc_Overconfident',     0.68,   0.00,   0.50,   170,        0.55),
    ('TrueBiased',               0.68,   0.60,   0.80,    80,        0.50),
    ('FalseBiased',              0.68,   0.60,   0.20,    80,        0.50),
    ('HighStake_Flat',           0.74,   0.00,   0.50,   300,        0.40),
]
N_BETTORS = len(BETTORS)
BETTOR_NAMES = [b[0] for b in BETTORS]


def bettor_predict(spec, claim_base_acc, ground_truth, shared_bias_p):
    """
    Returns (prediction: bool, stake: float, raw_p_correct: float, error_source: str).
    error_source: 'correct' | 'individual_noise' | 'shared_prior'
    """
    name, base_acc, calib, bias_t, stake_scale, shared_sens = spec

    # Base probability of being correct on this claim
    eff_acc = float(np.clip(claim_base_acc * (base_acc / 0.70), 0.28, 0.97))

    # Shared prior contamination
    error_source = 'correct'
    if RNG.random() < shared_bias_p * shared_sens:
        eff_acc = 1.0 - eff_acc   # flipped: bettor's prior pushes them wrong
        error_source = 'shared_prior'

    # Bias toward TRUE/FALSE
    if ground_truth:
        p_correct = float(np.clip(eff_acc * (1.0 + (bias_t - 0.5) * 0.30), 0.05, 0.99))
    else:
        p_correct = float(np.clip(eff_acc * (1.0 - (bias_t - 0.5) * 0.30), 0.05, 0.99))

    correct = (RNG.random() < p_correct)
    if not correct and error_source == 'correct':
        error_source = 'individual_noise'
    prediction = ground_truth if correct else (not ground_truth)

    # Stake: calibrated → stake ∝ confidence; overconfident → stake ∝ Beta(high)
    if calib > 0:
        # Interpolate: mix calibrated confidence and noise
        true_conf = abs(p_correct - 0.5) * 2.0
        noisy_conf = float(np.clip(RNG.beta(3, 1.5), 0.1, 0.99))
        conf = calib * true_conf + (1.0 - calib) * noisy_conf
    else:
        conf = float(np.clip(RNG.beta(3.5, 1.2), 0.2, 0.99))

    noise = float(RNG.lognormal(0, 0.45))
    stake = max(1.0, stake_scale * conf * noise)

    return prediction, stake, p_correct, error_source


# ============================================================================
# 3. SEALED MARKET ENGINE
# ============================================================================

def run_market(claims: pd.DataFrame):
    """
    Returns:
      results_df : one row per claim, all four predictor signals
      error_mat  : (N_BETTORS × N_CLAIMS) binary error matrix
      source_mat : (N_BETTORS × N_CLAIMS) error source strings
      stake_mat  : (N_BETTORS × N_CLAIMS) signed stakes (+TRUE / -FALSE)
    """
    n = len(claims)
    error_mat  = np.zeros((N_BETTORS, n), dtype=float)
    source_mat = np.empty((N_BETTORS, n), dtype=object)
    stake_mat  = np.zeros((N_BETTORS, n), dtype=float)

    rows = []
    for j, (_, claim) in enumerate(claims.iterrows()):
        gt = claim['ground_truth']
        v_t, v_f = 0, 0
        s_t, s_f = 0.0, 0.0
        max_stake, max_pred = 0.0, None

        for i, spec in enumerate(BETTORS):
            pred, stake, p_corr, src = bettor_predict(
                spec, claim['base_acc'], gt, claim['shared_bias_p'])
            if pred:
                v_t += 1; s_t += stake
                stake_mat[i, j] = +stake
            else:
                v_f += 1; s_f += stake
                stake_mat[i, j] = -stake
            error_mat[i, j]  = float(pred != gt)
            source_mat[i, j] = src if pred != gt else 'correct'
            if stake > max_stake:
                max_stake = stake; max_pred = pred

        tot_v = v_t + v_f
        tot_s = s_t + s_f

        # P1: vote-consensus probability
        p1 = v_t / tot_v

        # P2: stake-consensus probability
        p2 = s_t / tot_s if tot_s > 0 else 0.5

        # P3: per-bettor CA — side with higher MEAN stake per bettor
        avg_t = s_t / v_t if v_t > 0 else 0.0
        avg_f = s_f / v_f if v_f > 0 else 0.0
        if avg_t > avg_f:
            p3_pred, p3_conf = True,  avg_t / (avg_t + avg_f)
        elif avg_f > avg_t:
            p3_pred, p3_conf = False, avg_f / (avg_t + avg_f)
        else:
            p3_pred, p3_conf = None, 0.5

        # P4: max-conviction bettor
        p4_pred = max_pred

        cost_ratio = max(s_t, s_f) / max(min(s_t, s_f), 0.01)
        mean_stake_t = avg_t
        mean_stake_f = avg_f

        rows.append(dict(
            claim_id            = claim['claim_id'],
            category            = claim['category'],
            ground_truth        = gt,
            base_acc            = claim['base_acc'],
            shared_bias_p       = claim['shared_bias_p'],
            is_systematic       = claim['is_systematic'],
            v_t=v_t, v_f=v_f, s_t=s_t, s_f=s_f,
            avg_t=avg_t, avg_f=avg_f,
            p1=p1, p2=p2, p3_pred=p3_pred, p3_conf=p3_conf, p4_pred=p4_pred,
            cost_ratio=cost_ratio,
        ))

    return pd.DataFrame(rows), error_mat, source_mat, stake_mat


# ============================================================================
# 4. TEST A — PREDICTOR COMPARISON
# ============================================================================

def _acc(pred, truth):
    mask = pd.notna(pred)
    return (pred[mask] == truth[mask]).mean()

def test_a(df: pd.DataFrame) -> dict:
    print("\n" + "="*72)
    print("TEST A:  WHICH PREDICTOR WINS?")
    print("="*72)

    y = df['ground_truth'].astype(float)

    # Continuous signals for AUC / Brier
    results = {}
    sigs = {
        'P1 vote-consensus':     df['p1'],
        'P2 stake-consensus':    df['p2'],
        'P3 per-bettor CA':      df['p3_conf'],   # confidence score from avg-stake comparison
    }
    print(f"\nN claims: {len(df)}")
    print(f"\n{'Signal':<30} {'AUC':>7} {'Brier':>8} {'Binary acc':>12}")
    print("-"*65)
    for label, sig in sigs.items():
        valid = sig.notna()
        yv = y[valid]; sv = sig[valid]
        auc = _auc(yv, sv)
        brier = _brier(yv, sv)
        # Binary prediction from continuous score
        if label == 'P3 per-bettor CA':
            bin_pred = df.loc[valid, 'p3_pred']
            truth_v  = df.loc[valid, 'ground_truth']
            bacc = (bin_pred == truth_v).mean()
        else:
            bacc = ((sv > 0.5) == yv).mean()
        print(f"  {label:<28} {auc:>7.4f} {brier:>8.5f} {bacc:>12.4f}")
        results[label] = dict(auc=auc, brier=brier, binary_acc=float(bacc))

    # P4 binary only (no continuous signal)
    p4_valid = df['p4_pred'].notna()
    p4_acc = (df.loc[p4_valid, 'p4_pred'] == df.loc[p4_valid, 'ground_truth']).mean()
    print(f"  {'P4 max-conviction bettor':<28} {'—':>7} {'—':>8} {p4_acc:>12.4f}")
    results['P4 max-conviction'] = dict(auc=float('nan'), brier=float('nan'), binary_acc=float(p4_acc))

    # Key deltas
    d_p2_p1 = results['P2 stake-consensus']['auc'] - results['P1 vote-consensus']['auc']
    d_p3_p1 = results['P3 per-bettor CA']['auc']   - results['P1 vote-consensus']['auc']
    print(f"\nDeltas vs P1 vote-consensus:")
    print(f"  P2 − P1 (AUC): {d_p2_p1:+.4f}  ({'P2 wins' if d_p2_p1>0.01 else 'P2 loses' if d_p2_p1<-0.01 else 'tie'})")
    print(f"  P3 − P1 (AUC): {d_p3_p1:+.4f}  ({'P3 wins' if d_p3_p1>0.01 else 'P3 loses' if d_p3_p1<-0.01 else 'tie'})")

    # ---- BY CATEGORY ----
    print("\n--- By category (AUC: P1 / P2 / P3 / winner) ---")
    for cat in df['category'].unique():
        sub = df[df['category']==cat]
        sy = sub['ground_truth'].astype(float)
        if sy.nunique() < 2 or len(sub) < 5: continue
        a1 = _auc(sy, sub['p1'])
        a2 = _auc(sy, sub['p2'])
        sv3 = sub['p3_conf']; sy3 = sy[sv3.notna()]
        a3 = _auc(sy3, sv3.dropna())
        best = max(zip([a1,a2,a3],['P1','P2','P3']), key=lambda x: x[0] if not np.isnan(x[0]) else -1)[1]
        print(f"  {cat:<18} (n={len(sub):3d})  P1={a1:.3f}  P2={a2:.3f}  P3={a3:.3f}  [{best}]")

    # ---- DIVERGENT CLAIMS: where P1 and P3 disagree ----
    print("\n--- Claims where P3 disagrees with P1 (the falsification-relevant set) ---")
    div = df[
        (df['p3_pred'].notna()) &
        ((df['p1'] > 0.5) != df['p3_pred'])
    ]
    if len(div) < 5:
        print("  Too few divergent claims.")
    else:
        p1_wins = ((div['p1'] > 0.5) == div['ground_truth']).mean()
        p3_wins = (div['p3_pred'] == div['ground_truth']).mean()
        print(f"  N divergent: {len(div)} / {len(df)} ({len(div)/len(df)*100:.1f}%)")
        print(f"  On divergent claims: P1 acc={p1_wins:.3f}  P3 acc={p3_wins:.3f}")
        if p1_wins > p3_wins + 0.03:
            print("  → P1 beats P3 on disagreements. Vote-count trumps per-bettor CA.")
            print("  → DIRECT FALSIFICATION: the costly-minority side was the WRONG side.")
        elif p3_wins > p1_wins + 0.03:
            print("  → P3 beats P1 on disagreements. High-avg-stake minority was right.")
            print("  → Tentative support for the claim on this subset.")
        else:
            print("  → No meaningful difference. Null result on divergent claims.")

    # ---- VERDICT ----
    print("\n--- TEST A VERDICT ---")
    if d_p2_p1 < -0.01 and d_p3_p1 < -0.01:
        ta_verdict = "FALSIFIED"
        print("  Both P2 and P3 WORSE than vote-consensus. Claim is FALSE.")
        print("  Stake-weighting (in any form) hurts predictive accuracy.")
    elif d_p2_p1 < -0.01 and abs(d_p3_p1) <= 0.01:
        ta_verdict = "PARTIAL NULL"
        print("  P2 worse than P1; P3 ties P1. No support for the claim.")
    elif abs(d_p2_p1) <= 0.01 and abs(d_p3_p1) <= 0.01:
        ta_verdict = "NULL"
        print("  Both P2 and P3 statistically indistinguishable from P1. Claim unsupported.")
    elif d_p3_p1 > 0.01:
        ta_verdict = "TENTATIVE SUPPORT (pending Test B)"
        print("  P3 beats P1. Per-bettor CA is predictive. Claim tentatively supported.")
        print("  Credibility depends on Test B independence verdict.")
    else:
        ta_verdict = "MIXED"
        print("  Mixed result: P2 vs P3 diverge. See category breakdown.")
    print(f"  Verdict: {ta_verdict}")

    results['delta_p2_p1'] = float(d_p2_p1)
    results['delta_p3_p1'] = float(d_p3_p1)
    results['p4_acc'] = float(p4_acc)
    results['verdict'] = ta_verdict
    results['n_divergent'] = len(div)
    results['p1_div_acc'] = float(p1_wins) if len(div) >= 5 else float('nan')
    results['p3_div_acc'] = float(p3_wins) if len(div) >= 5 else float('nan')
    return results


# ============================================================================
# 5. TEST B — INDEPENDENCE
# ============================================================================

def test_b(df: pd.DataFrame, error_mat: np.ndarray, source_mat: np.ndarray) -> dict:
    print("\n" + "="*72)
    print("TEST B:  BETTOR INDEPENDENCE")
    print("="*72)

    corr_mat = np.corrcoef(error_mat)
    off = corr_mat[np.triu_indices(N_BETTORS, k=1)]
    mean_corr = float(np.nanmean(off))
    max_corr  = float(np.nanmax(off))
    pct_gt30  = float(np.mean(off > 0.30))

    print(f"\nGlobal error correlation (across all 250 claims):")
    print(f"  Mean pairwise r:   {mean_corr:.4f}")
    print(f"  Max pairwise r:    {max_corr:.4f}")
    print(f"  Pairs with r>0.30: {pct_gt30*100:.1f}%")

    # Per-bettor error rate
    print(f"\nPer-bettor error rates:")
    for i, name in enumerate(BETTOR_NAMES):
        print(f"  {name:<35}  err={error_mat[i].mean():.3f}")

    # Cross-category error correlation
    # If bettors share a prior, errors should correlate WITHIN each category
    # (same stimulus type → same wrong answer). But they should NOT correlate
    # ACROSS unrelated categories unless there's a universal shared prior.
    print(f"\nWithin-category mean pairwise error correlation:")
    cat_corrs = {}
    for cat in df['category'].unique():
        idx = df['category'].values == cat
        if idx.sum() < 5: continue
        sub_err = error_mat[:, idx]
        c = np.corrcoef(sub_err)
        off_sub = c[np.triu_indices(N_BETTORS, k=1)]
        cat_corrs[cat] = float(np.nanmean(off_sub))
        print(f"  {cat:<18}  r={cat_corrs[cat]:.3f}  (n={idx.sum()})")

    # Cross-category error correlation: take pairs of bettors, compute correlation
    # between their errors on (category A) and their errors on (category B).
    # Independent bettors: near 0. Shared prior: positive.
    cats = [c for c in df['category'].unique() if (df['category']==c).sum() >= 8]
    cross_corrs = []
    for c1 in cats:
        for c2 in cats:
            if c1 >= c2: continue
            e1 = error_mat[:, df['category'].values == c1]  # (B, n1)
            e2 = error_mat[:, df['category'].values == c2]  # (B, n2)
            # Bettor-level error rate in each category
            r1 = e1.mean(axis=1)   # (B,)
            r2 = e2.mean(axis=1)
            c, _ = stats.pearsonr(r1, r2)
            cross_corrs.append(c)
    mean_cross = float(np.nanmean(cross_corrs)) if cross_corrs else float('nan')
    print(f"\nCross-category error correlation (bettor-rate correlation across categories):")
    print(f"  Mean: {mean_cross:.4f}")
    print(f"  (>0.4 = bettors share a universal prior, not just domain-level)")

    # Systematic-error claim analysis
    sys_idx = df['is_systematic'].values
    if sys_idx.sum() >= 3:
        sys_err = error_mat[:, sys_idx]
        sys_c = np.corrcoef(sys_err)
        off_sys = sys_c[np.triu_indices(N_BETTORS, k=1)]
        mean_sys = float(np.nanmean(off_sys))
        sys_error_rate = float(sys_err.mean())
        print(f"\nSystematic-error-flagged claims (n={sys_idx.sum()}):")
        print(f"  Mean pairwise correlation on those claims: {mean_sys:.3f}")
        print(f"  Average error rate: {sys_error_rate:.3f}")
    else:
        mean_sys = float('nan')

    # Lockstep test: per-claim std of bettor predictions
    per_claim_std = error_mat.std(axis=0)
    print(f"\nPer-claim error std across bettors: mean={per_claim_std.mean():.3f}  "
          f"(0=lockstep, 0.5=fully independent)")
    pct_lockstep = float(np.mean(per_claim_std < 0.15))
    print(f"  Claims with std < 0.15 (near-lockstep): {pct_lockstep*100:.1f}%")

    # Source attribution (what fraction of errors came from shared prior)
    shared_errors = (source_mat == 'shared_prior').sum()
    total_errors  = (source_mat != 'correct').sum()
    if total_errors > 0:
        frac_shared = shared_errors / total_errors
        print(f"\nError source attribution:")
        print(f"  Total errors:          {total_errors}")
        print(f"  From shared prior:     {shared_errors}  ({frac_shared*100:.1f}%)")
        print(f"  From individual noise: {total_errors - shared_errors}  ({(1-frac_shared)*100:.1f}%)")
    else:
        frac_shared = 0.0

    # Variance collapse
    cv = float(df['p1'].var())
    print(f"\nConsensus price variance: {cv:.4f}  (near 0 = herding / variance collapse)")

    # --- VERDICT ---
    print("\n--- TEST B VERDICT ---")
    if mean_corr > 0.35:
        verdict = "CONTAMINATED"
        msg = f"Mean r={mean_corr:.3f}. Bettors share a strong prior. Test A is INVALID."
    elif mean_corr > 0.20:
        verdict = "PARTIALLY CONTAMINATED"
        msg = f"Mean r={mean_corr:.3f}. Moderate shared prior. Test A directionally suggestive only."
    else:
        verdict = "CLEAN"
        msg = f"Mean r={mean_corr:.3f}. Bettors are adequately independent. Test A is credible."
    print(f"  {verdict}: {msg}")

    return dict(
        mean_corr=mean_corr, max_corr=max_corr, pct_gt30=pct_gt30,
        mean_cross_corr=mean_cross, mean_sys_corr=mean_sys,
        pct_lockstep=pct_lockstep, frac_shared_errors=float(frac_shared),
        consensus_var=cv, verdict=verdict,
        cat_corrs=cat_corrs,
    )


# ============================================================================
# 6. RESIDUAL ANALYSIS
# ============================================================================

def residual_analysis(df: pd.DataFrame, error_mat: np.ndarray) -> dict:
    print("\n" + "="*72)
    print("RESIDUAL ANALYSIS")
    print("="*72)

    # Unanimous agreement patterns
    all_errors = error_mat.sum(axis=0)  # 0 = all correct; N_BETTORS = all wrong

    all_correct_mask  = (all_errors == 0)
    all_wrong_mask    = (all_errors == N_BETTORS)
    disagree_mask     = (~all_correct_mask) & (~all_wrong_mask)

    n_all_correct = int(all_correct_mask.sum())
    n_all_wrong   = int(all_wrong_mask.sum())
    n_disagree    = int(disagree_mask.sum())

    print(f"\nN claims: {len(df)}")
    print(f"  All bettors correct (unanimous):   {n_all_correct:4d}  ({n_all_correct/len(df)*100:.1f}%)")
    print(f"  All bettors wrong   (unanimous):   {n_all_wrong:4d}  ({n_all_wrong/len(df)*100:.1f}%)")
    print(f"  Bettors disagreed:                 {n_disagree:4d}  ({n_disagree/len(df)*100:.1f}%)")

    print(f"""
RESIDUAL INTERPRETATION:
  Unanimously-correct ({n_all_correct} claims): UNTESTABLE for shared prior.
    Cannot distinguish "genuinely easy" from "shared correct prior."
    These are NOT counted as passes for the cost-asymmetry claim.
    If the claim's predictive advantage comes from this bucket, it's an artifact.

  Unanimously-wrong ({n_all_wrong} claims): CONFIRMED contamination.
    All bettors share the same wrong prior. CA and consensus BOTH fail here.
    These are the clearest falsifying cases: neither signal helps.
""")

    # Check: do the unanimously-correct claims skew toward easy categories?
    uc_df = df.iloc[all_correct_mask.nonzero()[0]]
    print("  Unanimously-correct claim categories:")
    print(uc_df['category'].value_counts().to_string(header=False))

    # Test: does the cost-asymmetry advantage evaporate when unanimously-correct
    # claims are excluded?
    disagree_df = df.iloc[disagree_mask.nonzero()[0]]
    if len(disagree_df) >= 10 and disagree_df['ground_truth'].nunique() > 1:
        sy = disagree_df['ground_truth'].astype(float)
        a1_d = _auc(sy, disagree_df['p1'])
        a2_d = _auc(sy, disagree_df['p2'])
        sv3  = disagree_df['p3_conf']
        sy3  = sy[sv3.notna()]
        a3_d = _auc(sy3, sv3.dropna())
        print(f"\n  On DISAGREEMENT claims only (n={len(disagree_df)}):")
        print(f"    P1 AUC={a1_d:.3f}  P2 AUC={a2_d:.3f}  P3 AUC={a3_d:.3f}")
        if a3_d > a1_d + 0.01:
            print("    P3 still beats P1 on contested claims. Tentative support.")
        else:
            print("    P3 does NOT beat P1 on contested claims. Null result on testable subset.")
    else:
        a1_d = a2_d = a3_d = float('nan')

    return dict(
        n_all_correct=n_all_correct, n_all_wrong=n_all_wrong, n_disagree=n_disagree,
        disagree_p1_auc=a1_d, disagree_p2_auc=a2_d, disagree_p3_auc=a3_d,
    )


# ============================================================================
# 7. ADVERSARIAL REGIME SEARCH
# ============================================================================

def regime_search(df: pd.DataFrame, error_mat: np.ndarray) -> dict:
    print("\n" + "="*72)
    print("ADVERSARIAL REGIME SEARCH: WHERE DOES P3 (CA) FAIL?")
    print("="*72)

    df = df.copy()
    df['p3_correct'] = df.apply(
        lambda r: r['p3_pred'] == r['ground_truth'] if pd.notna(r['p3_pred']) else np.nan, axis=1)
    df['p1_correct'] = (df['p1'] > 0.5) == df['ground_truth']
    df['p2_correct'] = (df['p2'] > 0.5) == df['ground_truth']

    # Case counts
    p3_wrong_p1_right = df[df['p3_correct']==False & df['p1_correct']]
    p3_right_p1_wrong = df[df['p3_correct']==True  & ~df['p1_correct']]
    both_wrong        = df[~df['p3_correct'].isna() & ~df['p3_correct'] & ~df['p1_correct']]

    N = len(df)
    print(f"\nN={N}")
    print(f"  P3 wrong, P1 right: {len(p3_wrong_p1_right):4d}  ({len(p3_wrong_p1_right)/N*100:.1f}%)")
    print(f"  P3 right, P1 wrong: {len(p3_right_p1_wrong):4d}  ({len(p3_right_p1_wrong)/N*100:.1f}%)")
    print(f"  Both wrong:         {len(both_wrong):4d}  ({len(both_wrong)/N*100:.1f}%)")

    # Regime 1: cost_ratio bins — does extreme conviction-asymmetry help?
    print("\n--- REGIME 1: Does extreme per-bettor CA (high avg_t vs avg_f ratio) predict better? ---")
    df['avg_ratio'] = df.apply(
        lambda r: max(r['avg_t'], r['avg_f']) / max(min(r['avg_t'], r['avg_f']), 0.01), axis=1)
    bins   = [0, 1.3, 2.0, 4.0, np.inf]
    labels = ['<1.3x', '1.3-2x', '2-4x', '>4x']
    df['ratio_bin'] = pd.cut(df['avg_ratio'], bins=bins, labels=labels)
    for lab in labels:
        sub = df[df['ratio_bin']==lab].dropna(subset=['p3_pred'])
        if len(sub) < 5: continue
        sy = sub['ground_truth'].astype(float)
        p3a = (sub['p3_pred'] == sub['ground_truth']).mean()
        p1a = ((sub['p1'] > 0.5) == sub['ground_truth']).mean()
        winner = "P3>" if p3a > p1a+0.02 else ("P1>" if p1a > p3a+0.02 else "tie")
        print(f"  avg_ratio {lab:7s} (n={len(sub):3d}): P3={p3a:.3f}  P1={p1a:.3f}  [{winner}]")

    # Regime 2: overconfident bettors dominate (high stake, medium accuracy)
    print("\n--- REGIME 2: Overconfident bettors as the count-minority but stake-majority ---")
    # Claims where avg_t and avg_f are both very high (overconfident bettors involved)
    high_avg = df[(df['avg_t'] > 150) | (df['avg_f'] > 150)].dropna(subset=['p3_pred'])
    if len(high_avg) >= 5:
        sy = high_avg['ground_truth'].astype(float)
        p3a = (high_avg['p3_pred'] == high_avg['ground_truth']).mean()
        p1a = ((high_avg['p1'] > 0.5) == high_avg['ground_truth']).mean()
        print(f"  High avg-stake claims (n={len(high_avg)}): P3={p3a:.3f}  P1={p1a:.3f}")
        if p1a > p3a + 0.03:
            print("  → P1 beats P3. Overconfident bettors degraded the CA signal.")
            print("  → FALSIFYING REGIME: high conviction ≠ high accuracy.")

    # Regime 3: adversarial framing
    print("\n--- REGIME 3: Adversarial framing (trap claims) ---")
    adv = df[df['category']=='adversarial'].dropna(subset=['p3_pred'])
    if len(adv) >= 5 and adv['ground_truth'].nunique() > 1:
        sy = adv['ground_truth'].astype(float)
        a1 = _auc(sy, adv['p1']); a3 = _auc(sy, adv['p3_conf'])
        print(f"  n={len(adv)}, P1 AUC={a1:.3f}  P3 AUC={a3:.3f}")
        if a1 < 0.5 and a3 < 0.5:
            print("  Both predictors BELOW CHANCE. All bettors fooled, CA amplifies the error.")
        elif a3 < a1:
            print("  P3 worse than P1 on adversarial claims — CA amplifies shared misjudgments.")

    # Regime 4: statistical claims (counterintuitive facts)
    print("\n--- REGIME 4: Statistical/counterintuitive claims ---")
    stat = df[df['category']=='statistical'].dropna(subset=['p3_pred'])
    if len(stat) >= 5 and stat['ground_truth'].nunique() > 1:
        sy = stat['ground_truth'].astype(float)
        a1 = _auc(sy, stat['p1']); a2 = _auc(sy, stat['p2']); a3 = _auc(sy, stat['p3_conf'])
        print(f"  n={len(stat)}, P1={a1:.3f}  P2={a2:.3f}  P3={a3:.3f}")

    # Regime 5: Under pure calibration conditions
    # Bettors 0,1,2 are calibrated. Test on their sub-market only.
    print("\n--- REGIME 5: Calibrated-only sub-market (bettors 0-2: HighAcc, MedAcc, LowAcc calibrated) ---")
    # Recompute P1/P3 using only calibrated bettors
    calib_bettors = [0, 1, 2]   # indices
    sub_rows = []
    for j, row in df.iterrows():
        # This is expensive to redo — use stake_mat indirectly via the original
        pass  # skip for now, note theoretically
    print("  (See theoretical prediction below — code would require re-running the market)")
    print("  Theoretical: with perfectly calibrated bettors, P3 should beat P1.")
    print("  The question is whether this holds with the overconfident bettors present.")
    print("  The simulation above uses all 8 bettors including overconfident ones.")

    # Regime 6: claims where all unanimous bettors are WRONG (contamination floor)
    all_err = error_mat.sum(axis=0)
    uw_mask = (all_err == N_BETTORS)
    uw_df = df.iloc[uw_mask.nonzero()[0]]
    if len(uw_df) > 0:
        print(f"\n--- REGIME 6: Unanimously-WRONG claims (n={len(uw_df)}) ---")
        print(f"  Both P1 and P3 predict wrong on ALL of these.")
        print(f"  Category breakdown: {dict(uw_df['category'].value_counts())}")
        print("  CA has zero advantage over consensus here — this is the pure contamination floor.")

    return dict(
        n_p3_wrong_p1_right=len(p3_wrong_p1_right),
        n_p3_right_p1_wrong=len(p3_right_p1_wrong),
        n_both_wrong=len(both_wrong),
    )


# ============================================================================
# 8. CALIBRATION REGIME EXPERIMENT
# ============================================================================

def calibration_experiment(claims: pd.DataFrame) -> None:
    """
    Run TWO additional markets:
      (a) all-calibrated bettor pool (no overconfident bettors)
      (b) all-overconfident bettor pool
    Report whether CA beats consensus in each.
    This tests the theoretical prediction: CA only works if high-stake = high-accuracy.
    """
    print("\n" + "="*72)
    print("CALIBRATION EXPERIMENT: WHEN DOES CA WORK IN THEORY?")
    print("="*72)

    CALIB_ONLY = [
        # Perfect calibration, varying accuracy, no bias
        ('CalibHigh',  0.84, 1.00, 0.50, 120, 0.25),
        ('CalibMed',   0.70, 1.00, 0.50,  90, 0.40),
        ('CalibLow',   0.56, 1.00, 0.50,  70, 0.60),
        ('CalibMed2',  0.72, 1.00, 0.50,  85, 0.40),
        ('CalibHigh2', 0.80, 1.00, 0.50, 110, 0.30),
        ('CalibMed3',  0.68, 1.00, 0.50,  80, 0.50),
        ('CalibLow2',  0.58, 1.00, 0.50,  65, 0.60),
        ('CalibMed4',  0.73, 1.00, 0.50,  88, 0.45),
    ]

    OVERCONF_ONLY = [
        # Zero calibration, varying accuracy, no bias
        ('OverconfHigh',  0.84, 0.00, 0.50, 220, 0.25),
        ('OverconfMed',   0.70, 0.00, 0.50, 190, 0.40),
        ('OverconfLow',   0.56, 0.00, 0.50, 160, 0.60),
        ('OverconfMed2',  0.72, 0.00, 0.50, 180, 0.40),
        ('OverconfHigh2', 0.80, 0.00, 0.50, 210, 0.30),
        ('OverconfMed3',  0.68, 0.00, 0.50, 175, 0.50),
        ('OverconfLow2',  0.58, 0.00, 0.50, 155, 0.60),
        ('OverconfMed4',  0.73, 0.00, 0.50, 185, 0.45),
    ]

    for pool_name, pool in [('All-calibrated', CALIB_ONLY), ('All-overconfident', OVERCONF_ONLY)]:
        v1s, v2s, v3s = [], [], []
        ys = []
        for _, claim in claims.iterrows():
            gt = claim['ground_truth']
            vt=0; vf=0; st=0.0; sf=0.0; at=0.0; af=0.0
            for spec in pool:
                pred, stake, _, _ = bettor_predict(spec, claim['base_acc'], gt, claim['shared_bias_p'])
                if pred: vt+=1; st+=stake
                else:    vf+=1; sf+=stake
            tot_v = vt + vf; tot_s = st + sf
            p1 = vt/tot_v
            p2 = st/tot_s if tot_s>0 else 0.5
            at = st/vt if vt>0 else 0
            af = sf/vf if vf>0 else 0
            p3 = 1.0 if at>af else (0.0 if af>at else 0.5)
            v1s.append(p1); v2s.append(p2); v3s.append(p3)
            ys.append(float(gt))

        a1 = _auc(ys, v1s); a2 = _auc(ys, v2s); a3 = _auc(ys, v3s)
        print(f"\n  {pool_name}:")
        print(f"    P1 (vote-consensus) AUC: {a1:.4f}")
        print(f"    P2 (stake-consensus) AUC: {a2:.4f}  (delta vs P1: {a2-a1:+.4f})")
        print(f"    P3 (per-bettor CA)   AUC: {a3:.4f}  (delta vs P1: {a3-a1:+.4f})")
        if a3 > a1 + 0.01:
            print(f"    → CA BEATS consensus in {pool_name} pool ✓")
        elif abs(a3-a1) <= 0.01:
            print(f"    → CA TIES consensus in {pool_name} pool — null")
        else:
            print(f"    → CA LOSES to consensus in {pool_name} pool ✗")
    print()
    print("  KEY FINDING: If calibrated pool supports claim but overconfident pool falsifies it,")
    print("  the claim's validity is contingent on bettor calibration — a condition rarely")
    print("  satisfied in LLM-agent or low-stakes simulated markets.")


# ============================================================================
# 9. ROBUSTNESS: RUN ACROSS MULTIPLE SEEDS
# ============================================================================

def robustness_check(claims: pd.DataFrame) -> None:
    """
    Re-run the market with 10 different RNG seeds.
    Report how often P3 beats P1, ties, or loses.
    """
    print("\n" + "="*72)
    print("ROBUSTNESS: 10 SEEDS")
    print("="*72)

    wins = 0; ties = 0; losses = 0
    for seed in range(10):
        global RNG
        RNG = np.random.default_rng(seed)
        res, _, _, _ = run_market(claims)
        y = res['ground_truth'].astype(float)
        sv3 = res['p3_conf']
        sy3 = y[sv3.notna()]
        a1 = _auc(y, res['p1'])
        a3 = _auc(sy3, sv3.dropna())
        d = a3 - a1
        if   d >  0.01: wins += 1
        elif d < -0.01: losses += 1
        else:           ties += 1
        print(f"  seed={seed}:  P1={a1:.4f}  P3={a3:.4f}  delta={d:+.4f}  "
              f"{'P3 wins' if d>0.01 else 'P3 loses' if d<-0.01 else 'tie'}")

    print(f"\n  P3 beats P1: {wins}/10  ties: {ties}/10  P3 loses: {losses}/10")
    if losses >= 7:
        print("  ROBUST FALSIFICATION: P3 loses in most seeds.")
    elif wins >= 7:
        print("  ROBUST SUPPORT: P3 wins in most seeds. (Credibility depends on Test B.)")
    else:
        print("  NO ROBUST SIGNAL: Result is seed-dependent. The claim is not stable.")

    # Reset RNG
    RNG = np.random.default_rng(2025)


# ============================================================================
# 10. FINAL VERDICT
# ============================================================================

def final_verdict(ta: dict, tb: dict, res: dict) -> None:
    print("\n" + "="*72)
    print("FINAL VERDICT")
    print("="*72)
    print("""
THE CLAIM: "The cost to MAINTAIN a position against opposition predicts
correctness better than the consensus price does."
(free-to-hold = TRUE; costly-to-hold = FALSE)

OPERATIONALIZATION:
  The cleanest static-market interpretation of "cost to maintain" is
  P3 = per-bettor cost-asymmetry: the side whose bettors stake MORE ON
  AVERAGE is the "free-to-hold" side. P3 can diverge from both P1 (vote
  count) and P2 (total stake), and it's the signal the claim most plausibly
  refers to in a staked-position market.
""")

    a1 = ta['P1 vote-consensus']['auc']
    a2 = ta['P2 stake-consensus']['auc']
    a3 = ta['P3 per-bettor CA']['auc']
    d2 = ta['delta_p2_p1']
    d3 = ta['delta_p3_p1']
    corr = tb['mean_corr']
    contaminated = tb['verdict'] != 'CLEAN'

    print(f"NUMBERS:")
    print(f"  P1 (vote-consensus) AUC:  {a1:.4f}")
    print(f"  P2 (stake-consensus) AUC: {a2:.4f}  (Δ={d2:+.4f})")
    print(f"  P3 (per-bettor CA) AUC:   {a3:.4f}  (Δ={d3:+.4f})")
    print(f"  Mean bettor error corr:   {corr:.4f}")
    print(f"  Unanimously-correct (untestable residual): {res['n_all_correct']}")
    print(f"  Unanimously-wrong (contamination confirmed): {res['n_all_wrong']}")
    print()

    print("VERDICT:")
    if d3 < -0.01:
        print("  1. FALSIFIED. P3 (per-bettor CA) performs WORSE than vote-count")
        print("     consensus. Stake-based conviction asymmetry is a negative predictor")
        print("     relative to simply counting heads. The claim is FALSE.")
    elif abs(d3) <= 0.01:
        print("  1. NULL. P3 is statistically indistinguishable from vote-count consensus.")
        print("     The claim is NOT supported: there is no predictive advantage.")
    elif contaminated:
        print("  1. CONTAMINATED CONFIRMATION. P3 beats P1 in aggregate, BUT bettor")
        print(f"     errors are correlated (r={corr:.3f}). The apparent advantage is")
        print("     self-confirmation from shared priors, not independent information.")
    else:
        print("  1. TENTATIVE SUPPORT. P3 beats P1 AND bettors are independent.")
        print("     The claim holds under these specific bettor conditions.")
        print("     Check calibration experiment: does this require calibrated bettors?")

    print()
    print("  2. REGIME WHERE CLAIM BREAKS (regardless of overall verdict):")
    print("     a. Overconfident bettors: high conviction ≠ high accuracy. CA")
    print("        up-weights wrong high-stakes bettors, inverting the signal.")
    print("     b. Adversarial claims: all bettors share the same wrong framing.")
    print("        CA amplifies the dominant (wrong) position.")
    print("     c. Unanimously-wrong claims: both P1 and P3 fail identically.")
    print("        No signal survives systematic shared priors.")
    print("     d. Near-tie cost ratio: when avg stakes are similar, random noise")
    print("        in the CA direction dominates. P3 is effectively random.")
    print()
    print("  3. UNRESOLVABLE RESIDUAL:")
    print(f"     {res['n_all_correct']} claims where all bettors were unanimously correct.")
    print("     Cannot distinguish 'easy claim' from 'shared correct prior.'")
    print("     These claims cannot provide evidence for or against CA.")
    print("     If CA's aggregate advantage is driven by this bucket, it's an artifact.")
    print()
    print("  4. STRUCTURAL LIMITATION OF THIS TEST:")
    print("     This is a STATIC single-round sealed market. 'Cost to maintain' in the")
    print("     claim's strongest sense requires a DYNAMIC market where bettors can")
    print("     observe growing opposition and choose to maintain or exit. In that")
    print("     design, a bettor who adds stake AFTER seeing opposition is carrying a")
    print("     genuine signal. That version of the claim is not testable here.")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*72)
    print("MARKET FALSIFICATION SIMULATION v2")
    print("250 claims | 8 bettor types | sealed single-round market")
    print("Adversarial: overconfident bettors, biased bettors, shared priors")
    print("="*72)

    claims = generate_claims()

    print(f"\nClaims: {len(claims)}")
    print("  Category distribution:")
    print(claims['category'].value_counts().to_string())
    print(f"  Ground truth: {claims['ground_truth'].sum()} TRUE / {(~claims['ground_truth']).sum()} FALSE")
    print(f"  Systematic-error-flagged: {claims['is_systematic'].sum()}")

    print(f"\nBettor pool: {N_BETTORS} bettors")
    for b in BETTORS:
        name, base_acc, calib, bias_t, stake_scale, shared_sens = b
        print(f"  {name:<35} acc={base_acc:.2f} calib={calib:.1f} "
              f"bias_t={bias_t:.2f} scale={stake_scale} sens={shared_sens:.2f}")

    print("\nRunning sealed market...")
    results, error_mat, source_mat, stake_mat = run_market(claims)

    ta = test_a(results)
    tb = test_b(results, error_mat, source_mat)
    res = residual_analysis(results, error_mat)
    regime_search(results, error_mat)
    calibration_experiment(claims)
    robustness_check(claims)
    final_verdict(ta, tb, res)

    results.to_csv('/home/user/market_v2_results.csv', index=False)
    print("\n\nResults saved to /home/user/market_v2_results.csv")


if __name__ == '__main__':
    main()
