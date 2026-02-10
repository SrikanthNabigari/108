import 'dart:math';
import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import '../models/state_vector.dart';

/// Current-state overview card — mirrors the "NOW" card pattern from
/// the timeline screen. Shows composite score as a radial gauge,
/// mental state text, confluence badge, and hora lord.
class StateNowCard extends StatelessWidget {
  final StateVector state;

  const StateNowCard({super.key, required this.state});

  @override
  Widget build(BuildContext context) {
    final horaColor = planetColor(state.horaLord);

    return GlassContainer(
      padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
      child: Row(
        children: [
          // Radial gauge
          SizedBox(
            width: 90,
            height: 90,
            child: CustomPaint(
              painter: _CompositeGaugePainter(
                score: state.composite,
                confluence: state.confluence,
                color: _scoreColor(state.composite),
              ),
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      state.composite.toStringAsFixed(1),
                      style: T.h2.copyWith(
                        color: _scoreColor(state.composite),
                        fontSize: 22,
                      ),
                    ),
                    Text('/10',
                        style: T.caption.copyWith(
                            fontSize: 9, color: C.textMuted)),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(width: S.lg),
          // Text
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // NOW badge
                _NowBadge(),
                const SizedBox(height: S.sm),
                // Mental state
                Text(
                  state.mentalState,
                  style: T.h3.copyWith(
                    color: _scoreColor(state.composite),
                    fontSize: 20,
                  ),
                ),
                const SizedBox(height: 4),
                // Hora lord
                Row(
                  children: [
                    Text(
                      planetGlyph(state.horaLord),
                      style: TextStyle(fontSize: 14, color: horaColor),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${planetName(state.horaLord)} Hora',
                      style:
                          T.bodySm.copyWith(color: horaColor, fontSize: 13),
                    ),
                  ],
                ),
                const SizedBox(height: S.sm),
                // Confluence indicator
                Row(
                  children: [
                    ...List.generate(6, (i) {
                      final filled = i < state.confluence.round();
                      return Padding(
                        padding: const EdgeInsets.only(right: 3),
                        child: Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: filled
                                ? _scoreColor(state.composite)
                                    .withValues(alpha: 0.8)
                                : C.glassBorder,
                          ),
                        ),
                      );
                    }),
                    const SizedBox(width: 4),
                    Text(
                      'Confluence',
                      style: T.caption.copyWith(fontSize: 9),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _scoreColor(double score) {
    if (score >= 7) return C.positive;
    if (score >= 5) return C.warning;
    return C.negative;
  }
}

class _NowBadge extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: S.sm, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: R.xlBr,
        color: C.accentDim,
        border: Border.all(color: C.glassBorder),
      ),
      child: Text(
        'NOW',
        style:
            T.label.copyWith(color: C.accent, letterSpacing: 1.0, fontSize: 9),
      ),
    );
  }
}

/// Draws a radial arc gauge showing the composite score (0-10).
/// Outer ring = composite progress, inner dots = confluence.
class _CompositeGaugePainter extends CustomPainter {
  final double score;
  final double confluence;
  final Color color;

  _CompositeGaugePainter({
    required this.score,
    required this.confluence,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 6;
    const stroke = 5.0;
    const startAngle = -pi * 0.75; // Start at 7-o'clock
    const sweepTotal = pi * 1.5; // Sweep 270°

    // Background arc
    final bgPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = stroke
      ..strokeCap = StrokeCap.round
      ..color = C.glassBorder;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepTotal,
      false,
      bgPaint,
    );

    // Score arc
    final progress = (score / 10).clamp(0.0, 1.0);
    final arcPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = stroke
      ..strokeCap = StrokeCap.round
      ..color = color;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepTotal * progress,
      false,
      arcPaint,
    );
  }

  @override
  bool shouldRepaint(covariant _CompositeGaugePainter old) =>
      old.score != score || old.color != color;
}
