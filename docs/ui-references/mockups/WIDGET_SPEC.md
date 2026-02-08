# 108 Widget Specification

42 widgets mapped to the 108-core data system, organized by category. Each widget includes its Flutter class name, Riverpod provider, API endpoint, key properties, and implementation guidance for Flutter 3.x with Riverpod, fl_chart, and dark cosmic theme.

---

## Design Tokens (Reference)

### Colors
```dart
// Primary cosmics
const Color cosmicBg = Color(0xFF0F0F23);      // Deep space
const Color cosmicCard = Color(0xFF1A1A3E);    // Card overlay
const Color cosmicBorder = Color(0xFF2A2A5E);  // Subtle divider

// Accent planets
const Color sunGold = Color(0xFFFFD700);       // Sun
const Color moonSilver = Color(0xFFE8E8E8);    // Moon
const Color marsRed = Color(0xFFE74C3C);       // Mars
const Color mercuryGreen = Color(0xFF22C55E);  // Mercury
const Color jupiterOrange = Color(0xFFF59E0B); // Jupiter
const Color venusBlue = Color(0xFF3B82F6);     // Venus
const Color saturnPurple = Color(0xA78BFA);    // Saturn
const Color rahuBlack = Color(0xFF404060);     // Rahu
const Color ketuGray = Color(0xFF808080);      // Ketu

// Status colors
const Color successGreen = Color(0xFF10B981);  // Pass/auspicious
const Color warningOrange = Color(0xFFF59E0B); // Caution
const Color dangerRed = Color(0xFFEF4444);     // Alert/afflicted
const Color infoBlue = Color(0xFF06B6D4);      // Info/hint

// Gradient overlays
const LinearGradient cosmicGradient = LinearGradient(
  colors: [Color(0xFF0F0F23), Color(0xFF1A1A5E)],
  begin: Alignment.topCenter,
  end: Alignment.bottomCenter,
);
```

### Text Styles
```dart
// Headlines
const TextStyle h1 = TextStyle(
  fontSize: 32, fontWeight: FontWeight.bold, color: moonSilver,
);
const TextStyle h2 = TextStyle(
  fontSize: 24, fontWeight: FontWeight.bold, color: moonSilver,
);
const TextStyle h3 = TextStyle(
  fontSize: 20, fontWeight: FontWeight.w600, color: moonSilver,
);

// Body
const TextStyle bodyLarge = TextStyle(
  fontSize: 16, fontWeight: FontWeight.w500, color: Color(0xFFCCCCCC),
);
const TextStyle bodyMed = TextStyle(
  fontSize: 14, fontWeight: FontWeight.w400, color: Color(0xFFAAAAAA),
);
const TextStyle bodySm = TextStyle(
  fontSize: 12, fontWeight: FontWeight.w400, color: Color(0xFF888888),
);

// Mono (scores, numbers)
const TextStyle monoLg = TextStyle(
  fontFamily: 'RobotoMono',
  fontSize: 18, fontWeight: FontWeight.bold, color: sunGold,
);
const TextStyle monoMed = TextStyle(
  fontFamily: 'RobotoMono',
  fontSize: 14, fontWeight: FontWeight.w600, color: moonSilver,
);
```

### Card Decoration
```dart
const BoxDecoration glassCard = BoxDecoration(
  color: Color(0xFF1A1A3E).withOpacity(0.8),
  border: Border.all(color: Color(0xFF2A2A5E), width: 1.5),
  borderRadius: BorderRadius.all(Radius.circular(12)),
);

const BoxDecoration cosmicCard = BoxDecoration(
  color: Color(0xFF1A1A3E),
  border: Border.all(color: Color(0xFF3A3A6E), width: 1.0),
  borderRadius: BorderRadius.all(Radius.circular(8)),
);

const BoxDecoration activeBorder = BoxDecoration(
  color: Color(0xFF1A1A3E),
  border: Border.all(color: Color(0xFF22C55E), width: 2.0),
  borderRadius: BorderRadius.all(Radius.circular(8)),
);
```

### Spacing & Padding
```dart
const double p4 = 4.0;    // Micro
const double p8 = 8.0;    // Xs
const double p12 = 12.0;  // Sm
const double p16 = 16.0;  // Md
const double p24 = 24.0;  // Lg
const double p32 = 32.0;  // Xl
const double p48 = 48.0;  // 2xl
```

---

## Category 1: Score & Rating Widgets (8)

### 1. DayScoreRing
- **Class**: `DayScoreRing extends ConsumerWidget`
- **Provider**: `dailyForecastProvider(String date)`
- **API**: `GET /api/v1/forecast/daily?date={date}` → `day_rating` (0–10)
- **Key Props**: `score` (double), `label` (String), `variant` ('hero'|'compact')
- **Flutter Impl**: `CustomPaint` with `Canvas.drawArc()`, gradient shader from cosmicGradient
- **Sizes**: Hero 120×120, Compact 48×48
- **Animation**: `AnimationController` 300ms, `Tween<double>(0, score)`, easeOutQuart
- **Tier**: Free
- **Notes**: Ring thickness 8px (hero), 4px (compact); center text is monoLg

### 2. AreaRatingBars
- **Class**: `AreaRatingBars extends ConsumerWidget`
- **Provider**: `weeklyForecastProvider`
- **API**: `GET /api/v1/forecast/weekly` → `area_ratings` {career, finance, health, relationships, spiritual}
- **Key Props**: `ratings` (Map<String, double>), `showLabels` (bool)
- **Flutter Impl**: `fl_chart` BarChart with 5 bars, each colored by domain (mercuryGreen=career, jupiterOrange=finance, etc.)
- **Size**: 280×160
- **Animation**: Stagger bar animations, 100ms delay between
- **Tier**: Free
- **Notes**: Use `BarChartData` with `maxY: 10`, `barWidth: 12`, tooltip on tap

### 3. MiniScoreBadge
- **Class**: `MiniScoreBadge extends StatelessWidget`
- **Provider**: N/A (inline, receives score as param)
- **Key Props**: `score` (double 0–10), `size` ('sm'|'md'|'lg')
- **Flutter Impl**: `Container` with circular gradient, Stack with score text centered
- **Sizes**: Sm 32×32, Md 48×48, Lg 64×64
- **Animation**: No animation (static)
- **Tier**: Free
- **Notes**: Color shifts from red (<4) → orange (4–6) → green (>6)

### 4. CompatibilityRing
- **Class**: `CompatibilityRing extends ConsumerWidget`
- **Provider**: `synastryAnalysisProvider(String otherId)`
- **API**: `GET /api/v1/compatibility/synastry/{otherId}` → `overall_score`
- **Key Props**: `score` (double 0–100), `otherName` (String)
- **Flutter Impl**: `CustomPaint` donut ring, two-tone gradient (outer=success, inner=warning based on score)
- **Size**: 160×160
- **Animation**: 500ms reveal, easeInOutCubic
- **Tier**: Pro
- **Notes**: Center shows percentage; subtitle = "Overall Compatibility"

### 5. ShadbalaGauge
- **Class**: `ShadbalaGauge extends ConsumerWidget`
- **Provider**: `shadbalaProvider(String planet)`
- **API**: `GET /api/v1/strength/shadbala/{planet}` → `total_strength`
- **Key Props**: `planet` (String), `strength` (double 0–600), `detailed` (bool)
- **Flutter Impl**: `fl_chart` PieChart in donut mode, 6 segments (one per bala component), each colored per component
- **Size**: 140×140
- **Animation**: 400ms sequential segment reveals
- **Tier**: Pro
- **Notes**: Tap segment to show component strength in overlay

### 6. MuhurtaBadge
- **Class**: `MuhurtaBadge extends ConsumerWidget`
- **Provider**: `muhurtaCheckProvider(String datetime, String activity)`
- **API**: `GET /api/v1/muhurta/check` → `muhurta_quality` (poor/fair/good/excellent)
- **Key Props**: `quality` (String), `time` (DateTime)
- **Flutter Impl**: `Container` with icon + text, background color per quality
- **Size**: 80×32
- **Animation**: Pulse effect on good/excellent
- **Tier**: Free
- **Notes**: poor=dangerRed, fair=warningOrange, good=infoBlue, excellent=successGreen

### 7. VimshopakaStar
- **Class**: `VimshopakaStar extends StatelessWidget`
- **Provider**: N/A (receives vimshopaka score as param)
- **Key Props**: `score` (double 0–20), `label` (String), `planet` (String)
- **Flutter Impl**: `Stack` of 5 stars (Icon), filled based on score (0–5 stars), color per planet
- **Size**: 120×24
- **Animation**: Star fill stagger 50ms per star
- **Tier**: Premium
- **Notes**: Tap to show score tooltip; color = planetColor[planet]

### 8. BhavaBalaChart
- **Class**: `BhavaBalaChart extends ConsumerWidget`
- **Provider**: `bhavaBalasProvider`
- **API**: `GET /api/v1/strength/bhava-balas` → array of {house, bala_strength}
- **Key Props**: `showLabels` (bool), `interactive` (bool)
- **Flutter Impl**: `fl_chart` BarChart horizontal, 12 bars (houses 1–12), colored green→red (weak→strong)
- **Size**: 300×240
- **Animation**: Bars grow from 0, stagger 50ms
- **Tier**: Premium
- **Notes**: Tap house to show detailed bala breakdown; x-axis = house numbers

---

## Category 2: Period & Timeline Widgets (6)

### 9. DashaPeriodBar
- **Class**: `DashaPeriodBar extends ConsumerWidget`
- **Provider**: `currentDashaProvider`
- **API**: `GET /api/v1/dasha/current` → {mahadasha_lord, antardasha_lord, remaining_days}
- **Key Props**: `lord` (String), `remaining` (int days), `variant` ('inline'|'card')
- **Flutter Impl**: `Column` > `Row` (planet glyph + name) + linear progress bar
- **Size**: Inline 280×48, Card 320×80
- **Animation**: Progress fill 600ms easeOutQuart
- **Tier**: Free
- **Notes**: Show exact months/days in tooltip; color = planetColor[lord]

### 10. NestedDashaRings
- **Class**: `NestedDashaRings extends ConsumerWidget`
- **Provider**: `currentDashaProvider`
- **API**: `GET /api/v1/dasha/current`
- **Key Props**: `mahadasha` (String), `antardasha` (String), `pratyantardasha` (String)
- **Flutter Impl**: `CustomPaint` 3 concentric rings (outer=MD, mid=AD, inner=PD), each ring rotated by progress
- **Size**: 200×200
- **Animation**: Sequential ring rotations 500ms each, easeInOutQuad
- **Tier**: Pro
- **Notes**: Labels at 12 o'clock for each ring; planetColor for each lord

### 11. LifeChapterCard
- **Class**: `LifeChapterCard extends StatelessWidget`
- **Provider**: N/A (receives chapter data)
- **Key Props**: `chapter` (Map with start_age, end_age, theme), `isCurrent` (bool)
- **Flutter Impl**: `GlassCard` (Container with glassCard BoxDecoration), age range on left, theme text right
- **Size**: 320×80
- **Animation**: Scale up 200ms if current
- **Tier**: Free
- **Notes**: Border highlights success/warning/danger based on theme tone

### 12. DashaTimelineStrip
- **Class**: `DashaTimelineStrip extends ConsumerWidget`
- **Provider**: `dashaPeriodProvider(int years)`
- **API**: `GET /api/v1/dasha/periods?years={years}` → array of periods
- **Key Props**: `years` (int), `compact` (bool)
- **Flutter Impl**: `ListView.horizontal` of small rings/badges per dasha, with connecting lines in CustomPaint
- **Size**: Full width, height 80
- **Animation**: Stagger in 100ms per period
- **Tier**: Pro
- **Notes**: Current period has highlighted border; tap to expand period card

### 13. TransitEventRow
- **Class**: `TransitEventRow extends StatelessWidget`
- **Provider**: N/A (receives event data)
- **Key Props**: `event` (Map), `isHighlight` (bool)
- **Flutter Impl**: `Row` with planet glyph + icon (ingress/conjunction/retrograde) + text + date
- **Size**: 320×56
- **Animation**: Slide in 300ms if highlight
- **Tier**: Free
- **Notes**: Color per event type (ingress=infoBlue, conjunction=jupiterOrange, retrograde=dangerRed)

### 14. AntardashaTimeline
- **Class**: `AntardashaTimeline extends ConsumerWidget`
- **Provider**: `antardashaPeriodsProvider(String mahadashaLord)`
- **API**: `GET /api/v1/dasha/antardasha/{lord}` → array of periods
- **Key Props**: `mahadashaLord` (String)
- **Flutter Impl**: `Column` of DashaEventCards with vertical divider on left (CustomPaint line)
- **Size**: 300×(dynamic)
- **Animation**: Stagger cards 80ms per card
- **Tier**: Pro
- **Notes**: Collapsible pratyantardasha sub-timeline on tap

---

## Category 3: Chart & Grid Widgets (5)

### 15. SouthIndianChart
- **Class**: `SouthIndianChart extends ConsumerWidget`
- **Provider**: `natalChartProvider`
- **API**: `GET /api/v1/chart/rashi` → {lagna, planets_by_house}
- **Key Props**: `chart` (Map), `variant` ('natal'|'navamsha'|'dashamsha')
- **Flutter Impl**: `CustomPaint` grid (9×3 South Indian layout), `Canvas.drawRect()` for boxes, centered glyph + sign per cell
- **Size**: 280×280
- **Animation**: Cell fills stagger 50ms per cell
- **Tier**: Pro
- **Notes**: Lagna cell has special border; tap cell to show house details

### 16. PlanetBadge
- **Class**: `PlanetBadge extends StatelessWidget`
- **Provider**: N/A (receives planet data)
- **Key Props**: `planet` (String), `sign` (String), `house` (int), `size` ('sm'|'md'|'lg')
- **Flutter Impl**: `Container` with planet glyph centered, label below (sign + house), colored border
- **Size**: Sm 48×48, Md 64×64, Lg 80×80
- **Animation**: No animation
- **Tier**: Free
- **Notes**: Border color = planetColor[planet]; background = dark cosmic

### 17. PlanetDetailRow
- **Class**: `PlanetDetailRow extends StatelessWidget`
- **Provider**: N/A (receives planet detail)
- **Key Props**: `planet` (String), `longitude` (double), `sign` (String), `house` (int), `nakshatra` (String), `showSpeed` (bool)
- **Flutter Impl**: `Row` > [glyph, planet name, longitude (mono), sign badge, house badge, nakshatra chip]
- **Size**: Full width, height 56
- **Animation**: No animation
- **Tier**: Free
- **Notes**: Tap row to navigate to planet detail page

### 18. AshtakavargaHeatmap
- **Class**: `AshtakavargaHeatmap extends ConsumerWidget`
- **Provider**: `ashtakavargaProvider`
- **API**: `GET /api/v1/strength/ashtakavarga` → {planets, sarvashtakavarga}
- **Key Props**: `type` ('planet'|'sava')
- **Flutter Impl**: `GridView` 9×12 (planets × rashi), each cell is `Container` colored by bindu count (0–8 = light→bright green)
- **Size**: 320×300
- **Animation**: Cell color gradient in 200ms per cell
- **Tier**: Premium
- **Notes**: Tap cell to show bindu breakdown; x-axis = rashis, y-axis = planets

### 19. DivisionalChartChip
- **Class**: `DivisionalChartChip extends StatelessWidget`
- **Provider**: N/A (receives D-chart position)
- **Key Props**: `division` (int), `planet` (String), `sign` (String), `selected` (bool)
- **Flutter Impl**: `Container` with D-chart label (D1, D9, D27, etc.) + planet glyph + sign, toggle border on select
- **Size**: 96×40
- **Animation**: Scale 150ms on select
- **Tier**: Premium
- **Notes**: Background light when selected; used in D-chart selector row

---

## Category 4: Status & Alert Widgets (7)

### 20. SadeSatiBanner
- **Class**: `SadeSatiBanner extends ConsumerWidget`
- **Provider**: `sadeSatiStatusProvider`
- **API**: `GET /api/v1/transits/sade-sati` → {status, phase, severity}
- **Key Props**: `severity` ('none'|'rising'|'peak'|'setting'), `showRemedies` (bool)
- **Flutter Impl**: `GlassCard` with warning icon (left) + title + phase text + remedies list (if showRemedies=true)
- **Size**: Full width, height 100–160
- **Animation**: Pulse icon 2s infinite if peak
- **Tier**: Free
- **Notes**: Background color: none=transparent, rising=infoBlue, peak=dangerRed, setting=warningOrange

### 21. DoshaAlertCard
- **Class**: `DoshaAlertCard extends StatelessWidget`
- **Provider**: N/A (receives dosha data)
- **Key Props**: `dosha` (String), `severity` (String), `planets` (List<String>)
- **Flutter Impl**: `GlassCard` with dosha icon + name + severity badge + affected planets row
- **Size**: 300×96
- **Animation**: Border glow 1.5s infinite if severe
- **Tier**: Free
- **Notes**: Color per severity: mild=infoBlue, moderate=warningOrange, severe=dangerRed

### 22. YogaBadge
- **Class**: `YogaBadge extends StatelessWidget`
- **Provider**: N/A (receives yoga data)
- **Key Props**: `yoga` (String), `planets` (List<String>), `strength` (double 0–1.0), `cancelled` (bool)
- **Flutter Impl**: `Container` badge with yoga icon + text, opacity reduced if cancelled, gradient border if strong
- **Size**: 120×36
- **Animation**: No animation
- **Tier**: Free
- **Notes**: Background green if benefic and strong, gray if cancelled

### 23. CombustionWarning
- **Class**: `CombustionWarning extends StatelessWidget`
- **Provider**: N/A (receives combustion state)
- **Key Props**: `planet` (String), `distance` (double degrees), `strength` (double 0–1.0)
- **Flutter Impl**: `Container` compact row: planet glyph + icon (flame) + text ("Combusted") + strength percentage
- **Size**: 200×40
- **Animation**: Flame icon flickers 1s
- **Tier**: Free
- **Notes**: Danger red background; tap to show combustion details

### 24. RetrogradeBadge
- **Class**: `RetrogradeBadge extends StatelessWidget`
- **Provider**: N/A (receives retrograde state)
- **Key Props**: `planet` (String), `isRetrograde` (bool), `daysUntilDirect` (int?)
- **Flutter Impl**: `Container` badge: planet glyph + "Rx" text + days (if present), rotate icon 180°
- **Size**: 100×32
- **Animation**: Slow rotate 3s infinite if retrograde
- **Tier**: Free
- **Notes**: Background dangerRed if retrograde; tap for retrograde effects

### 25. PlanetaryWarAlert
- **Class**: `PlanetaryWarAlert extends StatelessWidget`
- **Provider**: N/A (receives war data)
- **Key Props**: `planets` (List<String, String>), `winner` (String), `loser` (String)
- **Flutter Impl**: `GlassCard`: [loser glyph] ⚔️ [winner glyph], title "Planetary War", date/time
- **Size**: 280×80
- **Animation**: Sword icon bounces 500ms
- **Tier**: Pro
- **Notes**: Highlight loser planet in dangerRed; background darker

### 26. EclipseAlertBanner
- **Class**: `EclipseAlertBanner extends StatelessWidget`
- **Provider**: N/A (receives eclipse data)
- **Key Props**: `eclipseType` ('solar'|'lunar'), `date` (DateTime), `inauspiciousDuration` (Duration)
- **Flutter Impl**: `GlassCard` with eclipse icon (top center) + type + date + "No muhurta during eclipse" warning
- **Size**: Full width, height 120
- **Animation**: Icon pulse 2s if upcoming (within 7 days)
- **Tier**: Free
- **Notes**: Background slightly darker; prominently warn against auspicious activities

---

## Category 5: Panchanga & Calendar Widgets (5)

### 27. PanchangaStrip
- **Class**: `PanchangaStrip extends ConsumerWidget`
- **Provider**: `panchangaProvider(String date)`
- **API**: `GET /api/v1/panchanga?date={date}` → {tithi, nakshatra, yoga, karana, vara}
- **Key Props**: `date` (DateTime), `compact` (bool)
- **Flutter Impl**: `Row` of 5 compact cards, each showing one panchanga limb with name + value
- **Size**: Full width, height 80 (compact: 60)
- **Animation**: Stagger cards 60ms per card
- **Tier**: Free
- **Notes**: Tap card to expand details; background glassCard

### 28. ChoghadiyaStrip
- **Class**: `ChoghadiyaStrip extends ConsumerWidget`
- **Provider**: `choghadiyaProvider(String date)`
- **API**: `GET /api/v1/choghadiya?date={date}` → array of {period, muhurta, duration, lord}
- **Key Props**: `date` (DateTime)
- **Flutter Impl**: `ListView.horizontal` small time blocks, colored per muhurta type (auspicious=green, mixed=yellow, evil=red)
- **Size**: Full width, height 60
- **Animation**: Current block has animated border 1.5s
- **Tier**: Free
- **Notes**: Show time range on hover; tooltip shows muhurta name

### 29. RahuKaalBadge
- **Class**: `RahuKaalBadge extends ConsumerWidget`
- **Provider**: `rahuKaalProvider(String date)`
- **API**: `GET /api/v1/rahu-kaal?date={date}` → {start, end, is_active}
- **Key Props**: `isActive` (bool)
- **Flutter Impl**: `Container` with clock icon + time range text + "Rahu Kaal" label
- **Size**: 180×40
- **Animation**: Glow effect 1.5s if active
- **Tier**: Free
- **Notes**: Background dangerRed if active; blurred background if inactive

### 30. AbhijitMuhurtaCard
- **Class**: `AbhijitMuhurtaCard extends ConsumerWidget`
- **Provider**: `abhijitMuhurtaProvider(String date)`
- **API**: `GET /api/v1/abhijit-muhurta?date={date}` → {start, end}
- **Key Props**: `date` (DateTime), `isCurrent` (bool)
- **Flutter Impl**: `GlassCard`: "Abhijit Muhurta" (h3) + time range (monoMed) + "Most auspicious time" subtitle
- **Size**: 280×100
- **Animation**: Border glow 2s infinite if current
- **Tier**: Free
- **Notes**: Background subtle gold tint; tap to set reminder

### 31. CalendarDayCell
- **Class**: `CalendarDayCell extends StatelessWidget`
- **Provider**: N/A (receives panchanga data)
- **Key Props**: `date` (DateTime), `panchanga` (Map), `isToday` (bool), `isCurrentMonth` (bool)
- **Flutter Impl**: `Container` grid cell: day number (top) + small tithi badge + small yoga badge, background darker if not current month
- **Size**: 48×48
- **Animation**: Scale 150ms on tap
- **Tier**: Free
- **Notes**: Border highlight if isToday; tap to show full panchanga

---

## Category 6: Recommendation & Action Widgets (5)

### 32. GemRecommendationCard
- **Class**: `GemRecommendationCard extends ConsumerWidget`
- **Provider**: `gemRecommendationProvider`
- **API**: `GET /api/v1/recommendations/gemstones` → {primary_gem, supporting_gems, avoiding}
- **Key Props**: `gem` (Map), `tier` ('free'|'pro'|'premium')
- **Flutter Impl**: `GlassCard`: gem icon (centered, large) + name (h3) + planet + wearing instructions (bodySm)
- **Size**: 200×200
- **Animation**: Icon glow 2s infinite
- **Tier**: Pro (primary), Free (basic suggest)
- **Notes**: Bottom banner showing if pro/premium only; tap to expand instructions

### 33. RemedyCard
- **Class**: `RemedyCard extends StatelessWidget`
- **Provider**: N/A (receives remedy data)
- **Key Props**: `remedy` (Map: type, description, frequency), `priority` ('urgent'|'recommended'|'optional')
- **Flutter Impl**: `GlassCard`: priority badge (top-right) + remedy icon + title (h3) + description (bodySm) + frequency chip
- **Size**: 280×120
- **Animation**: Border highlight 1.5s if urgent
- **Tier**: Free
- **Notes**: Background color: urgent=dangerRed faint, recommended=infoBlue faint, optional=transparent

### 34. ReportProductCard
- **Class**: `ReportProductCard extends StatelessWidget`
- **Provider**: N/A (receives product data)
- **Key Props**: `title` (String), `sections` (int), `estimatedTime` (Duration), `locked` (bool), `tier` (String)
- **Flutter Impl**: `GlassCard`: title (h3) + "x sections" subtitle + time estimate + "Get Report" button + LockedOverlay if locked
- **Size**: 280×100
- **Animation**: Button pulse on hover
- **Tier**: Mixed (free/pro/premium)
- **Notes**: Show tier badge on locked overlay

### 35. CreditBalanceWidget
- **Class**: `CreditBalanceWidget extends ConsumerWidget`
- **Provider**: `creditBalanceProvider`
- **API**: `GET /api/v1/user/credits` → {balance, tier, tier_limit}
- **Key Props**: `showHistory` (bool)
- **Flutter Impl**: `GlassCard`: "Credits" label + balance (monoLg, large gold) + tier badge + small progress bar showing tier usage
- **Size**: 240×80
- **Animation**: Balance number updates with counter animation 200ms
- **Tier**: Free
- **Notes**: Tap to show credit history modal; button to buy credits

### 36. LockedFeatureOverlay
- **Class**: `LockedFeatureOverlay extends StatelessWidget`
- **Provider**: N/A (receives lock data)
- **Key Props**: `requiredTier` (String), `unlockAt` (DateTime?), `featureTitle` (String)
- **Flutter Impl**: `Stack` overlay: `BackdropFilter(blur)` + centered `GlassCard` with lock icon + "Upgrade to {tier}" + optional countdown
- **Size**: Full (overlay)
- **Animation**: Slide up 300ms, blur fade 200ms
- **Tier**: Core
- **Notes**: Center button to "Upgrade" or "Remind Me"; show tier requirements

---

## Category 7: Chat-Specific Widgets (4)

### 37. ChatScoreCard
- **Class**: `ChatScoreCard extends StatelessWidget`
- **Provider**: N/A (receives score data from chat context)
- **Key Props**: `score` (double 0–10), `title` (String), `context` (String: "daily"|"compatibility"|"yoga")
- **Flutter Impl**: `GlassCard`: score ring on left (80×80), title + context on right, align left
- **Size**: 280×120
- **Animation**: Ring animation 400ms on appear
- **Tier**: Free
- **Notes**: Clickable to expand details; used in chat responses

### 38. ChatDataTable
- **Class**: `ChatDataTable extends StatelessWidget`
- **Provider**: N/A (receives table data)
- **Key Props**: `headers` (List<String>), `rows` (List<List<String>>), `maxRows` (int?)
- **Flutter Impl**: `SingleChildScrollView` > `Table` with styled header row (bold, infoBlue bg) + data rows, alternating subtle bg
- **Size**: Full width, dynamic height (max 5 rows then scrollable)
- **Animation**: No animation
- **Tier**: Free
- **Notes**: Horizontal scroll on small screens; tap row to expand if needed

### 39. ChatActionCard
- **Class**: `ChatActionCard extends StatelessWidget`
- **Provider**: N/A (receives action data)
- **Key Props**: `title` (String), `description` (String), `actionLabel` (String), `actionRoute` (String)
- **Flutter Impl**: `GlassCard`: title (h3) + description (bodySm) + button bottom-right, align left text
- **Size**: 300×100
- **Animation**: Button scale 150ms on hover
- **Tier**: Free
- **Notes**: Tap button to navigate; used for follow-up actions in chat

### 40. SuggestedQuestionChips
- **Class**: `SuggestedQuestionChips extends StatelessWidget`
- **Provider**: N/A (receives questions list)
- **Key Props**: `questions` (List<String>), `onTap` (Function(String))
- **Flutter Impl**: `Wrap` of `FilterChip`, no selection state, tap triggers onTap callback
- **Size**: Full width, dynamic height (usually 2–3 rows)
- **Animation**: Chip scale 150ms on tap
- **Tier**: Free
- **Notes**: Appear after chat message; wrap with max 4 per row

---

## Category 8: Soul & Spiritual Widgets (2)

### 41. AtmakarakaCard
- **Class**: `AtmakarakaCard extends ConsumerWidget`
- **Provider**: `atmakarakaProvider`
- **API**: `GET /api/v1/jaimini/atmakaraka` → {planet, sign, house, soul_purpose, ishta_devata}
- **Key Props**: None (auto-fetches from provider)
- **Flutter Impl**: `GlassCard`: planet glyph (large center) + "Atmakaraka" label below + "Soul's Purpose" section (indented text) + deity name (bottom, italics)
- **Size**: 300×200
- **Animation**: Glyph scale 400ms on appear
- **Tier**: Premium
- **Notes**: Background subtle gradient related to planet; tap to expand soul-purpose detail

### 42. NakshatraInfoCard
- **Class**: `NakshatraInfoCard extends StatelessWidget`
- **Provider**: N/A (receives nakshatra data)
- **Key Props**: `nakshatra` (String), `pada` (int), `lord` (String), `deity` (String), `qualities` (List<String>)
- **Flutter Impl**: `GlassCard`: nakshatra name (h3, top) + pada badge (top-right, small) + deity name (subtitle) + symbol/glyph (center) + qualities row (bottom, small chips)
- **Size**: 280×160
- **Animation**: Glyph fade in 300ms
- **Tier**: Free
- **Notes**: Tap to show full nakshatra interpretation; use planetColor[lord] for accent

---

## Shared Building Blocks

### GlassCard
Reusable glassmorphic container with semi-transparent background, subtle border, and rounded corners.

```dart
class GlassCard extends StatelessWidget {
  final Widget child;
  final double? width, height;
  final EdgeInsets padding;
  final VoidCallback? onTap;

  const GlassCard({
    required this.child,
    this.width, this.height,
    this.padding = const EdgeInsets.all(16),
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: Container(
          width: width,
          height: height,
          padding: padding,
          decoration: BoxDecoration(
            color: Color(0xFF1A1A3E).withOpacity(0.8),
            border: Border.all(color: Color(0xFF2A2A5E), width: 1.5),
            borderRadius: BorderRadius.circular(12),
            backdropFilter: ImageFilter.blur(sigmaX: 4, sigmaY: 4),
          ),
          child: child,
        ),
      ),
    );
  }
}
```

### PlanetGlyph
Renders planet symbol with color, supports multiple sizes.

```dart
class PlanetGlyph extends StatelessWidget {
  final String planet;
  final double size;
  final bool retrograde;

  const PlanetGlyph({
    required this.planet,
    this.size = 24,
    this.retrograde = false,
  });

  @override
  Widget build(BuildContext context) {
    const Map<String, IconData> glyphs = {
      'sun': Icons.wb_sunny,
      'moon': Icons.nights_stay,
      'mars': Icons.sports_bar,
      'mercury': Icons.person_outline,
      'jupiter': Icons.cloud,
      'venus': Icons.favorite,
      'saturn': Icons.settings,
      'rahu': Icons.cancel,
      'ketu': Icons.check_circle,
    };
    const Map<String, Color> colors = {
      'sun': sunGold,
      'moon': moonSilver,
      'mars': marsRed,
      'mercury': mercuryGreen,
      'jupiter': jupiterOrange,
      'venus': venusBlue,
      'saturn': saturnPurple,
      'rahu': rahuBlack,
      'ketu': ketuGray,
    };

    return Transform.scale(
      scaleX: retrograde ? -1 : 1,
      child: Icon(
        glyphs[planet] ?? Icons.circle,
        size: size,
        color: colors[planet] ?? moonSilver,
      ),
    );
  }
}
```

### ScoreRing
Reusable circular progress indicator with gradient fill.

```dart
class ScoreRing extends StatefulWidget {
  final double score;
  final double size;
  final Color? color;
  final Duration duration;

  const ScoreRing({
    required this.score,
    this.size = 120,
    this.color,
    this.duration = const Duration(milliseconds: 800),
  });

  @override
  State<ScoreRing> createState() => _ScoreRingState();
}

class _ScoreRingState extends State<ScoreRing>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(duration: widget.duration, vsync: this);
    _animation = Tween<double>(begin: 0, end: widget.score).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutQuart),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return CustomPaint(
          size: Size(widget.size, widget.size),
          painter: _RingPainter(
            score: _animation.value,
            color: widget.color ?? successGreen,
          ),
        );
      },
    );
  }
}

class _RingPainter extends CustomPainter {
  final double score;
  final Color color;

  _RingPainter({required this.score, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 8;

    // Background ring
    canvas.drawCircle(
      center,
      radius,
      Paint()
        ..color = Color(0xFF2A2A5E)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 8,
    );

    // Score ring
    final sweepAngle = (score / 10) * 2 * pi;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -pi / 2,
      sweepAngle,
      false,
      Paint()
        ..shader = LinearGradient(
          colors: [color, color.withOpacity(0.5)],
        ).createShader(Rect.fromCircle(center: center, radius: radius))
        ..style = PaintingStyle.stroke
        ..strokeWidth = 8
        ..strokeCap = StrokeCap.round,
    );

    // Center text
    final textSpan = TextSpan(
      text: score.toStringAsFixed(1),
      style: monoLg,
    );
    final textPainter = TextPainter(text: textSpan, textDirection: TextDirection.ltr);
    textPainter.layout();
    textPainter.paint(
      canvas,
      center - Offset(textPainter.width / 2, textPainter.height / 2),
    );
  }

  @override
  bool shouldRepaint(_RingPainter oldDelegate) => oldDelegate.score != score;
}
```

### CosmicLoader
Animated loading state with cosmic theme.

```dart
class CosmicLoader extends StatefulWidget {
  final double size;
  final Duration duration;

  const CosmicLoader({
    this.size = 48,
    this.duration = const Duration(seconds: 2),
  });

  @override
  State<CosmicLoader> createState() => _CosmicLoaderState();
}

class _CosmicLoaderState extends State<CosmicLoader>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(duration: widget.duration, vsync: this)
      ..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return RotationTransition(
      turns: _controller,
      child: Container(
        width: widget.size,
        height: widget.size,
        decoration: BoxDecoration(
          border: Border.all(color: Color(0xFF3A3A6E), width: 2),
          borderRadius: BorderRadius.circular(widget.size / 2),
        ),
        child: Center(
          child: Container(
            width: widget.size * 0.6,
            height: widget.size * 0.6,
            decoration: BoxDecoration(
              border: Border.all(color: sunGold, width: 1.5),
              borderRadius: BorderRadius.circular(widget.size / 3),
            ),
          ),
        ),
      ),
    );
  }
}
```

### LockedOverlay
Blur + lock visual for gated features.

```dart
class LockedOverlay extends StatelessWidget {
  final String requiredTier;
  final String featureTitle;
  final VoidCallback onUpgrade;

  const LockedOverlay({
    required this.requiredTier,
    required this.featureTitle,
    required this.onUpgrade,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 4, sigmaY: 4),
          child: Container(color: Colors.transparent),
        ),
        Center(
          child: GlassCard(
            width: 280,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.lock, size: 48, color: dangerRed),
                SizedBox(height: 16),
                Text(featureTitle, style: h3),
                SizedBox(height: 8),
                Text(
                  'Upgrade to $requiredTier',
                  style: bodyMed,
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 24),
                ElevatedButton(
                  onPressed: onUpgrade,
                  child: Text('Upgrade'),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
```

### TierBadge
Shows which tier is required for a feature.

```dart
class TierBadge extends StatelessWidget {
  final String tier;
  final Size size;

  const TierBadge({
    required this.tier,
    this.size = const Size(80, 28),
  });

  @override
  Widget build(BuildContext context) {
    const Map<String, Color> colors = {
      'free': infoBlue,
      'pro': jupiterOrange,
      'premium': sunGold,
    };

    return Container(
      width: size.width,
      height: size.height,
      decoration: BoxDecoration(
        color: colors[tier]?.withOpacity(0.2) ?? Colors.transparent,
        border: Border.all(color: colors[tier] ?? infoBlue, width: 1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Center(
        child: Text(
          tier.toUpperCase(),
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            color: colors[tier] ?? infoBlue,
          ),
        ),
      ),
    );
  }
}
```

### GradientText
Text with gradient fill, useful for headings.

```dart
class GradientText extends StatelessWidget {
  final String text;
  final List<Color> colors;
  final TextStyle baseStyle;

  const GradientText(
    this.text, {
    required this.colors,
    required this.baseStyle,
  });

  @override
  Widget build(BuildContext context) {
    return ShaderMask(
      shaderCallback: (bounds) => LinearGradient(
        colors: colors,
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ).createShader(bounds),
      child: Text(
        text,
        style: baseStyle.copyWith(color: Colors.white),
      ),
    );
  }
}
```

---

## Quick Reference: Provider Patterns

All providers follow Riverpod 2.x conventions:

```dart
// Stateless provider
final dailyForecastProvider = FutureProvider.family<DailyForecast, String>((ref, date) async {
  final api = ref.watch(apiClientProvider);
  return api.getDailyForecast(date);
});

// Stateful provider with local state
final chartStateProvider = StateNotifierProvider<ChartNotifier, ChartState>((ref) {
  return ChartNotifier();
});

// Consumer widget pattern
class DayScoreRing extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final forecast = ref.watch(dailyForecastProvider(date));
    return forecast.when(
      data: (data) => _buildRing(data.dayRating),
      loading: () => CosmicLoader(),
      error: (err, stack) => ErrorWidget(error: err),
    );
  }
}
```

---

## Animation Timing Reference

| Duration | Use Case |
|----------|----------|
| 150ms | Quick toggles, badge fills |
| 200ms | Score updates, text changes |
| 300ms | Standard transitions, slide-ins |
| 400ms | Ring animations, reveals |
| 500ms–800ms | Complex reveals, nested rings |
| 1.5s–2s | Continuous effects (glow, pulse, rotate) |

**Curves**: easeOutQuart (standard reveal), easeInOutQuad (rings), easeInOutCubic (smooth transitions)

---

## Tier Gating Reference

| Tier | Included Widgets |
|------|------------------|
| **Free** | Score rings, badges, alerts, panchanga basics, chat widgets, basic remedies |
| **Pro** | Dasha timelines, compatibility, shadbala, planetary wars, Sade Sati, D-charts, gems |
| **Premium** | Vimshopaka, ashtakavarga heatmap, atmakaraka, advanced dashboards, full reports |

Use `LockedOverlay` + `TierBadge` consistently for pro/premium features.

---

**Last Updated**: 2026-02-07
**Flutter Version**: 3.x
**Riverpod Version**: 2.x
**Dependencies**: fl_chart, riverpod, flutter_hooks
