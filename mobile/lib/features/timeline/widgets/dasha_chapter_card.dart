import 'package:flutter/material.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/planet_glyph.dart';

/// Dasha period card showing planetary period information.
class DashaChapterCard extends StatelessWidget {
  final String planetName;
  final String periodLabel;
  final String dateRange;
  final List<String> themes;
  final double progressPercent;
  final bool isCurrent;

  const DashaChapterCard({
    Key? key,
    required this.planetName,
    required this.periodLabel,
    required this.dateRange,
    required this.themes,
    this.progressPercent = 0.5,
    this.isCurrent = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 12),
      border: isCurrent
          ? Border.all(
              color: const Color(0xff6C63FF),
              width: 2,
            )
          : null,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Planet and title
          Row(
            children: [
              PlanetGlyph(
                planetName: planetName,
                size: 40,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      periodLabel,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            color: Colors.white,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      dateRange,
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            color: Colors.white54,
                          ),
                    ),
                  ],
                ),
              ),
              if (isCurrent)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(6),
                    color: const Color(0xff6C63FF).withOpacity(0.2),
                  ),
                  child: Text(
                    'Current',
                    style: TextStyle(
                      color: const Color(0xff6C63FF),
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          // Progress bar
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Progress',
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: Colors.white54,
                    ),
              ),
              const SizedBox(height: 6),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: progressPercent,
                  minHeight: 4,
                  backgroundColor: Colors.white.withOpacity(0.1),
                  valueColor: AlwaysStoppedAnimation<Color>(
                    isCurrent
                        ? const Color(0xff6C63FF)
                        : Colors.white.withOpacity(0.3),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          // Themes
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: themes
                .map(
                  (theme) => Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(6),
                      color: Colors.white.withOpacity(0.05),
                      border: Border.all(
                        color: Colors.white.withOpacity(0.2),
                      ),
                    ),
                    child: Text(
                      theme,
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            color: Colors.white70,
                          ),
                    ),
                  ),
                )
                .toList(),
          ),
        ],
      ),
    );
  }
}
