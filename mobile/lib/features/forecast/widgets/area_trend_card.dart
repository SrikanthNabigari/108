import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/features/state_map/models/state_vector.dart';

/// Compact card for a single life area, used in horizontal scroll lists.
///
/// Shows area icon, name, score, and trend arrow.
class AreaTrendCard extends StatelessWidget {
  final String areaId;
  final double score;
  final String? trend;

  const AreaTrendCard({
    super.key,
    required this.areaId,
    required this.score,
    this.trend,
  });

  @override
  Widget build(BuildContext context) {
    final planet = kAreaPlanets[areaId] ?? 'sun';
    final color = planetColor(planet);
    final icon = kAreaIcons[areaId] ?? '?';
    final name = kAreaNames[areaId] ?? areaId;

    return GlassContainer(
      padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.md),
      borderRadius: R.md,
      backgroundColor: color.withValues(alpha: 0.06),
      borderColor: color.withValues(alpha: 0.2),
      child: SizedBox(
        width: 100,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(icon, style: const TextStyle(fontSize: 22)),
            const SizedBox(height: S.xs),
            Text(
              name,
              style: T.caption.copyWith(
                color: C.textSecondary,
                fontWeight: FontWeight.w500,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: S.xs),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  score.toStringAsFixed(1),
                  style: T.h3.copyWith(
                    color: color,
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(width: S.xs),
                _trendArrow(trend),
              ],
            ),
          ],
        ),
      ),
    );
  }

  static Widget _trendArrow(String? trend) {
    switch (trend) {
      case 'up':
        return const Icon(Icons.arrow_upward, size: 14, color: C.positive);
      case 'down':
        return const Icon(Icons.arrow_downward, size: 14, color: C.negative);
      default:
        return const Icon(Icons.arrow_forward, size: 14, color: C.textMuted);
    }
  }
}
