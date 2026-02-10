import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import '../models/state_vector.dart';

const _factorExplainers = {
  'gochara': {
    'title': 'What is Gochara?',
    'body': 'Gochara means "transit of planets." It tracks where the 9 planets '
        'are RIGHT NOW relative to your Moon sign. Each planet in each house '
        'from Moon creates different effects — some favorable, some challenging.\n\n'
        'Classical texts grade each planet\'s transit through all 12 houses. '
        'Slow planets (Jupiter, Saturn) matter most because they stay for months or years.',
    'key_concept': 'House from Moon \u2192 effect quality',
  },
  'panchanga': {
    'title': 'What is Panchanga?',
    'body': 'Panchanga means "five limbs" — the 5 elements of the Vedic calendar:\n\n'
        '\u2022 Tithi — lunar day (phase of Moon)\n'
        '\u2022 Vara — weekday lord (Sun, Moon, Mars...)\n'
        '\u2022 Nakshatra — Moon\'s constellation (27 total)\n'
        '\u2022 Yoga — Sun-Moon angular relationship\n'
        '\u2022 Karana — half of a tithi\n\n'
        'Together they define the quality of any moment.',
    'key_concept': 'Universal — same for everyone on a given day',
  },
  'transit_moon': {
    'title': 'What is Transit Moon?',
    'body': 'The Moon changes sign every 2.5 days, making it the fastest-moving '
        'factor. Its current sign relative to your birth Moon (Tarabala) and '
        'relative to your lagna determines emotional tone, mental clarity, '
        'and receptivity.\n\n'
        'Good Moon transits bring emotional ease; challenging ones create '
        'restlessness or sensitivity.',
    'key_concept': 'Emotional tone changes every 2.5 days',
  },
  'dasha': {
    'title': 'What is Dasha?',
    'body': 'Vimshottari Dasha is the Vedic planetary period system. Your life '
        'is divided into chapters ruled by different planets:\n\n'
        '\u2022 Mahadasha (MD) — the big period (years)\n'
        '\u2022 Antardasha (AD) — sub-period (months)\n'
        '\u2022 Pratyantardasha (PD) — sub-sub-period (weeks)\n\n'
        'The dignity and nature of each lord in YOUR chart determines '
        'whether these periods bring growth or challenges.',
    'key_concept': 'MD \u2192 AD \u2192 PD = life chapter hierarchy',
  },
  'yoga_activation': {
    'title': 'What is Yoga Activation?',
    'body': 'Natal yogas are planetary combinations in your birth chart that '
        'hold promises — like Gajakesari (Jupiter-Moon), or Panch Mahapurusha. '
        'These promises are ACTIVATED when current transits touch the yoga\'s '
        'involved houses or planets.\n\n'
        'A dormant yoga is potential; an activated yoga delivers results.',
    'key_concept': 'Promise (natal) + trigger (transit) = result',
  },
  'shadbala': {
    'title': 'What is Shadbala?',
    'body': 'Shadbala means "six-fold strength" — the most comprehensive '
        'measure of a planet\'s power:\n\n'
        '\u2022 Sthana Bala — positional (sign, house)\n'
        '\u2022 Dig Bala — directional (angular houses)\n'
        '\u2022 Kaala Bala — temporal (day/night, season)\n'
        '\u2022 Chesta Bala — motional (speed, retrogression)\n'
        '\u2022 Naisargika Bala — natural (inherent to planet)\n'
        '\u2022 Drik Bala — aspectual (aspects received)\n\n'
        'Higher Shadbala means more capacity to produce results.',
    'key_concept': 'Sthana + Dig + Kaala + Chesta + Naisargika + Drik',
  },
  'ashtakavarga': {
    'title': 'What is Ashtakavarga?',
    'body': 'Ashtakavarga assigns "benefic points" (bindus, 0-8) to each sign '
        'for each planet. When a planet transits a sign with high bindus, '
        'it delivers good results; low bindus bring difficulty.\n\n'
        'SAV (Sarvashtakavarga) combines all planets\' contributions to show '
        'which signs in YOUR chart are inherently supportive.',
    'key_concept': 'Higher bindus = more support in that sign',
  },
};

/// Bottom sheet detail panel — opened when a heat map cell is tapped.
///
/// Follows the DashaDetailPanel pattern: DraggableScrollableSheet with
/// gradient header and scrollable content.
class FactorDetailPanel extends StatelessWidget {
  final StateVector vector;
  final int factorIndex; // 0-6 = individual factor, 7 = composite

  const FactorDetailPanel({
    super.key,
    required this.vector,
    required this.factorIndex,
  });

  /// Show as a modal bottom sheet (matches DashaDetailPanel.show pattern).
  static void show(
    BuildContext context, {
    required StateVector vector,
    required int factorIndex,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => FactorDetailPanel(
        vector: vector,
        factorIndex: factorIndex,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isComposite = factorIndex >= 7 || factorIndex >= vector.factors.length;
    final factor = isComposite ? null : vector.factors[factorIndex];
    final score = isComposite ? vector.composite : factor!.score;
    final title = isComposite ? 'Overall State' : factor!.name;
    final planet = isComposite ? vector.horaLord : factor!.dominantPlanet;
    final color = planet.isNotEmpty ? planetColor(planet) : _scoreColor(score);

    return DraggableScrollableSheet(
      initialChildSize: 0.65,
      minChildSize: 0.35,
      maxChildSize: 0.85,
      builder: (context, scrollController) {
        return Container(
          decoration: BoxDecoration(
            color: C.surface,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
            border: Border.all(color: C.glassBorder),
          ),
          child: Column(
            children: [
              // Drag handle
              const SizedBox(height: 8),
              Container(
                width: 32,
                height: 4,
                decoration: BoxDecoration(
                  borderRadius: R.smBr,
                  color: C.glassBorder,
                ),
              ),
              const SizedBox(height: 4),

              // ── Gradient header ──
              Container(
                width: double.infinity,
                padding: const EdgeInsets.fromLTRB(S.xl, S.md, S.xl, S.lg),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      color.withValues(alpha: 0.12),
                      Colors.transparent,
                    ],
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Date
                    Text(
                      _formatDate(vector.date),
                      style: T.caption.copyWith(color: C.textSecondary),
                    ),
                    const SizedBox(height: S.sm),
                    Row(
                      children: [
                        if (planet.isNotEmpty) ...[
                          Text(
                            planetGlyph(planet),
                            style: TextStyle(fontSize: 28, color: color),
                          ),
                          const SizedBox(width: S.md),
                        ],
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(title,
                                  style: T.h2.copyWith(color: color)),
                              if (!isComposite)
                                Text(factor!.description,
                                    style: T.bodySm
                                        .copyWith(color: C.textSecondary)),
                            ],
                          ),
                        ),
                        // Score badge
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: S.md, vertical: S.sm),
                          decoration: BoxDecoration(
                            borderRadius: R.lgBr,
                            color: color.withValues(alpha: 0.15),
                            border:
                                Border.all(color: color.withValues(alpha: 0.4)),
                          ),
                          child: Text(
                            score.toStringAsFixed(1),
                            style: T.h2.copyWith(color: color, fontSize: 24),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // ── Scrollable content ──
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(
                      horizontal: S.xl, vertical: S.md),
                  children: [
                    if (isComposite) ...[
                      // Show all factors breakdown
                      _SectionTitle(text: 'Factor Breakdown'),
                      const SizedBox(height: S.sm),
                      ...vector.factors.map((f) => _FactorRow(factor: f)),
                      const SizedBox(height: S.xl),
                      // Area scores
                      _SectionTitle(text: 'Life Areas'),
                      const SizedBox(height: S.sm),
                      ...vector.areas.map((a) => _AreaRow(area: a)),
                      const SizedBox(height: S.xl),
                      // Mental state
                      GlassContainer(
                        padding: const EdgeInsets.all(S.lg),
                        child: Row(
                          children: [
                            Text('Mental State',
                                style: T.bodySm
                                    .copyWith(color: C.textSecondary)),
                            const Spacer(),
                            Text(
                              vector.mentalState,
                              style: T.h3.copyWith(
                                  color: _scoreColor(vector.composite)),
                            ),
                          ],
                        ),
                      ),
                    ] else ...[
                      // ── What is [Factor]? ──
                      if (_factorExplainers.containsKey(factor!.id)) ...[
                        _SectionTitle(text: _factorExplainers[factor.id]!['title']!),
                        const SizedBox(height: S.sm),
                        GlassContainer(
                          padding: const EdgeInsets.all(S.lg),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _factorExplainers[factor.id]!['body']!,
                                style: T.bodySm.copyWith(
                                  color: C.textSecondary,
                                  height: 1.6,
                                ),
                              ),
                              const SizedBox(height: S.md),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: S.md, vertical: S.sm),
                                decoration: BoxDecoration(
                                  borderRadius: R.mdBr,
                                  color: color.withValues(alpha: 0.1),
                                  border: Border.all(color: color.withValues(alpha: 0.3)),
                                ),
                                child: Text(
                                  _factorExplainers[factor.id]!['key_concept']!,
                                  style: T.bodySm.copyWith(
                                    color: color,
                                    fontWeight: FontWeight.w600,
                                    fontSize: 12,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: S.xl),
                      ],
                      // Single factor detail
                      _SectionTitle(text: 'Score Interpretation'),
                      const SizedBox(height: S.sm),
                      GlassContainer(
                        padding: const EdgeInsets.all(S.lg),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _ScoreBar(
                                label: factor!.name, score: factor.score),
                            const SizedBox(height: S.md),
                            Text(
                              _interpretScore(factor.id, factor.score),
                              style: T.bodySm.copyWith(height: 1.6),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: S.xl),
                      // Dominant planet
                      if (factor!.dominantPlanet.isNotEmpty) ...[
                        _SectionTitle(text: 'Dominant Planet'),
                        const SizedBox(height: S.sm),
                        GlassContainer(
                          padding: const EdgeInsets.all(S.lg),
                          child: Row(
                            children: [
                              Text(
                                planetGlyph(factor.dominantPlanet),
                                style: TextStyle(
                                  fontSize: 24,
                                  color:
                                      planetColor(factor.dominantPlanet),
                                ),
                              ),
                              const SizedBox(width: S.md),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment:
                                      CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      planetName(factor.dominantPlanet),
                                      style: T.h3.copyWith(
                                          color: planetColor(
                                              factor.dominantPlanet)),
                                    ),
                                    Text(
                                      'Primary influence on ${factor.name.toLowerCase()}',
                                      style: T.bodySm.copyWith(
                                          color: C.textSecondary),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                      const SizedBox(height: S.xl),
                      // ── Affects These Areas ──
                      if (factor!.dominantPlanet.isNotEmpty) ...[
                        _SectionTitle(text: 'Affects These Areas'),
                        const SizedBox(height: S.sm),
                        Wrap(
                          spacing: S.sm,
                          runSpacing: S.sm,
                          children: kAreaPlanets.entries
                              .where((e) => e.value == factor.dominantPlanet)
                              .map((e) => Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: S.md, vertical: S.xs),
                                    decoration: BoxDecoration(
                                      borderRadius: R.xlBr,
                                      color: color.withValues(alpha: 0.08),
                                      border: Border.all(
                                        color: color.withValues(alpha: 0.2)),
                                    ),
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        Text(
                                          kAreaIcons[e.key] ?? '\u2022',
                                          style: const TextStyle(fontSize: 12),
                                        ),
                                        const SizedBox(width: S.xs),
                                        Text(
                                          kAreaNames[e.key] ?? e.key,
                                          style: T.bodySm.copyWith(
                                            color: C.textPrimary,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ))
                              .toList(),
                        ),
                        const SizedBox(height: S.xl),
                      ],
                      // Context within other factors
                      _SectionTitle(text: 'In Context'),
                      const SizedBox(height: S.sm),
                      ...vector.factors.map((f) => _FactorRow(
                            factor: f,
                            highlight: f.id == factor!.id,
                          )),
                    ],
                    const SizedBox(height: S.xxl),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  String _formatDate(DateTime dt) {
    const months = [
      '', 'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    const weekdays = [
      '', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
      'Saturday', 'Sunday'
    ];
    return '${weekdays[dt.weekday]}, ${months[dt.month]} ${dt.day}, ${dt.year}';
  }

  static String _interpretScore(String factorId, double score) {
    final level =
        score >= 7 ? 'high' : (score >= 4 ? 'moderate' : 'low');
    final descriptions = {
      'panchanga': {
        'high': 'Auspicious tithi, favorable vara, and supportive yoga create an excellent cosmic backdrop.',
        'moderate': 'Mixed panchanga elements — some support, some resistance.',
        'low': 'Challenging tithi or karana. Best for reflection rather than new initiatives.',
      },
      'transit_moon': {
        'high': 'Moon in a strong nakshatra with high Ashtakavarga bindus. Emotional clarity.',
        'moderate': 'Moon transit is neutral. Steady emotional state.',
        'low': 'Moon in a challenging position. Emotional sensitivity heightened.',
      },
      'gochara': {
        'high': 'Most transits are favorable from your natal Moon. Supportive period.',
        'moderate': 'Mixed transit influences. Some planets support, others challenge.',
        'low': 'Multiple unfavorable transits. External pressures may feel stronger.',
      },
      'dasha': {
        'high': 'Current dasha lords are dignified and benefic. Natural flow in life.',
        'moderate': 'Dasha lords give mixed results. Balance effort with patience.',
        'low': 'Dasha lords in challenging dignity. Growth through perseverance.',
      },
      'yoga_activation': {
        'high': 'Your natal yogas are being activated by current transits. Potential manifesting.',
        'moderate': 'Partial yoga activation. Some promises becoming active.',
        'low': 'Yogas are dormant in this period. Preparation time.',
      },
      'shadbala': {
        'high': 'The dominant planet has strong six-fold strength. Actions bear fruit.',
        'moderate': 'Moderate planetary strength. Steady progress possible.',
        'low': 'Dominant planet is weakened. Conserve energy.',
      },
      'ashtakavarga': {
        'high': 'High benefic points in the current transit sign. Environment is supportive.',
        'moderate': 'Average benefic points. Neither especially helpful nor harmful.',
        'low': 'Low benefic points in transit sign. External resistance likely.',
      },
    };
    return descriptions[factorId]?[level] ?? 'Score: ${score.toStringAsFixed(1)}/10';
  }

  Color _scoreColor(double score) {
    if (score >= 7) return C.positive;
    if (score >= 4) return C.warning;
    return C.negative;
  }
}

// ── Sub-widgets ──

class _SectionTitle extends StatelessWidget {
  final String text;
  const _SectionTitle({required this.text});

  @override
  Widget build(BuildContext context) {
    return Text(
      text.toUpperCase(),
      style: T.label.copyWith(color: C.textMuted, letterSpacing: 1.2),
    );
  }
}

class _FactorRow extends StatelessWidget {
  final FactorScore factor;
  final bool highlight;
  const _FactorRow({required this.factor, this.highlight = false});

  @override
  Widget build(BuildContext context) {
    final color = factor.dominantPlanet.isNotEmpty
        ? planetColor(factor.dominantPlanet)
        : _scoreColor(factor.score);

    return Container(
      margin: const EdgeInsets.only(bottom: S.sm),
      padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
      decoration: BoxDecoration(
        borderRadius: R.mdBr,
        color: highlight ? color.withValues(alpha: 0.1) : C.glassBg,
        border: Border.all(
          color: highlight ? color.withValues(alpha: 0.4) : C.glassBorder,
          width: highlight ? 1.5 : 0.5,
        ),
      ),
      child: Row(
        children: [
          if (factor.dominantPlanet.isNotEmpty) ...[
            Text(
              planetGlyph(factor.dominantPlanet),
              style: TextStyle(fontSize: 14, color: color),
            ),
            const SizedBox(width: S.sm),
          ],
          Expanded(
            child: Text(
              factor.name,
              style: T.bodySm.copyWith(
                color: C.textPrimary,
                fontSize: 13,
                fontWeight: highlight ? FontWeight.w600 : FontWeight.w400,
              ),
            ),
          ),
          // Mini bar
          SizedBox(
            width: 60,
            child: ClipRRect(
              borderRadius: R.smBr,
              child: LinearProgressIndicator(
                value: (factor.score / 10).clamp(0.0, 1.0),
                minHeight: 4,
                backgroundColor: C.glassBorder,
                valueColor: AlwaysStoppedAnimation(color),
              ),
            ),
          ),
          const SizedBox(width: S.sm),
          SizedBox(
            width: 28,
            child: Text(
              factor.score.toStringAsFixed(1),
              textAlign: TextAlign.right,
              style: T.bodySm.copyWith(
                color: color,
                fontWeight: FontWeight.w600,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _scoreColor(double score) {
    if (score >= 7) return C.positive;
    if (score >= 4) return C.warning;
    return C.negative;
  }
}

class _AreaRow extends StatelessWidget {
  final AreaScore area;
  const _AreaRow({required this.area});

  @override
  Widget build(BuildContext context) {
    final color = area.dominantPlanet.isNotEmpty
        ? planetColor(area.dominantPlanet)
        : _scoreColor(area.score);
    final icon = kAreaIcons[area.id] ?? '•';

    return Container(
      margin: const EdgeInsets.only(bottom: S.sm),
      padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
      decoration: BoxDecoration(
        borderRadius: R.mdBr,
        color: C.glassBg,
        border: Border.all(color: C.glassBorder, width: 0.5),
      ),
      child: Row(
        children: [
          Text(icon, style: const TextStyle(fontSize: 16)),
          const SizedBox(width: S.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(area.name,
                    style: T.bodySm
                        .copyWith(color: C.textPrimary, fontSize: 13)),
                if (area.insight.isNotEmpty)
                  Text(area.insight,
                      style: T.caption
                          .copyWith(fontSize: 10, color: C.textMuted)),
              ],
            ),
          ),
          SizedBox(
            width: 60,
            child: ClipRRect(
              borderRadius: R.smBr,
              child: LinearProgressIndicator(
                value: (area.score / 10).clamp(0.0, 1.0),
                minHeight: 4,
                backgroundColor: C.glassBorder,
                valueColor: AlwaysStoppedAnimation(color),
              ),
            ),
          ),
          const SizedBox(width: S.sm),
          SizedBox(
            width: 28,
            child: Text(
              area.score.toStringAsFixed(1),
              textAlign: TextAlign.right,
              style: T.bodySm.copyWith(
                  color: color, fontWeight: FontWeight.w600, fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }

  Color _scoreColor(double score) {
    if (score >= 7) return C.positive;
    if (score >= 4) return C.warning;
    return C.negative;
  }
}

class _ScoreBar extends StatelessWidget {
  final String label;
  final double score;
  const _ScoreBar({required this.label, required this.score});

  @override
  Widget build(BuildContext context) {
    final color = score >= 7
        ? C.positive
        : (score >= 4 ? C.warning : C.negative);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(label, style: T.bodySm.copyWith(color: C.textPrimary)),
            const Spacer(),
            Text('${score.toStringAsFixed(1)}/10',
                style: T.bodySm.copyWith(color: color, fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: R.smBr,
          child: LinearProgressIndicator(
            value: (score / 10).clamp(0.0, 1.0),
            minHeight: 6,
            backgroundColor: C.glassBorder,
            valueColor: AlwaysStoppedAnimation(color),
          ),
        ),
      ],
    );
  }
}
