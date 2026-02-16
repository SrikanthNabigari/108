import 'dart:math';
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
// Query types
// ---------------------------------------------------------------------------

class _QueryType {
  final String id;
  final String label;
  final String house;
  final IconData icon;
  final Color color;

  const _QueryType({
    required this.id,
    required this.label,
    required this.house,
    required this.icon,
    required this.color,
  });
}

const _kQueries = <_QueryType>[
  _QueryType(id: 'marriage', label: 'Marriage', house: 'H7', icon: Icons.favorite, color: C.venus),
  _QueryType(id: 'career', label: 'Career', house: 'H10', icon: Icons.work, color: C.saturn),
  _QueryType(id: 'children', label: 'Children', house: 'H5', icon: Icons.child_care, color: C.jupiter),
  _QueryType(id: 'wealth', label: 'Wealth', house: 'H2', icon: Icons.account_balance_wallet, color: C.jupiter),
  _QueryType(id: 'health', label: 'Health', house: 'H1', icon: Icons.favorite_border, color: C.sun),
  _QueryType(id: 'education', label: 'Education', house: 'H4', icon: Icons.school, color: C.mercury),
  _QueryType(id: 'travel_short', label: 'Short Travel', house: 'H3', icon: Icons.directions_car, color: C.mercury),
  _QueryType(id: 'travel_foreign', label: 'Foreign Travel', house: 'H9/12', icon: Icons.flight, color: C.rahu),
  _QueryType(id: 'property', label: 'Property', house: 'H4', icon: Icons.home, color: C.moon),
  _QueryType(id: 'legal', label: 'Legal Matters', house: 'H6', icon: Icons.gavel, color: C.mars),
  _QueryType(id: 'spiritual', label: 'Spiritual', house: 'H9', icon: Icons.self_improvement, color: C.ketu),
];

// ---------------------------------------------------------------------------
// Mock result
// ---------------------------------------------------------------------------

final _kMockResult = <String, dynamic>{
  'prediction': {
    'query_type': 'career',
    'primary_house': 10,
    'cusp_analysis': {
      'sign': 'Cancer',
      'sign_lord': 'Moon',
      'star_lord': 'Saturn',
      'sub_lord': 'Mercury',
    },
    'judgment': 'favorable',
    'confidence': 78,
    'timing_hints': [
      'Moon dasha activates career house',
      'Saturn transit over 10th cusp in 2026',
      'Mercury sub-period favorable for communication roles',
    ],
    'explanation':
        'Sub-lord Mercury significates houses 2 (family/wealth), 10 (career/status), '
            '11 (gains/income/friends) — strong support. Star lord Saturn backs via '
            'houses 6 (enemies/service/health issues). Mercury is retrograde — delayed '
            'but not denied.',
  },
  'significators': {
    '10': {
      'level_1': ['Moon'],
      'level_2': ['Saturn', 'Mars'],
      'level_3': ['Mercury', 'Venus'],
      'level_4': ['Jupiter'],
      'all_significators': ['Moon', 'Saturn', 'Mars', 'Mercury', 'Venus', 'Jupiter'],
    },
  },
  'timing_windows': [
    {
      'md_lord': 'Venus',
      'ad_lord': 'Moon',
      'start': '2013-08-10',
      'end': '2015-04-10',
      'is_past': true,
      'is_current': false,
      'pd_periods': <Map<String, dynamic>>[],
    },
    {
      'md_lord': 'Mercury',
      'ad_lord': 'Moon',
      'start': '2025-11-14',
      'end': '2027-04-12',
      'is_past': false,
      'is_current': true,
      'pd_periods': <Map<String, dynamic>>[
        {
          'pd_lord': 'Saturn',
          'start': '2026-03-14',
          'end': '2026-06-22',
          'duration_days': 100,
          'window_type': 'peak',
          'sd_periods': <Map<String, dynamic>>[
            {
              'sd_lord': 'Moon',
              'start': '2026-04-02',
              'end': '2026-04-12',
              'duration_days': 10,
            },
            {
              'sd_lord': 'Jupiter',
              'start': '2026-05-08',
              'end': '2026-05-25',
              'duration_days': 17,
            },
          ],
        },
        {
          'pd_lord': 'Jupiter',
          'start': '2026-06-22',
          'end': '2026-10-18',
          'duration_days': 118,
          'window_type': 'peak',
          'sd_periods': <Map<String, dynamic>>[
            {
              'sd_lord': 'Saturn',
              'start': '2026-07-15',
              'end': '2026-08-02',
              'duration_days': 18,
            },
          ],
        },
      ],
    },
    {
      'md_lord': 'Mercury',
      'ad_lord': 'Saturn',
      'start': '2029-06-23',
      'end': '2032-03-03',
      'is_past': false,
      'is_current': false,
      'pd_periods': <Map<String, dynamic>>[
        {
          'pd_lord': 'Moon',
          'start': '2030-01-10',
          'end': '2030-06-15',
          'duration_days': 156,
          'window_type': 'peak',
          'sd_periods': <Map<String, dynamic>>[],
        },
      ],
    },
  ],
  'transit_triggers': <Map<String, dynamic>>[
    {
      'date': '2026-03-18',
      'planet': 'sun',
      'nakshatra': 'Pushya',
      'nakshatra_lord': 'Saturn',
      'type': 'sun_nakshatra_trigger',
      'precision': '~13 days',
    },
    {
      'date': '2026-03-22',
      'planet': 'moon',
      'nakshatra': 'Uttara Bhadrapada',
      'nakshatra_lord': 'Saturn',
      'type': 'moon_nakshatra_trigger',
      'precision': '~1 day',
    },
    {
      'date': '2026-04-05',
      'planet': 'moon',
      'nakshatra': 'Rohini',
      'nakshatra_lord': 'Moon',
      'type': 'moon_nakshatra_trigger',
      'precision': '~1 day',
    },
    {
      'date': '2026-04-14',
      'planet': 'sun',
      'nakshatra': 'Bharani',
      'nakshatra_lord': 'Venus',
      'type': 'sun_nakshatra_trigger',
      'precision': '~13 days',
    },
  ],
};

// ===========================================================================
// Screen
// ===========================================================================

class KpAnalysisScreen extends ConsumerStatefulWidget {
  const KpAnalysisScreen({super.key});

  @override
  ConsumerState<KpAnalysisScreen> createState() => _KpAnalysisScreenState();
}

class _KpAnalysisScreenState extends ConsumerState<KpAnalysisScreen> {
  _QueryType? _selectedQuery;
  Map<String, dynamic>? _result;
  bool _loading = false;
  // bool _showAllWindows = false;  // uncomment when timing UI is re-enabled

  Future<void> _analyze(_QueryType query) async {
    setState(() {
      _selectedQuery = query;
      _loading = true;
      _result = null;
    });

    try {
      final result = await ApiService().post<Map<String, dynamic>>(
        ApiConstants.analysisKp,
        body: {'event_type': query.id},
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (!mounted) return;
      setState(() {
        _result = result;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _result = _kMockResult;
        _loading = false;
      });
    }
  }

  void _reset() {
    setState(() {
      _selectedQuery = null;
      _result = null;
    });
  }

  @override
  Widget build(BuildContext context) {
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
                    Text('KP Analysis', style: T.h3),
                  ],
                ),
              ),
              const Divider(height: 1),

              Expanded(
                child: _selectedQuery == null
                    ? _buildQuestionGrid()
                    : _buildResults(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // -----------------------------------------------------------------------
  // Phase 1 — Question selection
  // -----------------------------------------------------------------------

  Widget _buildQuestionGrid() {
    return ListView(
      padding: S.pagePadding.copyWith(top: S.xl, bottom: S.xxxl),
      children: [
        Text('What do you want to know?',
            style: T.h2, textAlign: TextAlign.center),
        const SizedBox(height: S.sm),
        Text(
          'Select a life area for KP Krishnamurti analysis',
          style: T.bodySm,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: S.xl),

        // 2-column grid
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _kQueries.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            mainAxisSpacing: S.sm,
            crossAxisSpacing: S.sm,
            childAspectRatio: 1.6,
          ),
          itemBuilder: (_, i) {
            final q = _kQueries[i];
            return GestureDetector(
              onTap: () => _analyze(q),
              child: GlassContainer(
                padding: const EdgeInsets.all(S.md),
                borderColor: q.color.withValues(alpha: 0.15),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: q.color.withValues(alpha: 0.12),
                      ),
                      child: Icon(q.icon, color: q.color, size: 18),
                    ),
                    const SizedBox(height: S.sm),
                    Text(
                      q.label,
                      style: T.bodySm.copyWith(
                          color: C.textPrimary,
                          fontWeight: FontWeight.w500,
                          fontSize: 12),
                      textAlign: TextAlign.center,
                    ),
                    Text(q.house,
                        style: T.caption.copyWith(fontSize: 10)),
                  ],
                ),
              ),
            );
          },
        ),

        const SizedBox(height: S.xl),

        // Educational card
        GlassContainer(
          padding: const EdgeInsets.all(S.lg),
          borderColor: C.ketu.withValues(alpha: 0.2),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.school, color: C.ketu, size: 18),
                  const SizedBox(width: S.sm),
                  Text(
                    'What is KP System?',
                    style: T.bodySm.copyWith(
                        color: C.ketu, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
              const SizedBox(height: S.sm),
              Text(
                'Krishnamurti Paddhati (KP) is a modern, precise astrology system '
                'developed by Prof. K.S. Krishnamurti. It uses sub-lord theory '
                'to give clear Yes/No judgments for life questions. Each cusp '
                '(house starting point) has a sign lord, star lord, and sub lord '
                '— the sub lord is the final decision-maker.',
                style: T.bodySm.copyWith(height: 1.6),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // -----------------------------------------------------------------------
  // Phase 2 — Results
  // -----------------------------------------------------------------------

  Widget _buildResults() {
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(strokeWidth: 2, color: C.accent),
      );
    }

    final pred = (_result?['prediction'] as Map<String, dynamic>?) ?? {};
    final judgment = (pred['judgment'] as String?) ?? 'mixed';
    final confidence = (pred['confidence'] as num?)?.toInt() ?? 50;
    final cusp = (pred['cusp_analysis'] as Map<String, dynamic>?) ?? {};
    final hints = (pred['timing_hints'] as List<dynamic>?) ?? [];
    final explanation = (pred['explanation'] as String?) ?? '';
    final allSigs = (_result?['significators'] as Map<String, dynamic>?) ?? {};
    final primaryHouse = (pred['primary_house'] as num?)?.toString() ?? '';
    final q = _selectedQuery!;

    // Show only the primary house significators
    final primarySigs = <MapEntry<String, dynamic>>[];
    if (allSigs.containsKey(primaryHouse)) {
      primarySigs.add(MapEntry(primaryHouse, allSigs[primaryHouse]));
    }

    return ListView(
      padding: S.pagePadding.copyWith(top: S.xl, bottom: S.xxxl),
      children: [
        // Judgment hero
        Center(child: _buildJudgmentRing(judgment, confidence, q)),
        const SizedBox(height: S.xl),

        // Primary house cusp card
        if (cusp.isNotEmpty && cusp['sign'] != null && (cusp['sign'] as String).isNotEmpty) ...[
          Text('Primary House Cusp',
              style: T.h3.copyWith(fontSize: 16)),
          const SizedBox(height: S.sm),
          _buildCuspCard(cusp),
          const SizedBox(height: S.xl),
        ],

        // Significator hierarchy (primary house only)
        if (primarySigs.isNotEmpty) ...[
          Text('Significator Hierarchy',
              style: T.h3.copyWith(fontSize: 16)),
          const SizedBox(height: S.sm),
          ...primarySigs.map((e) =>
              _buildSignificatorCard(e.key, e.value as Map<String, dynamic>)),
          const SizedBox(height: S.xl),
        ],

        // TODO: Timing windows, transit triggers, SD periods need better
        // filtering logic before showing in UI. Backend computes them but
        // display is commented out until significator-based filtering is tightened.

        // Timing hints
        if (hints.isNotEmpty) ...[
          Text('Timing Hints',
              style: T.h3.copyWith(fontSize: 16)),
          const SizedBox(height: S.sm),
          Wrap(
            spacing: S.sm,
            runSpacing: S.sm,
            children: hints
                .map((h) => Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: S.md, vertical: S.sm),
                      decoration: BoxDecoration(
                        color: C.jupiter.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                            color: C.jupiter.withValues(alpha: 0.15)),
                      ),
                      child: Text(h.toString(),
                          style: T.caption.copyWith(
                              color: C.textSecondary, fontSize: 11)),
                    ))
                .toList(),
          ),
          const SizedBox(height: S.xl),
        ],

        // Explanation
        if (explanation.isNotEmpty) ...[
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Analysis',
                    style: T.bodySm.copyWith(
                        color: C.textPrimary, fontWeight: FontWeight.w600)),
                const SizedBox(height: S.sm),
                Text(explanation,
                    style: T.bodySm.copyWith(height: 1.6)),
              ],
            ),
          ),
          const SizedBox(height: S.xl),
        ],

        // Reset button
        Center(
          child: OutlinedButton(
            onPressed: _reset,
            child: const Text('Ask Another Question'),
          ),
        ),
      ],
    );
  }

  Widget _buildJudgmentRing(String judgment, int confidence, _QueryType q) {
    final isGood = judgment == 'favorable';
    final isBad = judgment == 'unfavorable';
    final ringColor =
        isGood ? C.positive : isBad ? C.negative : C.warning;
    final label =
        isGood ? 'Favorable' : isBad ? 'Unfavorable' : 'Mixed';

    return Column(
      children: [
        SizedBox(
          width: 140,
          height: 140,
          child: CustomPaint(
            painter: _ConfidenceRingPainter(
                confidence: confidence / 100, color: ringColor),
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '$confidence%',
                    style: T.h2.copyWith(
                        color: ringColor, fontWeight: FontWeight.w700),
                  ),
                  Text('confidence', style: T.caption.copyWith(fontSize: 10)),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: S.md),
        Container(
          padding:
              const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.sm),
          decoration: BoxDecoration(
            color: ringColor.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: ringColor.withValues(alpha: 0.3)),
          ),
          child: Text(
            label,
            style: T.bodySm.copyWith(
                color: ringColor, fontWeight: FontWeight.w600),
          ),
        ),
        const SizedBox(height: S.sm),
        Text('${q.label} (${q.house})',
            style: T.bodySm.copyWith(color: C.textSecondary)),
      ],
    );
  }

  // _buildTimingWindows, _buildTimingRow, _buildTransitTriggers removed —
  // re-add when timing/filtering logic is improved

  String _formatDateRange(String start, String end) {
    try {
      final s = DateTime.parse(start);
      final e = DateTime.parse(end);
      const months = [
        '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
      ];
      return '${months[s.month]} ${s.year} - ${months[e.month]} ${e.year}';
    } catch (_) {
      return '$start - $end';
    }
  }

  Widget _buildCuspCard(Map<String, dynamic> cusp) {
    String cap(String s) =>
        s.isEmpty ? '-' : s[0].toUpperCase() + s.substring(1);
    return GlassContainer(
      padding: const EdgeInsets.all(S.lg),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          Flexible(child: _cuspItem('Sign', cap(cusp['sign'] ?? ''))),
          Flexible(child: _cuspItem('Sign Lord', cap(cusp['sign_lord'] ?? ''))),
          Flexible(child: _cuspItem('Star Lord', cap(cusp['star_lord'] ?? ''))),
          Flexible(child: _cuspItem('Sub Lord', cap(cusp['sub_lord'] ?? ''))),
        ],
      ),
    );
  }

  Widget _cuspItem(String label, String value) {
    final pColor = planetColor(value.toLowerCase());
    return Column(
      children: [
        Text(label, style: T.caption.copyWith(fontSize: 10)),
        const SizedBox(height: S.xs),
        Text(
          value,
          style: T.bodySm.copyWith(
              color: pColor, fontWeight: FontWeight.w600, fontSize: 13),
        ),
      ],
    );
  }

  Widget _buildSignificatorCard(String houseNum, Map<String, dynamic> sig) {
    final levels = [
      ('Level 1 (Planets in stars of occupants)', sig['level_1']),
      ('Level 2 (Occupants)', sig['level_2']),
      ('Level 3 (Planets in stars of owners)', sig['level_3']),
      ('Level 4 (Owners)', sig['level_4']),
    ];

    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: GlassContainer(
        padding: const EdgeInsets.all(S.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('House $houseNum Significators',
                style: T.bodySm.copyWith(
                    color: C.textPrimary, fontWeight: FontWeight.w600)),
            const SizedBox(height: S.sm),
            ...levels.map((l) {
              final planets =
                  (l.$2 as List<dynamic>?)?.cast<String>() ?? [];
              if (planets.isEmpty) return const SizedBox.shrink();
              return Padding(
                padding: const EdgeInsets.only(bottom: S.sm),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Flexible(
                      flex: 3,
                      child: Text(l.$1,
                          style: T.caption.copyWith(fontSize: 10)),
                    ),
                    const SizedBox(width: S.sm),
                    Flexible(
                      flex: 2,
                      child: Wrap(
                        spacing: S.xs,
                        runSpacing: S.xs,
                        children: planets
                            .map((p) => Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: S.sm, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: planetColor(p.toLowerCase())
                                        .withValues(alpha: 0.12),
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Text(planetGlyph(p.toLowerCase()),
                                          style: const TextStyle(
                                              fontSize: 11)),
                                      const SizedBox(width: 2),
                                      Text(p,
                                          style: T.caption.copyWith(
                                            color: planetColor(
                                                p.toLowerCase()),
                                            fontWeight: FontWeight.w600,
                                            fontSize: 10,
                                          )),
                                    ],
                                  ),
                                ))
                            .toList(),
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Confidence ring painter
// ---------------------------------------------------------------------------

class _ConfidenceRingPainter extends CustomPainter {
  final double confidence; // 0..1
  final Color color;

  _ConfidenceRingPainter({required this.confidence, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - 10;
    const strokeWidth = 8.0;
    const startAngle = 135 * pi / 180;
    const totalSweep = 270 * pi / 180;
    final scoreSweep = totalSweep * confidence.clamp(0.0, 1.0);
    final rect = Rect.fromCircle(center: center, radius: radius);

    // Background track
    final bgPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round
      ..color = C.glassBorder;
    canvas.drawArc(rect, startAngle, totalSweep, false, bgPaint);

    // Score arc
    if (confidence > 0) {
      final scorePaint = Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.round
        ..color = color;
      canvas.drawArc(rect, startAngle, scoreSweep, false, scorePaint);
    }
  }

  @override
  bool shouldRepaint(covariant _ConfidenceRingPainter old) =>
      old.confidence != confidence || old.color != color;
}
