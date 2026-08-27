"""
Jadhagam (Tamil Horoscope / Birth Chart) Generator
Calculates Rasi chart, planetary positions, Dasha periods, and predictions.
"""

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding="utf-8", errors="replace")

from datetime import datetime, timedelta
import math


# ─── Constants ───────────────────────────────────────────────────────────────

RASI_NAMES_TAMIL = [
    "மேஷம் (Mesham/Aries)",
    "ரிஷபம் (Rishabam/Taurus)",
    "மிதுனம் (Mithunam/Gemini)",
    "கடகம் (Kadagam/Cancer)",
    "சிம்மம் (Simmam/Leo)",
    "கன்னி (Kanni/Virgo)",
    "துலாம் (Thulam/Libra)",
    "விருச்சிகம் (Viruchigam/Scorpio)",
    "தனுசு (Dhanusu/Sagittarius)",
    "மகரம் (Magaram/Capricorn)",
    "கும்பம் (Kumbam/Aquarius)",
    "மீனம் (Meenam/Pisces)",
]

NAKSHATRA_NAMES = [
    "அஸ்வினி (Ashwini)",
    "பரணி (Bharani)",
    "கார்த்திகை (Krittika)",
    "ரோகிணி (Rohini)",
    "மிருகசீரிஷம் (Mrigashira)",
    "திருவாதிரை (Ardra)",
    "புனர்பூசம் (Punarvasu)",
    "பூசம் (Pushya)",
    "ஆயில்யம் (Ashlesha)",
    "மகம் (Magha)",
    "பூரம் (Purva Phalguni)",
    "உத்திரம் (Uttara Phalguni)",
    "ஹஸ்தம் (Hasta)",
    "சித்திரை (Chitra)",
    "சுவாதி (Swati)",
    "விசாகம் (Vishakha)",
    "அனுஷம் (Anuradha)",
    "கேட்டை (Jyeshtha)",
    "மூலம் (Mula)",
    "பூராடம் (Purva Ashadha)",
    "உத்திராடம் (Uttara Ashadha)",
    "திருவோணம் (Shravana)",
    "அவிட்டம் (Dhanishtha)",
    "சதயம் (Shatabhisha)",
    "பூரட்டாதி (Purva Bhadrapada)",
    "உத்திரட்டாதி (Uttara Bhadrapada)",
    "ரேவதி (Revati)",
]

PLANETS = ["சூரியன்", "சந்திரன்", "செவ்வாய்", "புதன்", "குரு", "சுக்கிரன்", "சனி", "ராகு", "கேது"]
PLANETS_EN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Vimshottari Dasha order and years
DASHA_ORDER = ["கேது", "சுக்கிரன்", "சூரியன்", "சந்திரன்", "செவ்வாய்", "ராகு", "குரு", "சனி", "புதன்"]
DASHA_YEARS = {"கேது": 7, "சுக்கிரன்": 20, "சூரியன்": 6, "சந்திரன்": 10,
               "செவ்வாய்": 7, "ராகு": 18, "குரு": 16, "சனி": 19, "புதன்": 17}

# Nakshatra → ruling planet
NAKSHATRA_LORD = [
    "கேது", "சுக்கிரன்", "சூரியன்", "சந்திரன்", "செவ்வாய்",
    "ராகு", "குரு", "சனி", "புதன்", "கேது", "சுக்கிரன்", "சூரியன்",
    "சந்திரன்", "செவ்வாய்", "ராகு", "குரு", "சனி", "புதன்",
    "கேது", "சுக்கிரன்", "சூரியன்", "சந்திரன்", "செவ்வாய்",
    "ராகு", "குரு", "சனி", "புதன்",
]

PLANET_COLORS = {
    "சூரியன்": "☀️", "சந்திரன்": "🌙", "செவ்வாய்": "🔴",
    "புதன்": "💚", "குரு": "🟡", "சுக்கிரன்": "⚪",
    "சனி": "🔵", "ராகு": "☊", "கேது": "☋",
}


# ─── Astronomical Calculations ────────────────────────────────────────────────

def julian_day(year, month, day, hour=12, minute=0):
    """Convert calendar date to Julian Day Number."""
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
    jd += (hour + minute / 60) / 24
    return jd


def sun_longitude(jd):
    """Approximate Sun longitude (degrees)."""
    T = (jd - 2451545.0) / 36525.0
    L0 = 280.46646 + 36000.76983 * T
    M = math.radians(357.52911 + 35999.05029 * T)
    C = (1.914602 - 0.004817 * T) * math.sin(M)
    C += 0.019993 * math.sin(2 * M)
    C += 0.000289 * math.sin(3 * M)
    sun_lon = L0 + C
    # Ayanamsa (Lahiri) approx
    ayanamsa = 23.85 + (jd - 2415020.0) / 365.25 * 0.01396
    return sun_lon % 360, (sun_lon - ayanamsa) % 360


def moon_longitude(jd):
    """Approximate Moon longitude (degrees)."""
    T = (jd - 2451545.0) / 36525.0
    L = 218.3165 + 481267.8813 * T
    M = math.radians(134.9634 + 477198.8676 * T)
    D = math.radians(297.8502 + 445267.1115 * T)
    F = math.radians(93.2721 + 483202.0175 * T)
    moon_lon = L + 6.2888 * math.sin(M) + 1.2740 * math.sin(2 * D - M)
    moon_lon += 0.6583 * math.sin(2 * D) + 0.2136 * math.sin(2 * M)
    ayanamsa = 23.85 + (jd - 2415020.0) / 365.25 * 0.01396
    return moon_lon % 360, (moon_lon - ayanamsa) % 360


def planet_approximate_longitude(jd, planet):
    """Approximate sidereal longitude for planets."""
    T = (jd - 2451545.0) / 36525.0
    ayanamsa = 23.85 + (jd - 2415020.0) / 365.25 * 0.01396
    params = {
        "செவ்வாய்":  (355.433, 19141.6964, 0.0, 1.8497),
        "புதன்":     (252.251, 149472.6674, 23.4405, 7.0048),
        "குரு":      (34.396,  3034.7460,  0.0,  1.3032),
        "சுக்கிரன்": (181.979, 58517.8156, 3.3947, 3.3947),
        "சனி":       (50.077,  1222.1138,  0.0,  2.4884),
    }
    if planet not in params:
        return 0.0
    L0, rate, _, _ = params[planet]
    lon = (L0 + rate * T) % 360
    return (lon - ayanamsa) % 360


def rahu_longitude(jd):
    """Approximate Rahu (mean node) longitude."""
    T = (jd - 2451545.0) / 36525.0
    rahu = (125.0445 - 1934.1362 * T) % 360
    ayanamsa = 23.85 + (jd - 2415020.0) / 365.25 * 0.01396
    return (rahu - ayanamsa) % 360


def get_rasi(longitude):
    """Return Rasi index (0-11) from longitude."""
    return int(longitude / 30) % 12


def get_nakshatra(longitude):
    """Return Nakshatra index (0-26) from longitude."""
    return int(longitude / (360 / 27)) % 27


def get_nakshatra_pada(longitude):
    """Return pada (1-4) within nakshatra."""
    nak_deg = longitude % (360 / 27)
    pada = int(nak_deg / (360 / 27 / 4)) + 1
    return min(pada, 4)


# ─── Dasha Calculation ────────────────────────────────────────────────────────

def calculate_dasha(birth_dt, moon_lon):
    """Calculate current Vimshottari Dasha and Antardasha."""
    nak_idx = get_nakshatra(moon_lon)
    nak_lord = NAKSHATRA_LORD[nak_idx]

    # Elapsed portion in birth nakshatra
    nak_span = 360 / 27
    nak_start = nak_idx * nak_span
    elapsed_deg = moon_lon - nak_start
    elapsed_frac = elapsed_deg / nak_span
    total_years = DASHA_YEARS[nak_lord]
    elapsed_years = elapsed_frac * total_years
    remaining_years = total_years - elapsed_years

    # Build dasha timeline
    dasha_start_idx = DASHA_ORDER.index(nak_lord)
    timeline = []
    dt = birth_dt
    # first dasha (partial)
    end_dt = dt + timedelta(days=remaining_years * 365.25)
    timeline.append({"planet": nak_lord, "start": dt, "end": end_dt, "years": remaining_years})
    dt = end_dt

    for i in range(1, 9):
        idx = (dasha_start_idx + i) % 9
        planet = DASHA_ORDER[idx]
        yrs = DASHA_YEARS[planet]
        end_dt = dt + timedelta(days=yrs * 365.25)
        timeline.append({"planet": planet, "start": dt, "end": end_dt, "years": yrs})
        dt = end_dt

    # Find current dasha
    today = datetime.now()
    current_dasha = None
    for d in timeline:
        if d["start"] <= today <= d["end"]:
            current_dasha = d
            break

    return timeline, current_dasha


# ─── Predictions ─────────────────────────────────────────────────────────────

PLANET_PREDICTIONS = {
    "சூரியன்": {
        "general": "தலைமைத்துவம், அரசு வேலை, தந்தை தொடர்பான விஷயங்களில் கவனம் செலுத்துங்கள்.",
        "positive": "புகழ், அதிகாரம், ஆரோக்கியம் வளரும்.",
        "negative": "அஹங்காரம் மற்றும் கோபத்தை கட்டுப்படுத்துங்கள்.",
    },
    "சந்திரன்": {
        "general": "மனநிலை, தாய், இல்லத்தில் மாற்றங்கள் ஏற்படும்.",
        "positive": "உணர்வு ரீதியான செழிப்பு, நல்ல நட்பு கிடைக்கும்.",
        "negative": "மனக்கலக்கம் மற்றும் கவலையை தவிர்க்கவும்.",
    },
    "செவ்வாய்": {
        "general": "தைரியம், ஆற்றல், சகோதர உறவுகளில் கவனம்.",
        "positive": "தொழில் முன்னேற்றம், வீர செயல்களில் வெற்றி.",
        "negative": "சண்டை, விபத்து, அவசரப்படாதீர்கள்.",
    },
    "புதன்": {
        "general": "கல்வி, வணிகம், தகவல் தொடர்பு துறைகளில் முன்னேற்றம்.",
        "positive": "புத்திசாலித்தனம் வளரும், நல்ல பேச்சாற்றல் கிடைக்கும்.",
        "negative": "முடிவெடுக்கும் தாமதத்தை தவிர்க்கவும்.",
    },
    "குரு": {
        "general": "ஆசிர்வாதம், வளர்ச்சி, ஞானம் மற்றும் செல்வம் பெருகும்.",
        "positive": "திருமணம், குழந்தை பாக்கியம், வெளிநாட்டு வாய்ப்புகள்.",
        "negative": "அதீத நம்பிக்கை மற்றும் சோம்பேறித்தனம் தவிர்க்கவும்.",
    },
    "சுக்கிரன்": {
        "general": "காதல், திருமணம், கலை, செலவு விஷயங்களில் கவனம்.",
        "positive": "ஆடம்பரம், இன்பம், வாழ்க்கையில் சுகம் கிடைக்கும்.",
        "negative": "அதிகமான சுக போகத்தை தவிர்க்கவும்.",
    },
    "சனி": {
        "general": "கடினமான உழைப்பு, கர்மா, நீதி தொடர்பான காலம்.",
        "positive": "நிலையான முன்னேற்றம், நீண்டகால லாபம் கிடைக்கும்.",
        "negative": "தாமதங்களை ஏற்றுக்கொள்ளுங்கள், பொறுமை அவசியம்.",
    },
    "ராகு": {
        "general": "அசாதாரண வாய்ப்புகள், வெளிநாட்டு தொடர்பு, இலட்சியங்கள்.",
        "positive": "தொழில்நுட்பம், அரசியல், வர்த்தகத்தில் உயர்வு.",
        "negative": "கவலை, மருட்சி, ஆன்மீக ஒழுங்கை கடைப்பிடிக்கவும்.",
    },
    "கேது": {
        "general": "ஆன்மீகம், வைராக்கியம், கடந்த கால கர்மா தீரும்.",
        "positive": "மோட்சம், ஆன்மீக அனுபவம், உள்ளுணர்வு வளரும்.",
        "negative": "தனிமை மற்றும் குழப்பத்தை தவிர்க்க யோகா செய்யுங்கள்.",
    },
}

RASI_CHARACTERISTICS = [
    "தீரம், தலைமைத்துவம், ஆற்றல் மிக்கவர். முன்னோக்கி செல்லும் இயல்பு.",
    "நிலைத்தன்மை, பொருளாதார புத்திசாலித்தனம், சொகுசுக்கு விரும்பும் இயல்பு.",
    "புத்திசாலி, தகவல் தொடர்பு திறமை, இரட்டை இயல்பு கொண்டவர்.",
    "உணர்வுகளை முன்னிறுத்துவர், இல்லம் மற்றும் குடும்பத்தை நேசிப்பர்.",
    "தலைமைத்துவம், கலை, படைப்பாற்றல் கொண்டவர்.",
    "கடினமான உழைப்பு, நுணுக்கம், ஆரோக்கியம் கவனிப்பவர்.",
    "நீதி, சமநிலை, உறவுகளை முக்கியமாக கருதுவர்.",
    "ஆழமான சிந்தனை, மர்மம், தீவிர இயல்பு கொண்டவர்.",
    "தாராள மனது, பயணம், தத்துவம் விரும்புவர்.",
    "கடினமான உழைப்பு, கட்டுப்பாடு, லட்சியம் உள்ளவர்.",
    "புதுமை, சமூக சேவை, சுதந்திர சிந்தனையாளர்.",
    "கனவுகள், ஆன்மீகம், ஈர உணர்வு கொண்டவர்.",
]


# ─── Jadhagam Generator ───────────────────────────────────────────────────────

def generate_jadhagam(name, birth_date, birth_time, birth_place="India"):
    """
    Generate a complete Jadhagam for the given birth details.
    birth_date: datetime.date
    birth_time: datetime.time
    """
    birth_dt = datetime.combine(birth_date, birth_time)
    jd = julian_day(birth_date.year, birth_date.month, birth_date.day,
                    birth_time.hour, birth_time.minute)

    # Calculate planetary longitudes
    _, sun_sid = sun_longitude(jd)
    _, moon_sid = moon_longitude(jd)
    mars_sid = planet_approximate_longitude(jd, "செவ்வாய்")
    mercury_sid = planet_approximate_longitude(jd, "புதன்")
    jupiter_sid = planet_approximate_longitude(jd, "குரு")
    venus_sid = planet_approximate_longitude(jd, "சுக்கிரன்")
    saturn_sid = planet_approximate_longitude(jd, "சனி")
    rahu_sid = rahu_longitude(jd)
    ketu_sid = (rahu_sid + 180) % 360

    planet_lons = {
        "சூரியன்": sun_sid, "சந்திரன்": moon_sid, "செவ்வாய்": mars_sid,
        "புதன்": mercury_sid, "குரு": jupiter_sid, "சுக்கிரன்": venus_sid,
        "சனி": saturn_sid, "ராகு": rahu_sid, "கேது": ketu_sid,
    }

    # Lagna (Ascendant) - simplified: use Sun rasi shifted by birth hour
    lagna_offset = (birth_time.hour * 30 / 24) % 360
    lagna_lon = (sun_sid + lagna_offset) % 360
    lagna_rasi = get_rasi(lagna_lon)

    # Moon Rasi and Nakshatra
    moon_rasi = get_rasi(moon_sid)
    moon_nak = get_nakshatra(moon_sid)
    moon_pada = get_nakshatra_pada(moon_sid)

    # Dasha
    dasha_timeline, current_dasha = calculate_dasha(birth_dt, moon_sid)

    # Build Rasi chart (which planets in which rasi)
    rasi_chart = {i: [] for i in range(12)}
    rasi_chart[lagna_rasi].append("லக்னம்")
    for planet, lon in planet_lons.items():
        rasi_chart[get_rasi(lon)].append(planet)

    return {
        "name": name,
        "birth_dt": birth_dt,
        "birth_place": birth_place,
        "planet_lons": planet_lons,
        "lagna_rasi": lagna_rasi,
        "moon_rasi": moon_rasi,
        "moon_nak": moon_nak,
        "moon_pada": moon_pada,
        "rasi_chart": rasi_chart,
        "dasha_timeline": dasha_timeline,
        "current_dasha": current_dasha,
    }


# ─── Display ──────────────────────────────────────────────────────────────────

def print_jadhagam(data):
    print("\n" + "═" * 60)
    print(f"  ஜாதகம் (JADHAGAM) — {data['name']}")
    print("═" * 60)
    print(f"  பிறந்த தேதி  : {data['birth_dt'].strftime('%d-%m-%Y')}")
    print(f"  பிறந்த நேரம் : {data['birth_dt'].strftime('%I:%M %p')}")
    print(f"  பிறந்த இடம்  : {data['birth_place']}")
    print("─" * 60)

    # Lagna & Moon
    print(f"\n  லக்னம்       : {RASI_NAMES_TAMIL[data['lagna_rasi']]}")
    print(f"  ஜன்ம ராசி   : {RASI_NAMES_TAMIL[data['moon_rasi']]}")
    print(f"  நட்சத்திரம்  : {NAKSHATRA_NAMES[data['moon_nak']]} — பாதம் {data['moon_pada']}")

    # Planetary positions
    print("\n" + "─" * 60)
    print("  கிரக நிலைகள் (Planetary Positions):")
    print("─" * 60)
    for planet, lon in data["planet_lons"].items():
        rasi = RASI_NAMES_TAMIL[get_rasi(lon)]
        nak = NAKSHATRA_NAMES[get_nakshatra(lon)]
        icon = PLANET_COLORS.get(planet, "•")
        print(f"  {icon} {planet:<12} : {rasi:<30} | {nak}")

    # Rasi Chart (text grid)
    print("\n" + "─" * 60)
    print("  ராசி சக்கரம் (Rasi Chart):")
    print("─" * 60)
    _print_rasi_chart(data["rasi_chart"])

    # Dasha
    print("\n" + "─" * 60)
    print("  விம்சோத்தரி தசா (Vimshottari Dasha):")
    print("─" * 60)
    today = datetime.now()
    for d in data["dasha_timeline"]:
        marker = " ◄ நடப்பு" if d["start"] <= today <= d["end"] else ""
        icon = PLANET_COLORS.get(d["planet"], "•")
        print(f"  {icon} {d['planet']:<12} : {d['start'].strftime('%Y-%m-%d')} → {d['end'].strftime('%Y-%m-%d')}{marker}")

    # Predictions
    if data["current_dasha"]:
        cd = data["current_dasha"]["planet"]
        print("\n" + "─" * 60)
        print(f"  கணிப்புகள் — நடப்பு தசா: {PLANET_COLORS.get(cd,'')} {cd}")
        print("─" * 60)
        pred = PLANET_PREDICTIONS.get(cd, {})
        print(f"  பொதுவான விளைவு  : {pred.get('general', '')}")
        print(f"  நேர்மறை பலன்கள் : {pred.get('positive', '')}")
        print(f"  எச்சரிக்கை       : {pred.get('negative', '')}")

    # Rasi characteristics
    moon_rasi = data["moon_rasi"]
    print("\n" + "─" * 60)
    print(f"  ராசி குணநலன்கள் — {RASI_NAMES_TAMIL[moon_rasi]}:")
    print("─" * 60)
    print(f"  {RASI_CHARACTERISTICS[moon_rasi]}")
    print("\n" + "═" * 60 + "\n")


def _print_rasi_chart(rasi_chart):
    """Print a 4x3 South Indian style Rasi chart."""
    # South Indian chart layout (fixed rasi positions)
    # Row0: 12,1,2,3  Row1: 11,_,_,4  Row2: 10,_,_,5  Row3: 9,8,7,6
    layout = [
        [11, 0, 1, 2],
        [10, -1, -1, 3],
        [9, -1, -1, 4],
        [8, 7, 6, 5],
    ]
    cell_w = 13
    border = "+" + ("-" * cell_w + "+") * 4

    for row in layout:
        print("  " + border)
        line = "  |"
        for rasi_idx in row:
            if rasi_idx == -1:
                line += " " * cell_w + "|"
            else:
                planets = rasi_chart.get(rasi_idx, [])
                content = ",".join(p[:3] for p in planets) if planets else ""
                rasi_short = str(rasi_idx + 1)
                cell = f"{rasi_short}:{content}"
                line += cell[:cell_w].ljust(cell_w) + "|"
        print(line)
    print("  " + border)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "★" * 60)
    print("  வரவேற்கிறோம் — ஜாதகம் கணிப்பு மென்பொருள்")
    print("  Welcome to Jadhagam (Tamil Horoscope) Generator")
    print("★" * 60)

    name = input("\n  உங்கள் பெயர் (Name): ").strip() or "அன்பர்"

    print("\n  பிறந்த தேதி உள்ளிடவும் (Enter birth date):")
    day   = int(input("    நாள் (Day  1-31)   : "))
    month = int(input("    மாதம் (Month 1-12) : "))
    year  = int(input("    ஆண்டு (Year)       : "))

    print("\n  பிறந்த நேரம் உள்ளிடவும் (Enter birth time, 24h format):")
    hour   = int(input("    மணி (Hour  0-23)   : "))
    minute = int(input("    நிமிடம் (Minute)   : "))

    place = input("\n  பிறந்த இடம் (Birth place): ").strip() or "India"

    try:
        birth_date = datetime(year, month, day).date()
        birth_time = datetime(year, month, day, hour, minute).time()
    except ValueError as e:
        print(f"\n  பிழை: {e}")
        return

    data = generate_jadhagam(name, birth_date, birth_time, place)
    print_jadhagam(data)

    # Save to file
    save = input("  ஜாதகத்தை கோப்பில் சேமிக்கவா? (Save to file? y/n): ").strip().lower()
    if save == "y":
        filename = f"jadhagam_{name.replace(' ','_')}_{year}{month:02d}{day:02d}.txt"
        import sys, io
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        print_jadhagam(data)
        sys.stdout = old_stdout
        with open(filename, "w", encoding="utf-8") as f:
            f.write(buffer.getvalue())
        print(f"\n  சேமிக்கப்பட்டது: {filename}")


if __name__ == "__main__":
    main()
