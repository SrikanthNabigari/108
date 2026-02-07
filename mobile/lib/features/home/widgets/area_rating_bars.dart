import 'package:flutter/material.dart';

/// Rating bars for life areas (Career, Finance, Health, Relationships, Spiritual).
class AreaRatingBars extends StatelessWidget {
  final Map<String, double> areaScores;

  const AreaRatingBars({
    Key? key,
    this.areaScores = const {
      'Career': 7.2,
      'Finance': 6.5,
      'Health': 8.1,
      'Relationships': 7.8,
      'Spiritual': 8.5,
    },
  }) : super(key: key);

  Color _getScoreColor(double score) {
    if (score < 4) return const Color(0xFFE74C3C);
    if (score < 6) return const Color(0xFFF39C12);
    if (score < 8) return const Color(0xFF2ECC71);
    return const Color(0xFF27AE60);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: areaScores.entries.map((entry) {
        final area = entry.key;
        final score = entry.value;
        final color = _getScoreColor(score);

        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    area,
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                          color: Colors.white70,
                        ),
                  ),
                  Text(
                    score.toStringAsFixed(1),
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                          color: color,
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: score / 10,
                  minHeight: 6,
                  backgroundColor: Colors.white.withOpacity(0.1),
                  valueColor: AlwaysStoppedAnimation<Color>(color),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}
