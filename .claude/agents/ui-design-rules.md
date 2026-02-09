# 108 UI Design Rules & References

## Design Language — "Cosmic Glass"

All screens MUST follow the same dark glassmorphism language established by the Dasha Timeline screen.

### Colors (from `core/theme/app_theme.dart`)
- Background: `C.bg` (#050508) — near black
- Surface: `C.surface` (#0D0D14) — card backgrounds
- Glass: `C.glassBg` (white 6%), `C.glassBorder` (white 10%)
- Accent: `C.accent` (#E8E8E8) — soft white, NOT a bright color
- Planet colors: `C.sun`, `C.moon`, `C.mars`, `C.mercury`, `C.jupiter`, `C.venus`, `C.saturn`, `C.rahu`, `C.ketu`
- Status: `C.positive` (green), `C.warning` (amber), `C.negative` (red)
- Text: `C.textPrimary` (white-ish), `C.textSecondary` (grey), `C.textMuted` (dark grey)

### Card Pattern — `_PeriodCard` (timeline_screen.dart:767)
Every tappable data card follows this pattern:
- `Container` with `borderRadius: R.lgBr` (16px)
- Background: `planetColor.withValues(alpha: 0.04)` (dim) or `0.18` (highlighted)
- Border: `planetColor.withValues(alpha: 0.15)` (dim) or `0.6` (highlighted)
- Content: Glyph → Name → Info → Badge
- Current item gets a "NOW" badge pill
- Selected item gets brighter border

### Horizontal Scroll Sections
- Section header: `_SectionLabel(title:, subtitle:)` — title in `T.h3(fontSize:16)`, subtitle in `T.caption`
- Cards in `SizedBox(height: N)` + `ListView.separated(scrollDirection: Axis.horizontal)`
- Card sizes: large=100w, medium=90w, small=76w
- Separator: `SizedBox(width: S.sm)` (8px)

### Glass Container (`shared/widgets/glass_container.dart`)
- For larger info sections (not scrollable cards)
- `GlassContainer(blur: 0, padding: EdgeInsets.all(S.lg))` — no blur for perf
- Has frosted border and shadow

### Bottom Sheet Pattern (`transit_detail_panel.dart`)
- `showModalBottomSheet(backgroundColor: transparent, isScrollControlled: true)`
- `DraggableScrollableSheet(initialChildSize: 0.65-0.75)`
- Container with `C.surface` background + top rounded corners
- Gradient header: planet/area color fading to transparent
- Drag handle bar at top (40×4, glassBorder color)
- Content in ListView with scroll controller
- "Ask AI" button at bottom with SafeArea

### Planet Helpers (`shared/utils/planet_helpers.dart`)
- `planetGlyph(name)` → Unicode glyph (☉ ☽ ♂ ☿ ♃ ♀ ♄ ☊ ☋)
- `planetName(name)` → Capitalized name
- `planetColor(name)` → Theme color
- `rashiNames[0-11]` → Full sign names
- `rashiAbbrev[0-11]` → 3-letter abbreviations

### Ambient Background (`shared/widgets/ambient_background.dart`)
- Wrap every screen's Scaffold body with `AmbientBackground(child:)`
- Provides the star field / cosmic background

### API Pattern (`data/services/api_service.dart`)
- `ApiService().get(url, fromJson: (json) => json as Map<String, dynamic>)`
- Constants in `core/constants/api_constants.dart`
- Always provide demo data fallback for offline mode

## Screen Architecture

### Flow: Timeline → Today → Home
```
TimelineScreen (/timeline) — "Your Life Chapters" (WHEN)
  │ [Continue button]
  ▼
TransitDashboardScreen (/transits) — "What's Happening Now" (WHAT + WHEN + WHY)
  │ [Continue button]
  ▼
HomeScreen (/home) — Daily brief + chat
```

### WHAT / WHEN / WHY Framework
Every transit/forecast screen should answer three questions:
- **WHAT** is happening? → Life areas, yogas, patterns (SELF layer)
- **WHEN** is it happening? → Dasha periods, transit duration (CONTEXT layer)
- **WHY** is it happening? → Planets causing it, double transit, lordship (CONTEXT + SELF)

### Data Sources for "Today" Board
| Section | Endpoint | Key fields |
|---------|----------|------------|
| Current dasha context | `/analysis/dasha` | current.mahadasha_lord, antardasha_lord, pratyantardasha_lord |
| House activations (WHAT) | `/analysis/transits/snapshot` | house_activations[].score, themes, planets_present |
| Planet positions (WHY) | `/analysis/transits/snapshot` | transit_positions.{planet}.rashi, house |
| Double transit | `/analysis/transits/snapshot` | double_transit_houses, lordship_summary |
| Upcoming triggers (WHEN) | `/analysis/transits/triggers?days=30` | triggers[].date, trigger, type, significance |
| Active yogas | `/analysis/yogas` | detected yogas with involved_planets |
| Active aspects | `/analysis/transits/aspects` | aspects[].transit_planet, effect |

### House → Life Area Mapping
Houses should NEVER be shown as "House 10" to users. Always use life area names:
```dart
const houseLifeArea = {
  1: 'Self & Health',     2: 'Wealth & Family',
  3: 'Courage & Effort',  4: 'Home & Education',
  5: 'Children & Romance',6: 'Health & Service',
  7: 'Partnership',       8: 'Transformation',
  9: 'Fortune & Dharma',  10: 'Career & Status',
  11: 'Gains & Friends',  12: 'Spirituality',
};
```

### Demo Data
Every screen MUST have static demo data fallback for when API is unreachable.
Use the user's actual chart data for realistic demos (Libra lagna, Mercury MD).
