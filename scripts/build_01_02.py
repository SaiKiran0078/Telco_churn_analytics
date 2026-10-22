"""Build + execute notebooks 01 (cleaning) and 02 (EDA / business analysis)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from nbtools import build, insert_after  # noqa: E402

NB1 = [
("md", """# 01 · Data cleaning and quality checks
**Goal:** turn the raw Telco customer file into a trustworthy analysis table, and record every change.

**Question this notebook answers:** is the data fit to analyse, and what did we have to fix?"""),
("code", """import sys; sys.path.insert(0, '../src'); sys.path.insert(0, '../scripts')
import pandas as pd, numpy as np
import style
from churn.data import load_raw, quality_report, clean
from churn.config import CLEAN
pd.set_option('display.width', 140)
raw = load_raw()
raw.shape"""),
("md", "## 1. First look"),
("code", "raw.head()"),
("code", "raw.dtypes.to_frame('dtype').T"),
("md", """## 2. Quality report on the raw file
`TotalCharges` is read as text, which means it contains something that is not a number."""),
("code", """q = quality_report(raw)
pd.Series(q, name='value').to_frame()"""),
("code", """blank = raw[raw['TotalCharges'].str.strip() == '']
blank[['customerID', 'tenure', 'MonthlyCharges', 'TotalCharges', 'Contract', 'Churn']]"""),
("md", """**Finding.** The 11 blank `TotalCharges` values all belong to customers with `tenure = 0`: they signed up but have not yet been billed. The correct value is 0, not the median or a dropped row. Dropping them would remove 11 customers who are all still active."""),
("md", "## 3. Consistency checks beyond missing values"),
("code", """# Does TotalCharges roughly equal tenure x MonthlyCharges? (it should, unless prices changed)
tc = pd.to_numeric(raw['TotalCharges'], errors='coerce')
expected = raw['tenure'] * raw['MonthlyCharges']
ratio = (tc / expected).replace([np.inf, -np.inf], np.nan).dropna()
print('median billed / expected:', round(ratio.median(), 3))
print('share within +/-25%:', round(((ratio > .75) & (ratio < 1.25)).mean() * 100, 1), '%')
print('customers billed more than 1.5x expected:', int((ratio > 1.5).sum()))"""),
("code", """# Labels that mean the same thing as 'No'
for c in ['MultipleLines', 'OnlineSecurity', 'StreamingTV']:
    print(c, raw[c].value_counts().to_dict())
print('SeniorCitizen', raw['SeniorCitizen'].value_counts().to_dict())"""),
("code", """# Impossible or suspicious values
checks = {
    'tenure outside 0-72': int((~raw['tenure'].between(0, 72)).sum()),
    'MonthlyCharges <= 0': int((raw['MonthlyCharges'] <= 0).sum()),
    'internet add-on but InternetService = No': int(((raw['InternetService'] == 'No') & (raw['OnlineSecurity'] == 'Yes')).sum()),
    'duplicate customerID': int(raw['customerID'].duplicated().sum()),
}
pd.Series(checks, name='rows').to_frame()"""),
("md", "## 4. Apply the cleaning (see `src/churn/data.py`) and log every change"),
("code", """df, log = clean(raw)
pd.DataFrame(log, columns=['change', 'rows touched'])"""),
("code", """print('rows before/after:', len(raw), len(df))
print('missing values after cleaning:', int(df.isna().sum().sum()))
df.dtypes.value_counts().to_frame('columns')"""),
("md", "## 5. Outliers in the numeric columns"),
("code", """import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(13, 3.2))
for a, c in zip(ax, ['tenure', 'MonthlyCharges', 'TotalCharges']):
    a.hist(df[c], bins=40, color=style.BLUE, alpha=.85); a.set_title(c)
plt.tight_layout()
df[['tenure', 'MonthlyCharges', 'TotalCharges']].describe().round(1)"""),
("md", """**Finding.** No outliers need removing: distributions are plausible (tenure 0-72 months, monthly charges about 18 to 119). `MonthlyCharges` has a spike near 20 (phone-only customers) and `tenure` has peaks at 1 and 72 months, which are real business patterns (new sign-ups and long-term customers), not errors."""),
("md", "## 6. Save the analysis table"),
("code", """CLEAN.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(CLEAN, index=False)
print('saved', CLEAN.name, df.shape)
import json
from churn.config import TABLES
TABLES.mkdir(parents=True, exist_ok=True)
pd.DataFrame(log, columns=['change', 'rows_touched']).to_csv(TABLES / 'cleaning_log.csv', index=False)
with open(TABLES / 'raw_quality_report.json', 'w', encoding='utf-8') as f:
    json.dump(q, f, indent=2)"""),
]

NB2 = [
("md", """# 02 · Exploratory and business analysis
**Business question:** who is leaving, how much revenue does that put at risk, and which factors move churn the most?

Every number below is computed on the cleaned table from notebook 01."""),
("code", """import sys; sys.path.insert(0, '../src'); sys.path.insert(0, '../scripts')
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from scipy import stats
import style
from style import BLUE, RED, GREY
from churn.config import CLEAN, FIG, TABLES
from churn.data import tenure_bucket
FIG.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(CLEAN)
df['TenureBucket'] = tenure_bucket(df['tenure'])
def save(name): plt.savefig(FIG / f'{name}.png', dpi=130, bbox_inches='tight')
df.shape"""),
("md", "## 1. Headline KPIs"),
("code", """churned = df[df.ChurnFlag == 1]
kpi = {
    'Customers': len(df),
    'Churned customers': len(churned),
    'Churn rate %': round(df.ChurnFlag.mean() * 100, 1),
    'Monthly recurring revenue (MRR), $': round(df.MonthlyCharges.sum()),
    'MRR lost to churners, $': round(churned.MonthlyCharges.sum()),
    'Share of MRR lost %': round(churned.MonthlyCharges.sum() / df.MonthlyCharges.sum() * 100, 1),
    'Avg monthly charge: churned $': round(churned.MonthlyCharges.mean(), 1),
    'Avg monthly charge: retained $': round(df[df.ChurnFlag == 0].MonthlyCharges.mean(), 1),
    'Median tenure: churned (months)': float(churned.tenure.median()),
    'Median tenure: retained (months)': float(df[df.ChurnFlag == 0].tenure.median()),
}
kdf = pd.Series(kpi, name='value').to_frame(); kdf.to_csv(TABLES / 'headline_kpis.csv'); kdf"""),
("md", "## 2. Churn by the main customer attributes"),
("code", """def churn_by(col, order=None):
    t = df.groupby(col).agg(customers=('ChurnFlag', 'size'), churners=('ChurnFlag', 'sum'), churn_rate=('ChurnFlag', 'mean'), mrr=('MonthlyCharges', 'sum'),
                            mrr_lost=('MonthlyCharges', lambda s: s[df.loc[s.index, 'ChurnFlag'] == 1].sum()))
    t['churn_rate'] = (t['churn_rate'] * 100).round(1)
    t['share_of_all_churners_%'] = (t['churners'] / df.ChurnFlag.sum() * 100).round(1)
    t[['mrr', 'mrr_lost']] = t[['mrr', 'mrr_lost']].round(0)
    t = t.drop(columns='churners')
    return t.reindex(order) if order else t.sort_values('churn_rate', ascending=False)
churn_by('Contract', ['Month-to-month', 'One year', 'Two year'])"""),
("code", "churn_by('TenureBucket', ['0-6 m', '7-12 m', '13-24 m', '25-48 m', '49-72 m'])"),
("code", "churn_by('InternetService')"),
("code", "churn_by('PaymentMethod')"),
("code", """pd.concat({c: churn_by(c)[['customers', 'churn_rate']] for c in ['OnlineSecurity', 'TechSupport', 'OnlineBackup', 'DeviceProtection', 'StreamingTV', 'SeniorCitizen', 'Partner', 'Dependents', 'PaperlessBilling', 'gender']}, names=['feature', 'value'])"""),
("md", "## 3. The picture: where churn concentrates"),
("code", """fig, ax = plt.subplots(2, 2, figsize=(13, 8))
order = {'Contract': ['Month-to-month', 'One year', 'Two year'], 'TenureBucket': ['0-6 m', '7-12 m', '13-24 m', '25-48 m', '49-72 m'],
         'InternetService': ['Fiber optic', 'DSL', 'No'], 'PaymentMethod': ['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card']}
avg = df.ChurnFlag.mean() * 100
for a, (c, o) in zip(ax.ravel(), order.items()):
    t = churn_by(c, o)
    bars = a.bar(t.index.astype(str), t['churn_rate'], color=[RED if v > avg else BLUE for v in t['churn_rate']])
    a.axhline(avg, color=GREY, ls='--', lw=1); a.text(len(t) - .5, avg + 1, f'average {avg:.1f}%', ha='right', color=GREY, fontsize=9)
    for b, v in zip(bars, t['churn_rate']): a.text(b.get_x() + b.get_width() / 2, v + .6, f'{v:.0f}%', ha='center', fontsize=10)
    a.set_title(f'Churn rate by {c}'); a.set_ylabel('% churned'); a.grid(axis='x', visible=False)
plt.tight_layout(); save('01_churn_by_segment')"""),
("md", "## 4. Tenure and price: when do customers leave, and does price matter?"),
("code", """fig, ax = plt.subplots(1, 2, figsize=(13, 4))
for flag, col, lab in [(0, BLUE, 'Retained'), (1, RED, 'Churned')]:
    ax[0].hist(df[df.ChurnFlag == flag].tenure, bins=36, alpha=.65, color=col, label=lab, density=True)
    ax[1].hist(df[df.ChurnFlag == flag].MonthlyCharges, bins=36, alpha=.65, color=col, label=lab, density=True)
ax[0].set_title('Tenure (months): churners leave early'); ax[1].set_title('Monthly charge ($): churners pay more')
for a in ax: a.legend(); a.set_ylabel('share of group')
plt.tight_layout(); save('02_tenure_price_distribution')"""),
("code", """# Survival-style view: share of each tenure cohort that has churned
s = df.groupby('tenure').ChurnFlag.mean().rolling(3, center=True, min_periods=1).mean() * 100
plt.figure(figsize=(9, 3.6)); plt.plot(s.index, s.values, color=RED, lw=2)
plt.fill_between(s.index, s.values, color=RED, alpha=.12); plt.xlabel('tenure (months)'); plt.ylabel('% churned (3-month smoothing)')
plt.title('Churn rate falls steadily as tenure grows'); save('03_churn_by_tenure')"""),
("md", """## 5. Are these differences real? Statistical tests
With 7,043 customers even small gaps can be significant, so we also report **effect size** (Cramér's V for categories; 0.1 small, 0.3 medium, 0.5 large)."""),
("code", """def cramers_v(col):
    ct = pd.crosstab(df[col], df.ChurnFlag); chi2, p, dof, _ = stats.chi2_contingency(ct)
    return pd.Series({'chi2': chi2, 'p_value': p, 'cramers_v': np.sqrt(chi2 / (len(df) * (min(ct.shape) - 1)))})
cats = ['Contract', 'InternetService', 'PaymentMethod', 'OnlineSecurity', 'TechSupport', 'OnlineBackup', 'DeviceProtection',
        'StreamingTV', 'StreamingMovies', 'PaperlessBilling', 'SeniorCitizen', 'Partner', 'Dependents', 'MultipleLines', 'PhoneService', 'gender']
cv = pd.DataFrame({c: cramers_v(c) for c in cats}).T.sort_values('cramers_v', ascending=False)
cv['significant (p<0.05)'] = cv.p_value < .05
cv.assign(p_value=cv.p_value.map(lambda x: f'{x:.1e}'), chi2=cv.chi2.round(1), cramers_v=cv.cramers_v.round(3)).to_csv(TABLES / 'association_tests.csv')
cv.round(4)"""),
("code", """# Numeric columns: Mann-Whitney U (no normality assumption) + rank-biserial effect size
rows = []
for c in ['tenure', 'MonthlyCharges', 'TotalCharges']:
    a, b = df[df.ChurnFlag == 1][c], df[df.ChurnFlag == 0][c]
    u, p = stats.mannwhitneyu(a, b); rb = 1 - 2 * u / (len(a) * len(b))
    rows.append({'feature': c, 'median_churned': a.median(), 'median_retained': b.median(), 'p_value': p, 'effect_size_rank_biserial': round(rb, 3)})
pd.DataFrame(rows).round(4)"""),
("code", """top = cv.head(10)
plt.figure(figsize=(8, 4.2)); plt.barh(top.index[::-1], top.cramers_v[::-1], color=BLUE)
plt.title("Strength of association with churn (Cramér's V)"); plt.xlabel("Cramér's V"); plt.tight_layout(); save('04_association_strength')"""),
("md", "## 6. Combined effect: contract x tenure x internet service"),
("code", """pivot = df.pivot_table(index='Contract', columns='TenureBucket', values='ChurnFlag', aggfunc='mean', observed=True) * 100
cnt = df.pivot_table(index='Contract', columns='TenureBucket', values='ChurnFlag', aggfunc='size', observed=True)
plt.figure(figsize=(8, 3.4)); sns.heatmap(pivot, annot=True, fmt='.0f', cmap='Reds', cbar_kws={'label': '% churned'}, linewidths=.5)
plt.title('Churn rate (%) by contract and tenure'); plt.tight_layout(); save('05_heatmap_contract_tenure')
pivot.round(1)"""),
("code", """# The riskiest identifiable group: month-to-month, fiber optic, no tech support / security
risky = df[(df.Contract == 'Month-to-month') & (df.InternetService == 'Fiber optic') & (df.TechSupport == 'No') & (df.OnlineSecurity == 'No')]
print(f'Risky group: {len(risky):,} customers = {len(risky)/len(df):.0%} of base')
print(f'Churn rate: {risky.ChurnFlag.mean():.1%} vs {df.ChurnFlag.mean():.1%} overall')
print(f'Share of all churners: {risky.ChurnFlag.sum()/df.ChurnFlag.sum():.0%}')
print(f'MRR lost in this group: ${risky[risky.ChurnFlag==1].MonthlyCharges.sum():,.0f} of ${df[df.ChurnFlag==1].MonthlyCharges.sum():,.0f}')"""),
("md", "## 7. Revenue at risk by segment"),
("code", """seg = churn_by('Contract', ['Month-to-month', 'One year', 'Two year'])
fig, ax = plt.subplots(1, 2, figsize=(12, 3.6))
ax[0].bar(seg.index, seg.mrr_lost, color=RED); ax[0].set_title('Monthly revenue lost to churn ($)')
for i, v in enumerate(seg.mrr_lost): ax[0].text(i, v + 500, f'${v:,.0f}', ha='center')
ax[1].bar(seg.index, seg['share_of_all_churners_%'], color=BLUE); ax[1].set_title('Share of all churners (%)')
for i, v in enumerate(seg['share_of_all_churners_%']): ax[1].text(i, v + 1, f'{v:.0f}%', ha='center')
for a in ax: a.grid(axis='x', visible=False)
plt.tight_layout(); save('06_revenue_at_risk_by_contract')"""),
]

F2 = [
("kdf = pd.Series(kpi", """**Finding.** 1,869 of 7,043 customers (26.5%) have left, taking **$139k of the $456k monthly revenue (30.5%)** with them. Churners pay more ($74 vs $61 a month) and are far newer (median tenure 10 vs 38 months)."""),
("churn_by('PaymentMethod')", """**Findings.**
- **Contract is the strongest lever.** Month-to-month customers are 55% of the base but **88.6% of all churners** (43% churn). Two-year customers churn at 2.8%.
- **Early life is the danger zone:** 53% of customers churn within their first six months, falling to 10% after four years.
- **Fiber optic customers churn at 42%** vs 19% for DSL, and **electronic-check payers at 45%** vs 15-19% for every other payment method.
- Customers **without online security or tech support churn at about 31%**, versus about 15% for those who have them.
- Gender makes no difference (26.9% vs 26.2%).

These are associations, not proof of cause: fiber customers also pay more and are more often on month-to-month contracts."""),
("cv.assign(p_value", """**Findings.** Contract (V = 0.41), internet service (0.32) and payment method (0.30) have medium-to-large associations with churn. Gender and phone service are not statistically significant (p > 0.3). Among numeric columns, **tenure has the largest effect** (rank-biserial 0.48): churners stay a median 10 months against 38."""),
("risky = df[", """**Finding.** One in five customers (22%) is on a month-to-month fiber plan with no security or tech support. They churn at **60.7%** and account for **49% of all churners** and $78k of the $139k monthly revenue lost. This is the first group a retention programme should target."""),
]

if __name__ == "__main__":
    for a, t in F2: insert_after(NB2, a, t)
    ns = {}
    build(ROOT / "notebooks" / "01_data_cleaning_and_quality.ipynb", NB1, ns)
    build(ROOT / "notebooks" / "02_eda_business_analysis.ipynb", NB2, {})
