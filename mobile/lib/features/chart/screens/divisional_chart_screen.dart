import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';

// ---------------------------------------------------------------------------
// Division metadata
// ---------------------------------------------------------------------------

class _DivisionInfo {
  final int number;
  final String name;
  final String sanskrit;
  final String purpose;
  final bool popular;

  const _DivisionInfo({
    required this.number,
    required this.name,
    required this.sanskrit,
    required this.purpose,
    this.popular = false,
  });
}

const _kDivisions = <_DivisionInfo>[
  _DivisionInfo(number: 1, name: 'Rashi', sanskrit: 'Rashi', purpose: 'Main birth chart — overall life blueprint', popular: true),
  _DivisionInfo(number: 2, name: 'Hora', sanskrit: 'Hora', purpose: 'Wealth and financial prosperity'),
  _DivisionInfo(number: 3, name: 'Drekkana', sanskrit: 'Drekkana', purpose: 'Siblings, courage, and communication'),
  _DivisionInfo(number: 4, name: 'Chaturthamsha', sanskrit: 'Chaturthamsha', purpose: 'Property, home, and fixed assets'),
  _DivisionInfo(number: 7, name: 'Saptamsha', sanskrit: 'Saptamsha', purpose: 'Children and progeny'),
  _DivisionInfo(number: 9, name: 'Navamsha', sanskrit: 'Navamsha', purpose: 'Marriage, dharma, and inner self', popular: true),
  _DivisionInfo(number: 10, name: 'Dashamsha', sanskrit: 'Dashamsha', purpose: 'Career, profession, and public image', popular: true),
  _DivisionInfo(number: 12, name: 'Dwadashamsha', sanskrit: 'Dwadashamsha', purpose: 'Parents and ancestral karma'),
  _DivisionInfo(number: 16, name: 'Shodashamsha', sanskrit: 'Shodashamsha', purpose: 'Vehicles, comforts, and luxuries'),
  _DivisionInfo(number: 20, name: 'Vimshamsha', sanskrit: 'Vimshamsha', purpose: 'Spiritual progress and upasana'),
  _DivisionInfo(number: 24, name: 'Chaturvimshamsha', sanskrit: 'Chaturvimshamsha', purpose: 'Education, learning, and knowledge'),
  _DivisionInfo(number: 27, name: 'Bhamsha', sanskrit: 'Nakshatramsha', purpose: 'Strengths and weaknesses'),
  _DivisionInfo(number: 30, name: 'Trimshamsha', sanskrit: 'Trimshamsha', purpose: 'Misfortunes and hardships'),
  _DivisionInfo(number: 40, name: 'Khavedamsha', sanskrit: 'Khavedamsha', purpose: 'Auspicious and inauspicious effects'),
  _DivisionInfo(number: 45, name: 'Akshavedamsha', sanskrit: 'Akshavedamsha', purpose: 'General well-being and character'),
  _DivisionInfo(number: 60, name: 'Shashtiamsha', sanskrit: 'Shashtiamsha', purpose: 'Past-life karma — most subtle division'),
];

// ---------------------------------------------------------------------------
// Dignity tables (standard Parashari exaltation/debilitation)
// ---------------------------------------------------------------------------

const _kExaltation = <String, String>{
  'sun': 'Aries', 'moon': 'Taurus', 'mars': 'Capricorn',
  'mercury': 'Virgo', 'jupiter': 'Cancer', 'venus': 'Pisces',
  'saturn': 'Libra',
};

const _kDebilitation = <String, String>{
  'sun': 'Libra', 'moon': 'Scorpio', 'mars': 'Cancer',
  'mercury': 'Pisces', 'jupiter': 'Capricorn', 'venus': 'Virgo',
  'saturn': 'Aries',
};

const _kOwnSigns = <String, List<String>>{
  'sun': ['Leo'],
  'moon': ['Cancer'],
  'mars': ['Aries', 'Scorpio'],
  'mercury': ['Gemini', 'Virgo'],
  'jupiter': ['Sagittarius', 'Pisces'],
  'venus': ['Taurus', 'Libra'],
  'saturn': ['Capricorn', 'Aquarius'],
};

String _dignity(String planet, String rashi) {
  final p = planet.toLowerCase();
  if (_kExaltation[p] == rashi) return 'Exalted';
  if (_kDebilitation[p] == rashi) return 'Debilitated';
  if (_kOwnSigns[p]?.contains(rashi) ?? false) return 'Own';
  return 'Neutral';
}

Color _dignityColor(String dignity) {
  switch (dignity) {
    case 'Exalted':
      return C.positive;
    case 'Own':
      return C.jupiter;
    case 'Debilitated':
      return C.negative;
    default:
      return C.textMuted;
  }
}

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

final _kMockD9 = <Map<String, dynamic>>[
  {'name': 'Sun', 'longitude': 228.5, 'rashi': 'Scorpio', 'rashi_number': 8, 'degree_in_sign': 18.5},
  {'name': 'Moon', 'longitude': 116.3, 'rashi': 'Cancer', 'rashi_number': 4, 'degree_in_sign': 26.3},
  {'name': 'Mars', 'longitude': 275.8, 'rashi': 'Capricorn', 'rashi_number': 10, 'degree_in_sign': 5.8},
  {'name': 'Mercury', 'longitude': 205.1, 'rashi': 'Libra', 'rashi_number': 7, 'degree_in_sign': 25.1},
  {'name': 'Jupiter', 'longitude': 344.6, 'rashi': 'Pisces', 'rashi_number': 12, 'degree_in_sign': 14.6},
  {'name': 'Venus', 'longitude': 162.9, 'rashi': 'Virgo', 'rashi_number': 6, 'degree_in_sign': 12.9},
  {'name': 'Saturn', 'longitude': 310.4, 'rashi': 'Aquarius', 'rashi_number': 11, 'degree_in_sign': 10.4},
  {'name': 'Rahu', 'longitude': 55.2, 'rashi': 'Taurus', 'rashi_number': 2, 'degree_in_sign': 25.2},
  {'name': 'Ketu', 'longitude': 235.2, 'rashi': 'Scorpio', 'rashi_number': 8, 'degree_in_sign': 25.2},
];

// ===========================================================================
// Screen
// ===========================================================================

class DivisionalChartScreen extends ConsumerStatefulWidget {
  const DivisionalChartScreen({super.key});

  @override
  ConsumerState<DivisionalChartScreen> createState() =>
      _DivisionalChartScreenState();
}

class _DivisionalChartScreenState extends ConsumerState<DivisionalChartScreen> {
  int _selectedIndex = 5; // default D9 (index 5 in _kDivisions)
  List<Map<String, dynamic>> _planets = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchChart();
  }

  Future<void> _fetchChart() async {
    setState(() => _loading = true);
    final div = _kDivisions[_selectedIndex];
    try {
      final result = await ApiService().get<Map<String, dynamic>>(
        ApiConstants.chartDivisional(div.number.toString()),
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (!mounted) return;
      setState(() {
        _planets = (result['planets'] as List<dynamic>)
            .cast<Map<String, dynamic>>();
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _planets = _kMockD9;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final div = _kDivisions[_selectedIndex];

    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          bottom: false,
          child: Column(
            children: [
              // App bar
              Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.lg, vertical: S.sm),
                child: Row(
                  children: [
                    GestureDetector(
                      onTap: () => context.canPop()
                          ? context.pop()
                          : context.go('/home'),
                      child: const Icon(Icons.arrow_back_ios,
                          color: C.textSecondary, size: 18),
                    ),
                    const SizedBox(width: S.sm),
                    Text('Divisional Charts', style: T.h3),
                  ],
                ),
              ),
              const Divider(height: 1),

              // Division chips
              SizedBox(
                height: 48,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(
                      horizontal: S.lg, vertical: S.sm),
                  itemCount: _kDivisions.length,
                  separatorBuilder: (_, __) => const SizedBox(width: S.sm),
                  itemBuilder: (_, i) {
                    final d = _kDivisions[i];
                    final selected = i == _selectedIndex;
                    final chipColor = d.popular ? C.jupiter : C.accent;
                    return GestureDetector(
                      onTap: () {
                        setState(() => _selectedIndex = i);
                        _fetchChart();
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: S.md, vertical: S.xs),
                        decoration: BoxDecoration(
                          color: selected
                              ? chipColor.withValues(alpha: 0.15)
                              : Colors.transparent,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: selected
                                ? chipColor.withValues(alpha: 0.4)
                                : C.glassBorder,
                          ),
                        ),
                        child: Center(
                          child: Text(
                            'D${d.number}',
                            style: T.bodySm.copyWith(
                              color: selected ? chipColor : C.textSecondary,
                              fontWeight:
                                  selected ? FontWeight.w600 : FontWeight.w400,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),

              // Content
              Expanded(
                child: RefreshIndicator(
                  onRefresh: _fetchChart,
                  color: C.accent,
                  backgroundColor: C.surface,
                  child: ListView(
                    padding: S.pagePadding.copyWith(top: S.lg, bottom: S.xxxl),
                    children: [
                      // Title section
                      Text(
                        'D${div.number} — ${div.name}',
                        style: T.h2,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: S.xs),
                      Text(
                        div.sanskrit,
                        style: T.bodySm.copyWith(color: C.textMuted),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: S.sm),
                      Text(
                        div.purpose,
                        style: T.bodySm,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: S.xl),

                      // Planet grid
                      if (_loading)
                        const Padding(
                          padding: EdgeInsets.only(top: S.xxxl),
                          child: Center(
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: C.accent),
                          ),
                        )
                      else
                        _buildPlanetGrid(),

                      const SizedBox(height: S.xl),

                      // Educational card
                      GlassContainer(
                        padding: const EdgeInsets.all(S.lg),
                        borderColor: C.saturn.withValues(alpha: 0.2),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.school,
                                    color: C.saturn, size: 18),
                                const SizedBox(width: S.sm),
                                Text(
                                  'About D${div.number} ${div.name}',
                                  style: T.bodySm.copyWith(
                                    color: C.saturn,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: S.sm),
                            Text(
                              _educationalText(div),
                              style: T.bodySm.copyWith(height: 1.6),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPlanetGrid() {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: _planets.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: S.sm,
        crossAxisSpacing: S.sm,
        childAspectRatio: 0.85,
      ),
      itemBuilder: (_, i) => _buildPlanetCard(_planets[i]),
    );
  }

  Widget _buildPlanetCard(Map<String, dynamic> planet) {
    final name = (planet['name'] as String?) ?? '';
    final rashi = (planet['rashi'] as String?) ?? '';
    final degree = (planet['degree_in_sign'] as num?)?.toDouble() ?? 0;
    final pKey = name.toLowerCase();
    final glyph = planetGlyph(pKey);
    final color = planetColor(pKey);
    final dig = _dignity(pKey, rashi);
    final digColor = _dignityColor(dig);

    return GlassContainer(
      padding: const EdgeInsets.all(S.sm),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Glyph
          Text(glyph,
              style: TextStyle(fontSize: 22, color: color)),
          const SizedBox(height: S.xs),
          // Name
          Text(name,
              style: T.bodySm.copyWith(
                  color: C.textPrimary,
                  fontWeight: FontWeight.w600,
                  fontSize: 12)),
          const SizedBox(height: 2),
          // Rashi + degree
          Text(
            '$rashi ${degree.toStringAsFixed(1)}',
            style: T.caption.copyWith(fontSize: 10),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: S.xs),
          // Dignity badge
          Container(
            padding: const EdgeInsets.symmetric(
                horizontal: S.sm, vertical: 2),
            decoration: BoxDecoration(
              color: digColor.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              dig,
              style: T.caption.copyWith(
                color: digColor,
                fontWeight: FontWeight.w600,
                fontSize: 9,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _educationalText(_DivisionInfo div) {
    switch (div.number) {
      case 1:
        return 'The Rashi chart (D1) is the foundation of all analysis. '
            'It shows where planets were placed in the zodiac at the moment '
            'of birth and reveals the overall life pattern.';
      case 9:
        return 'Navamsha (D9) is the most important divisional chart after D1. '
            'It reveals the quality of marriage, inner spiritual nature, and '
            'the strength of planets. A well-placed planet in D9 strengthens '
            'its D1 promise.';
      case 10:
        return 'Dashamsha (D10) focuses on career and professional life. '
            'Planet placements here show the nature of your profession, '
            'success potential, and public standing.';
      default:
        return 'The D${div.number} (${div.name}) chart divides each sign into '
            '${div.number} equal parts. It is specifically analyzed for: '
            '${div.purpose.toLowerCase()}. Examine planet placements here '
            'to understand this area of life in greater depth.';
    }
  }
}
