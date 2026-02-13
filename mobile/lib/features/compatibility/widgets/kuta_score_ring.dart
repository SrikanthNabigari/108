import 'dart:math';
import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';

/// Circular arc gauge displaying a 0-36 Kuta compatibility score.
///
/// The arc spans 270 degrees (open at the bottom). Color gradient:
/// red (low) -> amber (mid) -> green (high).
class KutaScoreRing extends StatelessWidget {
  final double score;
  final double maxScore;
  final double size;

  const KutaScoreRing({
    super.key,
    required this.score,
    this.maxScore = 36,
    this.size = 160,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _KutaRingPainter(score: score, maxScore: maxScore),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                score.toStringAsFixed(0),
                style: T.h1.copyWith(
                  fontSize: size * 0.22,
                  color: _scoreColor(score / maxScore),
                  fontWeight: FontWeight.w700,
                ),
              ),
              Text(
                '/${maxScore.toStringAsFixed(0)}',
                style: T.caption.copyWith(fontSize: size * 0.09),
              ),
            ],
          ),
        ),
      ),
    );
  }

  static Color _scoreColor(double ratio) {
    if (ratio >= 0.7) return C.positive;
    if (ratio >= 0.4) return C.warning;
    return C.negative;
  }
}

class _KutaRingPainter extends CustomPainter {
  final double score;
  final double maxScore;

  _KutaRingPainter({required this.score, required this.maxScore});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - 12;
    const strokeWidth = 12.0;
    const startAngle = 135 * pi / 180;
    const totalSweep = 270 * pi / 180;
    final ratio = (score / maxScore).clamp(0.0, 1.0);
    final scoreSweep = totalSweep * ratio;

    final rect = Rect.fromCircle(center: center, radius: radius);

    // Background track
    final bgPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round
      ..color = C.glassBorder;
    canvas.drawArc(rect, startAngle, totalSweep, false, bgPaint);

    // Score arc with gradient
    if (score > 0) {
      final gradient = SweepGradient(
        startAngle: startAngle,
        endAngle: startAngle + totalSweep,
        colors: const [C.negative, C.warning, C.positive],
        stops: const [0.0, 0.45, 0.75],
      );

      final scorePaint = Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.round
        ..shader = gradient.createShader(rect);
      canvas.drawArc(rect, startAngle, scoreSweep, false, scorePaint);
    }
  }

  @override
  bool shouldRepaint(covariant _KutaRingPainter old) =>
      old.score != score || old.maxScore != maxScore;
}
