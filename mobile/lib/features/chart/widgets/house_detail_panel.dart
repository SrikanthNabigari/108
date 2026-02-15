import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Bottom sheet panel showing rich house details with interpretations.
///
/// Matches other detail panel patterns: gradient header, educational card,
/// planet interpretation cards, matching yogas/doshas, and Ask AI button.
class HouseDetailPanel extends ConsumerWidget {
  final int houseNum;
  final int signNum;
  final String signName;
  final String lord;
  final List<Map<String, dynamic>> planetsHere;
  final Map<String, dynamic> houseInfo;
  final List<Map<String, dynamic>> matchingYogas;
  final List<Map<String, dynamic>> matchingDoshas;

  const HouseDetailPanel({
    super.key,
    required this.houseNum,
    required this.signNum,
    required this.signName,
    required this.lord,
    required this.planetsHere,
    required this.houseInfo,
    required this.matchingYogas,
    required this.matchingDoshas,
  });

  static void show(
    BuildContext context, {
    required int houseNum,
    required int signNum,
    required String signName,
    required String lord,
    required List<Map<String, dynamic>> planetsHere,
    required Map<String, dynamic> houseInfo,
    required List<Map<String, dynamic>> matchingYogas,
    required List<Map<String, dynamic>> matchingDoshas,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => HouseDetailPanel(
        houseNum: houseNum,
        signNum: signNum,
        signName: signName,
        lord: lord,
        planetsHere: planetsHere,
        houseInfo: houseInfo,
        matchingYogas: matchingYogas,
        matchingDoshas: matchingDoshas,
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lordColor = planetColor(lord);
    final houseName = houseInfo['name'] as String? ?? '';
    final significations = houseInfo['significations'] as List? ?? [];
    final karaka = houseInfo['karaka'] as String? ?? '';
    final bodyParts = houseInfo['body_parts'] as List? ?? [];

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
              _buildHeader(lordColor, houseName),
              // B. Scrollable content
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: S.lg),
                  children: [
                    const SizedBox(height: S.sm),
                    // Significations + karaka
                    if (significations.isNotEmpty || karaka.isNotEmpty)
                      _buildSignifications(
                          significations, karaka, bodyParts, lordColor),
                    const SizedBox(height: S.md),
                    // House lord card
                    _buildLordCard(lordColor),
                    const SizedBox(height: S.md),
                    // Planet interpretations
                    if (planetsHere.isNotEmpty) ...[
                      _buildPlanetInterpretations(lordColor),
                      const SizedBox(height: S.md),
                    ] else ...[
                      _buildEmptyHouse(lordColor),
                      const SizedBox(height: S.md),
                    ],
                    // Matching yogas
                    if (matchingYogas.isNotEmpty) ...[
                      _buildMatchingYogas(),
                      const SizedBox(height: S.md),
                    ],
                    // Matching doshas
                    if (matchingDoshas.isNotEmpty) ...[
                      _buildMatchingDoshas(),
                      const SizedBox(height: S.md),
                    ],
                    const SizedBox(height: S.xl),
                  ],
                ),
              ),
              // C. Ask AI button
              _buildAskAiButton(context, lordColor),
            ],
          ),
        );
      },
    );
  }

  // ── A. Gradient Header ──

  Widget _buildHeader(Color color, String houseName) {
    final lifeArea = _houseAreas[houseNum] ?? '';

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
          Row(
            children: [
              // House number circle
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: color.withValues(alpha: 0.15),
                  border: Border.all(color: color.withValues(alpha: 0.4)),
                ),
                child: Center(
                  child: Text(
                    '$houseNum',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                      color: color,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: S.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          houseName.isNotEmpty
                              ? houseName
                              : 'House $houseNum',
                          style: T.h2.copyWith(color: color),
                        ),
                        const SizedBox(width: S.sm),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: S.sm, vertical: 2),
                          decoration: BoxDecoration(
                            borderRadius: R.xlBr,
                            color: C.accent.withValues(alpha: 0.15),
                            border: Border.all(
                                color: C.accent.withValues(alpha: 0.3)),
                          ),
                          child: Text(
                            signName,
                            style: T.caption
                                .copyWith(color: C.accent, fontSize: 10),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(lifeArea, style: T.caption),
                  ],
                ),
              ),
              // Planet count badge
              if (planetsHere.isNotEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: S.sm, vertical: 4),
                  decoration: BoxDecoration(
                    borderRadius: R.xlBr,
                    color: color.withValues(alpha: 0.12),
                  ),
                  child: Text(
                    '${planetsHere.length} planet${planetsHere.length > 1 ? 's' : ''}',
                    style: T.caption.copyWith(
                        color: color,
                        fontSize: 10,
                        fontWeight: FontWeight.w600),
                  ),
                ),
            ],
          ),
          // Planet glyphs row
          if (planetsHere.isNotEmpty) ...[
            const SizedBox(height: S.sm),
            Row(
              children: planetsHere.map((p) {
                final name = (p['name'] as String? ?? '').toLowerCase();
                final retro =
                    p['retrograde'] == true || p['is_retrograde'] == true;
                final pc = planetColor(name);
                return Padding(
                  padding: const EdgeInsets.only(right: S.sm),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(planetGlyph(name),
                          style: TextStyle(fontSize: 18, color: pc)),
                      const SizedBox(width: 2),
                      Text(
                        '${planetName(name)}${retro ? ' Rx' : ''}',
                        style: T.caption.copyWith(
                            color: pc, fontWeight: FontWeight.w500),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }

  // ── Significations Card ──

  Widget _buildSignifications(
      List significations, String karaka, List bodyParts, Color color) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.auto_stories, color: color, size: 20),
              const SizedBox(width: S.sm),
              Text(
                'House $houseNum Governs',
                style: T.bodySm.copyWith(
                    color: C.textPrimary, fontWeight: FontWeight.w600),
              ),
            ],
          ),
          const SizedBox(height: S.sm),
          // Signification chips
          if (significations.isNotEmpty)
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: significations.map((s) {
                return Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: S.sm, vertical: 4),
                  decoration: BoxDecoration(
                    borderRadius: R.xlBr,
                    color: color.withValues(alpha: 0.08),
                    border:
                        Border.all(color: color.withValues(alpha: 0.15)),
                  ),
                  child: Text(
                    '$s',
                    style: T.caption.copyWith(
                        color: C.textSecondary, fontSize: 11),
                  ),
                );
              }).toList(),
            ),
          // Karaka
          if (karaka.isNotEmpty) ...[
            const SizedBox(height: S.sm),
            Row(
              children: [
                Text('Karaka: ',
                    style: T.caption.copyWith(
                        color: C.textMuted, fontSize: 11)),
                Text(karaka,
                    style: T.caption.copyWith(
                        color: color,
                        fontSize: 11,
                        fontWeight: FontWeight.w600)),
              ],
            ),
          ],
          // Body parts
          if (bodyParts.isNotEmpty) ...[
            const SizedBox(height: 4),
            Row(
              children: [
                Text('Body: ',
                    style: T.caption.copyWith(
                        color: C.textMuted, fontSize: 11)),
                Expanded(
                  child: Text(
                    bodyParts.join(', '),
                    style: T.caption.copyWith(
                        color: C.textSecondary, fontSize: 11),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  // ── House Lord Card ──

  Widget _buildLordCard(Color lordColor) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(S.md),
      decoration: BoxDecoration(
        borderRadius: R.mdBr,
        color: lordColor.withValues(alpha: 0.06),
        border: Border.all(color: lordColor.withValues(alpha: 0.15)),
      ),
      child: Row(
        children: [
          Text(planetGlyph(lord),
              style: TextStyle(fontSize: 22, color: lordColor)),
          const SizedBox(width: S.sm),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('House Lord',
                  style: T.caption.copyWith(color: C.textMuted)),
              Text(planetName(lord),
                  style: T.bodySm.copyWith(
                      color: lordColor, fontWeight: FontWeight.w600)),
            ],
          ),
          const Spacer(),
          Text('$signName',
              style: T.caption.copyWith(
                  color: C.accent, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  // ── Planet Interpretation Cards ──

  Widget _buildPlanetInterpretations(Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Planets in This House',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        ...planetsHere.map((p) => _planetInterpCard(p)),
      ],
    );
  }

  Widget _planetInterpCard(Map<String, dynamic> planet) {
    final name = (planet['name'] as String? ?? '').toLowerCase();
    final retro =
        planet['retrograde'] == true || planet['is_retrograde'] == true;
    final pc = planetColor(name);
    final houseSummary = planet['house_summary'] as String? ?? '';
    final housePositive = planet['house_positive'] as List? ?? [];
    final houseNegative = planet['house_negative'] as List? ?? [];
    final signSummary = planet['sign_summary'] as String? ?? '';

    final hasContent = houseSummary.isNotEmpty ||
        housePositive.isNotEmpty ||
        houseNegative.isNotEmpty ||
        signSummary.isNotEmpty;

    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(S.md),
        decoration: BoxDecoration(
          borderRadius: R.mdBr,
          color: pc.withValues(alpha: 0.04),
          border: Border.all(color: pc.withValues(alpha: 0.12)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Planet header
            Row(
              children: [
                Text(planetGlyph(name),
                    style: TextStyle(fontSize: 20, color: pc)),
                const SizedBox(width: S.sm),
                Text(
                  '${planetName(name)}${retro ? ' (Retrograde)' : ''} in House $houseNum',
                  style: T.bodySm.copyWith(
                      color: pc, fontWeight: FontWeight.w600),
                ),
              ],
            ),
            if (hasContent) ...[
              const SizedBox(height: S.sm),
              // House summary
              if (houseSummary.isNotEmpty) ...[
                Text(houseSummary,
                    style: T.caption
                        .copyWith(color: C.textSecondary, height: 1.5)),
                const SizedBox(height: S.sm),
              ],
              // Sign summary
              if (signSummary.isNotEmpty) ...[
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Padding(
                      padding: EdgeInsets.only(top: 3),
                      child: Icon(Icons.place, size: 12, color: C.accent),
                    ),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        'In $signName: $signSummary',
                        style: T.caption.copyWith(
                            color: C.textSecondary,
                            height: 1.4,
                            fontStyle: FontStyle.italic),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: S.sm),
              ],
              // Positive effects
              if (housePositive.isNotEmpty) ...[
                ...housePositive.map((e) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Padding(
                            padding: EdgeInsets.only(top: 4),
                            child: Icon(Icons.add_circle_outline,
                                size: 10, color: C.positive),
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
              // Negative effects
              if (houseNegative.isNotEmpty) ...[
                ...houseNegative.map((e) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Padding(
                            padding: EdgeInsets.only(top: 4),
                            child: Icon(Icons.remove_circle_outline,
                                size: 10, color: C.warning),
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
            ] else ...[
              const SizedBox(height: S.xs),
              Text(
                '${planetName(name)} occupies this house.',
                style: T.caption.copyWith(color: C.textMuted),
              ),
            ],
          ],
        ),
      ),
    );
  }

  // ── Empty House ──

  Widget _buildEmptyHouse(Color color) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(S.md),
      decoration: BoxDecoration(
        borderRadius: R.mdBr,
        color: color.withValues(alpha: 0.03),
        border: Border.all(color: color.withValues(alpha: 0.08)),
      ),
      child: Row(
        children: [
          Icon(Icons.circle_outlined, color: C.textMuted, size: 18),
          const SizedBox(width: S.sm),
          Expanded(
            child: Text(
              'No planets occupy this house. Results depend on the house lord '
              '${planetName(lord)} and any aspects received.',
              style:
                  T.caption.copyWith(color: C.textSecondary, height: 1.4),
            ),
          ),
        ],
      ),
    );
  }

  // ── Matching Yogas ──

  Widget _buildMatchingYogas() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.auto_awesome, size: 16, color: C.jupiter),
            const SizedBox(width: 6),
            Text('Active Yogas Here',
                style: T.bodySm.copyWith(
                    color: C.textPrimary, fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: S.sm),
        ...matchingYogas.map((yoga) {
          final name = yoga['name'] as String? ?? '';
          final category =
              (yoga['category'] as String? ?? '').toLowerCase();
          final color = _yogaCategoryColor(category);
          return Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Container(
              width: double.infinity,
              padding:
                  const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
              decoration: BoxDecoration(
                borderRadius: R.mdBr,
                color: color.withValues(alpha: 0.06),
                border: Border.all(color: color.withValues(alpha: 0.15)),
              ),
              child: Row(
                children: [
                  Icon(Icons.star_rounded, size: 14, color: color),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(name,
                        style: T.bodySm.copyWith(
                            color: color, fontWeight: FontWeight.w500)),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      borderRadius: R.xlBr,
                      color: color.withValues(alpha: 0.12),
                    ),
                    child: Text(
                      category.isNotEmpty
                          ? category[0].toUpperCase() + category.substring(1)
                          : 'Yoga',
                      style: T.caption.copyWith(
                          color: color,
                          fontSize: 9,
                          fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
            ),
          );
        }),
      ],
    );
  }

  // ── Matching Doshas ──

  Widget _buildMatchingDoshas() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.warning_amber_rounded,
                size: 16, color: C.warning),
            const SizedBox(width: 6),
            Text('Doshas Affecting This House',
                style: T.bodySm.copyWith(
                    color: C.textPrimary, fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: S.sm),
        ...matchingDoshas.map((dosha) {
          final name = dosha['name'] as String? ?? '';
          final severity =
              (dosha['severity'] as String? ?? 'mild').toLowerCase();
          final color = severity == 'severe'
              ? C.negative
              : severity == 'moderate'
                  ? C.warning
                  : C.positive;
          return Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Container(
              width: double.infinity,
              padding:
                  const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
              decoration: BoxDecoration(
                borderRadius: R.mdBr,
                color: color.withValues(alpha: 0.06),
                border: Border.all(color: color.withValues(alpha: 0.15)),
              ),
              child: Row(
                children: [
                  Icon(Icons.warning_rounded, size: 14, color: color),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(name,
                        style: T.bodySm.copyWith(
                            color: color, fontWeight: FontWeight.w500)),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      borderRadius: R.xlBr,
                      color: color.withValues(alpha: 0.12),
                    ),
                    child: Text(
                      severity[0].toUpperCase() + severity.substring(1),
                      style: T.caption.copyWith(
                          color: color,
                          fontSize: 9,
                          fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
            ),
          );
        }),
      ],
    );
  }

  // ── Ask AI Button ──

  Widget _buildAskAiButton(BuildContext context, Color color) {
    final planetNames = planetsHere
        .map((p) => planetName((p['name'] as String? ?? '').toLowerCase()))
        .toList();
    final prompt = planetsHere.isNotEmpty
        ? 'Tell me about ${planetNames.join(" and ")} in my ${_ordinal(houseNum)} house ($signName) and how it affects my ${_houseAreas[houseNum] ?? "life"}'
        : 'Tell me about my ${_ordinal(houseNum)} house in $signName and what it means for my ${_houseAreas[houseNum] ?? "life"}';

    return Padding(
      padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.lg),
      child: SizedBox(
        width: double.infinity,
        height: 44,
        child: ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).pop();
            context.push(
                '/chat?prompt=${Uri.encodeComponent(prompt)}');
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: C.bg,
            shape: RoundedRectangleBorder(borderRadius: R.xlBr),
          ),
          icon: const Icon(Icons.auto_awesome, size: 18),
          label: Text(
            'Ask about House $houseNum',
            style: T.bodySm
                .copyWith(color: C.bg, fontWeight: FontWeight.w600),
          ),
        ),
      ),
    );
  }

  // ── Helpers ──

  String _ordinal(int n) {
    if (n == 1) return '1st';
    if (n == 2) return '2nd';
    if (n == 3) return '3rd';
    return '${n}th';
  }

  Color _yogaCategoryColor(String category) {
    switch (category) {
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
}

const _houseAreas = <int, String>{
  1: 'Self & Personality',
  2: 'Wealth & Family',
  3: 'Siblings & Courage',
  4: 'Home & Mother',
  5: 'Children & Creativity',
  6: 'Health & Enemies',
  7: 'Marriage & Partners',
  8: 'Transformation & Longevity',
  9: 'Fortune & Dharma',
  10: 'Career & Status',
  11: 'Gains & Friends',
  12: 'Spirituality & Liberation',
};
