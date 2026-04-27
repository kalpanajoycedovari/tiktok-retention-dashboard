# TikTok User Retention Dashboard

A end-to-end data analytics project analysing user retention, churn behaviour,
and feature impact across a synthetic TikTok EMEA user base of 50,000 users
spanning January to December 2024.

Live demo: https://tiktok-retention-dashboard.streamlit.app

---

## Why User Retention Matters

Acquiring a user is the easy part. Keeping them is where platforms either
build a business or burn through their growth budget.

For short-form video platforms like TikTok, Instagram Reels, and YouTube
Shorts, retention is everything. The entire revenue model — advertising —
depends on daily active users, session length, and how often people come
back. A user who installs TikTok and opens it twice before leaving generates
almost no value. A user who comes back every day for 90 days is worth
significantly more in ad impressions, data signals, and potential creator
revenue.

TikTok's particular challenge is that its core mechanic — the For You Page
algorithm — is both its biggest strength and its biggest retention risk. It
hooks users fast, but if the algorithm misjudges someone's interests in the
first few sessions, that user churns before the model ever gets a chance to
correct itself. This is why D1 retention (did the user come back the next
day?) is watched so closely internally at these companies. It is a signal of
whether the product delivered on its first impression.

Competitors face the same problem differently. Instagram Reels benefits from
the social graph — users come back because their friends are there, not just
because the content is good. YouTube Shorts has the advantage of search
intent and long-form content as a retention anchor. TikTok has neither of
those safety nets, which makes its retention engineering more aggressive and
more interesting to study.

Understanding where users drop off, which segments churn fastest, and which
features actually increase the probability of a user returning on Day 30 is
the kind of analysis that sits at the intersection of product, data science,
and business strategy. That is what this project explores.

---

## Dataset

The dataset is synthetically generated using `data/generate_data.py` and
produces 50,000 user records with 24 columns covering demographics, behaviour,
feature usage, and retention outcomes.

### Distributions and modelling choices

**User segments** are assigned using weighted random sampling across four
types: Casual (40%), Lurker (25%), Creator (20%), and Power User (15%). These
weights reflect a realistic platform composition — most users consume content
passively, a smaller group creates it, and a very small group uses everything
obsessively. Each segment has its own base retention probability and weekly
churn rate, which drives the rest of the simulation.

**Churn timing** is modelled using a geometric distribution. The geometric
distribution is appropriate here because it models the number of days until
a first failure (churn) in a series of independent Bernoulli trials — each
day, a user either stays or leaves. The daily churn probability is derived
from the segment's weekly churn rate using the formula:
daily_p = 1 - (1 - weekly_churn) ^ (1/7)
This gives Power Users a very flat survival curve (they take a long time to
churn) and Lurkers a steep early drop-off, which matches how these user types
behave on real platforms.

**Whether a user churns at all** within the 90-day observation window is
determined by a Bernoulli draw against the segment's base retention
probability. Users who survive this draw are marked as retained for the full
window. This creates a realistic mix of churned and retained users rather than
everyone eventually churning.

**Session counts** follow a Poisson distribution centred on each segment's
average sessions per active day. Poisson is the natural choice for count data
where events occur independently at a known average rate — how many times
someone opens an app in a day fits this model well.

**Watch time** is computed as sessions multiplied by a per-session duration
drawn from a normal distribution (mean 12 minutes, standard deviation 4
minutes), clipped at zero. This reflects real-world watch time distributions
where most sessions cluster around a typical length with some variance.

**Acquisition channels** (Organic, Paid Social, Referral, Influencer, App
Store) and **countries** (UK, Germany, France, Italy, Spain, Netherlands,
Poland, Other) are sampled from weighted categorical distributions reflecting
a realistic EMEA market mix.

**Feature flags** (FYP, Search, Live, Shop, Duet, Push Notifications) are
assigned with segment-conditional probabilities. Creators are more likely to
use Live and Duet. Power Users are more likely to use Search. This means
feature adoption correlates with retention in a non-trivial way, which makes
the feature impact analysis more meaningful than if features were randomly
assigned.

**Retention milestones** (D1, D7, D30) are computed as Bernoulli draws
conditional on the user having been active long enough to reach that day.
The base probabilities (70%, 45%, 28%) are calibrated to sit in a realistic
range for a consumer social platform.

---
---

## Dashboard Features

- **KPI cards** — overall churn rate, D1/D7/D30 retention with baseline comparison
- **Cohort heatmap** — monthly retention rates across the full year
- **Retention curves** — D1/D7/D30 breakdown by segment and acquisition channel
- **Churn analysis** — days-to-churn distribution, churn by segment and age group
- **Feature impact** — which product features correlate with higher D30 retention
- **Engagement scatter** — sessions vs watch time coloured by segment
- **Sidebar filters** — filter everything by segment, channel, device, country, date range

---

## Notebook Analysis

The Jupyter notebook goes deeper than the dashboard:

- Cohort retention heatmap with seaborn
- Survival curves per segment (Kaplan-Meier style) — probability of a user
  still being active at each day from 1 to 90
- Feature adoption impact bar charts
- Logistic regression churn predictor with ROC curve and feature coefficients

---

## Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt

# Generate the dataset
python data/generate_data.py

# Run the dashboard
streamlit run streamlit_app/app.py

# Open the notebook
jupyter notebook notebooks/TikTok_Retention_Analysis.ipynb
```

---

## Skills and Tools

`Python` · `pandas` · `NumPy` · `Streamlit` · `Plotly` · `Matplotlib` ·
`Seaborn` · `scikit-learn` · cohort analysis · survival analysis ·
churn modelling · logistic regression · synthetic data generation

---

## Author

Kalpana Joyce Dovari
MSc Artificial Intelligence — Northumbria University London
[LinkedIn](https://www.linkedin.com/in/kalpanajoycedovari) ·
[GitHub](https://github.com/kalpanajoycedovari) ·
[Portfolio](https://my-portfolio-taupe-kappa-13.vercel.app)
