import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Bottom sheet panel showing Atmakaraka, Ishta Devata, and Chara Karakas.
///
/// Matches dasha detail panel pattern: gradient header, educational card,
/// WHAT/WHY/WHEN sections, and colored Ask AI button.
class SoulPurposeDetailPanel extends ConsumerWidget {
  final Map<String, dynamic> data;

  const SoulPurposeDetailPanel({super.key, required this.data});

  static void show(BuildContext context,
      {required Map<String, dynamic> data}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => SoulPurposeDetailPanel(data: data),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ak = data['atmakaraka'] as Map<String, dynamic>? ?? {};
    final ishta = data['ishta_devata'] as Map<String, dynamic>?;
    final karakas = data['chara_karakas'] as List? ?? [];
    final akPlanet = ak['planet'] as String? ?? '';
    final akSign = ak['sign'] as String? ?? '';
    final akDegree = ak['degree'];
    final meaning = ak['soul_purpose'] as String? ??
        ak['meaning'] as String? ??
        '';
    final spiritualPath = ak['spiritual_path'] as String? ?? '';
    final careerDirection = ak['career_direction'] as String? ?? '';
    final color = planetColor(akPlanet);

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
              _buildHeader(akPlanet, akSign, akDegree, color),
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
                    // WHAT — soul lesson
                    if (meaning.isNotEmpty) ...[
                      _buildWhatSection(meaning, color),
                      const SizedBox(height: S.md),
                    ],
                    // WHY — spiritual path + career direction
                    if (spiritualPath.isNotEmpty ||
                        careerDirection.isNotEmpty) ...[
                      _buildWhySection(
                          spiritualPath, careerDirection, color),
                      const SizedBox(height: S.md),
                    ],
                    // Ishta Devata
                    if (ishta != null) ...[
                      _buildIshtaDevata(ishta, color),
                      const SizedBox(height: S.md),
                    ],
                    // All Chara Karakas
                    if (karakas.isNotEmpty) ...[
                      _buildCharaKarakas(karakas),
                      const SizedBox(height: S.md),
                    ],
                    const SizedBox(height: S.xl),
                  ],
                ),
              ),
              // C. Ask AI button
              _buildAskAiButton(context, color),
            ],
          ),
        );
      },
    );
  }

  // ── A. Gradient Header ──

  Widget _buildHeader(
      String akPlanet, String akSign, dynamic akDegree, Color color) {
    final signDisplay = akSign.isNotEmpty
        ? '${akSign[0].toUpperCase()}${akSign.substring(1)}'
        : '';

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
          // Planet glyph + title + AK badge
          Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: color.withValues(alpha: 0.15),
                  border:
                      Border.all(color: color.withValues(alpha: 0.4)),
                ),
                child: Center(
                  child: Text(planetGlyph(akPlanet),
                      style: TextStyle(fontSize: 22, color: color)),
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
                          'Soul Purpose',
                          style: T.h2.copyWith(color: color),
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
                            'AK',
                            style: T.caption
                                .copyWith(color: color, fontSize: 10),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${planetName(akPlanet)}'
                      '${signDisplay.isNotEmpty ? ' in $signDisplay' : ''}'
                      '${akDegree != null ? ' (${(akDegree as num).toStringAsFixed(1)}\u00B0)' : ''}',
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
                  'What is an Atmakaraka?',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                Text(
                  'The Atmakaraka is the planet with the highest degree in your '
                  'chart \u2014 it represents your soul\u2019s deepest desire and '
                  'the primary lesson of this lifetime. In Jaimini astrology, it '
                  'is the king of the chart, showing what your soul came here to learn.',
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

  // ── WHAT — Soul Lesson ──

  Widget _buildWhatSection(String meaning, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('What Your Soul Seeks',
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
            '\u201c$meaning\u201d',
            style: T.body.copyWith(
              color: color.withValues(alpha: 0.85),
              fontStyle: FontStyle.italic,
              fontSize: 15,
              height: 1.5,
            ),
          ),
        ),
      ],
    );
  }

  // ── WHY — Path & Direction ──

  Widget _buildWhySection(
      String spiritualPath, String careerDirection, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Life Direction',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        if (spiritualPath.isNotEmpty)
          _directionCard(
            icon: Icons.self_improvement,
            title: 'Spiritual Path',
            content: spiritualPath,
            color: color,
          ),
        if (careerDirection.isNotEmpty) ...[
          const SizedBox(height: S.sm),
          _directionCard(
            icon: Icons.work_outline,
            title: 'Career Direction',
            content: careerDirection,
            color: color,
          ),
        ],
      ],
    );
  }

  Widget _directionCard({
    required IconData icon,
    required String title,
    required String content,
    required Color color,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(S.md),
      decoration: BoxDecoration(
        borderRadius: R.mdBr,
        color: color.withValues(alpha: 0.04),
        border: Border.all(color: color.withValues(alpha: 0.1)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Icon(icon, size: 16, color: color),
          ),
          const SizedBox(width: S.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: T.caption.copyWith(
                        color: color, fontWeight: FontWeight.w600)),
                const SizedBox(height: 2),
                Text(content,
                    style: T.caption.copyWith(
                        color: C.textSecondary, height: 1.4)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Ishta Devata ──

  Widget _buildIshtaDevata(Map<String, dynamic> ishta, Color color) {
    final deity = ishta['deity'] as String? ?? 'Unknown';
    final sign = ishta['sign'] as String? ?? '';
    final worship = ishta['worship'] as String? ?? '';
    final interpretation = ishta['interpretation'] as String? ?? '';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.temple_hindu, color: C.jupiter, size: 18),
            const SizedBox(width: 6),
            Text('Ishta Devata',
                style: T.bodySm.copyWith(
                    color: C.textPrimary, fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.md),
          blur: 0,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                deity,
                style: T.h3.copyWith(color: C.jupiter),
              ),
              if (sign.isNotEmpty) ...[
                const SizedBox(height: S.xs),
                Text(
                  '12th from Karakamsha: $sign',
                  style: T.caption,
                ),
              ],
              if (worship.isNotEmpty) ...[
                const SizedBox(height: S.sm),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Padding(
                      padding: EdgeInsets.only(top: 2),
                      child: Icon(Icons.spa,
                          size: 12, color: C.positive),
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(worship,
                          style: T.caption.copyWith(
                              color: C.textSecondary, height: 1.4)),
                    ),
                  ],
                ),
              ],
              if (interpretation.isNotEmpty) ...[
                const SizedBox(height: S.sm),
                Text(interpretation,
                    style: T.caption.copyWith(
                        color: C.textMuted, height: 1.4)),
              ],
            ],
          ),
        ),
      ],
    );
  }

  // ── All Chara Karakas ──

  Widget _buildCharaKarakas(List karakas) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('All Chara Karakas',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.md),
        ...karakas.map((k) {
          final km = k as Map<String, dynamic>;
          final role = km['karaka'] as String? ??
              km['role'] as String? ??
              '';
          final kPlanet = km['planet'] as String? ?? '';
          final kDeg = km['degree'];
          final kSign = km['sign'] as String? ?? '';
          final kInterp = km['interpretation'] as String? ?? '';
          final kMeaning = _karakaMeaning(role);
          final kColor = planetColor(kPlanet);

          return Padding(
            padding: const EdgeInsets.only(bottom: S.sm),
            child: Container(
              padding: const EdgeInsets.all(S.md),
              decoration: BoxDecoration(
                borderRadius: R.mdBr,
                color: kColor.withValues(alpha: 0.04),
                border:
                    Border.all(color: kColor.withValues(alpha: 0.1)),
              ),
              child: Row(
                children: [
                  SizedBox(
                    width: 36,
                    child: Text(
                      planetGlyph(kPlanet),
                      style:
                          TextStyle(fontSize: 18, color: kColor),
                    ),
                  ),
                  const SizedBox(width: S.sm),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 6, vertical: 1),
                              decoration: BoxDecoration(
                                borderRadius: R.xlBr,
                                color:
                                    kColor.withValues(alpha: 0.15),
                              ),
                              child: Text(role,
                                  style: T.caption.copyWith(
                                      color: kColor,
                                      fontWeight: FontWeight.w700,
                                      fontSize: 10)),
                            ),
                            const SizedBox(width: S.sm),
                            Text(
                              '${planetName(kPlanet)}'
                              '${kSign.isNotEmpty ? ' in $kSign' : ''}'
                              '${kDeg != null ? ' (${(kDeg as num).toStringAsFixed(1)}\u00B0)' : ''}',
                              style: T.caption,
                            ),
                          ],
                        ),
                        if (kMeaning.isNotEmpty)
                          Text(kMeaning,
                              style: T.caption.copyWith(
                                  color: C.textSecondary)),
                        if (kInterp.isNotEmpty)
                          Text(kInterp,
                              style: T.caption.copyWith(
                                  color: C.textMuted),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis),
                      ],
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
    return Padding(
      padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.lg),
      child: SizedBox(
        width: double.infinity,
        height: 44,
        child: ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).pop();
            context.push('/chat?prompt=${Uri.encodeComponent("Tell me about my soul purpose and Atmakaraka — what is my dharma?")}');
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: C.bg,
            shape: RoundedRectangleBorder(borderRadius: R.xlBr),
          ),
          icon: const Icon(Icons.auto_awesome, size: 18),
          label: Text(
            'Ask about your soul purpose',
            style: T.bodySm
                .copyWith(color: C.bg, fontWeight: FontWeight.w600),
          ),
        ),
      ),
    );
  }

  // ── Helpers ──

  String _karakaMeaning(String karaka) {
    switch (karaka.toUpperCase()) {
      case 'AK':
        return 'Atmakaraka \u2014 Self, soul purpose';
      case 'AMK':
        return 'Amatyakaraka \u2014 Career, profession';
      case 'BK':
        return 'Bhratrikaraka \u2014 Siblings, courage';
      case 'MK':
        return 'Matrikaraka \u2014 Mother, nurturing';
      case 'PK':
        return 'Putrakaraka \u2014 Children, creativity';
      case 'GK':
        return 'Gnatikaraka \u2014 Obstacles, competition';
      case 'DK':
        return 'Darakaraka \u2014 Spouse, partnerships';
      default:
        return '';
    }
  }
}
