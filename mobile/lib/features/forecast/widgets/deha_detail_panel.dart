import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';

/// Bottom sheet panel showing rich Deha Dasha (Level 6) details.
///
/// Deha = body-level micro-period, the finest subdivision of Vimshottari.
/// Shows career, relationships, health, effects, timing quality, and micro-advice.
class DehaDetailPanel extends StatelessWidget {
  final Map<String, dynamic> dehaData;
  final String pranaLord;

  const DehaDetailPanel({
    super.key,
    required this.dehaData,
    required this.pranaLord,
  });

  /// Show the detail panel as a modal bottom sheet.
  static void show(
    BuildContext context, {
    required Map<String, dynamic> dehaData,
    required String pranaLord,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) =>
          DehaDetailPanel(dehaData: dehaData, pranaLord: pranaLord),
    );
  }

  @override
  Widget build(BuildContext context) {
    final lord = dehaData['lord'] as String? ?? '';
    final color = planetColor(lord);
    final pranaColor = planetColor(pranaLord);
    final start = dehaData['start'] as String? ?? '';
    final end = dehaData['end'] as String? ?? '';
    final startDt = dehaData['start_dt'] as String? ?? '';
    final endDt = dehaData['end_dt'] as String? ?? '';
    final theme = dehaData['theme'] as String? ?? '';
    final energy = dehaData['energy'] as String? ?? '';
    final bodyFocus = dehaData['body_focus'] as String? ?? '';
    final microAdvice = dehaData['micro_advice'] as List<dynamic>? ?? [];
    final relationship =
        dehaData['relationship_with_prana'] as String? ?? 'neutral';
    final combo =
        dehaData['combination_with_prana'] as Map<String, dynamic>? ?? {};

    final comboTheme = combo['theme'] as String? ?? '';
    final comboEffects = combo['effects'] as List<dynamic>? ?? [];
    final comboHealth = combo['health'] as String? ?? '';
    final comboCareer = combo['career'] as String? ?? '';
    final comboRelationships = combo['relationships'] as String? ?? '';
    final timingQuality = combo['timing_quality'] as String? ?? '';

    // Check if currently active
    bool isCurrent = false;
    try {
      if (startDt.isNotEmpty && endDt.isNotEmpty) {
        final s = DateTime.parse(startDt);
        final e = DateTime.parse(endDt);
        isCurrent = DateTime.now().isAfter(s) && DateTime.now().isBefore(e);
      }
    } catch (_) {}

    return DraggableScrollableSheet(
      initialChildSize: 0.75,
      minChildSize: 0.4,
      maxChildSize: 0.92,
      builder: (context, scrollController) => Container(
        decoration: const BoxDecoration(
          color: Color(0xFF0A0A1A),
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: ListView(
          controller: scrollController,
          padding: const EdgeInsets.all(S.md),
          children: [
            // Drag handle
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

            // 1. Header
            _buildHeader(lord, color, start, end, isCurrent, relationship),
            const SizedBox(height: S.md),

            // 2. Prana context
            _buildPranaContext(pranaColor, comboTheme),
            const SizedBox(height: S.md),

            // 3. Timing quality badge
            if (timingQuality.isNotEmpty) ...[
              _buildTimingBadge(timingQuality, color),
              const SizedBox(height: S.md),
            ],

            // 4. Career & Relationships (the actionable insights)
            if (comboCareer.isNotEmpty || comboRelationships.isNotEmpty) ...[
              _buildLifeInsights(comboCareer, comboRelationships, color),
              const SizedBox(height: S.md),
            ],

            // 5. Effects list
            if (comboEffects.isNotEmpty) ...[
              _buildEffects(comboEffects, color),
              const SizedBox(height: S.md),
            ],

            // 6. Health
            if (comboHealth.isNotEmpty) ...[
              _buildHealth(comboHealth, bodyFocus),
              const SizedBox(height: S.md),
            ],

            // 7. Micro-Advice
            if (microAdvice.isNotEmpty) ...[
              _buildMicroAdvice(microAdvice, color),
              const SizedBox(height: S.md),
            ],

            // 8. Energy tag
            if (energy.isNotEmpty || theme.isNotEmpty) ...[
              _buildEnergyTheme(theme, energy, color),
              const SizedBox(height: S.md),
            ],

            // 9. Ask AI
            _buildAskAiButton(context, lord, color),
            const SizedBox(height: S.lg),
          ],
        ),
      ),
    );
  }

  // ── 1. Header ──

  Widget _buildHeader(String lord, Color color, String start, String end,
      bool isCurrent, String relationship) {
    final relColor = switch (relationship) {
      'friend' => Colors.green,
      'enemy' => Colors.red,
      'same' => Colors.blue,
      _ => Colors.amber,
    };

    return Row(
      children: [
        Text(planetGlyph(lord),
            style: TextStyle(fontSize: 28, color: color)),
        const SizedBox(width: S.sm),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text('Deha Dasha',
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
                  const SizedBox(width: S.xs),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8),
                      color: relColor.withValues(alpha: 0.15),
                    ),
                    child: Text(relationship,
                        style: T.caption.copyWith(
                            color: relColor,
                            fontSize: 9,
                            fontWeight: FontWeight.w600)),
                  ),
                ],
              ),
              const SizedBox(height: 2),
              Text(planetName(lord), style: T.h2.copyWith(color: color)),
              if (start.isNotEmpty || end.isNotEmpty) ...[
                const SizedBox(height: 2),
                Text('$start  \u2192  $end',
                    style: T.caption.copyWith(color: C.textSecondary)),
              ],
            ],
          ),
        ),
      ],
    );
  }

  // ── 2. Prana context ──

  Widget _buildPranaContext(Color pranaColor, String comboTheme) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      borderColor: pranaColor.withValues(alpha: 0.2),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(planetGlyph(pranaLord),
                  style: TextStyle(fontSize: 14, color: pranaColor)),
              const SizedBox(width: 4),
              Text('Within ${planetName(pranaLord)} Prana',
                  style: T.bodySm.copyWith(
                      color: pranaColor, fontWeight: FontWeight.w600)),
            ],
          ),
          if (comboTheme.isNotEmpty) ...[
            const SizedBox(height: S.xs),
            Text(comboTheme,
                style: T.caption.copyWith(
                    color: C.textSecondary,
                    fontStyle: FontStyle.italic,
                    height: 1.4)),
          ],
        ],
      ),
    );
  }

  // ── 3. Timing quality ──

  Widget _buildTimingBadge(String quality, Color color) {
    final (badgeColor, icon) = switch (quality.toLowerCase()) {
      'favorable' => (Colors.green, Icons.thumb_up_outlined),
      'unfavorable' => (Colors.red, Icons.thumb_down_outlined),
      'mixed' => (Colors.amber, Icons.swap_horiz),
      'neutral' => (Colors.blueGrey, Icons.remove),
      _ => (Colors.amber, Icons.help_outline),
    };

    return Row(
      children: [
        Container(
          padding:
              const EdgeInsets.symmetric(horizontal: S.sm, vertical: S.xs),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: badgeColor.withValues(alpha: 0.12),
            border: Border.all(color: badgeColor.withValues(alpha: 0.25)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 14, color: badgeColor),
              const SizedBox(width: 4),
              Text(
                quality[0].toUpperCase() + quality.substring(1),
                style: T.bodySm.copyWith(
                    color: badgeColor, fontWeight: FontWeight.w600),
              ),
            ],
          ),
        ),
        const SizedBox(width: S.sm),
        Text('Timing Quality',
            style: T.caption.copyWith(color: C.textMuted)),
      ],
    );
  }

  // ── 4. Career & Relationships ──

  Widget _buildLifeInsights(
      String career, String relationships, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('What This Means For You',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        if (career.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: S.sm),
            child: GlassContainer(
              padding: const EdgeInsets.all(S.sm),
              blur: 0,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.work_outline, size: 16, color: color),
                  const SizedBox(width: S.sm),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Career',
                            style: T.caption.copyWith(
                                color: color,
                                fontWeight: FontWeight.w600,
                                fontSize: 10)),
                        const SizedBox(height: 2),
                        Text(career,
                            style: T.caption.copyWith(
                                color: C.textSecondary, height: 1.4)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        if (relationships.isNotEmpty)
          GlassContainer(
            padding: const EdgeInsets.all(S.sm),
            blur: 0,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.people_outline, size: 16, color: color),
                const SizedBox(width: S.sm),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Relationships',
                          style: T.caption.copyWith(
                              color: color,
                              fontWeight: FontWeight.w600,
                              fontSize: 10)),
                      const SizedBox(height: 2),
                      Text(relationships,
                          style: T.caption.copyWith(
                              color: C.textSecondary, height: 1.4)),
                    ],
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  // ── 5. Effects ──

  Widget _buildEffects(List<dynamic> effects, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('What You May Feel',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        ...effects.take(3).map((e) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: 5),
                    child: Icon(Icons.circle, size: 5, color: color),
                  ),
                  const SizedBox(width: S.sm),
                  Expanded(
                    child: Text(e.toString(),
                        style: T.caption.copyWith(
                            color: C.textSecondary, height: 1.4)),
                  ),
                ],
              ),
            )),
      ],
    );
  }

  // ── 6. Health ──

  Widget _buildHealth(String health, String bodyFocus) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.sm),
      blur: 0,
      borderColor: Colors.tealAccent.withValues(alpha: 0.15),
      backgroundColor: Colors.tealAccent.withValues(alpha: 0.03),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.favorite_outline,
                  size: 14, color: Colors.tealAccent),
              const SizedBox(width: 4),
              Text('Health',
                  style: T.caption.copyWith(
                      color: Colors.tealAccent,
                      fontWeight: FontWeight.w600,
                      fontSize: 10)),
              if (bodyFocus.isNotEmpty) ...[
                const Spacer(),
                Flexible(
                  child: Text(bodyFocus,
                      style: T.caption.copyWith(
                          color: C.textMuted,
                          fontSize: 9,
                          fontStyle: FontStyle.italic),
                      overflow: TextOverflow.ellipsis),
                ),
              ],
            ],
          ),
          const SizedBox(height: 4),
          Text(health,
              style: T.caption
                  .copyWith(color: C.textSecondary, height: 1.4)),
        ],
      ),
    );
  }

  // ── 7. Micro-Advice ──

  Widget _buildMicroAdvice(List<dynamic> advice, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Quick Actions',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        ...advice.take(4).map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: 3),
                    child:
                        Icon(Icons.arrow_right, size: 14, color: color),
                  ),
                  const SizedBox(width: 4),
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

  // ── 8. Energy + Theme ──

  Widget _buildEnergyTheme(String theme, String energy, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (energy.isNotEmpty)
          Container(
            padding: const EdgeInsets.symmetric(
                horizontal: S.sm, vertical: 4),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              color: color.withValues(alpha: 0.1),
              border: Border.all(color: color.withValues(alpha: 0.2)),
            ),
            child: Text(energy.replaceAll('_', ' '),
                style: T.caption
                    .copyWith(color: color, fontWeight: FontWeight.w600)),
          ),
        if (theme.isNotEmpty) ...[
          const SizedBox(height: S.xs),
          Text(theme,
              style: T.caption.copyWith(
                  color: C.textMuted,
                  fontSize: 10,
                  fontStyle: FontStyle.italic)),
        ],
      ],
    );
  }

  // ── 9. Ask AI ──

  Widget _buildAskAiButton(
      BuildContext context, String lord, Color color) {
    return SizedBox(
      width: double.infinity,
      height: 44,
      child: OutlinedButton.icon(
        onPressed: () {
          Navigator.of(context).pop();
          context.push(
              '/chat?prompt=${Uri.encodeComponent("Tell me about the $lord Deha period within ${planetName(pranaLord)} Prana \u2014 what should I focus on right now?")}');
        },
        style: OutlinedButton.styleFrom(
          foregroundColor: color,
          side: BorderSide(color: color.withValues(alpha: 0.3)),
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(R.xl)),
        ),
        icon: Icon(Icons.auto_awesome, size: 16, color: color),
        label: Text('Ask about this period',
            style: T.bodySm
                .copyWith(color: color, fontWeight: FontWeight.w600)),
      ),
    );
  }
}
