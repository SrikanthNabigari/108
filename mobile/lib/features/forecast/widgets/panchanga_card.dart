import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/data/models/forecast_model.dart';

/// Displays the five limbs of Panchanga in labeled rows inside a glass card.
class PanchangaCard extends StatelessWidget {
  final PanchangaData? panchanga;

  const PanchangaCard({super.key, required this.panchanga});

  @override
  Widget build(BuildContext context) {
    if (panchanga == null) return const SizedBox.shrink();

    final limbs = [
      ('Tithi', panchanga!.tithi),
      ('Nakshatra', panchanga!.nakshatra),
      ('Yoga', panchanga!.yoga),
      ('Karana', panchanga!.karana),
      ('Vara', panchanga!.vara),
    ];

    return GlassContainer(
      padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.auto_awesome, size: 14, color: C.textMuted),
              const SizedBox(width: S.sm),
              Text(
                'PANCHANGA',
                style: T.label.copyWith(letterSpacing: 1.5),
              ),
            ],
          ),
          const SizedBox(height: S.md),
          for (int i = 0; i < limbs.length; i++) ...[
            if (i > 0)
              Divider(
                color: C.glassBorder,
                height: 1,
                thickness: 0.5,
              ),
            Padding(
              padding: const EdgeInsets.symmetric(vertical: S.sm),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(limbs[i].$1, style: T.caption),
                  Text(
                    limbs[i].$2 ?? '--',
                    style: T.bodySm.copyWith(
                      color: C.textPrimary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
