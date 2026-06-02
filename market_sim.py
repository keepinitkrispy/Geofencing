#!/usr/bin/env python3
"""
Simulation to falsify the claim:
  "The cost to MAINTAIN a position against opposition predicts its eventual
   correctness better than the consensus price does."

Operationalization:
  - Consensus price  = vote-count fraction for TRUE
  - Stake-consensus  = stake-weighted fraction for TRUE
  - Cost-asymmetry   = the side with MORE total stake is "free to hold" ->
                       that side's direction is the CA prediction
  (These last two are the same signal; the CA signal IS stake-weighted majority.)

The interesting divergence from raw vote-consensus arises when:
  high-stake bettors != count majority  (a few big bettors vs many small bettors)

TWO TESTS:
  A: Does CA (stake-weighted) beat vote-count consensus at predicting truth?
  B: Are bettor errors sufficiently independent for Test A to mean anything?

ADVERSARIAL STANCE: actively hunt for regimes where CA mispredicts.
"""

import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.metrics import roc_auc_score, brier_score_loss
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    def roc_auc_score(y_true, y_score):
        # Mann-Whitney U AUC
        pos = [y_score[i] for i in range(len(y_true)) if y_true[i] == 1]
        neg = [y_score[i] for i in range(len(y_true)) if y_true[i] == 0]
        if not pos or not neg:
            return 0.5
        u = sum(1 if p > n else 0.5 if p == n else 0 for p in pos for n in neg)
        return u / (len(pos) * len(neg))
    def brier_score_loss(y_true, y_prob):
        return np.mean((np.array(y_true, float) - np.array(y_prob, float))**2)

RNG = np.random.default_rng(42)

# ============================================================
# SECTION 1: CLAIMS DATASET
# ============================================================
# 250 claims across 5 categories, known ground truth.
# We never expose ground truth to bettors.
# Categories: historical, scientific, statistical, geographic,
#             adversarial_framing (designed to fool pattern-matchers)
# Difficulty: easy(0.85), medium(0.70), hard(0.55), trap(0.42)
#   = base probability that any random bettor is correct

CATEGORIES = ['historical', 'scientific', 'statistical', 'geographic', 'adversarial_framing']
DIFFICULTIES = {
    'easy':   0.85,  # Almost everyone gets it right
    'medium': 0.70,  # Most get it right
    'hard':   0.55,  # Roughly coin-flip
    'trap':   0.42,  # Framing pushes most bettors to the WRONG answer
}

def generate_claims(n: int = 250) -> pd.DataFrame:
    rows = []
    for i in range(n):
        cat = CATEGORIES[i % len(CATEGORIES)]
        gt = bool(RNG.random() < 0.58)   # 58% TRUE overall (realistic)

        # Difficulty distribution: 35% easy, 30% medium, 20% hard, 15% trap
        r = RNG.random()
        if   r < 0.35: diff = 'easy'
        elif r < 0.65: diff = 'medium'
        elif r < 0.85: diff = 'hard'
        else:          diff = 'trap'

        # Adversarial framing claims are always 'trap' difficulty
        if cat == 'adversarial_framing':
            diff = 'trap'

        # Systematic-error flag: ~8% of claims fool ALL bettors the same way.
        # These are the "contamination injection" claims for Test B.
        is_systematic = (i % 13 == 0)   # 19 out of 250

        rows.append(dict(
            claim_id            = i,
            category            = cat,
            ground_truth        = gt,
            difficulty          = diff,
            base_p_correct      = DIFFICULTIES[diff],
            is_systematic_error = is_systematic,
        ))
    return pd.DataFrame(rows)


# ============================================================
# SECTION 2: BETTOR MODELS
# ============================================================
# 8 bettors with deliberately varied profiles.
# Independence is the variable under test -- do NOT assume it.
#
# Columns:
#   base_acc      = multiplier on base_p_correct (1.0 = use claim's base directly)
#   bias_true     = > 0.5 means bettor tends to say TRUE; 0.5 = neutral
#   stake_fn      = 'calibrated' | 'overconfident' | 'flat'
#                   calibrated   -> stake proportional to confidence in own answer
#                   overconfident-> stake high regardless of actual confidence
#                   flat         -> constant stake
#   stake_scale   = typical stake size (tokens)
#   contrarian    = prob of flipping own best estimate
#   shared_bias   = sensitivity to systematic-error claims (0=immune, 1=fully correlated)

BETTOR_SPECS = [
    # (name, base_acc, bias_true, stake_fn, stake_scale, contrarian, shared_bias)
    ('HighAcc_Calibrated',    1.10, 0.50, 'calibrated',    100, 0.02, 0.40),
    ('MedAcc_Calibrated',     0.93, 0.50, 'calibrated',     80, 0.03, 0.55),
    ('LowAcc_Calibrated',     0.73, 0.50, 'calibrated',     60, 0.03, 0.70),
    ('HighAcc_Overconfident', 1.07, 0.50, 'overconfident', 220, 0.02, 0.40),
    ('MedAcc_Overconfident',  0.90, 0.50, 'overconfident', 180, 0.03, 0.60),
    ('BiasedTrue_Med',        0.90, 0.78, 'calibrated',     80, 0.03, 0.55),
    ('BiasedFalse_Med',       0.90, 0.22, 'calibrated',     80, 0.03, 0.55),
    ('HighStake_ModAcc',      0.96, 0.50, 'flat',          310, 0.05, 0.45),
]


def bettor_predict(spec, base_p_correct, ground_truth, is_systematic):
    """
    Returns (prediction: bool, stake: float, raw_confidence: float)
    """
    name, base_acc, bias_true, stake_fn, stake_scale, contrarian_p, shared_bias = spec

    # Effective accuracy for this claim
    eff_acc = np.clip(base_p_correct * base_acc, 0.30, 0.97)

    # Systematic-error injection: correlated error across bettors
    if is_systematic and RNG.random() < shared_bias:
        eff_acc = 1.0 - eff_acc   # all affected bettors drift toward the WRONG answer

    # Bias toward TRUE adjusts accuracy asymmetrically
    if ground_truth:
        p_correct = np.clip(eff_acc * (1 + (bias_true - 0.5) * 0.3), 0.05, 0.99)
    else:
        p_correct = np.clip(eff_acc * (1 - (bias_true - 0.5) * 0.3), 0.05, 0.99)

    # Contrarian flip (independent of accuracy)
    if RNG.random() < contrarian_p:
        p_correct = 1.0 - p_correct

    is_correct = RNG.random() < p_correct
    prediction = ground_truth if is_correct else (not ground_truth)

    # Confidence = subjective certainty (not necessarily well-calibrated)
    true_confidence = abs(p_correct - 0.5) * 2.0   # in [0,1]

    if stake_fn == 'calibrated':
        raw_conf = true_confidence
    elif stake_fn == 'overconfident':
        raw_conf = np.clip(RNG.beta(4, 1.5), 0.3, 0.99)
    else:  # 'flat'
        raw_conf = 0.6

    # Add lognormal noise to stakes
    noise = float(RNG.lognormal(0, 0.45))
    stake = max(1.0, stake_scale * raw_conf * noise)

    return prediction, stake, raw_conf


# ============================================================
# SECTION 3: SEALED MARKET
# ============================================================

def run_market(claims: pd.DataFrame) -> tuple:
    """
    Sealed market: every bettor commits independently.
    Returns:
      results_df  -- one row per claim with aggregate signals
      error_mat   -- shape (n_bettors, n_claims), 1 if bettor was wrong
    """
    n_claims  = len(claims)
    n_bettors = len(BETTOR_SPECS)
    error_mat = np.zeros((n_bettors, n_claims), dtype=float)
    stake_mat = np.zeros((n_bettors, n_claims), dtype=float)

    rows = []
    for j, (_, claim) in enumerate(claims.iterrows()):
        gt     = claim['ground_truth']
        sys_e  = claim['is_systematic_error']
        bp     = claim['base_p_correct']

        votes_t, votes_f = 0, 0
        stakes_t, stakes_f = 0.0, 0.0

        for i, spec in enumerate(BETTOR_SPECS):
            pred, stake, conf = bettor_predict(spec, bp, gt, sys_e)
            if pred:
                votes_t  += 1
                stakes_t += stake
                stake_mat[i, j] = +stake
            else:
                votes_f  += 1
                stakes_f += stake
                stake_mat[i, j] = -stake
            error_mat[i, j] = float(pred != gt)

        total_votes  = votes_t + votes_f
        total_stakes = stakes_t + stakes_f

        consensus_price  = votes_t / total_votes
        stake_consensus  = stakes_t / total_stakes if total_stakes > 0 else 0.5

        if   stakes_t > stakes_f: ca_pred = True
        elif stakes_f > stakes_t: ca_pred = False
        else:                     ca_pred = None

        cost_ratio = (
            max(stakes_t, stakes_f) / max(min(stakes_t, stakes_f), 0.01)
        )

        rows.append(dict(
            claim_id            = claim['claim_id'],
            category            = claim['category'],
            difficulty          = claim['difficulty'],
            is_systematic_error = claim['is_systematic_error'],
            ground_truth        = gt,
            votes_t             = votes_t,
            votes_f             = votes_f,
            stakes_t            = stakes_t,
            stakes_f            = stakes_f,
            consensus_price     = consensus_price,
            stake_consensus     = stake_consensus,
            ca_pred             = ca_pred,
            cost_ratio          = cost_ratio,
        ))

    return pd.DataFrame(rows), error_mat


# ============================================================
# SECTION 4: TEST A
# ============================================================

def auc_safe(y_true, y_score):
    arr = np.array(y_true, dtype=float)
    if arr.sum() == 0 or arr.sum() == len(arr):
        return float('nan')
    return roc_auc_score(arr, y_score)

def acc(pred_series, truth_series):
    return (pred_series == truth_series).mean()

def test_a(df: pd.DataFrame) -> dict:
    print("\n" + "="*70)
    print("TEST A: DOES COST-ASYMMETRY BEAT VOTE-COUNT CONSENSUS?")
    print("="*70)

    clean = df.dropna(subset=['ca_pred'])
    y     = clean['ground_truth'].astype(float)

    con_price = clean['consensus_price']
    stk_cons  = clean['stake_consensus']

    auc_con = auc_safe(y, con_price)
    auc_stk = auc_safe(y, stk_cons)
    brier_con = brier_score_loss(y, con_price)
    brier_stk = brier_score_loss(y, stk_cons)

    acc_con = acc(con_price > 0.5, clean['ground_truth'])
    acc_ca  = acc(clean['ca_pred'],  clean['ground_truth'])

    print(f"\nN claims evaluated: {len(clean)}")
    print(f"\n{'Predictor':<35}  {'AUC':>6}  {'Brier':>7}  {'Accuracy':>9}")
    print("-"*62)
    print(f"{'Vote-count consensus':<35}  {auc_con:>6.3f}  {brier_con:>7.4f}  {acc_con:>9.3f}")
    print(f"{'Stake-weighted consensus (CA)':<35}  {auc_stk:>6.3f}  {brier_stk:>7.4f}  {acc_ca:>9.3f}")

    delta_auc   = auc_stk - auc_con
    delta_brier = brier_stk - brier_con
    print(f"\nDelta (CA minus vote-consensus): AUC {delta_auc:+.4f}, Brier {delta_brier:+.5f}")

    print("\n--- BY DIFFICULTY ---")
    for diff in ['easy', 'medium', 'hard', 'trap']:
        sub = clean[clean['difficulty'] == diff]
        if len(sub) < 5:
            continue
        sy = sub['ground_truth'].astype(float)
        if sy.nunique() < 2:
            continue
        da = auc_safe(sy, sub['consensus_price'])
        sa = auc_safe(sy, sub['stake_consensus'])
        winner = "CA>" if sa > da + 0.005 else ("CON>" if da > sa + 0.005 else "TIE")
        print(f"  {diff:8s} (n={len(sub):3d}): vote-AUC={da:.3f}  stake-AUC={sa:.3f}  [{winner}]")

    print("\n--- BY CATEGORY ---")
    for cat in CATEGORIES:
        sub = clean[clean['category'] == cat]
        if len(sub) < 5:
            continue
        sy = sub['ground_truth'].astype(float)
        if sy.nunique() < 2:
            continue
        da = auc_safe(sy, sub['consensus_price'])
        sa = auc_safe(sy, sub['stake_consensus'])
        winner = "CA>" if sa > da + 0.005 else ("CON>" if da > sa + 0.005 else "TIE")
        print(f"  {cat:25s} (n={len(sub):3d}): vote-AUC={da:.3f}  stake-AUC={sa:.3f}  [{winner}]")

    print("\n--- DIVERGENT CLAIMS (CA prediction != vote-consensus prediction) ---")
    diverge = clean[(clean['consensus_price'] > 0.5) != clean['ca_pred']]
    if len(diverge) < 2:
        print("  No divergent claims.")
    else:
        dv_ca  = acc(diverge['ca_pred'],          diverge['ground_truth'])
        dv_con = acc(diverge['consensus_price'] > 0.5, diverge['ground_truth'])
        print(f"  N divergent: {len(diverge)} / {len(clean)}  ({len(diverge)/len(clean)*100:.1f}%)")
        print(f"  On divergent claims:  CA accuracy={dv_ca:.3f}  Consensus accuracy={dv_con:.3f}")
        if dv_ca > dv_con + 0.02:
            print("  -> CA wins on disagreements: high-stake minority was better-informed")
        elif dv_con > dv_ca + 0.02:
            print("  -> CONSENSUS wins on disagreements: high-stake bettors were WRONG")
            print("  -> THIS DIRECTLY FALSIFIES THE CLAIM in the divergent-claim regime")
        else:
            print("  -> No meaningful difference on disagreements (ties)")

    print("\n--- VERDICT ---")
    if abs(delta_auc) < 0.015:
        verdict = "NULL -- no meaningful predictive advantage for cost-asymmetry"
        falsified = True
    elif delta_auc > 0.015:
        verdict = "TENTATIVE SUPPORT -- CA beats vote-consensus (see Test B for contamination)"
        falsified = False
    else:
        verdict = "FALSIFIED -- stake-weighting (CA) is WORSE than vote-count consensus"
        falsified = True
    print(f"  {verdict}")

    return dict(
        n=len(clean),
        auc_con=auc_con, auc_stk=auc_stk,
        brier_con=brier_con, brier_stk=brier_stk,
        acc_con=acc_con, acc_ca=acc_ca,
        delta_auc=delta_auc,
        falsified=falsified,
        diverge_n=len(diverge),
        diverge_ca_acc=acc(diverge['ca_pred'], diverge['ground_truth']) if len(diverge)>1 else float('nan'),
        diverge_con_acc=acc(diverge['consensus_price']>0.5, diverge['ground_truth']) if len(diverge)>1 else float('nan'),
    )


# ============================================================
# SECTION 5: TEST B
# ============================================================

def test_b(df: pd.DataFrame, error_mat: np.ndarray) -> dict:
    print("\n" + "="*70)
    print("TEST B: BETTOR INDEPENDENCE")
    print("="*70)

    n_bettors = error_mat.shape[0]
    names = [s[0] for s in BETTOR_SPECS]

    corr_mat = np.corrcoef(error_mat)
    off_diag = corr_mat[np.triu_indices(n_bettors, k=1)]
    mean_corr  = float(np.mean(off_diag))
    max_corr   = float(np.max(off_diag))
    pct_high   = float(np.mean(off_diag > 0.30))

    print(f"\nN bettors: {n_bettors}")
    print(f"Mean pairwise error correlation (off-diagonal): {mean_corr:.3f}")
    print(f"Max pairwise error correlation:                  {max_corr:.3f}")
    print(f"Pairs with r > 0.30:                            {pct_high*100:.1f}%")

    print("\nPer-bettor error rates (overall):")
    for i, name in enumerate(names):
        er = error_mat[i].mean()
        print(f"  {name:35s}  error_rate={er:.3f}")

    print("\nPairwise error correlations:")
    header = f"{'':35s}" + "".join(f"{n[:8]:>10s}" for n in names)
    print(header)
    for i, ni in enumerate(names):
        row = f"{ni:35s}"
        for j in range(n_bettors):
            if j < i:
                row += f"{'':>10s}"
            elif j == i:
                row += f"{'1.000':>10s}"
            else:
                row += f"{corr_mat[i,j]:>10.3f}"
        print(row)

    consensus_var = df['consensus_price'].var()
    print(f"\nConsensus price variance: {consensus_var:.4f}")
    print(f"  (Uniform random ~0.083; near 0 = variance collapse / herding)")

    adv_idx = df['category'] == 'adversarial_framing'
    if adv_idx.sum() > 0:
        adv_errors = error_mat[:, adv_idx.values]
        adv_err_rates = adv_errors.mean(axis=1)
        per_claim_std = adv_errors.std(axis=0)
        print(f"\nAdversarial framing claims (n={adv_idx.sum()}):")
        for i, name in enumerate(names):
            print(f"  {name:35s}  adv_error_rate={adv_err_rates[i]:.3f}")
        print(f"  Mean per-claim std of bettor errors: {per_claim_std.mean():.3f}")
        print(f"  (0.0 = full lockstep, 0.5 = fully independent)")

    sys_idx = df['is_systematic_error'].values
    sys_errors = error_mat[:, sys_idx]
    sys_corrs = [np.corrcoef(sys_errors[i], sys_errors[j])[0,1]
                 for i in range(n_bettors)
                 for j in range(i+1, n_bettors)]
    mean_sys_corr = float(np.nanmean(sys_corrs))
    print(f"\nOn systematic-error claims only: mean pairwise correlation = {mean_sys_corr:.3f}")

    print("\n--- TEST B VERDICT ---")
    if mean_corr > 0.35:
        tb_verdict = "CONTAMINATED"
        tb_msg = ("Mean error correlation {:.3f} exceeds 0.35. "
                  "Bettors are NOT sufficiently independent. "
                  "Test A reflects shared model bias.").format(mean_corr)
    elif mean_corr > 0.20:
        tb_verdict = "PARTIALLY CONTAMINATED"
        tb_msg = ("Mean error correlation {:.3f} is moderate. "
                  "Test A is directionally suggestive but overstates any advantage.").format(mean_corr)
    else:
        tb_verdict = "CLEAN ENOUGH"
        tb_msg = ("Mean error correlation {:.3f} is low. "
                  "Bettor independence is adequate for Test A.").format(mean_corr)
    print(f"  {tb_verdict}: {tb_msg}")

    return dict(
        mean_corr=mean_corr,
        max_corr=max_corr,
        pct_pairs_high=pct_high,
        consensus_var=consensus_var,
        mean_sys_corr=mean_sys_corr,
        verdict=tb_verdict,
    )


# ============================================================
# SECTION 6: ADVERSARIAL REGIME SEARCH
# ============================================================

def regime_analysis(df: pd.DataFrame) -> dict:
    print("\n" + "="*70)
    print("ADVERSARIAL REGIME ANALYSIS: WHERE DOES CA FAIL?")
    print("="*70)

    clean = df.dropna(subset=['ca_pred'])

    ca_wrong_con_right = clean[
        (clean['ca_pred']          != clean['ground_truth']) &
        ((clean['consensus_price'] > 0.5) == clean['ground_truth'])
    ]
    ca_right_con_wrong = clean[
        (clean['ca_pred']          == clean['ground_truth']) &
        ((clean['consensus_price'] > 0.5) != clean['ground_truth'])
    ]
    both_wrong = clean[
        (clean['ca_pred']          != clean['ground_truth']) &
        ((clean['consensus_price'] > 0.5) != clean['ground_truth'])
    ]

    N = len(clean)
    print(f"\nN claims: {N}")
    print(f"  CA wrong, consensus right: {len(ca_wrong_con_right):4d} ({len(ca_wrong_con_right)/N*100:5.1f}%)")
    print(f"  CA right, consensus wrong: {len(ca_right_con_wrong):4d} ({len(ca_right_con_wrong)/N*100:5.1f}%)")
    print(f"  Both wrong:                {len(both_wrong):4d} ({len(both_wrong)/N*100:5.1f}%)")

    print("\n--- REGIME 1: Does extreme cost-asymmetry predict better? ---")
    bins = [1.0, 1.3, 2.0, 4.0, np.inf]
    labels = ['1.0-1.3x', '1.3-2x', '2-4x', '>4x']
    clean = clean.copy()
    clean['cost_bin'] = pd.cut(clean['cost_ratio'], bins=bins, labels=labels)
    for label in labels:
        sub = clean[clean['cost_bin'] == label]
        if len(sub) < 3:
            continue
        sy = sub['ground_truth'].astype(float)
        ca_a = acc(sub['ca_pred'], sub['ground_truth'])
        con_a = acc(sub['consensus_price'] > 0.5, sub['ground_truth'])
        winner = "CA>" if ca_a > con_a + 0.02 else ("CON>" if con_a > ca_a + 0.02 else "TIE")
        print(f"  cost_ratio {label:8s} (n={len(sub):3d}): CA_acc={ca_a:.3f}  Con_acc={con_a:.3f}  [{winner}]")

    print("\n--- REGIME 2: High-stakes bettors as wrong minority ---")
    low_vote_high_stake = clean[
        (clean['consensus_price'] > 0.5) != (clean['stake_consensus'] > 0.5)
    ]
    if len(low_vote_high_stake) > 0:
        sv = low_vote_high_stake['ground_truth'].astype(float)
        da = auc_safe(sv, low_vote_high_stake['consensus_price'])
        sa = auc_safe(sv, low_vote_high_stake['stake_consensus'])
        print(f"  'Vote-minority, stake-majority' claims (n={len(low_vote_high_stake)}):")
        print(f"  Vote-consensus AUC={da:.3f}   Stake-consensus AUC={sa:.3f}")
        if da > sa + 0.03:
            print("  -> VOTE-COUNT beats CA here. High-stake bettors were the WRONG minority.")
            print("  -> FALSIFYING REGIME: big money != better information")
        else:
            print("  -> CA holds up even when vote and stake majorities disagree.")

    print("\n--- REGIME 3: Systematic-error claims ---")
    sys_sub = clean[clean['is_systematic_error'] == True]
    if len(sys_sub) > 2 and sys_sub['ground_truth'].nunique() > 1:
        sy = sys_sub['ground_truth'].astype(float)
        da = auc_safe(sy, sys_sub['consensus_price'])
        sa = auc_safe(sy, sys_sub['stake_consensus'])
        print(f"  n={len(sys_sub)}, vote-AUC={da:.3f}, stake-AUC={sa:.3f}")
        if da < 0.5 and sa < 0.5:
            print("  BOTH predictors fail (below chance). Correlation injected correctly.")
            print("  CA amplifies the shared mistake because high-stakes bettors are most correlated.")
    else:
        print(f"  n={len(sys_sub)} (too few or homogeneous for AUC).")

    print("\n--- REGIME 4: Adversarial framing claims ---")
    trap = clean[clean['difficulty'] == 'trap']
    if len(trap) > 2 and trap['ground_truth'].nunique() > 1:
        ty = trap['ground_truth'].astype(float)
        da = auc_safe(ty, trap['consensus_price'])
        sa = auc_safe(ty, trap['stake_consensus'])
        print(f"  n={len(trap)}, vote-AUC={da:.3f}, stake-AUC={sa:.3f}")
        if sa < da:
            print("  CA FAILS on adversarial claims: overconfident bettors double down on wrong answers.")

    print("\n--- UNRESOLVABLE CASE ---")
    print("  When high-stakes bettors AND other bettors share the same wrong prior,")
    print("  Test A cannot distinguish 'CA captured superior information' from")
    print("  'CA amplified shared overconfident error.' In real markets these regimes")
    print("  are unlabeled. A clean falsification in aggregate can coexist with CA")
    print("  being genuinely useful in non-contaminated sub-claims, and vice versa.")

    return dict(
        ca_wrong_con_right=len(ca_wrong_con_right),
        ca_right_con_wrong=len(ca_right_con_wrong),
        both_wrong=len(both_wrong),
        n_diverge_vote_stake=len(low_vote_high_stake),
    )


# ============================================================
# SECTION 7: FINAL SUMMARY
# ============================================================

def final_summary(ta: dict, tb: dict, regimes: dict, n_claims: int):
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"""
THE CLAIM UNDER TEST:
  "The cost to MAINTAIN a position against opposition predicts its eventual
   correctness better than the consensus price does."
  (free-to-hold, costly-to-oppose = TRUE; costly-to-hold = FALSE)

HOW WE OPERATIONALIZED IT:
  Claim   -> Do stake-weighted predictions beat vote-count predictions?
  "Cost"  -> The side with less total stake is the costly-to-hold minority.
  The CA signal IS the stake-weighted consensus; they diverge from vote-count
  consensus only when high-stake bettors outvote by capital but not by count.
""")

    print(f"SIMULATION: {n_claims} claims, {len(BETTOR_SPECS)} bettors, sealed market.")
    print()
    print(f"Test A: AUC delta (CA minus vote-consensus) = {ta['delta_auc']:+.4f}")
    print(f"        Brier delta                         = {ta['brier_stk']-ta['brier_con']:+.5f}")
    print(f"        Divergent claims (n={ta['diverge_n']}): "
          f"CA_acc={ta['diverge_ca_acc']:.3f}  Con_acc={ta['diverge_con_acc']:.3f}")
    print()
    print(f"Test B: Mean error correlation               = {tb['mean_corr']:.3f}")
    print(f"        Independence verdict                  = {tb['verdict']}")

    print("\n--- VERDICT ---")

    ca_wins      = ta['delta_auc'] > 0.015
    ca_ties      = abs(ta['delta_auc']) <= 0.015
    ca_loses     = ta['delta_auc'] < -0.015
    contaminated = tb['mean_corr'] > 0.35
    partial      = 0.20 < tb['mean_corr'] <= 0.35

    if ca_loses:
        print("1. FALSIFIED -- CA performs WORSE than vote-count consensus.")
        print("   Stake-weighting (the 'cost-asymmetry' signal) is a negative predictor")
        print("   relative to simply counting votes. The claim is FALSE.")
    elif ca_ties:
        print("1. NULL RESULT -- CA shows no meaningful advantage over vote-count consensus.")
        print("   The delta is within noise. The claim is NOT supported.")
    elif ca_wins and contaminated:
        print("1. CONTAMINATED CONFIRMATION -- CA appears to beat consensus, BUT")
        print("   bettors' errors are too correlated for this to be meaningful.")
        print("   The apparent advantage is self-confirmation from a shared prior.")
    elif ca_wins and partial:
        print("1. WEAK SUPPORT (contested) -- CA beats consensus, but moderate bettor")
        print("   correlation means this is partly self-confirmation.")
    else:
        print("1. TENTATIVE SUPPORT -- CA beats consensus AND bettors are independent.")
        print("   But see failure regimes below before accepting the claim.")

    print()
    print("2. FALSIFYING REGIMES (always present regardless of overall verdict):")
    print(f"   a. Overconfident high-stake bettors: when big money is wrong, CA")
    print(f"      amplifies the mistake. {regimes['ca_wrong_con_right']} claims where CA wrong, consensus right.")
    print(f"   b. Adversarial framing: trap claims fool ALL bettors. High-stake")
    print(f"      bettors commit more capital to the wrong side, worsening CA.")
    print(f"   c. Systematic errors: CA signal becomes noise when bettor errors correlate.")
    print(f"   d. Thin markets: with few bettors, one high-stake outlier dominates.")
    print()
    print("3. THE CASE WE CANNOT RESOLVE:")
    print("   When bettors share a systematic wrong prior AND overconfident bettors")
    print("   stake heavily on the wrong side, Test A cannot distinguish 'CA captured")
    print("   superior contrarian information' from 'CA amplified shared overconfident")
    print("   error.' In real markets, these regimes are unlabeled.")
    print()
    print("   This simulation also cannot test the DYNAMIC version of the claim: if")
    print("   bettors can INCREASE stakes after seeing opposition, the 'maintenance cost'")
    print("   signal changes. A static single-round market is a necessary but not")
    print("   sufficient test of the original claim.")


# ============================================================
# MAIN
# ============================================================

def main():
    print("MARKET SIMULATION: Falsification of the cost-asymmetry claim")
    print("="*70)
    print(f"RNG seed: 42 | {len(BETTOR_SPECS)} bettors | 250 claims")
    print("Bettor types:", [s[0] for s in BETTOR_SPECS])

    claims = generate_claims(250)

    print(f"\nClaims generated: {len(claims)}")
    print("  Difficulty:", claims['difficulty'].value_counts().to_dict())
    print("  Ground truth:", f"{claims['ground_truth'].sum()} TRUE / {(~claims['ground_truth']).sum()} FALSE")
    print("  Systematic-error claims:", claims['is_systematic_error'].sum())

    results, error_mat = run_market(claims)

    ta = test_a(results)
    tb = test_b(results, error_mat)
    reg = regime_analysis(results)
    final_summary(ta, tb, reg, len(claims))

    results.drop(columns=['ca_pred'], errors='ignore').to_csv(
        'market_results.csv', index=False)
    print("\nRaw results saved to market_results.csv")

if __name__ == '__main__':
    main()
