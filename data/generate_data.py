"""
TikTok User Retention — Synthetic Data Generator
Generates 50,000 users with cohort signup dates, daily engagement,
feature usage, and churn events.
Run: python data/generate_data.py
Output: data/tiktok_retention_data.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# ── Config ──────────────────────────────────────────────────────────────────
SEED = 42
N_USERS = 50_000
START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2024, 12, 31)
OBSERVATION_DAYS = 90
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "tiktok_retention_data.csv")

np.random.seed(SEED)
rng = np.random.default_rng(SEED)

# ── User segments ────────────────────────────────────────────────────────────
SEGMENTS = ["Casual", "Creator", "Power User", "Lurker"]
SEGMENT_WEIGHTS = [0.40, 0.20, 0.15, 0.25]

SEGMENT_PARAMS = {
    "Casual":     dict(base_retention=0.55, weekly_churn=0.08, avg_sessions=2.5),
    "Creator":    dict(base_retention=0.72, weekly_churn=0.04, avg_sessions=5.1),
    "Power User": dict(base_retention=0.85, weekly_churn=0.02, avg_sessions=8.3),
    "Lurker":     dict(base_retention=0.35, weekly_churn=0.14, avg_sessions=1.2),
}

CHANNELS = ["Organic", "Paid Social", "Referral", "Influencer", "App Store"]
CHANNEL_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.10]

DEVICES = ["iOS", "Android"]
DEVICE_WEIGHTS = [0.52, 0.48]

COUNTRIES = ["UK", "Germany", "France", "Italy", "Spain", "Netherlands", "Poland", "Other"]
COUNTRY_WEIGHTS = [0.22, 0.18, 0.15, 0.10, 0.09, 0.08, 0.07, 0.11]

# ── Generate users ────────────────────────────────────────────────────────────
print(f"Generating {N_USERS:,} synthetic TikTok users...")

signup_day_offsets = rng.integers(0, (END_DATE - START_DATE).days, size=N_USERS)
signup_dates = [START_DATE + timedelta(days=int(d)) for d in signup_day_offsets]

segments  = rng.choice(SEGMENTS, size=N_USERS, p=SEGMENT_WEIGHTS)
channels  = rng.choice(CHANNELS,  size=N_USERS, p=CHANNEL_WEIGHTS)
devices   = rng.choice(DEVICES,   size=N_USERS, p=DEVICE_WEIGHTS)
countries = rng.choice(COUNTRIES, size=N_USERS, p=COUNTRY_WEIGHTS)

AGE_GROUPS = ["13-17", "18-24", "25-34", "35-44", "45+"]
AGE_WEIGHTS = [0.14, 0.35, 0.28, 0.14, 0.09]
age_groups = rng.choice(AGE_GROUPS, size=N_USERS, p=AGE_WEIGHTS)

# ── Simulate retention trajectory per user ───────────────────────────────────
records = []

for i in range(N_USERS):
    seg    = segments[i]
    params = SEGMENT_PARAMS[seg]

    survival_prob = 1 - params["weekly_churn"]
    geom_p = max(0.001, min(0.999, 1 - survival_prob ** (1/7)))

    will_churn = rng.random() > params["base_retention"]
    if will_churn:
        days_until_churn = int(rng.geometric(geom_p))
        days_until_churn = max(1, min(days_until_churn, OBSERVATION_DAYS))
    else:
        days_until_churn = OBSERVATION_DAYS + 1

    churned = days_until_churn <= OBSERVATION_DAYS
    active_days_observed = days_until_churn if churned else OBSERVATION_DAYS

    active_day_count = rng.binomial(active_days_observed, params["base_retention"])
    total_sessions   = int(rng.poisson(params["avg_sessions"]) * active_day_count)
    total_sessions   = max(0, total_sessions)

    avg_min_per_session = rng.normal(12, 4)
    total_watch_minutes = max(0, int(total_sessions * avg_min_per_session))

    used_fyp        = rng.random() < 0.95
    used_search     = rng.random() < (0.60 if seg == "Power User" else 0.35)
    used_live       = rng.random() < (0.45 if seg == "Creator" else 0.10)
    used_shop       = rng.random() < 0.25
    used_duet       = rng.random() < (0.50 if seg == "Creator" else 0.15)
    posted_video    = rng.random() < (0.80 if seg == "Creator" else 0.08)
    video_count     = int(rng.poisson(8)) if posted_video else 0

    notif_enabled = rng.random() < 0.65

    d1_retained  = active_days_observed >= 1  and rng.random() < 0.70
    d7_retained  = active_days_observed >= 7  and rng.random() < 0.45
    d30_retained = active_days_observed >= 30 and rng.random() < 0.28

    signup_dt = signup_dates[i]
    cohort_week  = signup_dt.strftime("%Y-W%V")
    cohort_month = signup_dt.strftime("%Y-%m")

    records.append({
        "user_id":              f"U{i+1:06d}",
        "signup_date":          signup_dt.strftime("%Y-%m-%d"),
        "cohort_week":          cohort_week,
        "cohort_month":         cohort_month,
        "segment":              seg,
        "acquisition_channel":  channels[i],
        "device":               devices[i],
        "country":              countries[i],
        "age_group":            age_groups[i],
        "churned":              int(churned),
        "days_active":          active_day_count,
        "days_until_churn":     days_until_churn,
        "total_sessions":       total_sessions,
        "total_watch_minutes":  total_watch_minutes,
        "videos_posted":        video_count,
        "used_fyp":             int(used_fyp),
        "used_search":          int(used_search),
        "used_live":            int(used_live),
        "used_shop":            int(used_shop),
        "used_duet":            int(used_duet),
        "notification_enabled": int(notif_enabled),
        "d1_retained":          int(d1_retained),
        "d7_retained":          int(d7_retained),
        "d30_retained":         int(d30_retained),
    })

df = pd.DataFrame(records)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print(f"Saved → {OUTPUT_PATH}  ({len(df):,} rows × {len(df.columns)} cols)")
print(f"\nChurn rate: {df['churned'].mean():.1%}")
print(f"D1 retention: {df['d1_retained'].mean():.1%}")
print(f"D7 retention: {df['d7_retained'].mean():.1%}")
print(f"D30 retention: {df['d30_retained'].mean():.1%}")