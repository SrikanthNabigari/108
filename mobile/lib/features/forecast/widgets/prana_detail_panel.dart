import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';

/// Bottom sheet panel showing rich Prana Dasha details with Deha timeline.
///
/// This is a stateless display panel — all data is passed in, no API fetch.
/// Follows the DashaDetailPanel pattern but tailored for Level-5 Prana periods.
class PranaDetailPanel extends StatelessWidget {
  final Map<String, dynamic> pranaData;
  final String sdLord;

  const PranaDetailPanel({
    super.key,
    required this.pranaData,
    required this.sdLord,
  });

  /// Show the detail panel as a modal bottom sheet.
  static void show(
    BuildContext context, {
    required Map<String, dynamic> pranaData,
    required String sdLord,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => PranaDetailPanel(pranaData: pranaData, sdLord: sdLord),
    );
  }

  @override
  Widget build(BuildContext context) {
    final lord = pranaData['lord'] as String? ?? '';
    final color = planetColor(lord);
    final theme = pranaData['theme'] as String? ?? '';
    final energy = pranaData['energy_quality'] as String? ?? '';
    final startDt = pranaData['start_dt'] as String? ?? '';
    final endDt = pranaData['end_dt'] as String? ?? '';
    final start = pranaData['start'] as String? ?? '';
    final end = pranaData['end'] as String? ?? '';
    final combinationWithSd =
        pranaData['combination_with_sd'] as Map<String, dynamic>?;
    final whatHappens =
        pranaData['what_happens'] as Map<String, dynamic>?;
    final lifeAreas =
        pranaData['life_areas'] as Map<String, dynamic>?;
    final guidance = pranaData['guidance'] as List<dynamic>? ?? [];
    final challenges = pranaData['challenges'] as String? ?? '';
    final opportunities = pranaData['opportunities'] as String? ?? '';
    final dehas = pranaData['deha_timeline'] as List<dynamic>? ?? [];

    // Determine if this prana period is currently active
    bool isCurrent = false;
    try {
      if (startDt.isNotEmpty && endDt.isNotEmpty) {
        final s = DateTime.parse(startDt);
        final e = DateTime.parse(endDt);
        final now = DateTime.now();
        isCurrent = now.isAfter(s) && now.isBefore(e);
      }
    } catch (_) {}

    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      minChildSize: 0.4,
      maxChildSize: 0.95,
      builder: (context, scrollController) => Container(
        decoration: const BoxDecoration(
          color: Color(0xFF0A0A1A),
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: ListView(
          controller: scrollController,
          padding: const EdgeInsets.all(S.md),
          children: [
            // 1. Drag handle
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: C.glassBorder,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: S.md),

            // 2. Header
            _buildHeader(lord, color, start, end, isCurrent),
            const SizedBox(height: S.md),

            // 3. Theme + Energy
            if (theme.isNotEmpty || energy.isNotEmpty)
              _buildThemeEnergy(theme, energy, color),
            if (theme.isNotEmpty || energy.isNotEmpty)
              const SizedBox(height: S.md),

            // 4. SD Combination
            if (combinationWithSd != null &&
                (combinationWithSd['theme'] as String? ?? '').isNotEmpty)
              _buildSdCombination(combinationWithSd!, color),
            if (combinationWithSd != null &&
                (combinationWithSd['theme'] as String? ?? '').isNotEmpty)
              const SizedBox(height: S.md),

            // 5. What Happens
            if (whatHappens != null && whatHappens.isNotEmpty)
              _buildWhatHappens(whatHappens, color),
            if (whatHappens != null && whatHappens.isNotEmpty)
              const SizedBox(height: S.md),

            // 6. Life Areas
            if (lifeAreas != null && lifeAreas.isNotEmpty)
              _buildLifeAreas(lifeAreas, color),
            if (lifeAreas != null && lifeAreas.isNotEmpty)
              const SizedBox(height: S.md),

            // 7. Guidance
            if (guidance.isNotEmpty) _buildGuidance(guidance, color),
            if (guidance.isNotEmpty) const SizedBox(height: S.md),

            // 8. Challenges / Opportunities
            if (challenges.isNotEmpty || opportunities.isNotEmpty)
              _buildChallengesOpportunities(challenges, opportunities),
            if (challenges.isNotEmpty || opportunities.isNotEmpty)
              const SizedBox(height: S.md),

            // 9. Deha Timeline
            if (dehas.isNotEmpty) _buildDehaTimeline(dehas, color),
            if (dehas.isNotEmpty) const SizedBox(height: S.md),

            // 11. Ask AI button
            _buildAskAiButton(context, lord, color),
            const SizedBox(height: S.lg),
          ],
        ),
      ),
    );
  }

  // ── 2. Header ──

  Widget _buildHeader(
      String lord, Color color, String start, String end, bool isCurrent) {
    return Row(
      children: [
        Text(
          planetGlyph(lord),
          style: TextStyle(fontSize: 28, color: color),
        ),
        const SizedBox(width: S.sm),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text('Prana Dasha',
                      style: T.caption.copyWith(color: C.textMuted)),
                  if (isCurrent) ...[
                    const SizedBox(width: S.sm),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8),
                        color: color.withValues(alpha: 0.2),
                      ),
                      child: Text('NOW',
                          style: T.caption.copyWith(
                              color: color,
                              fontSize: 9,
                              fontWeight: FontWeight.w700)),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 2),
              Text(
                planetName(lord),
                style: T.h2.copyWith(color: color),
              ),
              if (start.isNotEmpty || end.isNotEmpty) ...[
                const SizedBox(height: 2),
                Text(
                  '$start  \u2192  $end',
                  style: T.caption.copyWith(color: C.textSecondary),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  // ── 3. Theme + Energy ──

  Widget _buildThemeEnergy(String theme, String energy, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (theme.isNotEmpty)
          GlassContainer(
            padding: const EdgeInsets.all(S.md),
            blur: 0,
            child: Text(
              '\u201c$theme\u201d',
              style: T.bodySm.copyWith(
                color: color.withValues(alpha: 0.85),
                fontStyle: FontStyle.italic,
                height: 1.5,
              ),
            ),
          ),
        if (energy.isNotEmpty) ...[
          const SizedBox(height: S.sm),
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: S.sm, vertical: 4),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              color: color.withValues(alpha: 0.1),
              border: Border.all(color: color.withValues(alpha: 0.2)),
            ),
            child: Text(
              energy,
              style:
                  T.caption.copyWith(color: color, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ],
    );
  }

  // ── 4. SD Combination ──

  Widget _buildSdCombination(
      Map<String, dynamic> combo, Color color) {
    final comboTheme = combo['theme'] as String? ?? '';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'With ${planetName(sdLord)}',
          style: T.bodySm.copyWith(
              color: C.textPrimary, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: S.xs),
        GlassContainer(
          padding: const EdgeInsets.all(S.md),
          blur: 0,
          borderColor: planetColor(sdLord).withValues(alpha: 0.2),
          child: Text(
            comboTheme,
            style: T.bodySm.copyWith(
              color: C.textSecondary,
              fontStyle: FontStyle.italic,
              height: 1.5,
            ),
          ),
        ),
      ],
    );
  }

  // ── 5. What Happens ──

  Widget _buildWhatHappens(Map<String, dynamic> whatHappens, Color color) {
    const fieldIcons = {
      'mind': Icons.psychology,
      'body': Icons.accessibility_new,
      'events': Icons.event,
      'career': Icons.work_outline,
      'relationships': Icons.people_outline,
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('What Happens',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        ...whatHappens.entries
            .where((e) => (e.value?.toString() ?? '').isNotEmpty)
            .map((e) {
          final icon = fieldIcons[e.key] ?? Icons.circle;
          final label =
              e.key[0].toUpperCase() + e.key.substring(1);
          return Padding(
            padding: const EdgeInsets.only(bottom: S.sm),
            child: GlassContainer(
              padding: const EdgeInsets.all(S.sm),
              blur: 0,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(icon, size: 16, color: color),
                  const SizedBox(width: S.sm),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(label,
                            style: T.caption.copyWith(
                                color: color,
                                fontWeight: FontWeight.w600,
                                fontSize: 10)),
                        const SizedBox(height: 2),
                        Text(e.value.toString(),
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
      ],
    );
  }

  // ── 6. Life Areas ──

  Widget _buildLifeAreas(Map<String, dynamic> areas, Color color) {
    const areaIcons = {
      'career': Icons.work_outline,
      'health': Icons.favorite_outline,
      'relationships': Icons.people_outline,
      'spiritual': Icons.self_improvement,
      'family': Icons.home_outlined,
      'education': Icons.school_outlined,
      'finance': Icons.account_balance_wallet_outlined,
      'travel': Icons.flight_outlined,
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Life Areas',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: areas.entries
              .where((e) => (e.value?.toString() ?? '').isNotEmpty)
              .map((e) {
            final icon = areaIcons[e.key] ?? Icons.circle;
            final label =
                e.key[0].toUpperCase() + e.key.substring(1);
            return Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: S.sm, vertical: S.xs),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                color: color.withValues(alpha: 0.08),
                border: Border.all(color: color.withValues(alpha: 0.15)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(icon, size: 12, color: color),
                  const SizedBox(width: 4),
                  Text(label,
                      style: T.caption.copyWith(
                          color: color,
                          fontWeight: FontWeight.w600,
                          fontSize: 10)),
                ],
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  // ── 7. Guidance ──

  Widget _buildGuidance(List<dynamic> guidance, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Guidance',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        ...guidance.take(8).map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Icon(Icons.circle, size: 5, color: color),
                  ),
                  const SizedBox(width: S.sm),
                  Expanded(
                    child: Text(item.toString(),
                        style: T.caption.copyWith(
                            color: C.textSecondary, height: 1.4)),
                  ),
                ],
              ),
            )),
      ],
    );
  }

  // ── 8. Challenges / Opportunities ──

  Widget _buildChallengesOpportunities(
      String challenges, String opportunities) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (opportunities.isNotEmpty)
          Expanded(
            child: GlassContainer(
              padding: const EdgeInsets.all(S.sm),
              blur: 0,
              borderColor: C.positive.withValues(alpha: 0.2),
              backgroundColor: C.positive.withValues(alpha: 0.04),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.trending_up,
                          size: 14, color: C.positive),
                      const SizedBox(width: 4),
                      Text('Opportunities',
                          style: T.caption.copyWith(
                              color: C.positive,
                              fontWeight: FontWeight.w600,
                              fontSize: 10)),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(opportunities,
                      style: T.caption.copyWith(
                          color: C.textSecondary, height: 1.4)),
                ],
              ),
            ),
          ),
        if (opportunities.isNotEmpty && challenges.isNotEmpty)
          const SizedBox(width: S.sm),
        if (challenges.isNotEmpty)
          Expanded(
            child: GlassContainer(
              padding: const EdgeInsets.all(S.sm),
              blur: 0,
              borderColor: C.negative.withValues(alpha: 0.2),
              backgroundColor: C.negative.withValues(alpha: 0.04),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.warning_amber_rounded,
                          size: 14, color: C.negative),
                      const SizedBox(width: 4),
                      Text('Challenges',
                          style: T.caption.copyWith(
                              color: C.negative,
                              fontWeight: FontWeight.w600,
                              fontSize: 10)),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(challenges,
                      style: T.caption.copyWith(
                          color: C.textSecondary, height: 1.4)),
                ],
              ),
            ),
          ),
      ],
    );
  }

  // ── 9. Deha Timeline ──

  Widget _buildDehaTimeline(List<dynamic> dehas, Color pranaColor) {
    final now = DateTime.now();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Deha Timeline',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: 2),
        Text('Body-level micro-periods',
            style: T.caption.copyWith(color: C.textMuted, fontSize: 10)),
        const SizedBox(height: S.sm),
        ...dehas.asMap().entries.map((entry) {
          final i = entry.key;
          final dh = entry.value as Map<String, dynamic>;
          final dhLord = dh['lord'] as String? ?? '';
          final dhColor = planetColor(dhLord);
          final startStr = dh['start'] as String? ?? '';
          final endStr = dh['end'] as String? ?? '';
          final theme = dh['theme'] as String? ?? '';
          final bodyFocus = dh['body_focus'] as String? ?? '';
          final relationship =
              dh['relationship_with_prana'] as String? ?? 'neutral';
          final combo = dh['combination_with_prana'] as Map<String, dynamic>?;
          final comboTheme = combo?['theme'] as String? ?? '';

          // Check if NOW
          bool isNow = false;
          try {
            final s = DateTime.parse(dh['start_dt'] as String? ?? '');
            final e = DateTime.parse(dh['end_dt'] as String? ?? '');
            isNow = now.isAfter(s) && now.isBefore(e);
          } catch (_) {}

          // Relationship chip colors
          final relColor = switch (relationship) {
            'friend' => Colors.green,
            'enemy' => Colors.red,
            'same' => Colors.blue,
            _ => Colors.amber,
          };

          final isLast = i == dehas.length - 1;

          return Padding(
            padding: EdgeInsets.only(bottom: isLast ? 0 : S.xs),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Time column
                SizedBox(
                  width: 42,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(startStr,
                          style: T.caption.copyWith(
                              color: isNow ? dhColor : C.textMuted,
                              fontWeight:
                                  isNow ? FontWeight.w700 : FontWeight.w500,
                              fontSize: 10)),
                      Text(endStr,
                          style: T.caption.copyWith(
                              color: C.textMuted, fontSize: 8)),
                    ],
                  ),
                ),
                const SizedBox(width: S.xs),
                // Dot + line
                Column(
                  children: [
                    Container(
                      width: isNow ? 10 : 6,
                      height: isNow ? 10 : 6,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isNow
                            ? dhColor
                            : dhColor.withValues(alpha: 0.3),
                        border: isNow
                            ? Border.all(
                                color: dhColor.withValues(alpha: 0.6),
                                width: 1.5)
                            : null,
                      ),
                    ),
                    if (!isLast)
                      Container(
                          width: 1,
                          height: 32,
                          color: dhColor.withValues(alpha: 0.15)),
                  ],
                ),
                const SizedBox(width: S.xs),
                // Content
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: S.xs, vertical: 3),
                    decoration: isNow
                        ? BoxDecoration(
                            borderRadius: BorderRadius.circular(6),
                            color: dhColor.withValues(alpha: 0.06),
                            border: Border.all(
                                color: dhColor.withValues(alpha: 0.2)),
                          )
                        : null,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(planetGlyph(dhLord),
                                style: TextStyle(
                                    fontSize: 11, color: dhColor)),
                            const SizedBox(width: 3),
                            Text(planetName(dhLord),
                                style: T.bodySm.copyWith(
                                    color:
                                        isNow ? dhColor : C.textPrimary,
                                    fontWeight: FontWeight.w600,
                                    fontSize: 11)),
                            if (isNow) ...[
                              const SizedBox(width: 4),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 5, vertical: 1),
                                decoration: BoxDecoration(
                                    borderRadius:
                                        BorderRadius.circular(6),
                                    color: dhColor
                                        .withValues(alpha: 0.2)),
                                child: Text('NOW',
                                    style: T.caption.copyWith(
                                        color: dhColor,
                                        fontSize: 7,
                                        fontWeight: FontWeight.w700)),
                              ),
                            ],
                            const Spacer(),
                            // Relationship chip
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 5, vertical: 1),
                              decoration: BoxDecoration(
                                  borderRadius:
                                      BorderRadius.circular(8),
                                  color:
                                      relColor.withValues(alpha: 0.15)),
                              child: Text(relationship,
                                  style: T.caption.copyWith(
                                      color: relColor,
                                      fontSize: 8,
                                      fontWeight: FontWeight.w600)),
                            ),
                          ],
                        ),
                        if (comboTheme.isNotEmpty) ...[
                          const SizedBox(height: 1),
                          Text(comboTheme,
                              style: T.caption.copyWith(
                                  color: C.textSecondary,
                                  fontSize: 9,
                                  height: 1.2),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis),
                        ] else if (theme.isNotEmpty) ...[
                          const SizedBox(height: 1),
                          Text(theme,
                              style: T.caption.copyWith(
                                  color: C.textSecondary,
                                  fontSize: 9,
                                  height: 1.2),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis),
                        ],
                        if (bodyFocus.isNotEmpty) ...[
                          const SizedBox(height: 1),
                          Text(bodyFocus,
                              style: T.caption.copyWith(
                                  color: C.textMuted,
                                  fontSize: 8,
                                  fontStyle: FontStyle.italic),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis),
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }

  // ── 10. Ask AI Button ──

  Widget _buildAskAiButton(BuildContext context, String lord, Color color) {
    return SizedBox(
      width: double.infinity,
      height: 44,
      child: OutlinedButton.icon(
        onPressed: () {
          Navigator.of(context).pop();
          context.push(
              '/chat?prompt=${Uri.encodeComponent("Tell me about my current $lord Prana Dasha period \u2014 what should I expect at this micro-timing level?")}');
        },
        style: OutlinedButton.styleFrom(
          foregroundColor: color,
          side: BorderSide(color: color.withValues(alpha: 0.3)),
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(R.xl)),
        ),
        icon: Icon(Icons.auto_awesome, size: 16, color: color),
        label: Text(
          'Ask about this period',
          style: T.bodySm.copyWith(color: color, fontWeight: FontWeight.w600),
        ),
      ),
    );
  }
}
