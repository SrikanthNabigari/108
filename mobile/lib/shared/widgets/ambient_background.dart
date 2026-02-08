import 'dart:math';
import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

/// Full-screen dark background with drifting animated stars.
///
/// Stars slowly drift in random directions, creating a living cosmic feel.
/// Place this behind [GlassContainer] widgets so BackdropFilter blur
/// has visible specks to frost.
class AmbientBackground extends StatefulWidget {
  final Widget child;

  const AmbientBackground({super.key, required this.child});

  @override
  State<AmbientBackground> createState() => _AmbientBackgroundState();
}

class _AmbientBackgroundState extends State<AmbientBackground>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 60),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: C.bg,
      child: Stack(
        children: [
          // Animated star field
          Positioned.fill(
            child: AnimatedBuilder(
              animation: _controller,
              builder: (context, _) => CustomPaint(
                painter: _StarFieldPainter(
                  progress: _controller.value,
                  screenSize: MediaQuery.sizeOf(context),
                ),
              ),
            ),
          ),
          // Subtle nebula glow (very faint, for glass blur content)
          Positioned(
            top: -120,
            right: -100,
            child: Container(
              width: 350,
              height: 350,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    Colors.white.withValues(alpha: 0.03),
                    Colors.white.withValues(alpha: 0.0),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: -150,
            left: -100,
            child: Container(
              width: 400,
              height: 400,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    Colors.white.withValues(alpha: 0.02),
                    Colors.white.withValues(alpha: 0.0),
                  ],
                ),
              ),
            ),
          ),
          // Content
          widget.child,
        ],
      ),
    );
  }
}

/// Paints a drifting star field. Stars are seeded once and drift slowly
/// based on [progress] (0.0 → 1.0 over 60 seconds, repeating).
class _StarFieldPainter extends CustomPainter {
  final double progress;
  final Size screenSize;

  static List<_Star>? _stars;
  static Size? _lastSize;

  _StarFieldPainter({required this.progress, required this.screenSize});

  @override
  void paint(Canvas canvas, Size size) {
    // Seed stars once (or when screen size changes)
    if (_stars == null || _lastSize != screenSize) {
      _lastSize = screenSize;
      _stars = _generateStars(screenSize);
    }

    final paint = Paint()..style = PaintingStyle.fill;

    for (final star in _stars!) {
      // Slow drift: each star moves in its own direction
      final drift = progress * star.speed;
      final dx = star.x + cos(star.angle) * drift * screenSize.width * 0.15;
      final dy = star.y + sin(star.angle) * drift * screenSize.height * 0.15;

      // Wrap around edges
      final wx = dx % screenSize.width;
      final wy = dy % screenSize.height;

      // Gentle twinkle
      final twinkle =
          0.5 + 0.5 * sin(progress * 2 * pi * star.twinkleRate + star.phase);
      final alpha = star.baseAlpha * twinkle;

      paint.color = Colors.white.withValues(alpha: alpha.clamp(0.0, 1.0));
      canvas.drawCircle(Offset(wx, wy), star.radius, paint);
    }
  }

  static List<_Star> _generateStars(Size size) {
    final rand = Random(42); // fixed seed for consistency
    final count = (size.width * size.height / 3000).round().clamp(60, 200);
    return List.generate(count, (_) {
      return _Star(
        x: rand.nextDouble() * size.width,
        y: rand.nextDouble() * size.height,
        radius: rand.nextDouble() * 1.2 + 0.3, // 0.3 – 1.5
        baseAlpha: rand.nextDouble() * 0.5 + 0.1, // 0.1 – 0.6
        speed: rand.nextDouble() * 0.8 + 0.2, // drift speed multiplier
        angle: rand.nextDouble() * 2 * pi, // drift direction
        twinkleRate: rand.nextDouble() * 2.0 + 0.5, // twinkle frequency
        phase: rand.nextDouble() * 2 * pi, // twinkle phase offset
      );
    });
  }

  @override
  bool shouldRepaint(covariant _StarFieldPainter old) =>
      old.progress != progress;
}

class _Star {
  final double x, y;
  final double radius;
  final double baseAlpha;
  final double speed;
  final double angle;
  final double twinkleRate;
  final double phase;

  _Star({
    required this.x,
    required this.y,
    required this.radius,
    required this.baseAlpha,
    required this.speed,
    required this.angle,
    required this.twinkleRate,
    required this.phase,
  });
}
