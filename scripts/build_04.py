"""Build + execute notebook 04 (segments, risk scores, ROI, playbook, dashboard figure)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from nbtools import build, insert_after  # noqa: E402

NB4 = [
("md", """# 04 · Customer segments, risk scores and retention strategy
**Goal:** turn the analysis and model into actions: who the customer groups are, which customers to call first, what it is worth, and what to do for each group."""),
("code", """import sys; sys.path.insert(0, '../src'); sys.path.insert(0, '../scripts')
import json, joblib, numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns
import style
from style import BLUE, RED, GREY, GREEN, ORANGE
from sklearn.base import clone
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from churn.config import CLEAN, FIG, TABLES, MODELS, ASSUMPTIONS, RANDOM_STATE
from churn.modeling import load_xy
from churn.evaluate import campaign_value
def save(name): plt.savefig(FIG / f'{name}.png', dpi=130, bbox_inches='tight')
df, X, y = load_xy(CLEAN)
with open(FIG.parent / 'metrics.json', encoding='utf-8') as f:
    M = json.load(f)
thr = M['threshold']
print('model:', M['final_model'], '| contact threshold:', thr)"""),
("md", """## 1. Customer segments (K-means)
Segments describe **who customers are**, independent of churn, using tenure, spend, number of services, contract, internet type, payment method, senior status and household. The churn label is not used to form segments, so differences in churn between segments are a genuine finding."""),
("code", """Z = pd.DataFrame({'tenure': df.tenure, 'MonthlyCharges': df.MonthlyCharges, 'NumServices': df.NumServices,
    'contract': df.Contract.map({'Month-to-month': 0, 'One year': 1, 'Two year': 2}), 'fiber': (df.InternetService == 'Fiber optic').astype(int),
    'no_internet': (df.InternetService == 'No').astype(int), 'autopay': df.PaymentMethod.isin(['Bank transfer', 'Credit card']).astype(int),
    'echeck': (df.PaymentMethod == 'Electronic check').astype(int), 'senior': (df.SeniorCitizen == 'Yes').astype(int),
    'household': ((df.Partner == 'Yes') | (df.Dependents == 'Yes')).astype(int)})
S = StandardScaler().fit_transform(Z)
ks = range(2, 9); sil, inertia = [], []
for k in ks:
    km = KMeans(k, n_init=10, random_state=RANDOM_STATE).fit(S); inertia.append(km.inertia_)
    sil.append(silhouette_score(S, km.labels_, sample_size=3000, random_state=1))
fig, ax = plt.subplots(1, 2, figsize=(11, 3.4))
ax[0].plot(list(ks), inertia, 'o-', color=BLUE); ax[0].set_title('Elbow (inertia)'); ax[0].set_xlabel('k')
ax[1].plot(list(ks), sil, 'o-', color=RED); ax[1].set_title('Silhouette score'); ax[1].set_xlabel('k')
plt.tight_layout(); pd.DataFrame({'k': list(ks), 'silhouette': np.round(sil, 3)}).set_index('k').T"""),
("md", """Silhouette scores are close between k = 3 and 6 (about 0.25-0.27), so statistics do not pick a clear winner. We use **k = 5** because it gives five groups that are large (at least 940 customers each), clearly different, and easy to describe to a business audience."""),
("code", """km = KMeans(5, n_init=10, random_state=RANDOM_STATE).fit(S); df['cluster'] = km.labels_
prof = df.groupby('cluster').agg(customers=('cluster', 'size'), churn_rate=('ChurnFlag', 'mean'), median_tenure=('tenure', 'median'),
    avg_monthly=('MonthlyCharges', 'mean'), avg_services=('NumServices', 'mean'),
    month_to_month=('Contract', lambda s: (s == 'Month-to-month').mean()), fiber=('InternetService', lambda s: (s == 'Fiber optic').mean()),
    no_internet=('InternetService', lambda s: (s == 'No').mean()), e_check=('PaymentMethod', lambda s: (s == 'Electronic check').mean()),
    senior=('SeniorCitizen', lambda s: (s == 'Yes').mean()))
def name(r):  # transparent, rule-based naming from each cluster's profile
    if r.no_internet > .9: return 'Phone-only budget'
    if r.median_tenure > 50 and r.month_to_month < .2: return 'Loyal multi-service'
    if r.senior > .9: return 'Senior fiber, month-to-month'
    if r.e_check > .9: return 'E-check fiber, month-to-month'
    return 'Mid-tenure month-to-month'
prof['segment'] = prof.apply(name, axis=1); assert prof.segment.is_unique
df['segment'] = df.cluster.map(prof.segment)
prof = prof.set_index('segment')
pf = prof.drop(columns='cluster', errors='ignore').copy()
for c in ['churn_rate', 'month_to_month', 'fiber', 'no_internet', 'e_check', 'senior']: pf[c] = (pf[c] * 100).round(0)
pf[['avg_monthly', 'avg_services']] = pf[['avg_monthly', 'avg_services']].round(1)
pf.sort_values('churn_rate', ascending=False).to_csv(TABLES / 'segment_profiles.csv'); pf.sort_values('churn_rate', ascending=False)"""),
("code", """seg = df.groupby('segment').agg(customers=('ChurnFlag', 'size'), churners=('ChurnFlag', 'sum'), mrr=('MonthlyCharges', 'sum'),
    mrr_lost=('MonthlyCharges', lambda s: s[df.loc[s.index, 'ChurnFlag'] == 1].sum())).assign(churn_rate=lambda d: d.churners / d.customers * 100)
seg['share_of_mrr_lost_%'] = seg.mrr_lost / seg.mrr_lost.sum() * 100
seg = seg.sort_values('mrr_lost', ascending=False); seg.round(1).to_csv(TABLES / 'segment_revenue_at_risk.csv')
fig, ax = plt.subplots(1, 2, figsize=(13, 3.8))
ax[0].barh(seg.index[::-1], seg.churn_rate[::-1], color=[RED if v > 26.5 else BLUE for v in seg.churn_rate[::-1]]); ax[0].set_title('Churn rate by segment (%)')
for i, v in enumerate(seg.churn_rate[::-1]): ax[0].text(v + .8, i, f'{v:.0f}%', va='center')
ax[1].barh(seg.index[::-1], seg.mrr_lost[::-1], color=RED); ax[1].set_title('Monthly revenue lost to churn ($)')
for i, v in enumerate(seg.mrr_lost[::-1]): ax[1].text(v + 600, i, f'${v:,.0f}', va='center')
for a in ax: a.grid(axis='y', visible=False)
plt.tight_layout(); save('12_segments'); seg.round(1)"""),
("md", """## 2. Score every customer
Each row is held out from its fold-specific model fit when this retrospective risk table is generated. Hyperparameters were selected using the training split, and this is a single-snapshot sample, so treat these scores as portfolio-analysis outputs—not prospective production probabilities. Held-out test performance is reported separately in Notebook 03."""),
("code", """final = joblib.load(MODELS / 'churn_model.joblib')
cv = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)
df['churn_probability'] = cross_val_predict(clone(final), X, y, cv=cv, method='predict_proba')[:, 1]
df['risk_tier'] = pd.cut(df.churn_probability, [-.01, thr, .5, 1.0], labels=['Low', 'Medium', 'High'])
tier = df.groupby('risk_tier', observed=True).agg(customers=('ChurnFlag', 'size'), actual_churn_rate=('ChurnFlag', 'mean'), avg_probability=('churn_probability', 'mean'),
    mrr=('MonthlyCharges', 'sum'), actual_churners=('ChurnFlag', 'sum'))
tier['share_of_all_churners_%'] = tier.actual_churners / tier.actual_churners.sum() * 100
tier = tier.round(3); tier.to_csv(TABLES / 'risk_tiers.csv'); tier"""),
("code", """ACTION = {'Phone-only budget': 'Low priority; light-touch loyalty offer', 'Loyal multi-service': 'Protect: loyalty perks, early renewal, no discounts needed',
          'Senior fiber, month-to-month': 'Proactive call; senior support and a 12-month price lock', 'E-check fiber, month-to-month': 'Offer a bill credit for switching to auto-pay and a 12-month contract',
          'Mid-tenure month-to-month': 'Contract-upgrade offer with a bundled add-on (security / tech support)'}
out = df[['customerID', 'segment', 'Contract', 'tenure', 'MonthlyCharges', 'churn_probability', 'risk_tier', 'ChurnFlag']].copy()
out['recommended_action'] = out.segment.map(ACTION); out['churn_probability'] = out.churn_probability.round(4)
out = out.sort_values('churn_probability', ascending=False)
out.to_csv(TABLES / 'customer_risk_scores.csv', index=False)
print('scored customers:', len(out)); out.head(8)"""),
("md", """## 3. What is a retention campaign worth? Sensitivity of the business case
The headline number depends on two assumptions we cannot know from this data: what an offer costs, and how often it works. Rather than pretend, we show the range."""),
("code", """mon = df.MonthlyCharges.values; p = df.churn_probability.values; yy = df.ChurnFlag.values
costs = [20, 35, 50, 75, 100]; rates = [.10, .20, .30, .40, .50]
grid = pd.DataFrame({f'{int(r*100)}%': [campaign_value(yy, p, mon, thr, c, r, ASSUMPTIONS['horizon_months'])['net'] / len(df) * 1000 for c in costs] for r in rates}, index=[f'${c}' for c in costs])
grid.index.name = 'offer cost'; grid.columns.name = 'offer success rate'
plt.figure(figsize=(7.5, 3.8)); sns.heatmap(grid, annot=True, fmt=',.0f', cmap='RdYlGn', center=0, cbar_kws={'label': 'net $ per 1,000 customers'}, linewidths=.5)
plt.title(f'Net value of the model-targeted campaign (threshold {thr:.2f})'); plt.tight_layout(); save('13_roi_sensitivity')
grid.round(0).to_csv(TABLES / 'roi_sensitivity.csv'); grid.round(0)"""),
("code", """# Break-even success rate at the base-case offer cost
c = ASSUMPTIONS['offer_cost']; sel = p >= thr
gain_per_unit_rate = (mon[sel & (yy == 1)] * ASSUMPTIONS['horizon_months']).sum()
cost_total = c * sel.sum()
print(f'Contacted: {sel.sum():,} customers ({sel.mean():.0%} of base), reaching {(sel & (yy == 1)).sum() / yy.sum():.0%} of churners')
print(f'Break-even offer success rate at ${c:.0f} per offer: {cost_total / gain_per_unit_rate:.1%} (we assumed {ASSUMPTIONS["offer_success_rate"]:.0%})')"""),
("md", "## 4. Executive dashboard (one page)"),
("code", """fig = plt.figure(figsize=(15, 8.4)); gs = fig.add_gridspec(3, 4, height_ratios=[.55, 1.4, 1.4], hspace=.55, wspace=.35)
churned = df[df.ChurnFlag == 1]
kp = [('Customers', f'{len(df):,}'), ('Churn rate', f'{df.ChurnFlag.mean():.1%}'), ('Monthly revenue lost', f'${churned.MonthlyCharges.sum():,.0f}'), ('Model ROC-AUC (test)', f"{M['test']['roc_auc']:.2f}")]
for i, (k, v) in enumerate(kp):
    a = fig.add_subplot(gs[0, i]); a.axis('off'); a.text(.5, .62, v, ha='center', fontsize=24, fontweight='bold', color=style.INK); a.text(.5, .12, k, ha='center', fontsize=11, color=GREY)
a = fig.add_subplot(gs[1, 0:2]); t = df.groupby('Contract').ChurnFlag.mean().reindex(['Month-to-month', 'One year', 'Two year']) * 100
a.bar(t.index, t.values, color=[RED, BLUE, BLUE]); a.set_title('Churn rate by contract (%)'); a.grid(axis='x', visible=False)
for i, v in enumerate(t.values): a.text(i, v + .8, f'{v:.0f}%', ha='center')
a = fig.add_subplot(gs[1, 2:4]); s = df.groupby('tenure').ChurnFlag.mean().rolling(3, center=True, min_periods=1).mean() * 100; a.plot(s.index, s.values, color=RED, lw=2); a.fill_between(s.index, s.values, color=RED, alpha=.12)
a.set_title('Churn rate by tenure (months)')
a = fig.add_subplot(gs[2, 0:2]); a.barh(seg.index[::-1], seg.mrr_lost[::-1], color=RED); a.set_title('Monthly revenue lost, by segment ($)'); a.grid(axis='y', visible=False)
a = fig.add_subplot(gs[2, 2:4]); a.bar(tier.index.astype(str), tier.actual_churn_rate * 100, color=[BLUE, ORANGE, RED]); a.set_title('Actual churn rate by model risk tier (%)'); a.grid(axis='x', visible=False)
for i, v in enumerate(tier.actual_churn_rate * 100): a.text(i, v + 1, f'{v:.0f}%', ha='center')
fig.suptitle('Telco customer churn: executive summary', fontsize=15, fontweight='bold', x=.06, ha='left', y=.99)
save('00_executive_dashboard')"""),
]

F4 = [
("fig, ax = plt.subplots(1, 2, figsize=(13, 3.8))", """**Finding.** Two month-to-month fiber groups (electronic-check payers and senior citizens) are 35% of customers but **68% of the monthly revenue lost**; both churn at 48%. The two loyal-looking groups (long-tenure multi-service customers and phone-only customers) churn under 8%."""),
("tier = tier.round(3)", """**Finding.** The High tier is 22% of customers, churns at **66%** and holds **55% of all churners**. The Low tier (59% of customers) churns at 9%. Predicted probabilities (average 0.65 for High) line up with what actually happened (0.66), so the scores can be read as probabilities."""),
("print(f'Contacted:", """**Finding.** At $50 per offer the campaign breaks even if offers rescue **about 10%** of would-be churners; we assumed 30%. It only loses money in the bottom-left of the table (expensive offers that rarely work). The assumptions are illustrative: the real success rate should be measured with a small A/B test before scaling."""),
]

if __name__ == "__main__":
    for a, t in F4: insert_after(NB4, a, t)
    build(ROOT / "notebooks" / "04_segments_risk_and_strategy.ipynb", NB4, {})
