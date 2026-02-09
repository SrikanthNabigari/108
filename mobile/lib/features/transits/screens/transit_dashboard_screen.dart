import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/features/timeline/widgets/transit_detail_panel.dart';
import 'package:one_zero_eight/features/transits/widgets/life_area_detail_panel.dart';

/// "Today" board — the house-centric transit dashboard.
///
/// Shows WHAT is active (life areas), WHY (planets + yogas), WHEN (dasha + triggers).
/// Follows the same design language as the dasha timeline screen.
class TransitDashboardScreen extends ConsumerStatefulWidget {
  const TransitDashboardScreen({super.key});

  @override
  ConsumerState<TransitDashboardScreen> createState() =>
      _TransitDashboardScreenState();
}

class _TransitDashboardScreenState extends ConsumerState<TransitDashboardScreen> {
  Map<String, dynamic>? _snapshotData;
  Map<String, dynamic>? _dashaData;
  List<dynamic>? _triggers;
  List<dynamic>? _yogas;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchAll();
  }

  Future<void> _fetchAll() async {
    final futures = await Future.wait([
      _safeFetch(ApiConstants.transitSnapshot),
      _safeFetch(ApiConstants.analysisDasha),
      _safeFetch(ApiConstants.transitTriggers(days: 30)),
      _safeFetch(ApiConstants.analysisYogas),
    ]);

    if (mounted) {
      setState(() {
        _snapshotData = futures[0] ?? _demoSnapshot;
        _dashaData = futures[1]?['current'] as Map<String, dynamic>? ?? _demoDasha;
        _triggers = (futures[2]?['triggers'] as List?) ?? [];
        _yogas = (futures[3]?['yogas'] as List?) ?? [];
        _loading = false;
      });
    }
  }

  Future<Map<String, dynamic>?> _safeFetch(String url) async {
    try {
      return await ApiService()
          .get(url, fromJson: (json) => json as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: _loading
              ? const Center(
                  child:
                      CircularProgressIndicator(color: C.accent, strokeWidth: 2),
                )
              : _buildBoard(),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════
  // MAIN BOARD
  // ═══════════════════════════════════════════════════════════════

  Widget _buildBoard() {
    final activations = _snapshotData?['house_activations'] as List? ?? [];
    final doubleTTHouses = (_snapshotData?['double_transit_houses'] as List?)
            ?.map((e) => e as int)
            .toSet() ??
        {};
    final trend = _snapshotData?['overall_trend'] as String? ?? 'mixed';
    final lordshipSummary =
        _snapshotData?['lordship_summary'] as Map<String, dynamic>? ?? {};
    final transitPositions =
        _snapshotData?['transit_positions'] as Map<String, dynamic>? ?? {};

    // Sort life areas by score (highest first)
    final sortedAreas = List<Map<String, dynamic>>.from(
      activations.map((a) => a as Map<String, dynamic>),
    )..sort((a, b) =>
        ((b['score'] as num?) ?? 0).compareTo((a['score'] as num?) ?? 0));

    // Count active areas (score >= 40)
    final activeCount = sortedAreas.where((a) => ((a['score'] as num?) ?? 0) >= 40).length;

    // Build planet list with house info
    final planetList = _buildPlanetList(transitPositions, activations);

    return SingleChildScrollView(
      padding: S.pagePadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: S.lg),

          // ── Header ──
          Center(
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    GestureDetector(
                      onTap: () => Navigator.of(context).pop(),
                      child: const Padding(
                        padding: EdgeInsets.only(right: S.sm),
                        child: Icon(Icons.arrow_back_ios, color: C.textSecondary, size: 18),
                      ),
                    ),
                    Text("What's Happening Now", style: T.h2),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'Transit activations on your chart',
                  style: T.bodySm.copyWith(color: C.textMuted),
                ),
              ],
            ),
          ),

          const SizedBox(height: S.xl),

          // ── Dasha Context + Trend ──
          GlassContainer(
            padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
            blur: 0,
            child: Row(
              children: [
                // Dasha info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (_dashaData != null) ...[
                        Row(
                          children: [
                            _planetDot(_dashaData!['mahadasha_lord'] as String? ?? ''),
                            const SizedBox(width: 4),
                            Text(
                              '${_capName(_dashaData!['mahadasha_lord'] as String? ?? '')} MD',
                              style: T.bodySm.copyWith(
                                color: C.textPrimary,
                                fontWeight: FontWeight.w600,
                                fontSize: 13,
                              ),
                            ),
                            if ((_dashaData!['antardasha_lord'] as String? ?? '').isNotEmpty) ...[
                              Text(' \u00b7 ', style: T.caption),
                              _planetDot(_dashaData!['antardasha_lord'] as String? ?? ''),
                              const SizedBox(width: 3),
                              Text(
                                '${_capName(_dashaData!['antardasha_lord'] as String? ?? '')} AD',
                                style: T.caption.copyWith(color: C.textSecondary, fontSize: 11),
                              ),
                            ],
                          ],
                        ),
                        if ((_dashaData!['pratyantardasha_lord'] as String? ?? '').isNotEmpty) ...[
                          const SizedBox(height: 2),
                          Row(
                            children: [
                              const SizedBox(width: 12),
                              _planetDot(_dashaData!['pratyantardasha_lord'] as String? ?? ''),
                              const SizedBox(width: 3),
                              Text(
                                '${_capName(_dashaData!['pratyantardasha_lord'] as String? ?? '')} PD',
                                style: T.caption.copyWith(fontSize: 10),
                              ),
                            ],
                          ),
                        ],
                      ],
                    ],
                  ),
                ),
                // Trend badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: S.sm, vertical: 4),
                  decoration: BoxDecoration(
                    borderRadius: R.xlBr,
                    color: _trendColor(trend).withValues(alpha: 0.15),
                    border: Border.all(color: _trendColor(trend).withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 6,
                        height: 6,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: _trendColor(trend),
                        ),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _capName(trend),
                        style: T.caption.copyWith(
                          color: _trendColor(trend),
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // ── Key insight ──
          if ((lordshipSummary['key_insight'] as String? ?? '').isNotEmpty) ...[
            const SizedBox(height: S.sm),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: S.xs),
              child: Text(
                lordshipSummary['key_insight'] as String,
                style: T.caption.copyWith(color: C.textSecondary, fontSize: 11),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],

          const SizedBox(height: S.xl),

          // ═══ WHAT — Life Areas ═══
          _SectionLabel(
            title: 'Life Areas',
            subtitle: '$activeCount active',
          ),
          const SizedBox(height: S.sm),
          SizedBox(
            height: 132,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: sortedAreas.length,
              separatorBuilder: (_, __) => const SizedBox(width: S.sm),
              itemBuilder: (_, i) {
                final area = sortedAreas[i];
                return _LifeAreaCard(
                  houseData: area,
                  isDoubleTT: doubleTTHouses.contains(area['house'] as int? ?? 0),
                  onTap: () => _onAreaTap(area),
                );
              },
            ),
          ),

          const SizedBox(height: S.xl),

          // ═══ WHY — Key Planets ═══
          _SectionLabel(
            title: 'Key Planets',
            subtitle: '${planetList.length} in transit',
          ),
          const SizedBox(height: S.sm),
          SizedBox(
            height: 100,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: planetList.length,
              separatorBuilder: (_, __) => const SizedBox(width: S.sm),
              itemBuilder: (_, i) {
                final p = planetList[i];
                return _PlanetCard(
                  planet: p['planet'] as String,
                  sign: p['sign'] as String,
                  lifeArea: p['life_area'] as String,
                  isRetrograde: p['is_retrograde'] as bool,
                  onTap: () =>
                      TransitDetailPanel.show(context, planet: p['planet'] as String),
                );
              },
            ),
          ),

          // ═══ Active Yogas (if available) ═══
          if (_yogas != null && _yogas!.isNotEmpty) ...[
            const SizedBox(height: S.xl),
            _SectionLabel(
              title: 'Active Yogas',
              subtitle: '${_yogas!.length} detected',
            ),
            const SizedBox(height: S.sm),
            GlassContainer(
              padding: const EdgeInsets.all(S.md),
              blur: 0,
              child: Column(
                children: _yogas!.take(5).map((y) {
                  final yoga = y as Map<String, dynamic>;
                  final name = yoga['name'] as String? ?? '';
                  final category = yoga['category'] as String? ?? '';
                  final strength = (yoga['strength'] as num?)?.toDouble() ?? 0;
                  final planets = (yoga['involved_planets'] as List?)?.cast<String>() ?? [];

                  return Padding(
                    padding: const EdgeInsets.only(bottom: S.sm),
                    child: Row(
                      children: [
                        // Strength dot
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: strength > 0.7
                                ? C.positive
                                : strength > 0.4
                                    ? C.warning
                                    : C.textMuted,
                          ),
                        ),
                        const SizedBox(width: S.sm),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                name,
                                style: T.bodySm.copyWith(
                                  color: C.textPrimary,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              Row(
                                children: [
                                  Text(
                                    category,
                                    style: T.caption.copyWith(
                                      color: _categoryColor(category),
                                      fontSize: 10,
                                    ),
                                  ),
                                  if (planets.isNotEmpty) ...[
                                    Text(' \u00b7 ', style: T.caption.copyWith(fontSize: 10)),
                                    ...planets.take(3).map((p) => Padding(
                                          padding: const EdgeInsets.only(right: 2),
                                          child: Text(
                                            planetGlyph(p),
                                            style: TextStyle(
                                                fontSize: 11, color: planetColor(p)),
                                          ),
                                        )),
                                  ],
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),
          ],

          // ═══ WHEN — Coming Up ═══
          if (_triggers != null && _triggers!.isNotEmpty) ...[
            const SizedBox(height: S.xl),
            _SectionLabel(
              title: 'Coming Up',
              subtitle: '30 days',
            ),
            const SizedBox(height: S.sm),
            ..._triggers!.take(8).map((t) {
              final trigger = t as Map<String, dynamic>;
              return _TriggerRow(trigger: trigger);
            }),
          ],

          const SizedBox(height: S.xl),

          // ── Continue to Home ──
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: () => context.go('/home'),
              child: const Text('Continue'),
            ),
          ),
          const SizedBox(height: S.xl),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════
  // HELPERS
  // ═══════════════════════════════════════════════════════════════

  void _onAreaTap(Map<String, dynamic> houseData) {
    final house = houseData['house'] as int? ?? 1;

    // Find lordship data
    final lordshipAnalysis = _snapshotData?['lordship_analysis'] as List? ?? [];
    Map<String, dynamic>? lordshipData;
    for (final l in lordshipAnalysis) {
      if ((l as Map<String, dynamic>)['house'] == house) {
        lordshipData = l;
        break;
      }
    }

    // Find yogas related to this house (simple: check if any involved planet is in this house)
    final relatedYogas = <Map<String, dynamic>>[];
    final planetsInHouse = (houseData['planets_present'] as List?)?.cast<String>() ?? [];
    for (final y in _yogas ?? []) {
      final yoga = y as Map<String, dynamic>;
      final involvedPlanets = (yoga['involved_planets'] as List?)?.cast<String>() ?? [];
      if (involvedPlanets.any((p) => planetsInHouse.contains(p.toLowerCase()))) {
        relatedYogas.add(yoga);
      }
    }

    // Filter triggers relevant to house's planets
    final relevantTriggers = <Map<String, dynamic>>[];
    final allHousePlanets = [...planetsInHouse, ...(houseData['planets_aspecting'] as List? ?? []).cast<String>()];
    for (final t in _triggers ?? []) {
      final trigger = t as Map<String, dynamic>;
      final triggerStr = (trigger['trigger'] as String? ?? '').toLowerCase();
      if (allHousePlanets.any((p) => triggerStr.contains(p.toLowerCase()))) {
        relevantTriggers.add(trigger);
      }
    }

    LifeAreaDetailPanel.show(
      context,
      houseData: houseData,
      lordshipData: lordshipData,
      dashaContext: _dashaData,
      triggers: relevantTriggers.take(5).toList(),
      activeYogas: relatedYogas,
    );
  }

  List<Map<String, dynamic>> _buildPlanetList(
    Map<String, dynamic> positions,
    List<dynamic> activations,
  ) {
    final result = <Map<String, dynamic>>[];
    for (final entry in positions.entries) {
      final planet = entry.key;
      final data = entry.value as Map<String, dynamic>? ?? {};
      final rashi = data['rashi'] as String? ?? '';
      final isRetro = data['is_retrograde'] as bool? ?? false;

      // Find which house this planet is in
      String lifeArea = '';
      for (final a in activations) {
        final h = a as Map<String, dynamic>;
        final planetsPresent = (h['planets_present'] as List?)?.cast<String>() ?? [];
        if (planetsPresent.any((p) => p.toLowerCase() == planet.toLowerCase())) {
          final houseNum = h['house'] as int? ?? 0;
          lifeArea = houseLifeArea[houseNum] ?? '';
          break;
        }
      }

      result.add({
        'planet': planet,
        'sign': rashi,
        'life_area': lifeArea,
        'is_retrograde': isRetro,
      });
    }
    return result;
  }

  Color _trendColor(String trend) => switch (trend) {
        'favorable' => C.positive,
        'challenging' => C.negative,
        _ => C.warning,
      };

  Color _categoryColor(String cat) => switch (cat) {
        'raja' => C.jupiter,
        'dhana' => C.venus,
        'pancha_mahapurusha' => C.saturn,
        _ => C.textSecondary,
      };

  String _capName(String s) => s.isEmpty ? '' : s[0].toUpperCase() + s.substring(1);

  Widget _planetDot(String planet) {
    if (planet.isEmpty) return const SizedBox.shrink();
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: planetColor(planet),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════
  // DEMO DATA
  // ═══════════════════════════════════════════════════════════════

  static final Map<String, dynamic> _demoDasha = {
    'mahadasha_lord': 'mercury',
    'antardasha_lord': 'venus',
    'pratyantardasha_lord': 'mars',
  };

  static final Map<String, dynamic> _demoSnapshot = {
    'transit_positions': {
      'sun': {'longitude': 294.5, 'rashi_num': 9, 'rashi': 'Capricorn', 'degree_in_rashi': 24.5, 'is_retrograde': false},
      'moon': {'longitude': 72.3, 'rashi_num': 2, 'rashi': 'Gemini', 'degree_in_rashi': 12.3, 'is_retrograde': false},
      'mars': {'longitude': 88.7, 'rashi_num': 2, 'rashi': 'Gemini', 'degree_in_rashi': 28.7, 'is_retrograde': false},
      'mercury': {'longitude': 280.1, 'rashi_num': 9, 'rashi': 'Capricorn', 'degree_in_rashi': 10.1, 'is_retrograde': false},
      'jupiter': {'longitude': 70.4, 'rashi_num': 2, 'rashi': 'Gemini', 'degree_in_rashi': 10.4, 'is_retrograde': false},
      'venus': {'longitude': 318.9, 'rashi_num': 10, 'rashi': 'Aquarius', 'degree_in_rashi': 18.9, 'is_retrograde': false},
      'saturn': {'longitude': 332.6, 'rashi_num': 11, 'rashi': 'Pisces', 'degree_in_rashi': 2.6, 'is_retrograde': false},
      'rahu': {'longitude': 330.2, 'rashi_num': 11, 'rashi': 'Pisces', 'degree_in_rashi': 0.2, 'is_retrograde': true},
      'ketu': {'longitude': 150.2, 'rashi_num': 5, 'rashi': 'Virgo', 'degree_in_rashi': 0.2, 'is_retrograde': true},
    },
    'house_activations': [
      {'house': 1, 'sign': 6, 'score': 42, 'grade': 'active', 'planets_present': [], 'planets_aspecting': ['jupiter'], 'double_transit': false, 'themes': ['self', 'health', 'personality'], 'summary': 'Jupiter aspect supports personal growth and confidence.'},
      {'house': 2, 'sign': 7, 'score': 18, 'grade': 'quiet', 'planets_present': [], 'planets_aspecting': [], 'double_transit': false, 'themes': ['wealth', 'speech', 'family'], 'summary': 'A quiet period for finances \u2014 good for saving.'},
      {'house': 3, 'sign': 8, 'score': 32, 'grade': 'moderate', 'planets_present': [], 'planets_aspecting': ['mars'], 'double_transit': false, 'themes': ['siblings', 'courage', 'short travel'], 'summary': 'Mars aspect brings energy to communications.'},
      {'house': 4, 'sign': 9, 'score': 55, 'grade': 'active', 'planets_present': ['sun', 'mercury'], 'planets_aspecting': [], 'double_transit': false, 'themes': ['home', 'mother', 'property', 'education'], 'summary': 'Sun-Mercury conjunction activates domestic and educational matters.'},
      {'house': 5, 'sign': 10, 'score': 38, 'grade': 'moderate', 'planets_present': ['venus'], 'planets_aspecting': [], 'double_transit': false, 'themes': ['children', 'creativity', 'romance'], 'summary': 'Venus brings creative inspiration and romantic energy.'},
      {'house': 6, 'sign': 11, 'score': 72, 'grade': 'highly_active', 'planets_present': ['saturn', 'rahu'], 'planets_aspecting': ['jupiter'], 'double_transit': true, 'themes': ['enemies', 'service', 'health', 'competition'], 'summary': 'Double transit \u2014 strong push to overcome obstacles and rivals.'},
      {'house': 7, 'sign': 0, 'score': 24, 'grade': 'moderate', 'planets_present': [], 'planets_aspecting': [], 'double_transit': false, 'themes': ['partnership', 'marriage', 'trade'], 'summary': 'Quiet period for partnerships \u2014 maintain status quo.'},
      {'house': 8, 'sign': 1, 'score': 15, 'grade': 'quiet', 'planets_present': [], 'planets_aspecting': [], 'double_transit': false, 'themes': ['transformation', 'longevity'], 'summary': 'Low activation \u2014 generally favorable for stability.'},
      {'house': 9, 'sign': 2, 'score': 68, 'grade': 'active', 'planets_present': ['jupiter', 'mars'], 'planets_aspecting': [], 'double_transit': false, 'themes': ['fortune', 'dharma', 'guru', 'father'], 'summary': 'Jupiter in 9th \u2014 excellent for spiritual growth and luck.'},
      {'house': 10, 'sign': 3, 'score': 78, 'grade': 'highly_active', 'planets_present': [], 'planets_aspecting': ['saturn', 'jupiter'], 'double_transit': true, 'themes': ['career', 'status', 'karma', 'public image'], 'summary': 'Double transit on career house \u2014 major developments expected.'},
      {'house': 11, 'sign': 4, 'score': 28, 'grade': 'moderate', 'planets_present': [], 'planets_aspecting': [], 'double_transit': false, 'themes': ['gains', 'friends', 'aspirations'], 'summary': 'Moderate networking and gains period.'},
      {'house': 12, 'sign': 5, 'score': 35, 'grade': 'moderate', 'planets_present': ['ketu'], 'planets_aspecting': [], 'double_transit': false, 'themes': ['loss', 'moksha', 'foreign', 'expenses'], 'summary': 'Ketu supports spiritual detachment and letting go.'},
    ],
    'double_transit_houses': [6, 10],
    'most_active_houses': [10, 6, 9],
    'overall_trend': 'favorable',
    'lordship_analysis': [],
    'lordship_summary': {
      'yogakaraka_transits': ['saturn'],
      'key_insight': 'Saturn yogakaraka in 6th conquers enemies while career gets double transit',
    },
  };
}

// ═══════════════════════════════════════════════════════════════
// WIDGETS
// ═══════════════════════════════════════════════════════════════

class _SectionLabel extends StatelessWidget {
  final String title;
  final String subtitle;
  const _SectionLabel({required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(title, style: T.h3.copyWith(fontSize: 16)),
        const SizedBox(width: S.sm),
        Text(subtitle, style: T.caption),
      ],
    );
  }
}

// ── Life Area Card (WHAT) ──

class _LifeAreaCard extends StatelessWidget {
  final Map<String, dynamic> houseData;
  final bool isDoubleTT;
  final VoidCallback? onTap;

  const _LifeAreaCard({
    required this.houseData,
    required this.isDoubleTT,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final house = houseData['house'] as int? ?? 1;
    final score = (houseData['score'] as num?)?.toDouble() ?? 0;
    final grade = houseData['grade'] as String? ?? 'quiet';
    final areaName = houseLifeArea[house] ?? 'House $house';
    final planetsPresent =
        (houseData['planets_present'] as List?)?.cast<String>() ?? [];
    final planetsAspecting =
        (houseData['planets_aspecting'] as List?)?.cast<String>() ?? [];

    final isHighlighted = grade == 'highly_active' || grade == 'active';
    final accentColor = isDoubleTT ? C.jupiter : _gradeAccent(grade);

    return GestureDetector(
      onTap: onTap,
      child: Stack(
        children: [
          Container(
            width: 104,
            padding: const EdgeInsets.symmetric(vertical: S.sm, horizontal: S.sm),
            decoration: BoxDecoration(
              borderRadius: R.lgBr,
              color: isHighlighted
                  ? accentColor.withValues(alpha: 0.14)
                  : accentColor.withValues(alpha: 0.04),
              border: Border.all(
                color: isHighlighted
                    ? accentColor.withValues(alpha: 0.5)
                    : accentColor.withValues(alpha: 0.12),
                width: isHighlighted ? 1.5 : 0.5,
              ),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Score
                Text(
                  '${score.toInt()}',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: accentColor,
                  ),
                ),
                const SizedBox(height: 2),
                // Life area name
                Text(
                  areaName,
                  style: T.bodySm.copyWith(
                    color: C.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 11,
                  ),
                  textAlign: TextAlign.center,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                // Planet glyphs
                if (planetsPresent.isNotEmpty || planetsAspecting.isNotEmpty)
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      ...planetsPresent.take(3).map((p) => Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 1),
                            child: Text(planetGlyph(p),
                                style: TextStyle(fontSize: 12, color: planetColor(p))),
                          )),
                      if (planetsAspecting.isNotEmpty && planetsPresent.isNotEmpty)
                        Text(' ', style: T.caption.copyWith(fontSize: 8)),
                      ...planetsAspecting.take(2).map((p) => Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 1),
                            child: Text(planetGlyph(p),
                                style: TextStyle(
                                    fontSize: 11,
                                    color: planetColor(p).withValues(alpha: 0.6))),
                          )),
                    ],
                  ),
                // Double transit badge
                if (isDoubleTT) ...[
                  const SizedBox(height: 3),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: S.sm, vertical: 2),
                    decoration: BoxDecoration(
                      borderRadius: R.xlBr,
                      color: C.jupiter.withValues(alpha: 0.2),
                    ),
                    child: const Text(
                      'DOUBLE',
                      style: TextStyle(
                        fontSize: 7,
                        fontWeight: FontWeight.w700,
                        color: C.jupiter,
                        letterSpacing: 0.8,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _gradeAccent(String grade) => switch (grade) {
        'highly_active' => C.positive,
        'active' => C.jupiter,
        'moderate' => C.textSecondary,
        _ => C.textMuted,
      };
}

// ── Planet Card (WHY) ──

class _PlanetCard extends StatelessWidget {
  final String planet;
  final String sign;
  final String lifeArea;
  final bool isRetrograde;
  final VoidCallback? onTap;

  const _PlanetCard({
    required this.planet,
    required this.sign,
    required this.lifeArea,
    required this.isRetrograde,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = planetColor(planet);

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 90,
        padding: const EdgeInsets.symmetric(vertical: S.sm, horizontal: S.xs),
        decoration: BoxDecoration(
          borderRadius: R.lgBr,
          color: color.withValues(alpha: 0.06),
          border: Border.all(color: color.withValues(alpha: 0.2), width: 0.5),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  planetGlyph(planet),
                  style: TextStyle(fontSize: 18, color: color),
                ),
                if (isRetrograde) ...[
                  const SizedBox(width: 2),
                  Text(
                    'Rx',
                    style: TextStyle(
                      fontSize: 8,
                      fontWeight: FontWeight.w700,
                      color: C.warning,
                    ),
                  ),
                ],
              ],
            ),
            const SizedBox(height: 2),
            Text(
              planetName(planet),
              style: T.bodySm.copyWith(
                color: C.textPrimary,
                fontWeight: FontWeight.w600,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 1),
            Text(
              sign,
              style: T.caption.copyWith(color: color, fontSize: 10),
            ),
            if (lifeArea.isNotEmpty) ...[
              const SizedBox(height: 2),
              Text(
                '\u2192 ${lifeArea.split(' & ').first}',
                style: T.caption.copyWith(fontSize: 9),
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

// ── Trigger Row (WHEN) ──

class _TriggerRow extends StatefulWidget {
  final Map<String, dynamic> trigger;
  const _TriggerRow({required this.trigger});

  @override
  State<_TriggerRow> createState() => _TriggerRowState();
}

class _TriggerRowState extends State<_TriggerRow> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final trigger = widget.trigger;
    final daysFromNow = trigger['days_from_now'] as int? ?? trigger['days'] as int? ?? 0;
    final text = trigger['trigger'] as String? ?? trigger['description'] as String? ?? '';
    final significance = trigger['significance'] as String? ?? 'medium';
    final effect = trigger['what'] as String? ?? trigger['effect'] as String? ?? '';

    final Color sigColor = switch (significance) {
      'high' => C.warning,
      'low' => C.textMuted,
      _ => C.textSecondary,
    };

    return GestureDetector(
      onTap: effect.isNotEmpty ? () => setState(() => _expanded = !_expanded) : null,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 2),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: 38,
              child: Column(
                children: [
                  Text(
                    '$daysFromNow',
                    style: T.bodySm.copyWith(
                      color: sigColor,
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                  Text(
                    daysFromNow == 1 ? 'day' : 'days',
                    style: T.caption.copyWith(fontSize: 8),
                  ),
                ],
              ),
            ),
            Column(
              children: [
                Container(
                  width: 6,
                  height: 6,
                  decoration: BoxDecoration(shape: BoxShape.circle, color: sigColor),
                ),
                Container(width: 1, height: _expanded ? 44 : 28, color: C.glassBorder),
              ],
            ),
            const SizedBox(width: S.sm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          text,
                          style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 12),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (effect.isNotEmpty)
                        Icon(
                          _expanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                          size: 16,
                          color: C.textMuted,
                        ),
                    ],
                  ),
                  if (effect.isNotEmpty && _expanded)
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        effect,
                        style: T.caption.copyWith(
                          color: C.textSecondary,
                          fontSize: 10,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
