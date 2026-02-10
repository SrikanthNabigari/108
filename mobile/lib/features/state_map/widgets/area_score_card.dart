import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import '../models/state_vector.dart';

/// Five horizontal bars showing life-area scores (Career, Love, Health, Money, Spirit).
///
/// Each bar uses the dominant planet's color as its fill.
class AreaScoreCard extends StatelessWidget {
  final List<AreaScore> areas;

  const AreaScoreCard({super.key, required this.areas});

  @override
  Widget build(BuildContext context) {
    if (areas.isEmpty) return const SizedBox.shrink();

    return GlassContainer(
      padding: const EdgeInsets.all(S.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('LIFE AREAS',
              style: T.label.copyWith(color: C.textMuted, letterSpacing: 1.2)),
          const SizedBox(height: S.md),
          ...areas.map((a) => _AreaBar(area: a)),
        ],
      ),
    );
  }
}

class _AreaBar extends StatelessWidget {
  final AreaScore area;
  const _AreaBar({required this.area});

  @override
  Widget build(BuildContext context) {
    final color = _areaColor(area);
    final fraction = (area.score / 10).clamp(0.0, 1.0);
    final icon = kAreaIcons[area.id] ?? '•';

    return Padding(
      padding: const EdgeInsets.only(bottom: S.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(icon, style: const TextStyle(fontSize: 14)),
              const SizedBox(width: S.xs),
              Text(
                area.name,
                style: T.bodySm.copyWith(
                    color: C.textPrimary,
                    fontWeight: FontWeight.w500,
                    fontSize: 13),
              ),
              const Spacer(),
              Text(
                area.score.toStringAsFixed(1),
                style: T.bodySm.copyWith(
                    color: color, fontWeight: FontWeight.w600, fontSize: 13),
              ),
            ],
          ),
          const SizedBox(height: 4),
          ClipRRect(
            borderRadius: R.smBr,
            child: LinearProgressIndicator(
              value: fraction,
              minHeight: 4,
              backgroundColor: C.glassBorder,
              valueColor: AlwaysStoppedAnimation(color),
            ),
          ),
          if (area.insight.isNotEmpty) ...[
            const SizedBox(height: 2),
            Text(area.insight,
                style: T.caption.copyWith(fontSize: 10, color: C.textMuted)),
          ],
        ],
      ),
    );
  }

  Color _areaColor(AreaScore a) {
    if (a.dominantPlanet.isNotEmpty) {
      return planetColor(a.dominantPlanet);
    }
    return _scoreColor(a.score);
  }

  Color _scoreColor(double score) {
    if (score >= 7) return C.positive;
    if (score >= 4) return C.warning;
    return C.negative;
  }
}
