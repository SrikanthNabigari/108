import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import '../models/state_vector.dart';

/// Horizontally scrollable life-area cards for the State Map.
///
/// Each card shows area icon, name, score, progress bar, badges
/// (DOUBLE transit, active yogas), and insight text. Tapping a card
/// opens [AreaDetailPanel] via the [onAreaTap] callback.
class AreaScoreCard extends StatelessWidget {
  final List<AreaScore> areas;
  final List<StateVector> rangeVectors;
  final DateTime? selectedDate;
  final void Function(AreaScore area)? onAreaTap;

  const AreaScoreCard({
    super.key,
    required this.areas,
    this.rangeVectors = const [],
    this.selectedDate,
    this.onAreaTap,
  });

  @override
  Widget build(BuildContext context) {
    if (areas.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text('Life Areas', style: T.h3.copyWith(fontSize: 16)),
            const SizedBox(width: S.sm),
            Text(
              _dateLabel(),
              style: T.caption,
            ),
          ],
        ),
        const SizedBox(height: S.sm),
        SizedBox(
          height: 132,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: areas.length,
            separatorBuilder: (_, __) => const SizedBox(width: S.sm),
            itemBuilder: (_, i) => _AreaCard(
              area: areas[i],
              onTap: onAreaTap != null ? () => onAreaTap!(areas[i]) : null,
            ),
          ),
        ),
      ],
    );
  }

  String _dateLabel() {
    if (selectedDate == null) return 'Today';
    final now = DateTime.now();
    final d = selectedDate!;
    if (d.year == now.year && d.month == now.month && d.day == now.day) {
      return 'Today';
    }
    const months = [
      '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    return '${months[d.month]} ${d.day}';
  }
}

class _AreaCard extends StatelessWidget {
  final AreaScore area;
  final VoidCallback? onTap;

  const _AreaCard({required this.area, this.onTap});

  @override
  Widget build(BuildContext context) {
    final planet = kAreaPlanets[area.id] ?? 'saturn';
    final color = planetColor(planet);
    final isHighlighted = area.score >= 7.0;
    final fraction = (area.score / 10).clamp(0.0, 1.0);
    final icon = kAreaIcons[area.id] ?? '\u2022';

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 144,
        padding: const EdgeInsets.all(S.md),
        decoration: BoxDecoration(
          borderRadius: R.lgBr,
          color: color.withValues(alpha: isHighlighted ? 0.18 : 0.04),
          border: Border.all(
            color: color.withValues(alpha: isHighlighted ? 0.6 : 0.15),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top row: icon + name + score
            Row(
              children: [
                Text(icon, style: const TextStyle(fontSize: 14)),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    area.name,
                    style: T.bodySm.copyWith(
                      color: C.textPrimary,
                      fontWeight: FontWeight.w500,
                      fontSize: 13,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Text(
                  area.score.toStringAsFixed(1),
                  style: T.bodySm.copyWith(
                    color: color,
                    fontWeight: FontWeight.w700,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),

            // Progress bar
            ClipRRect(
              borderRadius: R.smBr,
              child: LinearProgressIndicator(
                value: fraction,
                minHeight: 4,
                backgroundColor: C.glassBorder,
                valueColor: AlwaysStoppedAnimation(color),
              ),
            ),
            const SizedBox(height: 6),

            // Badges row
            Row(
              children: [
                if (area.doubleTransit) ...[
                  _Badge(
                    text: 'DOUBLE',
                    bgColor: const Color(0xFFBF8F00).withValues(alpha: 0.15),
                    textColor: const Color(0xFFD4A017),
                    borderColor: const Color(0xFFD4A017).withValues(alpha: 0.4),
                  ),
                  const SizedBox(width: 4),
                ],
                if (area.activeYogas.isNotEmpty)
                  _Badge(
                    text: '\u2726 ${area.activeYogas.length}',
                    bgColor: C.positive.withValues(alpha: 0.12),
                    textColor: C.positive,
                    borderColor: C.positive.withValues(alpha: 0.3),
                  ),
                if (!area.doubleTransit && area.activeYogas.isEmpty)
                  // Lordship quality badge as fallback
                  if (area.lordshipQuality != 'neutral')
                    _Badge(
                      text: area.lordshipQuality,
                      bgColor: color.withValues(alpha: 0.1),
                      textColor: color,
                      borderColor: color.withValues(alpha: 0.25),
                    ),
              ],
            ),

            const Spacer(),

            // Insight + chevron
            Row(
              children: [
                Expanded(
                  child: Text(
                    area.insight,
                    style: T.caption.copyWith(fontSize: 9, color: C.textMuted),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Icon(
                  Icons.chevron_right,
                  size: 14,
                  color: color.withValues(alpha: 0.5),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  final String text;
  final Color bgColor;
  final Color textColor;
  final Color borderColor;

  const _Badge({
    required this.text,
    required this.bgColor,
    required this.textColor,
    required this.borderColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: R.smBr,
        color: bgColor,
        border: Border.all(color: borderColor, width: 0.5),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 9,
          fontWeight: FontWeight.w700,
          color: textColor,
          letterSpacing: 0.5,
        ),
      ),
    );
  }
}
