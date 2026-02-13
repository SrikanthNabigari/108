import 'dart:math';
import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';

/// Circular arc gauge displaying a 0-10 day rating score.
///
/// The arc spans 270 degrees (open at the bottom). Color gradient:
/// red (0-3), amber (4-6), green (7-10).
class DayRatingRing extends StatelessWidget {
  final double score;
  final double size;

  const DayRatingRing({
    super.key,
    required this.score,
    this.size = 160,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _RingPainter(score: score),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                score.toStringAsFixed(1),
                style: T.h1.copyWith(
                  fontSize: size * 0.22,
                  color: _scoreColor(score),
                  fontWeight: FontWeight.w700,
                ),
              ),
              Text(
                '/10',
                style: T.caption.copyWith(fontSize: size * 0.09),
              ),
            ],
          ),
        ),
      ),
    );
  }

  static Color _scoreColor(double s) {
    if (s >= 7) return C.positive;
    if (s >= 4) return C.warning;
    return C.negative;
  }
}

class _RingPainter extends CustomPainter {
  final double score;

  _RingPainter({required this.score});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - 12;
    const strokeWidth = 10.0;
    // Arc spans 270 degrees, starting at 135 degrees (bottom-left)
    const startAngle = 135 * pi / 180;
    const totalSweep = 270 * pi / 180;
    final scoreSweep = totalSweep * (score / 10).clamp(0.0, 1.0);

    final rect = Rect.fromCircle(center: center, radius: radius);

    // Background track
    final bgPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round
      ..color = C.glassBorder;
    canvas.drawArc(rect, startAngle, totalSweep, false, bgPaint);

    // Score arc
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
  bool shouldRepaint(covariant _RingPainter old) => old.score != score;
}
