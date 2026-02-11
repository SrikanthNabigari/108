import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// House-to-life-area friendly names.
const houseLifeArea = <int, String>{
  1: 'Self & Health',
  2: 'Wealth & Family',
  3: 'Courage & Effort',
  4: 'Home & Education',
  5: 'Children & Romance',
  6: 'Health & Service',
  7: 'Partnership',
  8: 'Transformation',
  9: 'Fortune & Dharma',
  10: 'Career & Status',
  11: 'Gains & Friends',
  12: 'Spirituality',
};

/// Rich descriptions for what activation in each house means.
const _houseWhatDescription = <int, String>{
  1: 'Focus shifts to your personal identity, physical vitality, and self-image. A time to take initiative and redefine how the world sees you.',
  2: 'Financial matters and family dynamics come to the foreground. Earnings, savings, speech, and inherited values become active topics.',
  3: 'Communication, short travels, and sibling relationships activate. Your courage to take on new skills and creative expression is highlighted.',
  4: 'Domestic life, property matters, and emotional foundations are stirring. Education, vehicles, and your relationship with mother may be in focus.',
  5: 'Creativity, romance, and children-related matters light up. Investments, speculative gains, and intellectual pursuits get energized.',
  6: 'Health routines, daily work, and overcoming obstacles become central. Competition, legal matters, and service to others are activated.',
  7: 'Partnerships, marriage, and business alliances take center stage. One-on-one relationships and negotiations demand your attention.',
  8: 'Deep transformation, hidden resources, and shared finances activate. Research, occult interests, and life-changing events may emerge.',
  9: 'Higher learning, spiritual growth, and long-distance travel are energized. Your connection to teachers, philosophy, and fortune expands.',
  10: 'Career, public reputation, and life purpose are in the spotlight. Authority, achievements, and your professional path demand action.',
  11: 'Social networks, aspirations, and income from career become active. Friendships, community involvement, and wish fulfillment are highlighted.',
  12: 'Spiritual practices, solitude, and letting go are in focus. Foreign connections, expenses, and inner reflection take precedence.',
};

/// What each planet brings when transiting through a house.
const _planetInHouseEffect = <String, String>{
  'sun': 'brings visibility, authority energy, and government/father themes',
  'moon': 'brings emotional fluctuations, public interaction, and nurturing energy',
  'mars': 'brings assertive energy, competition, and drive for action',
  'mercury': 'brings communication, analytical thinking, and business activity',
  'jupiter': 'brings expansion, wisdom, blessings, and growth opportunities',
  'venus': 'brings pleasure, creativity, luxury, and relationship harmony',
  'saturn': 'brings discipline, karmic lessons, delays, and structural changes',
  'rahu': 'brings intense desire, unconventional approaches, and amplified themes',
  'ketu': 'brings spiritual detachment, past-life patterns, and inner wisdom',
};

/// Bottom sheet showing WHAT / WHEN / WHY for a life area (house activation).
///
/// Follows the [TransitDetailPanel] pattern — gradient header, draggable sheet.
class LifeAreaDetailPanel extends StatelessWidget {
  final Map<String, dynamic> houseData;
  final Map<String, dynamic>? lordshipData;
  final Map<String, dynamic>? dashaContext;
  final List<Map<String, dynamic>> triggers;
  final List<Map<String, dynamic>> activeYogas;

  const LifeAreaDetailPanel({
    super.key,
    required this.houseData,
    this.lordshipData,
    this.dashaContext,
    this.triggers = const [],
    this.activeYogas = const [],
  });

  /// Show the detail panel as a modal bottom sheet.
  static void show(
    BuildContext context, {
    required Map<String, dynamic> houseData,
    Map<String, dynamic>? lordshipData,
    Map<String, dynamic>? dashaContext,
    List<Map<String, dynamic>> triggers = const [],
    List<Map<String, dynamic>> activeYogas = const [],
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => LifeAreaDetailPanel(
        houseData: houseData,
        lordshipData: lordshipData,
        dashaContext: dashaContext,
        triggers: triggers,
        activeYogas: activeYogas,
      ),
    );
  }

  int get _house => houseData['house'] as int? ?? 1;
  double get _score => (houseData['score'] as num?)?.toDouble() ?? 0;
  String get _grade => houseData['grade'] as String? ?? 'quiet';
  bool get _hasDoubleTT => houseData['double_transit'] as bool? ?? false;
  String get _areaName => houseLifeArea[_house] ?? 'House $_house';

  Color get _gradeColor => switch (_grade) {
        'highly_active' => C.positive,
        'active' => C.jupiter,
        'moderate' => C.textSecondary,
        _ => C.textMuted,
      };

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.72,
      minChildSize: 0.35,
      maxChildSize: 0.93,
      builder: (context, scrollController) {
        return Container(
          decoration: const BoxDecoration(
            color: C.surface,
            borderRadius: BorderRadius.vertical(top: Radius.circular(R.xl)),
          ),
          child: Column(
            children: [
              _buildHeader(),
              Expanded(child: _buildContent(scrollController)),
              _buildAskAiButton(context),
            ],
          ),
        );
      },
    );
  }

  // ── Header ──

  Widget _buildHeader() {
    final signIdx = houseData['sign'] as int? ?? 0;
    final signName = (signIdx >= 0 && signIdx < 12) ? rashiNames[signIdx] : '';

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius: const BorderRadius.vertical(top: Radius.circular(R.xl)),
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            _gradeColor.withValues(alpha: 0.2),
            Colors.transparent,
          ],
        ),
      ),
      padding: const EdgeInsets.fromLTRB(S.lg, S.md, S.lg, S.sm),
      child: Column(
        children: [
          // Drag handle
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: C.glassBorder,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: S.md),
          Row(
            children: [
              // Score circle
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _gradeColor.withValues(alpha: 0.15),
                  border: Border.all(color: _gradeColor.withValues(alpha: 0.4)),
                ),
                child: Center(
                  child: Text(
                    '${_score.toInt()}',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: _gradeColor,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: S.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(_areaName, style: T.h3.copyWith(fontSize: 18)),
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        Text(signName, style: T.caption),
                        const SizedBox(width: S.sm),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            borderRadius: R.smBr,
                            color: _gradeColor.withValues(alpha: 0.15),
                            border: Border.all(color: _gradeColor.withValues(alpha: 0.3)),
                          ),
                          child: Text(
                            _grade.replaceAll('_', ' '),
                            style: T.caption.copyWith(
                              color: _gradeColor,
                              fontSize: 10,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        if (_hasDoubleTT) ...[
                          const SizedBox(width: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                            decoration: BoxDecoration(
                              borderRadius: R.smBr,
                              color: C.jupiter.withValues(alpha: 0.15),
                              border: Border.all(color: C.jupiter.withValues(alpha: 0.3)),
                            ),
                            child: Text(
                              'DOUBLE',
                              style: T.caption.copyWith(
                                color: C.jupiter,
                                fontSize: 9,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ── Content: WHAT / WHEN / WHY ──

  Widget _buildContent(ScrollController controller) {
    final summary = houseData['summary'] as String? ?? '';
    final themes = (houseData['themes'] as List?)?.cast<String>() ?? [];
    final planetsPresent = (houseData['planets_present'] as List?)?.cast<String>() ?? [];
    final planetsAspecting = (houseData['planets_aspecting'] as List?)?.cast<String>() ?? [];

    return ListView(
      controller: controller,
      padding: const EdgeInsets.symmetric(horizontal: S.lg),
      children: [
        const SizedBox(height: S.sm),

        // ── Score bar ──
        _buildScoreBar(),
        const SizedBox(height: S.lg),

        // ═══ WHAT ═══
        _buildSectionHeader('WHAT', 'is happening'),
        const SizedBox(height: S.sm),

        // House activation description
        if (_houseWhatDescription.containsKey(_house))
          Padding(
            padding: const EdgeInsets.only(bottom: S.sm),
            child: Text(
              _houseWhatDescription[_house]!,
              style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 13),
            ),
          ),

        if (summary.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: S.sm),
            child: GlassContainer(
              padding: const EdgeInsets.all(S.sm),
              blur: 0,
              child: Text(summary, style: T.caption.copyWith(color: C.textSecondary, fontSize: 12)),
            ),
          ),

        if (themes.isNotEmpty) ...[
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: themes
                .map((t) => Container(
                      padding: const EdgeInsets.symmetric(horizontal: S.sm, vertical: 3),
                      decoration: BoxDecoration(
                        borderRadius: R.smBr,
                        color: C.accentSurface,
                        border: Border.all(color: C.glassBorder),
                      ),
                      child: Text(t, style: T.caption.copyWith(color: C.textSecondary, fontSize: 11)),
                    ))
                .toList(),
          ),
          const SizedBox(height: S.sm),
        ],

        // Planet-in-house effects (from knowledge API or fallback)
        if (planetsPresent.isNotEmpty) ...[
          ..._buildPlanetInterpretations(planetsPresent),
          const SizedBox(height: S.xs),
        ],

        // Active yogas touching this house
        if (activeYogas.isNotEmpty) ...[
          for (final yoga in activeYogas)
            Padding(
              padding: const EdgeInsets.only(bottom: S.xs),
              child: Row(
                children: [
                  Text('\u26A1 ', style: TextStyle(fontSize: 12, color: C.jupiter)),
                  Expanded(
                    child: Text(
                      yoga['yoga_name'] as String? ?? '',
                      style: T.bodySm.copyWith(color: C.jupiter, fontSize: 12, fontWeight: FontWeight.w500),
                    ),
                  ),
                ],
              ),
            ),
          const SizedBox(height: S.sm),
        ],

        const SizedBox(height: S.md),

        // ═══ WHEN ═══
        _buildSectionHeader('WHEN', 'is this active'),
        const SizedBox(height: S.sm),

        GlassContainer(
          padding: const EdgeInsets.all(S.md),
          blur: 0,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (_hasDoubleTT)
                _whenRow('\u25CF', 'NOW \u2014 Double transit active', C.jupiter),
              if (dashaContext != null) ...[
                _whenRow(
                  '\u25CF',
                  'Dasha: ${_planetNameCap(dashaContext!['mahadasha_lord'] as String? ?? '')} MD \u2192 ${_planetNameCap(dashaContext!['antardasha_lord'] as String? ?? '')} AD',
                  C.accent,
                ),
              ],
              // Show relevant triggers for this house
              if (triggers.isNotEmpty)
                for (final t in triggers.take(3))
                  _whenRow(
                    '\u25CB',
                    '${t['trigger'] ?? t['description'] ?? ''}'
                        '${t['days_from_now'] != null ? ' \u2022 in ${t['days_from_now']}d' : ''}',
                    C.textSecondary,
                  ),
              if (!_hasDoubleTT && dashaContext == null && triggers.isEmpty)
                Text('Transit influence is moderate',
                    style: T.caption.copyWith(color: C.textSecondary)),
            ],
          ),
        ),

        const SizedBox(height: S.lg),

        // ═══ WHY ═══
        _buildSectionHeader('WHY', 'is this happening'),
        const SizedBox(height: S.sm),

        GlassContainer(
          padding: const EdgeInsets.all(S.md),
          blur: 0,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (planetsPresent.isNotEmpty) ...[
                Text('Planets in this area:',
                    style: T.caption.copyWith(color: C.textMuted, fontSize: 10)),
                const SizedBox(height: S.xs),
                _planetRow(planetsPresent),
                const SizedBox(height: S.sm),
              ],
              if (planetsAspecting.isNotEmpty) ...[
                Text('Planets influencing:',
                    style: T.caption.copyWith(color: C.textMuted, fontSize: 10)),
                const SizedBox(height: S.xs),
                _planetRow(planetsAspecting),
                const SizedBox(height: S.sm),
              ],
              if (_hasDoubleTT)
                Padding(
                  padding: const EdgeInsets.only(top: S.xs),
                  child: Text(
                    'Jupiter + Saturn both activate this area (Double Transit) \u2014 '
                    'the strongest transit trigger in Vedic astrology.',
                    style: T.caption.copyWith(color: C.jupiter, fontSize: 11),
                  ),
                ),
              if (lordshipData != null && lordshipData!.isNotEmpty) ...[
                const SizedBox(height: S.sm),
                _buildLordshipInfo(),
              ],
              if (planetsPresent.isEmpty && planetsAspecting.isEmpty && !_hasDoubleTT)
                Text('No strong planetary influence at this time',
                    style: T.caption.copyWith(color: C.textSecondary)),
            ],
          ),
        ),

        const SizedBox(height: S.xl),
      ],
    );
  }

  // ── Planet interpretation rows (knowledge-driven) ──

  List<Widget> _buildPlanetInterpretations(List<String> planetsPresent) {
    final apiInterps = (houseData['planet_interpretations'] as List?)
        ?.cast<Map<String, dynamic>>() ?? [];

    // Build a lookup by planet name
    final interpMap = <String, Map<String, dynamic>>{};
    for (final interp in apiInterps) {
      final planet = (interp['planet'] as String? ?? '').toLowerCase();
      if (planet.isNotEmpty) interpMap[planet] = interp;
    }

    final widgets = <Widget>[];
    for (final p in planetsPresent) {
      final pLower = p.toLowerCase();
      final interp = interpMap[pLower];

      if (interp != null) {
        // Rich interpretation from knowledge API
        final summary = interp['summary'] as String? ?? '';
        final positive = (interp['positive'] as List?)?.cast<String>() ?? [];
        final negative = (interp['negative'] as List?)?.cast<String>() ?? [];
        widgets.add(Padding(
          padding: const EdgeInsets.only(bottom: S.sm),
          child: GlassContainer(
            padding: const EdgeInsets.all(S.sm),
            blur: 0,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(planetGlyph(p), style: TextStyle(fontSize: 14, color: planetColor(p))),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        '${planetName(p)} in ${_ordinal(_house)} House',
                        style: T.bodySm.copyWith(color: planetColor(p), fontWeight: FontWeight.w600, fontSize: 12),
                      ),
                    ),
                  ],
                ),
                if (summary.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(summary, style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 12)),
                ],
                if (positive.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  ...positive.take(2).map((e) => Padding(
                    padding: const EdgeInsets.only(bottom: 1),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('+ ', style: T.caption.copyWith(color: C.positive, fontWeight: FontWeight.w700, fontSize: 10)),
                        Expanded(child: Text(e, style: T.caption.copyWith(color: C.textSecondary, fontSize: 10))),
                      ],
                    ),
                  )),
                ],
                if (negative.isNotEmpty) ...[
                  const SizedBox(height: 2),
                  ...negative.take(1).map((e) => Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('- ', style: T.caption.copyWith(color: C.negative, fontWeight: FontWeight.w700, fontSize: 10)),
                      Expanded(child: Text(e, style: T.caption.copyWith(color: C.textSecondary, fontSize: 10))),
                    ],
                  )),
                ],
              ],
            ),
          ),
        ));
      } else if (_planetInHouseEffect.containsKey(pLower)) {
        // Fallback to hardcoded one-liner
        widgets.add(Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(planetGlyph(p), style: TextStyle(fontSize: 13, color: planetColor(p))),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  '${planetName(p)} ${_planetInHouseEffect[pLower]}',
                  style: T.caption.copyWith(color: C.textSecondary, fontSize: 11),
                ),
              ),
            ],
          ),
        ));
      }
    }
    return widgets;
  }

  String _ordinal(int n) {
    if (n >= 11 && n <= 13) return '${n}th';
    switch (n % 10) {
      case 1: return '${n}st';
      case 2: return '${n}nd';
      case 3: return '${n}rd';
      default: return '${n}th';
    }
  }

  // ── Score bar ──

  Widget _buildScoreBar() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text('Activation',
                style: T.caption.copyWith(color: C.textMuted, fontSize: 10)),
            const Spacer(),
            Text(
              '${_score.toInt()}/100',
              style: T.caption.copyWith(color: _gradeColor, fontWeight: FontWeight.w600, fontSize: 11),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: R.smBr,
          child: LinearProgressIndicator(
            value: (_score / 100).clamp(0, 1),
            minHeight: 4,
            backgroundColor: C.glassBorder,
            valueColor: AlwaysStoppedAnimation<Color>(_gradeColor),
          ),
        ),
      ],
    );
  }

  // ── Section header ──

  Widget _buildSectionHeader(String title, String subtitle) {
    return Row(
      children: [
        Text(title,
            style: T.label.copyWith(
                color: C.accent, letterSpacing: 2.0, fontSize: 11)),
        const SizedBox(width: 6),
        Text(subtitle, style: T.caption.copyWith(fontSize: 11)),
      ],
    );
  }

  // ── When row ──

  Widget _whenRow(String bullet, String text, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('$bullet ', style: TextStyle(fontSize: 10, color: color)),
          Expanded(
            child: Text(text, style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 12)),
          ),
        ],
      ),
    );
  }

  // ── Planet row ──

  Widget _planetRow(List<String> planets) {
    return Wrap(
      spacing: S.md,
      runSpacing: S.sm,
      children: planets.map((p) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(planetGlyph(p), style: TextStyle(fontSize: 15, color: planetColor(p))),
            const SizedBox(width: 4),
            Text(planetName(p), style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 12)),
          ],
        );
      }).toList(),
    );
  }

  // ── Lordship info ──

  Widget _buildLordshipInfo() {
    final lord = lordshipData?['house_lord'] as String? ?? '';
    final nature = lordshipData?['functional_nature'] as String? ?? '';

    if (lord.isEmpty) return const SizedBox.shrink();

    final natureColor = switch (nature) {
      'yogakaraka' => C.jupiter,
      'benefic' => C.positive,
      'malefic' || 'maraka' => C.negative,
      _ => C.textSecondary,
    };

    return Row(
      children: [
        Text(planetGlyph(lord), style: TextStyle(fontSize: 14, color: planetColor(lord))),
        const SizedBox(width: 6),
        Text('${planetName(lord)} rules this area',
            style: T.caption.copyWith(color: C.textPrimary, fontSize: 11)),
        const SizedBox(width: 6),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
          decoration: BoxDecoration(
            borderRadius: R.smBr,
            color: natureColor.withValues(alpha: 0.15),
          ),
          child: Text(
            nature.replaceAll('_', ' '),
            style: T.caption.copyWith(color: natureColor, fontSize: 9, fontWeight: FontWeight.w600),
          ),
        ),
      ],
    );
  }

  // ── Ask AI ──

  Widget _buildAskAiButton(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.md),
        child: SizedBox(
          width: double.infinity,
          height: 44,
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.of(context).pop();
              context.push('/chat?prompt=${Uri.encodeComponent("How is my $_areaName right now? What transits are affecting it?")}');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: _gradeColor,
              foregroundColor: C.surface,
            ),
            icon: const Icon(Icons.auto_awesome, size: 16),
            label: Text('Ask about $_areaName'),
          ),
        ),
      ),
    );
  }

  String _planetNameCap(String p) => p.isEmpty ? '' : p[0].toUpperCase() + p.substring(1);
}
