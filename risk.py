# ============================================================
# FILE: risk.py
# ALGORITHM: Algorithm 4 — Weighted Scoring / MCDA
# PURPOSE: Environmental infiltration risk scoring
# BASED ON: Multi-Criteria Decision Analysis (MCDA)
#           Fischler & Bolles (1981), Fante (1975)
# ============================================================

# ── RISK WEIGHTS ──────────────────────────────────────────────
# Each weight based on military threat assessment research
# Higher weight = more impact on infiltration success
WEIGHTS = {
    'night':       25,   # No natural illumination — cameras less effective
    'fog':         20,   # Severely reduces camera visibility range
    'low_vis':     15,   # Visibility < 3km — movement hard to detect
    'dark_moon':   10,   # New/crescent moon — near-zero natural light
    'overcast':    10,   # Cloud > 70% — aerial detection impaired
    'med_vis':      7,   # Visibility 3-7km — partial concealment
    'calm_wind':    5,   # Wind < 5kt — footsteps and sounds audible
    'high_humid':   5,   # Humidity > 80% — fog formation likely
}

CRITICAL_THRESHOLD = 70
ELEVATED_THRESHOLD = 40


# ── ALGORITHM 4: WEIGHTED RISK SCORING ───────────────────────
def calculate_risk(conditions):
    """
    Calculates infiltration risk score using weighted MCDA.

    Algorithm: Multi-Criteria Decision Analysis (MCDA)
    - Takes 8 environmental conditions as input
    - Assigns pre-defined weight to each condition
    - Sums all weights for final score (0-100)
    - Classifies into threat level

    Input conditions dict:
    {
        'isDay':      bool,   True = daytime
        'fog':        bool,   True = fog present
        'visibility': float,  in km
        'cloudCover': int,    0-100%
        'wind':       float,  in knots
        'humidity':   int,    0-100%
        'moonPhase':  float,  0=new moon, 0.5=full moon, 1=new moon
    }

    Returns: (score, threat_level, breakdown)
    """
    score     = 0
    breakdown = {}

    # ── FACTOR 1: DAYLIGHT / NIGHT ────────────────────────────
    if not conditions.get('isDay', True):
        score              += WEIGHTS['night']
        breakdown['Night']  = WEIGHTS['night']

    # ── FACTOR 2: FOG ─────────────────────────────────────────
    if conditions.get('fog', False):
        score            += WEIGHTS['fog']
        breakdown['Fog']  = WEIGHTS['fog']

    # ── FACTOR 3: VISIBILITY ──────────────────────────────────
    vis = conditions.get('visibility', 10)
    if vis < 3:
        score                      += WEIGHTS['low_vis']
        breakdown['Low Visibility'] = WEIGHTS['low_vis']
    elif vis < 7:
        score                      += WEIGHTS['med_vis']
        breakdown['Med Visibility'] = WEIGHTS['med_vis']

    # ── FACTOR 4: CLOUD COVER ─────────────────────────────────
    if conditions.get('cloudCover', 0) > 70:
        score                  += WEIGHTS['overcast']
        breakdown['Overcast']   = WEIGHTS['overcast']

    # ── FACTOR 5: WIND SPEED ──────────────────────────────────
    if conditions.get('wind', 10) < 5:
        score                   += WEIGHTS['calm_wind']
        breakdown['Calm Wind']   = WEIGHTS['calm_wind']

    # ── FACTOR 6: HUMIDITY ────────────────────────────────────
    if conditions.get('humidity', 50) > 80:
        score                    += WEIGHTS['high_humid']
        breakdown['High Humidity'] = WEIGHTS['high_humid']

    # ── FACTOR 7: MOON PHASE ──────────────────────────────────
    moon = conditions.get('moonPhase', 0.5)
    if moon < 0.2 or moon > 0.8:
        score                   += WEIGHTS['dark_moon']
        breakdown['Dark Moon']   = WEIGHTS['dark_moon']

    # Cap at 100
    score = min(score, 100)

    # ── THREAT LEVEL CLASSIFICATION ───────────────────────────
    if score >= CRITICAL_THRESHOLD:
        level = 'CRITICAL'
    elif score >= ELEVATED_THRESHOLD:
        level = 'ELEVATED'
    else:
        level = 'LOW'

    return score, level, breakdown


def get_risk_advice(score, level):
    """Returns tactical advice based on risk score."""
    if level == 'CRITICAL':
        return "⚠ HEIGHTEN PERIMETER — CONDITIONS FAVOUR INFILTRATOR"
    elif level == 'ELEVATED':
        return "△ ELEVATED CAUTION — MONITOR ALL SECTORS"
    else:
        return "✓ CONDITIONS UNFAVOURABLE FOR INFILTRATION"


def test_risk_scenarios():
    """
    Test the risk engine on multiple weather scenarios.
    Run this to verify algorithm is working correctly.
    """
    scenarios = [
        {
            "name":        "WORST CASE (Night + Fog)",
            "isDay":       False,
            "fog":         True,
            "visibility":  1,
            "wind":        3,
            "humidity":    90,
            "cloudCover":  90,
            "moonPhase":   0.05
        },
        {
            "name":        "NIGHT CLEAR",
            "isDay":       False,
            "fog":         False,
            "visibility":  10,
            "wind":        15,
            "humidity":    60,
            "cloudCover":  10,
            "moonPhase":   0.5
        },
        {
            "name":        "DAY CLEAR",
            "isDay":       True,
            "fog":         False,
            "visibility":  15,
            "wind":        12,
            "humidity":    50,
            "cloudCover":  5,
            "moonPhase":   0.5
        },
        {
            "name":        "FOGGY NIGHT",
            "isDay":       False,
            "fog":         True,
            "visibility":  2,
            "wind":        2,
            "humidity":    92,
            "cloudCover":  100,
            "moonPhase":   0.1
        },
    ]

    print(f"\n{'='*55}")
    print(f"  ARGUS SENTINEL — Infiltration Risk Engine Test")
    print(f"{'='*55}")
    print(f"{'Scenario':<25} {'Score':<8} {'Level':<10} {'Advice'}")
    print(f"{'-'*55}")

    for s in scenarios:
        score, level, breakdown = calculate_risk(s)
        advice = get_risk_advice(score, level)
        print(f"{s['name']:<25} {score:<8} {level:<10} {advice}")

    print(f"{'='*55}\n")


# Run test if executed directly
if __name__ == "__main__":
    test_risk_scenarios()
