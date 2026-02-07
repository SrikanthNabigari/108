import 'package:flutter/material.dart';
import 'dart:math';

/// Animated starfield background widget with parallax effect.
class StarBackground extends StatefulWidget {
  final Widget child;
  final int starCount;

  const StarBackground({
    Key? key,
    required this.child,
    this.starCount = 50,
  }) : super(key: key);

  @override
  State<StarBackground> createState() => _StarBackgroundState();
}

class _StarBackgroundState extends State<StarBackground>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  final List<_Star> stars = [];
  final Random _random = Random();

  @override
  void initState() {
    super.initState();
    _initializeStars();
    _animationController = AnimationController(
      duration: const Duration(seconds: 20),
      vsync: this,
    )..repeat();
  }

  void _initializeStars() {
    for (int i = 0; i < widget.starCount; i++) {
      stars.add(_Star(
        x: _random.nextDouble(),
        y: _random.nextDouble(),
        size: _random.nextDouble() * 2 + 0.5,
        opacity: _random.nextDouble() * 0.7 + 0.3,
        duration: Duration(milliseconds: 2000 + _random.nextInt(3000)),
      ));
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Container(color: Colors.black),
        AnimatedBuilder(
          animation: _animationController,
          builder: (context, _) {
            return CustomPaint(
              painter: _StarFieldPainter(stars, _animationController.value),
              size: Size.infinite,
            );
          },
        ),
        widget.child,
      ],
    );
  }
}

class _Star {
  final double x;
  final double y;
  final double size;
  final double opacity;
  final Duration duration;

  _Star({
    required this.x,
    required this.y,
    required this.size,
    required this.opacity,
    required this.duration,
  });
}

class _StarFieldPainter extends CustomPainter {
  final List<_Star> stars;
  final double animationValue;

  _StarFieldPainter(this.stars, this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;

    for (final star in stars) {
      // Twinkle effect using sine wave
      final tweenProgress = (animationValue * 2 * pi) % (2 * pi);
      final twinkle = (sin(tweenProgress) + 1) / 2;
      final finalOpacity = star.opacity * (0.3 + twinkle * 0.7);

      paint.color = Colors.white.withOpacity(finalOpacity);

      // Subtle drift animation
      final driftY = sin(animationValue * 2 * pi + star.y) * 2;

      canvas.drawCircle(
        Offset(star.x * size.width, star.y * size.height + driftY),
        star.size,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(_StarFieldPainter oldDelegate) => true;
}
