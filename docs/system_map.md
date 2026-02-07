# 108 System Map — How Everything Connects

## The Big Picture

Jyotish is a system that answers three questions about a person's life:
- **WHAT** will happen? → Yogas, Doshas, House lords, Planet placements
- **WHEN** will it happen? → Dashas, Transits, Muhurta
- **WHY** is it happening now? → Current Dasha + Current Transits overlaid on natal chart

108 models this as 5 layers:

```
┌─────────────────────────────────────────────────────┐
│  GUIDE (agent.py)                                   │
│  The AI that talks to the user, combines all layers │
├─────────────────────────────────────────────────────┤
│  CONTEXT (timing)          │  SELF (patterns)       │
│  WHEN things happen        │  WHAT things happen    │
│  • Dashas (life periods)   │  • Yogas (combinations)│
│  • Transits (now)          │  • Doshas (afflictions)│
│  • Muhurta (timing)        │  • Strength (power)   │
│  • Progressions            │  • Jaimini analysis    │
├────────────────────────────┴────────────────────────┤
│  COSMOS (calculations)                              │
│  The raw astronomy — planets, houses, nakshatras    │
├─────────────────────────────────────────────────────┤
│  KNOWLEDGE (JSON rules + definitions)               │
│  The Jyotish wisdom — 522 yogas, 42 doshas, etc.   │
└─────────────────────────────────────────────────────┘
```

---

## Part 1: The Foundation — 9 Planets, 12 Signs, 27 Nakshatras, 12 Houses

### The 9 Grahas (Planets)

There are 9 grahas. 7 are physical celestial bodies. 2 (Rahu & Ketu) are mathematical points.

```
PHYSICAL PLANETS (7)                    SHADOW PLANETS (2)
┌─────────┬──────────┬───────────┐     ┌─────────────────────────────────┐
│ Planet  │ Rules    │ Karaka of │     │ Rahu & Ketu are the two points  │
├─────────┼──────────┼───────────┤     │ where the Moon's orbital plane  │
│ Sun ☉   │ Leo      │ Soul,     │     │ crosses the Sun's apparent path │
│         │          │ Father    │     │ (the ecliptic).                 │
│ Moon ☽  │ Cancer   │ Mind,     │     │                                 │
│         │          │ Mother    │     │ Rahu = North Node (ascending)   │
│ Mars ♂  │ Ari,Sco  │ Energy,   │     │   → Where you're GOING          │
│         │          │ Siblings  │     │   → Obsession, amplification    │
│ Mercury │ Gem,Vir  │ Intellect,│     │   → Material desires            │
│         │          │ Speech    │     │   → Foreign, unconventional     │
│ Jupiter │ Sag,Pis  │ Wisdom,   │     │                                 │
│         │          │ Children  │     │ Ketu = South Node (descending)  │
│ Venus ♀ │ Tau,Lib  │ Love,     │     │   → Where you've BEEN           │
│         │          │ Wealth    │     │   → Detachment, liberation      │
│ Saturn ♄│ Cap,Aqu  │ Karma,    │     │   → Spiritual, past-life       │
│         │          │ Discipline│     │   → Sudden, unexpected          │
└─────────┴──────────┴───────────┘     │                                 │
                                       │ They are ALWAYS exactly opposite│
                                       │ (180° apart). Always retrograde.│
                                       │ They don't "own" signs but act  │
                                       │ like the lord of the sign they  │
                                       │ occupy.                         │
                                       └─────────────────────────────────┘
```

**Why Rahu/Ketu matter so much:** They represent the karmic axis — what you're compulsively drawn toward (Rahu) vs what you've already mastered and need to let go of (Ketu). In your chart, Rahu is in your 2nd house (wealth obsession) and Ketu in 8th (detachment from hidden/occult things).

### How Planets Own Signs (Lordship)

Each planet rules 1 or 2 signs. This creates the **lordship** system — the foundation of everything:

```
        ♌ Leo          ♋ Cancer
        (Sun)          (Moon)
          │              │
    ♍ Virgo        ♊ Gemini
    (Mercury)      (Mercury)
          │              │
    ♎ Libra        ♉ Taurus
    (Venus)        (Venus)
          │              │
    ♏ Scorpio      ♈ Aries
    (Mars)         (Mars)
          │              │
    ♐ Sagittarius  ♓ Pisces
    (Jupiter)      (Jupiter)
          │              │
    ♑ Capricorn    ♒ Aquarius
    (Saturn)       (Saturn)
```

Sun and Moon each rule ONE sign. The other 5 planets rule TWO signs each.

### The 12 Houses (Bhavas)

Houses are WHERE in life things happen. They start from the Lagna (Ascendant sign):

```
┌──────────────┬──────────────────────────────────────────────────┐
│ House        │ What It Governs                                  │
├──────────────┼──────────────────────────────────────────────────┤
│ 1st (Lagna)  │ Self, body, personality, health, appearance      │
│ 2nd (Dhana)  │ Wealth, family, speech, food, stored money       │
│ 3rd (Sahaja) │ Siblings, courage, short travel, communication   │
│ 4th (Sukha)  │ Mother, home, property, vehicles, education      │
│ 5th (Putra)  │ Children, intelligence, speculation, creativity  │
│ 6th (Ari)    │ Enemies, disease, debt, daily work, competition  │
│ 7th (Yuvati) │ Marriage, partnerships, business, public dealing │
│ 8th (Randhra)│ Death, transformation, hidden things, insurance  │
│ 9th (Dharma) │ Fortune, father, guru, religion, foreign travel  │
│ 10th (Karma) │ Career, status, public image, government         │
│ 11th (Labha) │ Gains, income, friends, wishes fulfilled         │
│ 12th (Vyaya) │ Losses, foreign lands, spirituality, expenses    │
├──────────────┼──────────────────────────────────────────────────┤
│ CATEGORIES:  │                                                  │
│ Kendra       │ 1, 4, 7, 10 — pillars of life (strongest)       │
│ Trikona      │ 1, 5, 9 — fortune/dharma (most benefic)         │
│ Dusthana     │ 6, 8, 12 — suffering/challenges                 │
│ Upachaya     │ 3, 6, 10, 11 — growth through effort            │
│ Maraka       │ 2, 7 — death-inflicting                         │
└──────────────┴──────────────────────────────────────────────────┘
```

### The 27 Nakshatras (Lunar Mansions)

Each sign (30°) contains 2.25 nakshatras (13°20' each). Each nakshatra has 4 padas (3°20' each).

**Nakshatras add the PERSONALITY layer** — signs tell you WHAT, nakshatras tell you HOW.

```
Aries: Ashwini → Bharani → Krittika(1)
Taurus: Krittika(2-4) → Rohini → Mrigashira(1-2)
Gemini: Mrigashira(3-4) → Ardra → Punarvasu(1-3)
Cancer: Punarvasu(4) → Pushya → Ashlesha
Leo: Magha → Purva Phalguni → Uttara Phalguni(1)
Virgo: Uttara Phalguni(2-4) → Hasta → Chitra(1-2)
Libra: Chitra(3-4) → Swati → Vishakha(1-3)
Scorpio: Vishakha(4) → Anuradha → Jyeshtha
Sagittarius: Mula → Purva Ashadha → Uttara Ashadha(1)
Capricorn: Uttara Ashadha(2-4) → Shravana → Dhanishtha(1-2)
Aquarius: Dhanishtha(3-4) → Shatabhisha → Purva Bhadrapada(1-3)
Pisces: Purva Bhadrapada(4) → Uttara Bhadrapada → Revati
```

**Each nakshatra has a ruling planet** → This determines the Vimshottari Dasha sequence:

| Nakshatra Lord | Dasha Duration | Nakshatras Ruled |
|---------------|---------------|-----------------|
| Ketu | 7 years | Ashwini, Magha, Mula |
| Venus | 20 years | Bharani, P.Phalguni, P.Ashadha |
| Sun | 6 years | Krittika, U.Phalguni, U.Ashadha |
| Moon | 10 years | Rohini, Hasta, Shravana |
| Mars | 7 years | Mrigashira, Chitra, Dhanishtha |
| Rahu | 18 years | Ardra, Swati, Shatabhisha |
| Jupiter | 16 years | Punarvasu, Vishakha, P.Bhadrapada |
| Saturn | 19 years | Pushya, Anuradha, U.Bhadrapada |
| Mercury | 17 years | Ashlesha, Jyeshtha, Revati |

**Your Moon** is in Purva Bhadrapada → Jupiter-ruled → Your Mahadasha sequence starts from Jupiter.

---

## Part 2: How Lordship Creates Meaning — YOUR Chart (Libra Lagna)

This is where the magic happens. The SAME planet gives DIFFERENT results for DIFFERENT Lagnas because it lords different houses.

### Your House-Lord Map (Libra Lagna)

```
┌──────────┬──────────┬───────────┬─────────────────────────────────────┐
│ House    │ Sign     │ Lord      │ What This Lord Carries              │
├──────────┼──────────┼───────────┼─────────────────────────────────────┤
│ 1st      │ Libra    │ Venus     │ Self, body, identity                │
│ 2nd      │ Scorpio  │ Mars      │ Wealth, family, speech              │
│ 3rd      │ Sag      │ Jupiter   │ Siblings, courage, effort           │
│ 4th      │ Capricorn│ SATURN ★  │ Home, property, education, mother   │
│ 5th      │ Aquarius │ SATURN ★  │ Children, intelligence, speculation │
│ 6th      │ Pisces   │ Jupiter   │ Enemies, debt, daily work           │
│ 7th      │ Aries    │ Mars      │ Marriage, partnerships              │
│ 8th      │ Taurus   │ Venus     │ Transformation, hidden things       │
│ 9th      │ Gemini   │ Mercury   │ Fortune, father, guru, luck         │
│ 10th     │ Cancer   │ Moon      │ Career, status, public image        │
│ 11th     │ Leo      │ Sun       │ Gains, income, wishes               │
│ 12th     │ Virgo    │ Mercury   │ Expenses, foreign, spirituality     │
└──────────┴──────────┴───────────┴─────────────────────────────────────┘

★ Saturn rules BOTH 4th (kendra) AND 5th (trikona) = YOGA KARAKA
  → The single most beneficial planet for Libra Lagna
  → Every Saturn period/transit is amplified positive
```

### Your Planet Placement Map

```
YOUR CHART — What each planet DOES for you:

┌────────────┬────────────┬────────┬──────────────────────────────────────────────┐
│ Planet     │ Placed In  │ House  │ What It Means                                │
├────────────┼────────────┼────────┼──────────────────────────────────────────────┤
│ Mercury    │ Libra 28°  │ H1     │ 9th lord (fortune) + 12th lord (foreign)     │
│            │            │        │ in Lagna = fortune through self, foreign      │
│            │            │        │ connections, spiritual intellect              │
├────────────┼────────────┼────────┼──────────────────────────────────────────────┤
│ Sun        │ Scorpio 17°│ H2     │ 11th lord (gains) in 2nd (wealth)            │
│            │            │        │ = income flows into savings. DHANA YOGA.     │
├────────────┼────────────┼────────┼──────────────────────────────────────────────┤
│ Rahu       │ Scorpio 28°│ H2     │ Amplifies 2nd house (wealth obsession).      │
│            │            │        │ Rahu in 2nd = unconventional wealth paths,   │
│            │            │        │ tech/foreign money. Can give harsh speech.    │
├────────────┼────────────┼────────┼──────────────────────────────────────────────┤
│ Venus      │ Sag 29°   │ H3     │ Lagna lord in 3rd = self expressed through   │
│            │            │        │ effort, communication, skills. Self-made.    │
├────────────┼────────────┼────────┼──────────────────────────────────────────────┤
│ SATURN ★   │ Cap 19°   │ H4     │ YOGA KARAKA in OWN SIGN in kendra.           │
│            │ (own sign) │        │ 4th+5th lord in 4th = SASA YOGA.             │
│            │            │        │ Property, education, vehicles, mother.        │
│            │            │        │ Disciplined, structured, powerful foundation.│
├────────────┼────────────┼────────┼──────────────────────────────────────────────┤
│ Moon       │ Aqu 24°   │ H5     │ 10th lord (career) in 5th (intelligence)     │
│            │            │        │ = career through brains, creativity.         │
│            │            │        │ Also in Saturn's sign = career needs patience│
├────────────┼────────────┼────────┼──────────────────────────────────────────────┤
│ Ketu       │ Taurus 28°│ H8     │ Detachment from hidden/occult. Sudden        │
│            │            │        │ transformations. Past-life spiritual energy   │
│            │            │        │ in house of death/rebirth. Can give sudden   │
│            │            │        │ inheritance or insurance money.              │
├────────────┼────────────┼────────┼──────────────────────────────────────────────┤
│ Mars (R)   │ Cancer 3° │ H10    │ 2nd+7th lord in 10th. DEBILITATED but        │
│            │ (debil.)   │        │ RETROGRADE (Neecha Bhanga potential).         │
│            │            │        │ Wealth + partnerships through career.        │
│            │            │        │ Struggles in career but also drives ambition.│
├────────────┼────────────┼────────┼──────────────────────────────────────────────┤
│ Jupiter    │ Virgo 16° │ H12    │ 3rd+6th lord in 12th = Viparita Raja Yoga    │
│            │            │        │ (dusthana lord in dusthana = reversal).      │
│            │            │        │ Foreign connections, spiritual growth.       │
│            │            │        │ Enemies defeated through divine grace.       │
└────────────┴────────────┴────────┴──────────────────────────────────────────────┘
```

---

## Part 3: How Yogas Form — Combinations Create Destiny

Yogas are specific planetary combinations that produce specific results. They form when planets relate to each other through:

```
HOW YOGAS FORM:

1. CONJUNCTION — Two planets in the same sign
   Example: Sun + Rahu in your 2nd house

2. ASPECT — Planet "sees" another house (special drishti)
   • All planets aspect 7th from themselves (opposite house)
   • Mars ALSO aspects 4th and 8th from itself
   • Jupiter ALSO aspects 5th and 9th from itself
   • Saturn ALSO aspects 3rd and 10th from itself
   • Rahu/Ketu aspect 5th, 7th, 9th from themselves

3. LORDSHIP — Planet rules a specific house and sits in another
   Example: Your Sun (11th lord) sitting in 2nd = Dhana Yoga

4. EXCHANGE — Two planets sitting in each other's signs (Parivartana)

5. POSITION — Planet in specific dignity (exalted, own sign, debilitated)
   Example: Your Saturn in own sign Capricorn in kendra = Sasa Yoga
```

### Yoga Categories We Have (522 total)

```
YOGA MAP:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  PANCHA MAHAPURUSHA (5)     — Planet in own/exalted in kendra   │
│  ├── Ruchaka (Mars)         — Warrior, commander                │
│  ├── Bhadra (Mercury)       — Scholar, communicator             │
│  ├── Hamsa (Jupiter)        — Wise, spiritual                   │
│  ├── Malavya (Venus)        — Artistic, luxurious               │
│  └── SASA (Saturn) ★ YOURS  — Disciplined, powerful, authority  │
│                                                                 │
│  RAJA YOGAS (~50+)          — Kendra lord + Trikona lord combo  │
│  ├── 1st+5th lords connect  — Self + intelligence               │
│  ├── 1st+9th lords connect  — Self + fortune                    │
│  ├── 4th+5th lords connect ★— YOUR Saturn does BOTH alone!      │
│  └── etc.                                                       │
│                                                                 │
│  DHANA YOGAS (~40+)         — Wealth combinations               │
│  ├── 2nd lord + 11th lord   — Wealth + gains                    │
│  ├── 5th lord + 9th lord    — Luck + speculation                │
│  └── 11th lord in 2nd ★     — YOUR Sun (gains→wealth)           │
│                                                                 │
│  CHANDRA (Moon) YOGAS (~30) — Based on Moon's position          │
│  ├── Gajakesari             — Moon+Jupiter in kendra from each  │
│  ├── Sunapha/Anapha         — Planets 2nd/12th from Moon        │
│  └── Kemdrum                — No planets around Moon (dosha)    │
│                                                                 │
│  NABHAS YOGAS (~32)         — Based on planetary patterns       │
│  PARIVARTANA YOGAS (~12)    — Based on sign exchange            │
│  NEECHA BHANGA (~8)         — Debilitation cancellation         │
│  VIPARITA RAJA (~6)         — Dusthana lord in dusthana         │
│  SANYASA YOGAS (~10)        — Renunciation combinations         │
│  ARISHTA YOGAS (~30+)       — Health/misfortune indicators      │
│  DARIDRA YOGAS (~20+)       — Poverty/struggle indicators       │
│  NAKSHATRA YOGAS (~50+)     — Based on nakshatra positions      │
│  SPECIAL YOGAS (~200+)      — Miscellaneous combinations        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Doshas — The Afflictions (55 total)

```
DOSHA MAP:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  GRAHA DOSHAS (planet-based, ~20)                               │
│  ├── Mangal Dosha      — Mars in 1/2/4/7/8/12 (marriage delay) │
│  ├── Kaal Sarp Dosha   — All planets between Rahu-Ketu axis    │
│  ├── Pitra Dosha       — Sun+Rahu/Saturn (ancestral karma)     │
│  ├── Guru Chandal      — Jupiter+Rahu (corrupted wisdom)       │
│  ├── Shapit Dosha      — Saturn+Rahu (cursed past life)        │
│  ├── Kemdrum Dosha     — No planets around Moon (loneliness)   │
│  ├── Grahan Dosha      — Sun/Moon with Rahu/Ketu (eclipse)     │
│  └── Individual planet doshas (Shani, Rahu, Ketu, etc.)        │
│                                                                 │
│  BHAVA DOSHAS (house-based, ~9)                                 │
│  ├── Dhan Dosha        — 2nd house affliction (wealth loss)     │
│  ├── Putra Dosha       — 5th house affliction (children issues) │
│  ├── Vivah Dosha       — 7th house affliction (marriage issues) │
│  ├── Karma Dosha       — 10th house affliction (career blocks)  │
│  └── etc.                                                       │
│                                                                 │
│  NAKSHATRA DOSHAS (4)                                           │
│  ├── Gandmool Dosha    — Birth in junction nakshatras           │
│  ├── Nadi Dosha        — Same nadi in matching (fatal)          │
│  ├── Bhakoot Dosha     — Incompatible Moon signs in matching    │
│  └── Gana Dosha        — Incompatible temperaments in matching  │
│                                                                 │
│  TRANSIT DOSHAS (2)                                             │
│  ├── Sade Sati         — Saturn transiting 12th/1st/2nd from   │
│  │                       Moon (7.5 years of testing)            │
│  └── Dhaiya            — Saturn in 4th/8th from Moon (2.5 yrs) │
│                                                                 │
│  YOGA DOSHAS (5)                                                │
│  ├── Daridra Dosha     — Poverty combinations                   │
│  ├── Kemdrum Chandra   — Isolated Moon                          │
│  └── etc.                                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 4: How TIMING Works — The Dasha System

**The birth chart is static. Dashas make it dynamic.**

The Vimshottari Dasha system divides 120 years into 9 planetary periods. The sequence starts from the nakshatra lord of your Moon at birth.

```
THE DASHA HIERARCHY (3 levels):

MAHADASHA (major period)
└── ANTARDASHA (sub-period) — 9 per Mahadasha
    └── PRATYANTARDASHA (sub-sub-period) — 9 per Antardasha

Total: 9 × 9 × 9 = 729 unique time periods

YOUR TIMELINE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Jupiter MD    Saturn MD              Mercury MD          Ketu  Venus
(16 yrs)      (19 yrs)               (17 yrs)           (7yr) (20yr)
1992──────2003─────────────2022──────────────2039──────2046───2066
ages 0-11     ages 11-30              ages 30-47
3rd+6th lord  YOGA KARAKA ★★★         9th+12th lord
in 12th       4th+5th lord in 4th    in 1st (Lagna)
              OWN SIGN, SASA YOGA    CURRENT ←←←
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### How Dasha Lords Activate Yogas

**This is the critical insight:** A yoga exists in your chart permanently, but it only ACTIVATES during the dasha of the planets involved.

```
YOGA ACTIVATION MAP:

Sasa Yoga (Saturn own sign in kendra)
├── ACTIVE during: Saturn MD (2003-2022) ★ ages 11-30
├── ACTIVE during: Any Saturn AD within other MDs
└── Saturn aspects from H4: H6 (enemies), H10 (career), H1 (self)
    → These houses get Saturn's Yoga Karaka energy during Saturn periods

Dhana Yoga (Sun 11th lord in 2nd)
├── ACTIVE during: Sun AD within any MD
├── Semi-active when: Transiting Sun hits 2nd or 11th house
└── In Mercury MD currently → Mercury-Sun AD will be wealth period

Viparita Raja (Jupiter 3rd+6th lord in 12th)
├── ACTIVE during: Jupiter AD within any MD
├── Already activated: Jupiter MD (1992-2003, childhood)
└── Means: Enemies/competition defeated through unseen forces
```

### Alternative Dasha Systems We Support

| System | Cycle | Based On | When to Use |
|--------|-------|----------|-------------|
| **Vimshottari** | 120 years | Moon's nakshatra | PRIMARY — always |
| **Yogini** | 36 years | Moon's nakshatra | Confirmatory timing |
| **Ashtottari** | 108 years | Moon's nakshatra | When Rahu in kendra/trikona from Lagna lord |
| **Chara (Jaimini)** | 108 years | Lagna sign | Sign-based timing |
| **Narayana** | 108 years | Lagna sign | Advanced Jaimini timing |

---

## Part 5: How Transits Overlay — The NOW Layer

Transits are where planets are RIGHT NOW in the sky vs where they were at birth.

```
TRANSIT ANALYSIS LAYERS:

1. GOCHARA (from Moon)
   → Transit planets counted from natal Moon sign
   → Quick emotional/mental effects
   → Moon moves fastest (2.5 days/sign) → daily mood
   → Saturn moves slowest (2.5 years/sign) → Sade Sati

2. TRANSIT OVER NATAL POSITIONS
   → When a transit planet crosses the exact degree of a natal planet
   → Activates that natal planet's significations
   → Example: Transit Venus crossing your natal Moon at 24° Aquarius
     = Lagna lord (self) meets 10th lord (career) by transit

3. TRANSIT THROUGH NATAL HOUSES
   → Which of YOUR 12 houses is each transit planet currently in?
   → Example: Jupiter retrograde in your 9th (fortune) = slow-building luck

4. NAKSHATRA-LEVEL TRANSITS
   → Planet transiting through a specific nakshatra
   → Adds fine-grained timing (243 planet × nakshatra combinations)

5. ASHTAKAVARGA STRENGTH
   → Each planet has 0-8 "bindus" (benefic points) in each sign
   → When transiting through a high-bindu sign → good results
   → When through low-bindu sign → weak/bad results
```

---

## Part 6: Planetary Strength — How POWERFUL Each Planet Is

Not all planets are equally effective. Strength determines how much of its promise a planet actually delivers:

```
STRENGTH SYSTEMS:

SHADBALA (Six-fold Strength) — PRIMARY
├── Sthana Bala (positional) — dignity, own sign, exalted, etc.
├── Dig Bala (directional) — strongest in specific houses
│   ├── Jupiter/Mercury → strong in H1 (East)
│   ├── Sun/Mars → strong in H10 (South)
│   ├── Saturn → strong in H7 (West)
│   └── Moon/Venus → strong in H4 (North)
├── Kala Bala (temporal) — day/night, season, hora
├── Chesta Bala (motional) — retrograde adds strength!
├── Naisargika Bala (natural) — inherent planet power
└── Drik Bala (aspectual) — benefic/malefic aspects received

Score > 300 = Strong | Score < 200 = Weak

YOUR STRENGTHS:
Saturn: 318.57 (STRONG) — Yoga Karaka delivering at full power
Mercury: 318.21 (STRONG) — 9th lord in Lagna, powerful fortune

VIMSHOPAKA BALA — Strength across divisional charts
├── Checks planet's dignity in D1, D2, D3, D9, D12, D30
├── Weighted average across all vargas
└── Confirms if a planet is truly strong or just looks strong in D1

ASHTAKAVARGA — Transit strength scoring
├── Each planet gets 0-8 bindus per sign from all planets
├── Sarvashtakavarga (SAV) = total for each sign (0-56)
├── SAV > 28 = strong sign for transits
└── Used to predict WHICH transits actually deliver results
```

---

## Part 7: The Jaimini System — A Parallel Framework

Jaimini is a different (but complementary) system to Parashari. We support both:

```
PARASHARI (primary)              JAIMINI (parallel)
─────────────────               ──────────────────
Planet-based aspects             Sign-based aspects
Fixed planet lordship            Variable Chara Karakas
Vimshottari Dasha                Chara Dasha / Narayana Dasha
House lord analysis              Arudha Pada analysis

JAIMINI COMPONENTS WE HAVE:
├── Chara Karakas (7 variable significators)
│   → Atmakaraka (highest degree) = soul planet
│   → Amatyakaraka = career planet
│   → Etc.
├── Arudha Padas (12 image-of-house points)
│   → A1 (Arudha Lagna) = how world sees you
│   → A7 (Darapadha) = spouse image
│   → A10 = career image
│   → A11 = gains image
├── Jaimini Aspects (sign-based, not degree-based)
│   → Movable signs aspect Fixed (skip adjacent)
│   → Fixed signs aspect Movable (skip adjacent)
│   → Dual signs aspect other Duals
├── Upapada Lagna (marriage analysis)
└── Chara Dasha / Narayana Dasha (sign-based timing)
```

---

## Part 8: What We Show Users — The Report Types

### Currently Built Reports

| Report | File | What It Shows |
|--------|------|--------------|
| Life Dashboard | `life_dashboard_srikanth.md` | Full chart overview + dasha timeline + yoga activation + reality check |
| Weekly Forecast | `sample_weekly_forecast.md` | Transit-based weekly predictions |
| February Forecast | `february_2026_forecast_srikanth.md` | Month-specific money/opportunity analysis |
| Birth Chart Report | `sample_onboarding_report.md` | Initial chart reading |

---

## Part 9: INVENTORY — What's Built vs What's Missing

### WHAT WE HAVE (complete)

| Layer | Component | Count | Status |
|-------|-----------|-------|--------|
| **Knowledge** | Yoga definitions | 522 | ✅ Complete |
| | Dosha definitions | 55 | ✅ Complete |
| | Antardasha effects | 81 (9×9) | ✅ Complete |
| | Pratyantardasha effects | 729 (9×9×9) | ✅ Complete |
| | Nakshatra transit rules | 243 (9×27) | ✅ Complete |
| | Planet definitions | 9 | ✅ Complete |
| | Rashi definitions | 12 | ✅ Complete |
| | Nakshatra definitions | 27 | ✅ Complete |
| | House definitions | 12 | ✅ Complete |
| | Tithi/Karana/Vara/Yoga | 30+11+7+27 | ✅ Complete |
| | Combustion rules | 6 planets | ✅ Complete |
| | Retrograde rules | 5 planets | ✅ Complete |
| | Shadbala rules | 6 components | ✅ Complete |
| | Ashtakavarga rules | 7 planets | ✅ Complete |
| | Compatibility rules | 8 kutas | ✅ Complete |
| | Muhurta rules | 8 categories | ✅ Complete |
| | Remedy rules | 9 planets | ✅ Complete |
| | Planet-in-sign interpretations | 108 (9×12) | ✅ Complete |
| | Planet-in-house interpretations | 108 (9×12) | ✅ Complete |
| | Planet-in-nakshatra interps | 243 (9×27) | ✅ Complete |
| | House-lord-in-house interps | 144 (12×12) | ✅ Complete |
| | Divisional chart interpretations | D2+D3+D4+D7+D9+D10+D24 | ✅ Complete |
| | Yoga cancellation rules | 5 types + general | ✅ Session 21 |
| | Navamsha spouse rules | 153 rules | ✅ Session 21 |
| | Ashtakavarga transit rules | 83 rules | ✅ Session 21 |
| | Atmakaraka interpretation rules | 66 rules | ✅ Session 22 |
| | Synastry interpretation rules | 206 rules | ✅ Session 22 |
| | Gem prescription rules | 150 rules | ✅ Session 22 |
| **Cosmos** | Planetary positions | Swiss Ephemeris | ✅ Complete |
| | House cusps (6 systems) | Placidus/Whole/Equal/Koch/Campanus | ✅ Complete |
| | Nakshatra calculations | 27+padas | ✅ Complete |
| | Divisional charts | D1-D60 | ✅ Complete |
| | Panchanga | 5 limbs | ✅ Complete |
| | Sunrise/Sunset | Swiss Ephemeris | ✅ Complete |
| | Aspects (Parashari) | Full+Special | ✅ Complete |
| | Upagrahas | 11 sub-planets | ✅ Complete |
| | Bhava Chalit | Rashi vs cusp-midpoint | ✅ Session 21 |
| **Self** | Yoga detection | 522 rules | ✅ Complete |
| | Dosha detection | 55 rules | ✅ Complete |
| | Shadbala strength | 6 components | ✅ Complete |
| | Vimshopaka strength | 4 schemes | ✅ Complete |
| | Bhava Bala (house strength) | 12 houses | ✅ Complete |
| | Ashtakavarga | BAV+SAV | ✅ Complete |
| | Combustion check | 6 planets | ✅ Complete |
| | Retrograde effects | 5 planets | ✅ Complete |
| | Jaimini (Karakas, Arudhas, Aspects) | Full system | ✅ Complete |
| | Prashna (horary) | 10 categories | ✅ Complete |
| | Compatibility (Ashta Kuta) | 36 points | ✅ Complete |
| | Divisional interpretation | D2-D60 | ✅ Complete |
| | Upapada (marriage analysis) | Jaimini | ✅ Complete |
| | Yoga cancellation engine | Type-specific | ✅ Session 21 |
| | Neecha Bhanga detection | 5 conditions | ✅ Session 21 |
| | Planetary War (Graha Yuddha) | Latitude-based | ✅ Session 21 |
| | Remedies engine | Prioritized prescriptions | ✅ Session 21 |
| | Synastry & Composite Charts | Overlay + Aspects + Midpoint | ✅ Session 22 |
| | Gem Recommendation Engine | Lagna-based + contraindications | ✅ Session 22 |
| | Atmakaraka Deep Analysis | Soul purpose + Ishta Devata | ✅ Session 22 |
| | KP (Krishnamurti Paddhati) | Sub-lord table + significators + predictions | ✅ Session 23 |
| **Context** | Vimshottari Dasha | 120-year, 3 levels | ✅ Complete |
| | Yogini Dasha | 36-year | ✅ Complete |
| | Ashtottari Dasha | 108-year | ✅ Complete |
| | Chara Dasha (Jaimini) | 108-year | ✅ Complete |
| | Narayana Dasha | 108-year | ✅ Complete |
| | Gochara (transit analysis) | 9 planets | ✅ Complete |
| | Enriched transits (nakshatra-level) | 243 combos | ✅ Complete |
| | Sade Sati / Dhaiya | Saturn transit | ✅ Complete |
| | Muhurta evaluation | 10 activities | ✅ Complete |
| | Abhijit / Brahma Muhurta | Daily | ✅ Complete |
| | Eclipse periods | Monthly | ✅ Complete |
| | Marana Kaal | Daily | ✅ Complete |
| | Varshaphal (Solar Return) | Tajika + current year | ✅ Complete |
| | Secondary Progressions | Day=Year | ✅ Complete |
| | Dasha-Transit Cross-Analysis | 0-100 activation scoring | ✅ Session 21 |
| | Transit-to-Natal Aspects | Degree + Parashari special | ✅ Session 21 |
| | Event Correlation Engine | Past event → chart validation | ✅ Session 21 |
| | Transit Trigger Tracker | Upcoming ingresses/aspects/stations | ✅ Session 21 |
| | Daily Forecast Engine | Day rating + all timing layers | ✅ Session 22 |
| | Weekly Forecast Engine | 7-day area ratings + peak days | ✅ Session 22 |
| | Monthly Forecast Engine | Transits + retrogrades + areas | ✅ Session 22 |
| **MCP Tools** | Total tools | ~80 | ✅ Complete |
| **API Endpoints** | Total endpoints | 33 | ✅ Complete |
| **Tests** | Total test items | ~2,126 | ✅ Complete |

### WHAT'S MISSING OR INCOMPLETE

| Gap | Priority | What It Would Add |
|-----|----------|-------------------|
| **Chara Dasha antardashas** | LOW | Jaimini sub-period calculations within Chara Dasha sign periods |
| **KP Prashna (real-time)** | LOW | Live KP prashna using current moment chart for real-time queries |
| **Deeper Rashi aspects** | LOW | Jaimini sign-based aspects with detailed interpretations |
| **planet_in_nakshatra.json expansion** | LOW | Currently 78KB, expected ~200KB — partial coverage of 243 combinations |
| **Real-time push notifications** | MEDIUM | Live transit alerts when aspects become exact — needs infrastructure |
| **Multi-user auth** | MEDIUM | Proper user management with JWT/OAuth — needed for production |
| **Frontend (Next.js + React Native)** | HIGH | No UI yet — all features are API/MCP only |

### What We Need for the USER-FACING Product

| Feature | What User Sees | Backend Status |
|---------|---------------|----------------|
| **Onboarding report** | "Here's who you are" — personality, strengths, challenges | ✅ Have data, need template + UI |
| **Life timeline** | Visual dasha timeline with past events mapped | ✅ Have dasha engine + event correlator, need UI |
| **Daily forecast** | "Today's energy" based on transit Moon + panchanga | ✅ Complete — day rating, panchanga, choghadiya, dasha, transits |
| **Weekly forecast** | 7-day transit-based predictions | ✅ Complete — area ratings, peak/challenging days, transit aggregation |
| **Monthly forecast** | Money/career/relationship focus per month | ✅ Complete — major transits, retrogrades, weekly summaries, best dates |
| **Yoga report** | "Your superpowers" — what yogas you have, when they activate | ✅ Complete — yoga detection + cancellation + dasha-transit activation |
| **Dosha report** | "Your challenges" — what doshas, remedies, when they ease | ✅ Complete — detection + remedies engine + gem recommendations |
| **Compatibility report** | Match two charts — Ashta Kuta + Upapada + synastry | ✅ Complete — Ashta Kuta + Upapada + full synastry (overlay, aspects, composite) |
| **Muhurta finder** | "Best time to..." — marriage, business, travel | ✅ Complete |
| **Event validator** | User inputs past event → system shows why it happened | ✅ Complete — event correlation engine (Session 21) |
| **Remedies dashboard** | Current remedies based on active doshas + dashas | ✅ Complete — remedies engine + gem recommendations (Sessions 21+22) |
| **Real-time transit dashboard** | Live "what's happening now" with countdown to next trigger | ✅ Complete — transit trigger tracker (Session 21), needs UI |
| **Soul purpose report** | Atmakaraka analysis + Ishta Devata + spiritual path | ✅ Complete — atmakaraka deep analysis (Session 22) |
| **Gem prescription** | Personalized gem recommendations based on Lagna + dasha | ✅ Complete — gem recommendation engine (Session 22) |

---

## Part 10: The Data Flow — How a Reading Works

```
USER: "What's happening in my career?"

Step 1: COSMOS — Calculate positions
  └── Birth chart: planets, houses, nakshatras, ascendant
  └── Current transits: where planets are NOW

Step 2: SELF — Detect patterns
  └── Yogas: Sasa Yoga, Dhana Yoga, Viparita Raja...
  └── Doshas: Sade Sati (setting phase)...
  └── Strength: Saturn 318 (strong), Mercury 318 (strong)...
  └── Career houses: 10th lord Moon in 5th, Mars in 10th...

Step 3: CONTEXT — Apply timing
  └── Current Dasha: Mercury-Ketu-Venus
  └── Mercury = 9th lord in 1st → fortune through self
  └── Ketu = 8th house → sudden/unexpected events
  └── Current transit: Jupiter in 9th (fortune), stellium in 5th
  └── Sade Sati setting phase → pressure easing

Step 4: KNOWLEDGE — Interpret combinations
  └── Mercury MD + Ketu AD = "intellect meets detachment"
  └── Transit Jupiter in 9th = fortune house activated
  └── 10th lord Moon in 5th = "career through creativity"

Step 5: GUIDE — Synthesize for user
  └── "Your career is in a transition phase. Mercury Mahadasha
       activates your 9th lord (fortune) from the Lagna — this
       means opportunities come through YOUR initiative.
       Ketu Antardasha adds unpredictability — the next offer
       may come from an unexpected direction. The massive
       transit pile-up in your 5th house (Feb 24-26) is your
       peak window for career moves this month.

       Your Sasa Yoga (Saturn as Yoga Karaka) built your
       foundation during ages 11-30. Now Mercury MD is
       about building on that foundation through intellect
       and communication — your skills as a full-stack
       developer are your 9th house fortune manifesting."
```

---

*108 System Map — v2.0 | Feb 7, 2026*
*~80 MCP tools | 33 API endpoints | 522 yogas | 55 doshas | 729 pratyantardasha effects | ~2,126 tests*
*43 rule files | 15 definition files | 5 interpretation files | ~1,000 interpretation rules added (Sessions 21-22)*
