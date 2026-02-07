import 'package:flutter/material.dart';
import '../../../shared/widgets/glass_card.dart';

/// Circular score display for today's cosmic rating.
class TodayScoreCard extends StatelessWidget {
  final double score;
  final String label;

  const TodayScoreCard({
    Key? key,
    this.score = 7.5,
    this.label = 'Today\'s Cosmic Score',
  }) : super(key: key);

  Color _getScoreColor() {
    if (score < 4) return const Color(0xFFE74C3C); // Red
    if (score < 6) return const Color(0xFFF39C12); // Orange
    if (score < 8) return const Color(0xFF2ECC71); // Green
    return const Color(0xFF27AE60); // Bright green
  }

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          SizedBox(
            width: 120,
            height: 120,
            child: CustomPaint(
              painter: _ScoreRingPainter(score, _getScoreColor()),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      score.toStringAsFixed(1),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      '/10',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            color: Colors.white54,
                          ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.white70,
                ),
          ),
        ],
      ),
    );
  }
}

class _ScoreRingPainter extends CustomPainter {
  final double score;
  final Color scoreColor;

  _ScoreRingPainter(this.score, this.scoreColor);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 8;

    // Background ring
    canvas.drawCircle(
      center,
      radius,
      Paint()
        ..color = Colors.white.withOpacity(0.1)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4,
    );

    // Progress ring
    final sweepAngle = (score / 10) * 2 * 3.14159;
    final rect = Rect.fromCircle(center: center, radius: radius);

    canvas.drawArc(
      rect,
      -3.14159 / 2,
      sweepAngle,
      false,
      Paint()
        ..color = scoreColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4
        ..strokeCap = StrokeCap.round,
    );
  }

  @override
  bool shouldRepaint(_ScoreRingPainter oldDelegate) =>
      oldDelegate.score != score;
}
