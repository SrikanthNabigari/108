import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Bottom sheet panel showing rich yoga details.
///
/// Matches dasha detail panel pattern: gradient header, educational card,
/// WHAT/WHY sections, and colored Ask AI button.
class YogaDetailPanel extends ConsumerWidget {
  final Map<String, dynamic> yoga;

  const YogaDetailPanel({super.key, required this.yoga});

  static void show(BuildContext context, {required Map<String, dynamic> yoga}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => YogaDetailPanel(yoga: yoga),
    );
  }

  Color _categoryColor(String category) {
    switch (category.toLowerCase()) {
      case 'raja':
        return C.jupiter;
      case 'dhana':
        return const Color(0xFFFFD700);
      case 'pancha_mahapurusha':
        return C.mars;
      case 'nabhasa':
        return C.mercury;
      case 'chandra':
      case 'lunar':
        return C.moon;
      case 'solar':
        return C.sun;
      default:
        return C.accent;
    }
  }

  String _educationalText(String category) {
    switch (category.toLowerCase()) {
      case 'raja':
        return 'Raja Yogas are the most powerful planetary combinations in '
            'Vedic astrology. They bestow authority, leadership, fame, and '
            'success \u2014 like having a royal blessing in your chart.';
      case 'dhana':
        return 'Dhana Yogas are wealth-producing combinations formed by lords '
            'of wealth houses (2nd, 5th, 9th, 11th). They indicate financial '
            'prosperity and material abundance.';
      case 'pancha_mahapurusha':
        return 'Pancha Mahapurusha Yogas form when Mars, Mercury, Jupiter, '
            'Venus, or Saturn occupy their own or exalted sign in a kendra. '
            'They create extraordinary personality traits and life achievements.';
      case 'nabhasa':
        return 'Nabhasa Yogas are pattern-based combinations formed by the '
            'overall shape of planets across houses. They reveal the broad '
            'theme and direction of life.';
      case 'chandra':
      case 'lunar':
        return 'Chandra (Lunar) Yogas are formed relative to the Moon. '
            'Since the Moon governs the mind and emotions, these yogas '
            'deeply influence mental patterns, emotional well-being, and intuition.';
      default:
        return 'A Yoga is a specific planetary combination that produces '
            'special results in your life. When conditions are met in your '
            'birth chart, the yoga activates its unique blessings or challenges.';
    }
  }

  String _categoryLabel(String category) {
    switch (category.toLowerCase()) {
      case 'pancha_mahapurusha':
        return 'Pancha Mahapurusha';
      default:
        if (category.isEmpty) return 'Yoga';
        return category[0].toUpperCase() + category.substring(1);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final name = yoga['name'] as String? ?? 'Yoga';
    final category = yoga['category'] as String? ?? '';
    final description = yoga['description'] as String? ?? '';
    final involved = yoga['involved_planets'] as List? ?? [];
    final conditions = yoga['conditions_met'] as List? ?? [];
    final effect = yoga['effect'] as String? ?? '';
    final interpretation = yoga['interpretation'] as String? ?? '';
    final color = _categoryColor(category);

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
              // A. Gradient header (not scrollable)
              _buildHeader(name, category, color, involved),
              // B. Scrollable content
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: S.lg),
                  children: [
                    const SizedBox(height: S.sm),
                    // Educational card
                    _buildEducationalCard(category, color),
                    const SizedBox(height: S.md),
                    // WHAT — description + effect
                    if (description.isNotEmpty || effect.isNotEmpty) ...[
                      _buildWhatSection(description, effect, color),
                      const SizedBox(height: S.md),
                    ],
                    // WHY — involved planets + conditions
                    if (involved.isNotEmpty || conditions.isNotEmpty) ...[
                      _buildWhySection(involved, conditions, color),
                      const SizedBox(height: S.md),
                    ],
                    // Interpretation (deeper meaning)
                    if (interpretation.isNotEmpty) ...[
                      _buildInterpretation(interpretation, color),
                      const SizedBox(height: S.md),
                    ],
                    const SizedBox(height: S.xl),
                  ],
                ),
              ),
              // C. Ask AI button (fixed at bottom)
              _buildAskAiButton(context, name, color),
            ],
          ),
        );
      },
    );
  }

  // ── A. Gradient Header ──

  Widget _buildHeader(
      String name, String category, Color color, List involved) {
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
          // Planet glyphs + name + category badge
          Row(
            children: [
              // Show involved planet glyphs
              if (involved.isNotEmpty)
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: involved.take(3).map((p) {
                    final pStr = p.toString().toLowerCase();
                    return Padding(
                      padding: const EdgeInsets.only(right: 2),
                      child: Text(planetGlyph(pStr),
                          style: TextStyle(
                              fontSize: 24, color: planetColor(pStr))),
                    );
                  }).toList(),
                )
              else
                Icon(Icons.auto_awesome, color: color, size: 28),
              const SizedBox(width: S.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            name,
                            style: T.h2.copyWith(color: color),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: S.sm),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: S.sm, vertical: 2),
                          decoration: BoxDecoration(
                            borderRadius: R.xlBr,
                            color: color.withValues(alpha: 0.15),
                            border: Border.all(
                                color: color.withValues(alpha: 0.3)),
                          ),
                          child: Text(
                            _categoryLabel(category),
                            style: T.caption
                                .copyWith(color: color, fontSize: 10),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    if (involved.isNotEmpty)
                      Text(
                        involved
                            .map((p) => planetName(p.toString().toLowerCase()))
                            .join(' \u00b7 '),
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

  Widget _buildEducationalCard(String category, Color color) {
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
                  'What is a ${_categoryLabel(category)} Yoga?',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                Text(
                  _educationalText(category),
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

  Widget _buildWhatSection(String description, String effect, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('What It Brings',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        if (description.isNotEmpty)
          _ExpandableArea(
              title: 'Description', content: description, color: color),
        if (effect.isNotEmpty) ...[
          const SizedBox(height: S.sm),
          _ExpandableArea(title: 'Effect', content: effect, color: color),
        ],
      ],
    );
  }

  // ── WHY Section ──

  Widget _buildWhySection(List involved, List conditions, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Why It Forms',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        // Involved planets as chips
        if (involved.isNotEmpty) ...[
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: involved.map((p) {
              final pStr = p.toString().toLowerCase();
              return Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.sm, vertical: 4),
                decoration: BoxDecoration(
                  borderRadius: R.xlBr,
                  color: planetColor(pStr).withValues(alpha: 0.1),
                  border: Border.all(
                      color: planetColor(pStr).withValues(alpha: 0.2)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(planetGlyph(pStr),
                        style: TextStyle(
                            fontSize: 14, color: planetColor(pStr))),
                    const SizedBox(width: 4),
                    Text(planetName(pStr),
                        style:
                            T.caption.copyWith(color: planetColor(pStr))),
                  ],
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: S.sm),
        ],
        // Conditions met as checklist
        if (conditions.isNotEmpty) ...[
          ...conditions.take(6).map((c) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Padding(
                      padding: EdgeInsets.only(top: 4),
                      child: Icon(Icons.check_circle_outline,
                          size: 12, color: C.positive),
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text('$c',
                          style: T.caption.copyWith(
                              color: C.textSecondary, height: 1.4)),
                    ),
                  ],
                ),
              )),
        ],
      ],
    );
  }

  // ── Interpretation ──

  Widget _buildInterpretation(String interpretation, Color color) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.psychology, color: color, size: 18),
              const SizedBox(width: 6),
              Text('Deeper Meaning',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: S.sm),
          Text(interpretation,
              style:
                  T.caption.copyWith(color: C.textSecondary, height: 1.5)),
        ],
      ),
    );
  }

  // ── Ask AI Button ──

  Widget _buildAskAiButton(BuildContext context, String name, Color color) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.lg),
      child: SizedBox(
        width: double.infinity,
        height: 44,
        child: ElevatedButton.icon(
          onPressed: () => Navigator.of(context).pop(),
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: C.bg,
            shape: RoundedRectangleBorder(borderRadius: R.xlBr),
          ),
          icon: const Icon(Icons.auto_awesome, size: 18),
          label: Text(
            'Ask about $name',
            style: T.bodySm
                .copyWith(color: C.bg, fontWeight: FontWeight.w600),
          ),
        ),
      ),
    );
  }
}

// ── Expandable Area Card ──

class _ExpandableArea extends StatefulWidget {
  final String title;
  final String content;
  final Color color;

  const _ExpandableArea({
    required this.title,
    required this.content,
    required this.color,
  });

  @override
  State<_ExpandableArea> createState() => _ExpandableAreaState();
}

class _ExpandableAreaState extends State<_ExpandableArea> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final preview = widget.content.length > 80
        ? '${widget.content.substring(0, 80)}...'
        : widget.content;

    return GestureDetector(
      onTap: () => setState(() => _expanded = !_expanded),
      child: Container(
        padding: const EdgeInsets.all(S.md),
        decoration: BoxDecoration(
          borderRadius: R.mdBr,
          color: widget.color.withValues(alpha: 0.04),
          border: Border.all(color: widget.color.withValues(alpha: 0.1)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(widget.title,
                    style: T.bodySm.copyWith(
                        color: C.textPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 13)),
                const Spacer(),
                Icon(
                  _expanded ? Icons.expand_less : Icons.expand_more,
                  size: 16,
                  color: C.textMuted,
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              _expanded ? widget.content : preview,
              style:
                  T.caption.copyWith(color: C.textSecondary, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}
