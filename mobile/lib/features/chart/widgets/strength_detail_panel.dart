import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Bottom sheet panel showing Shadbala (six-fold strength) breakdown.
///
/// Matches dasha detail panel pattern: gradient header, educational card,
/// strength bars, and colored Ask AI button.
class StrengthDetailPanel extends ConsumerWidget {
  final Map<String, dynamic> data;

  const StrengthDetailPanel({super.key, required this.data});

  static void show(BuildContext context,
      {required Map<String, dynamic> data}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => StrengthDetailPanel(data: data),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final planet = data['planet'] as String? ?? '';
    final total = (data['total_shadbala'] as num?)?.toDouble() ?? 0.0;
    final grade = (data['grade'] as String? ?? 'average').toLowerCase();
    final components =
        data['components'] as Map<String, dynamic>? ?? {};
    final color = planetColor(planet);
    final gradeColor = grade == 'very_strong' || grade == 'strong'
        ? C.positive
        : grade == 'average'
            ? C.warning
            : C.negative;

    return DraggableScrollableSheet(
      initialChildSize: 0.75,
      minChildSize: 0.4,
      maxChildSize: 0.93,
      builder: (context, scrollController) {
        return Container(
          decoration: BoxDecoration(
            color: C.surface,
            borderRadius:
                const BorderRadius.vertical(top: Radius.circular(R.xl)),
          ),
          child: Column(
            children: [
              // A. Gradient header
              _buildHeader(planet, total, grade, gradeColor, color),
              // B. Scrollable content
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: S.lg),
                  children: [
                    const SizedBox(height: S.sm),
                    // Educational card
                    _buildEducationalCard(color),
                    const SizedBox(height: S.md),
                    // WHAT — what this strength means for you
                    _buildWhatSection(planet, grade, total, color),
                    const SizedBox(height: S.md),
                    // WHY — 6-fold breakdown
                    if (components.isNotEmpty) ...[
                      _buildBreakdown(components, color),
                      const SizedBox(height: S.md),
                    ],
                    // Overall bar
                    _buildOverallBar(total, grade, color, gradeColor),
                    const SizedBox(height: S.xl),
                  ],
                ),
              ),
              // C. Ask AI button
              _buildAskAiButton(context, planet, color),
            ],
          ),
        );
      },
    );
  }

  // ── A. Gradient Header ──

  Widget _buildHeader(String planet, double total, String grade,
      Color gradeColor, Color color) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius:
            const BorderRadius.vertical(top: Radius.circular(R.xl)),
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            color.withValues(alpha: 0.25),
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
          // Planet glyph + name + grade badge
          Row(
            children: [
              Text(planetGlyph(planet),
                  style: TextStyle(fontSize: 28, color: color)),
              const SizedBox(width: S.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          '${planetName(planet)} Strength',
                          style: T.h2.copyWith(color: color),
                        ),
                        const SizedBox(width: S.sm),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: S.sm, vertical: 2),
                          decoration: BoxDecoration(
                            borderRadius: R.xlBr,
                            color: gradeColor.withValues(alpha: 0.15),
                            border: Border.all(
                                color: gradeColor.withValues(alpha: 0.3)),
                          ),
                          child: Text(
                            grade.replaceAll('_', ' ').toUpperCase(),
                            style: T.caption.copyWith(
                                color: gradeColor, fontSize: 10),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Total Shadbala: ${total.toStringAsFixed(2)}',
                      style: T.caption,
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

  // ── Educational Card ──

  Widget _buildEducationalCard(Color color) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.auto_stories, color: color, size: 20),
          const SizedBox(width: S.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'What is Shadbala?',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                Text(
                  'Shadbala is the six-fold strength system in Vedic astrology. '
                  'It measures a planet\u2019s power across six dimensions: '
                  'position, direction, time, motion, natural strength, and aspects. '
                  'A strong planet delivers better results in its dasha periods and transits.',
                  style: T.caption
                      .copyWith(color: C.textSecondary, height: 1.5),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── WHAT Section ──

  Widget _buildWhatSection(
      String planet, String grade, double total, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('What This Means',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(S.md),
          decoration: BoxDecoration(
            borderRadius: R.mdBr,
            color: color.withValues(alpha: 0.04),
            border: Border.all(color: color.withValues(alpha: 0.1)),
          ),
          child: Text(
            _gradeDescription(planetName(planet), grade),
            style:
                T.caption.copyWith(color: C.textSecondary, height: 1.5),
          ),
        ),
      ],
    );
  }

  // ── WHY — 6-fold Breakdown ──

  Widget _buildBreakdown(Map<String, dynamic> components, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Six-fold Strength (Shadbala)',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.lg),
        ..._balaEntries.map((entry) {
          final value =
              (components[entry.key] as num?)?.toDouble() ?? 0.0;
          return _balaBar(
            label: entry.label,
            value: value,
            color: color,
            meaning: entry.meaning,
          );
        }),
      ],
    );
  }

  Widget _balaBar({
    required String label,
    required double value,
    required Color color,
    required String meaning,
  }) {
    final barFraction = (value / 1.5).clamp(0.0, 1.0);
    final barColor = barFraction >= 0.6
        ? C.positive
        : barFraction >= 0.3
            ? C.warning
            : C.negative;

    return Padding(
      padding: const EdgeInsets.only(bottom: S.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label,
                  style: T.bodySm.copyWith(
                      color: C.textPrimary,
                      fontWeight: FontWeight.w500)),
              Row(
                children: [
                  Text(value.toStringAsFixed(2), style: T.bodySm),
                  const SizedBox(width: S.xs),
                  Container(
                    width: 8,
                    height: 8,
                    decoration:
                        BoxDecoration(shape: BoxShape.circle, color: barColor),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: S.xs),
          ClipRRect(
            borderRadius: R.smBr,
            child: SizedBox(
              height: 8,
              child: LinearProgressIndicator(
                value: barFraction,
                backgroundColor: C.glassBg,
                valueColor: AlwaysStoppedAnimation<Color>(
                    color.withValues(alpha: 0.8)),
              ),
            ),
          ),
          const SizedBox(height: S.xs),
          Text(meaning,
              style: T.caption
                  .copyWith(color: C.textMuted, height: 1.3)),
        ],
      ),
    );
  }

  // ── Overall Bar ──

  Widget _buildOverallBar(
      double total, String grade, Color color, Color gradeColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Overall',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.md),
        ClipRRect(
          borderRadius: R.smBr,
          child: SizedBox(
            height: 12,
            child: LinearProgressIndicator(
              value: (total / 2.0).clamp(0.0, 1.0),
              backgroundColor: C.glassBg,
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
        ),
        const SizedBox(height: S.sm),
        Text(
          _overallDescription(grade),
          style: T.caption.copyWith(color: C.textSecondary, height: 1.4),
        ),
      ],
    );
  }

  // ── Ask AI Button ──

  Widget _buildAskAiButton(
      BuildContext context, String planet, Color color) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.lg),
      child: SizedBox(
        width: double.infinity,
        height: 44,
        child: ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).pop();
            context.push('/chat?prompt=${Uri.encodeComponent("Tell me about ${planetName(planet)}'s strength in my chart and what it means for me")}');
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: C.bg,
            shape: RoundedRectangleBorder(borderRadius: R.xlBr),
          ),
          icon: const Icon(Icons.auto_awesome, size: 18),
          label: Text(
            'Ask about ${planetName(planet)}\u2019s strength',
            style: T.bodySm
                .copyWith(color: C.bg, fontWeight: FontWeight.w600),
          ),
        ),
      ),
    );
  }

  // ── Helpers ──

  String _gradeDescription(String planet, String grade) {
    switch (grade) {
      case 'very_strong':
        return '$planet is exceptionally powerful in your chart. '
            'Its significations \u2014 the areas of life it governs \u2014 will '
            'thrive naturally. During $planet\u2019s dasha or transits, expect '
            'strong positive results with minimal effort.';
      case 'strong':
        return '$planet has solid strength in your chart. It delivers '
            'good results during its dasha periods and responds well to '
            'favorable transits. Its significations are well-supported.';
      case 'average':
        return '$planet has moderate strength. Results depend heavily on '
            'dasha timing and transit support. During favorable periods it '
            'performs well; during challenging ones, remedies can help.';
      case 'weak':
        return '$planet is below average in strength. Its significations '
            'may face delays or challenges. Appropriate remedies, gemstones, '
            'and favorable transit periods can compensate significantly.';
      default:
        return 'Strength analysis shows how well $planet can deliver '
            'results in its areas of influence.';
    }
  }

  String _overallDescription(String grade) {
    switch (grade) {
      case 'very_strong':
        return 'Exceptionally powerful planet \u2014 its significations thrive in your life.';
      case 'strong':
        return 'Solid strength \u2014 this planet delivers good results in its dasha and transits.';
      case 'average':
        return 'Moderate strength \u2014 results depend on dasha timing and transit support.';
      case 'weak':
        return 'Below average strength \u2014 remedies and favorable transits can help.';
      default:
        return '';
    }
  }
}

class _BalaEntry {
  final String key;
  final String label;
  final String meaning;
  const _BalaEntry(this.key, this.label, this.meaning);
}

const _balaEntries = [
  _BalaEntry('sthana_bala', 'Sthana Bala',
      'Positional strength \u2014 how well placed in sign, house, and navamsha.'),
  _BalaEntry('dig_bala', 'Dig Bala',
      'Directional strength \u2014 strongest when in its preferred direction (kendra).'),
  _BalaEntry('kala_bala', 'Kala Bala',
      'Temporal strength \u2014 day/night, weekday, hora, and seasonal factors.'),
  _BalaEntry('chesta_bala', 'Chesta Bala',
      'Motional strength \u2014 based on speed, retrograde status, and planetary war.'),
  _BalaEntry('naisargika_bala', 'Naisargika Bala',
      'Natural strength \u2014 inherent power: Sun > Moon > Venus > Jupiter > Mars > Mercury > Saturn.'),
  _BalaEntry('drik_bala', 'Drik Bala',
      'Aspectual strength \u2014 modified by aspects from benefics (+) and malefics (\u2212).'),
];
