import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Bottom sheet panel showing rich dosha details.
///
/// Matches dasha detail panel pattern: gradient header, educational card,
/// WHAT/WHY/HOW sections, and colored Ask AI button.
class DoshaDetailPanel extends ConsumerWidget {
  final Map<String, dynamic> dosha;

  const DoshaDetailPanel({super.key, required this.dosha});

  static void show(BuildContext context,
      {required Map<String, dynamic> dosha}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => DoshaDetailPanel(dosha: dosha),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final name = dosha['name'] as String? ?? 'Dosha';
    final severity = (dosha['severity'] as String? ?? 'mild').toLowerCase();
    final description = dosha['description'] as String? ?? '';
    final involved = dosha['involved_planets'] as List? ?? [];
    final remedies = dosha['remedies'] as List? ?? [];
    final isPresent = dosha['is_present'] as bool? ?? true;
    final conditions = dosha['conditions_met'] as List? ?? [];
    final effects = dosha['effects'] as List? ?? [];
    final sevColor = severity == 'severe'
        ? C.negative
        : severity == 'moderate'
            ? C.warning
            : C.positive;

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
              _buildHeader(name, severity, sevColor, isPresent, involved),
              // B. Scrollable content
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: S.lg),
                  children: [
                    const SizedBox(height: S.sm),
                    // Educational card
                    _buildEducationalCard(name, sevColor),
                    const SizedBox(height: S.md),
                    // WHAT — description + effects
                    if (description.isNotEmpty || effects.isNotEmpty) ...[
                      _buildWhatSection(description, effects, sevColor),
                      const SizedBox(height: S.md),
                    ],
                    // WHY — involved planets + conditions
                    if (involved.isNotEmpty || conditions.isNotEmpty) ...[
                      _buildWhySection(involved, conditions, sevColor),
                      const SizedBox(height: S.md),
                    ],
                    // HOW — remedies
                    if (remedies.isNotEmpty) ...[
                      _buildRemediesSection(remedies, sevColor),
                      const SizedBox(height: S.md),
                    ],
                    const SizedBox(height: S.xl),
                  ],
                ),
              ),
              // C. Ask AI button
              _buildAskAiButton(context, name, sevColor),
            ],
          ),
        );
      },
    );
  }

  // ── A. Gradient Header ──

  Widget _buildHeader(String name, String severity, Color sevColor,
      bool isPresent, List involved) {
    final symbol = _doshaSymbol(name);

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius:
            const BorderRadius.vertical(top: Radius.circular(R.xl)),
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            sevColor.withValues(alpha: 0.25),
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
          // Symbol + name + severity badge
          Row(
            children: [
              Text(symbol,
                  style: TextStyle(fontSize: 28, color: sevColor)),
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
                            style: T.h2.copyWith(color: sevColor),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: S.sm),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: S.sm, vertical: 2),
                          decoration: BoxDecoration(
                            borderRadius: R.xlBr,
                            color: sevColor.withValues(alpha: 0.15),
                            border: Border.all(
                                color: sevColor.withValues(alpha: 0.3)),
                          ),
                          child: Text(
                            severity[0].toUpperCase() +
                                severity.substring(1),
                            style: T.caption
                                .copyWith(color: sevColor, fontSize: 10),
                          ),
                        ),
                        if (!isPresent) ...[
                          const SizedBox(width: S.xs),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: S.sm, vertical: 2),
                            decoration: BoxDecoration(
                              borderRadius: R.xlBr,
                              color: C.positive.withValues(alpha: 0.15),
                              border: Border.all(
                                  color:
                                      C.positive.withValues(alpha: 0.3)),
                            ),
                            child: Text(
                              'Cancelled',
                              style: T.caption.copyWith(
                                  color: C.positive, fontSize: 10),
                            ),
                          ),
                        ],
                      ],
                    ),
                    if (involved.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(
                        involved
                            .map((p) =>
                                planetName(p.toString().toLowerCase()))
                            .join(' \u00b7 '),
                        style: T.caption,
                      ),
                    ],
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

  Widget _buildEducationalCard(String name, Color color) {
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
                  'What is $name?',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                Text(
                  _doshaEducation(name),
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

  Widget _buildWhatSection(String description, List effects, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('What It Means',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        if (description.isNotEmpty)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(S.md),
            decoration: BoxDecoration(
              borderRadius: R.mdBr,
              color: color.withValues(alpha: 0.04),
              border: Border.all(color: color.withValues(alpha: 0.1)),
            ),
            child: Text(description,
                style:
                    T.caption.copyWith(color: C.textSecondary, height: 1.5)),
          ),
        // Effects list from knowledge base
        if (effects.isNotEmpty) ...[
          const SizedBox(height: S.sm),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(S.md),
            decoration: BoxDecoration(
              borderRadius: R.mdBr,
              color: color.withValues(alpha: 0.04),
              border: Border.all(color: color.withValues(alpha: 0.1)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Effects',
                    style: T.bodySm.copyWith(
                        color: C.textPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 13)),
                const SizedBox(height: S.sm),
                ...effects.map((e) => Padding(
                      padding: const EdgeInsets.only(bottom: 6),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: const EdgeInsets.only(top: 4),
                            child: Icon(Icons.warning_amber_rounded,
                                size: 10, color: color),
                          ),
                          const SizedBox(width: 6),
                          Expanded(
                            child: Text('$e',
                                style: T.caption.copyWith(
                                    color: C.textSecondary, height: 1.4)),
                          ),
                        ],
                      ),
                    )),
              ],
            ),
          ),
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
        // Conditions
        if (conditions.isNotEmpty)
          ...conditions.take(6).map((c) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Icon(Icons.warning_amber_rounded,
                          size: 12, color: color),
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
    );
  }

  // ── HOW — Remedies Section ──

  Widget _buildRemediesSection(List remedies, Color color) {
    return _ExpandableRemedies(remedies: remedies, color: color);
  }

  // ── Ask AI Button ──

  Widget _buildAskAiButton(
      BuildContext context, String name, Color color) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.lg),
      child: SizedBox(
        width: double.infinity,
        height: 44,
        child: ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).pop();
            context.push('/chat?prompt=${Uri.encodeComponent("Tell me about my $name dosha — what does it mean and how does it affect me?")}');
          },
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

// ── Expandable Remedies ──

class _ExpandableRemedies extends StatefulWidget {
  final List remedies;
  final Color color;

  const _ExpandableRemedies({required this.remedies, required this.color});

  @override
  State<_ExpandableRemedies> createState() => _ExpandableRemediesState();
}

class _ExpandableRemediesState extends State<_ExpandableRemedies> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final showCount = _expanded ? widget.remedies.length : 2;
    final displayedRemedies = widget.remedies.take(showCount);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.spa, color: C.positive, size: 18),
            const SizedBox(width: 6),
            Text('How to Remedy',
                style: T.bodySm.copyWith(
                    color: C.textPrimary, fontWeight: FontWeight.w600)),
            const Spacer(),
            Text('${widget.remedies.length} remedies',
                style: T.caption.copyWith(color: C.textMuted)),
          ],
        ),
        const SizedBox(height: S.sm),
        ...displayedRemedies.map((r) {
          final remedy = r is Map ? r : {'text': r.toString()};
          final text = remedy['text'] as String? ??
              remedy['description'] as String? ??
              r.toString();
          final type = remedy['type'] as String? ?? '';
          return Padding(
            padding: const EdgeInsets.only(bottom: S.sm),
            child: Container(
              padding: const EdgeInsets.all(S.md),
              decoration: BoxDecoration(
                borderRadius: R.mdBr,
                color: C.positive.withValues(alpha: 0.04),
                border:
                    Border.all(color: C.positive.withValues(alpha: 0.1)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: 2),
                    child: Icon(_remedyIcon(type),
                        size: 14,
                        color: C.positive.withValues(alpha: 0.7)),
                  ),
                  const SizedBox(width: S.sm),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (type.isNotEmpty)
                          Text(
                            type[0].toUpperCase() + type.substring(1),
                            style: T.caption.copyWith(
                                color: C.positive,
                                fontWeight: FontWeight.w600,
                                fontSize: 10),
                          ),
                        Text(text,
                            style: T.caption.copyWith(
                                color: C.textSecondary, height: 1.4)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        }),
        if (widget.remedies.length > 2)
          GestureDetector(
            onTap: () => setState(() => _expanded = !_expanded),
            child: Row(
              children: [
                Icon(
                  _expanded ? Icons.expand_less : Icons.expand_more,
                  size: 14,
                  color: C.accent,
                ),
                const SizedBox(width: 4),
                Text(
                  _expanded
                      ? 'Show less'
                      : 'Show all ${widget.remedies.length} remedies',
                  style: T.caption.copyWith(color: C.accent, fontSize: 10),
                ),
              ],
            ),
          ),
      ],
    );
  }

  IconData _remedyIcon(String type) {
    switch (type.toLowerCase()) {
      case 'mantra':
        return Icons.music_note;
      case 'charity':
      case 'donation':
        return Icons.volunteer_activism;
      case 'gemstone':
        return Icons.diamond;
      case 'worship':
      case 'puja':
        return Icons.temple_hindu;
      case 'fasting':
        return Icons.restaurant;
      default:
        return Icons.spa;
    }
  }
}

// ── Dosha helpers ──

String _doshaSymbol(String name) {
  final n = name.toLowerCase();
  if (n.contains('mangal')) return '\u25B2';
  if (n.contains('kaal sarp')) return '\u25C6';
  if (n.contains('pitra')) return '\u2726';
  if (n.contains('grahan')) return '\u25D0';
  if (n.contains('guru chandal')) return '\u2B21';
  if (n.contains('angarak')) return '\u25B2';
  if (n.contains('vish')) return '\u25C9';
  if (n.contains('kemdrum')) return '\u25CB';
  return '\u26a0';
}

String _doshaEducation(String name) {
  final n = name.toLowerCase();
  if (n.contains('mangal')) {
    return 'Mangal Dosha occurs when Mars occupies the 1st, 2nd, 4th, 7th, '
        '8th, or 12th house. Mars\u2019 aggressive energy can create friction '
        'in partnerships, but remedies and cancellation conditions exist.';
  }
  if (n.contains('kaal sarp')) {
    return 'Kaal Sarpa Dosha forms when all planets are hemmed between Rahu '
        'and Ketu. It can create cycles of struggle followed by sudden '
        'breakthroughs, with intensity varying by the axis involved.';
  }
  if (n.contains('pitra')) {
    return 'Pitra Dosha indicates karmic debt from ancestors. It forms when '
        'Sun conjuncts Rahu, or certain afflictions to the 9th house occur. '
        'It can affect father figures and spiritual progress.';
  }
  if (n.contains('guru chandal')) {
    return 'Guru Chandal Dosha forms when Jupiter conjuncts Rahu. It can '
        'create confusion between wisdom and illusion, but can also give '
        'unconventional intelligence when handled well.';
  }
  if (n.contains('kemdrum')) {
    return 'Kemdrum Dosha occurs when the Moon has no planet in adjacent '
        'signs. It can create periods of loneliness or financial instability, '
        'though many cancellation conditions exist.';
  }
  return 'A Dosha is an affliction or challenging pattern in the birth chart. '
      'While it indicates areas of difficulty, understanding and appropriate '
      'remedies can significantly reduce its impact.';
}
