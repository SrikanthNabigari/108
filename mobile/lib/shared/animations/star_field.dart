import 'dart:math';

/// Star field animation controller for background effects.
class StarFieldAnimation {
  final Random _random;
  final List<StarParticle> particles;
  double _time = 0;

  StarFieldAnimation({int particleCount = 50})
      : _random = Random(),
        particles = [] {
    _generateStars(particleCount);
  }

  void _generateStars(int count) {
    particles.clear();
    for (int i = 0; i < count; i++) {
      particles.add(
        StarParticle(
          x: _random.nextDouble(),
          y: _random.nextDouble(),
          size: _random.nextDouble() * 2 + 0.5,
          baseOpacity: _random.nextDouble() * 0.7 + 0.3,
          twinklePeriod: 2000 + _random.nextInt(3000),
          driftSpeed: _random.nextDouble() * 0.002,
        ),
      );
    }
  }

  void update(double deltaTime) {
    _time += deltaTime;
    for (final particle in particles) {
      particle.update(_time);
    }
  }

  void reset() {
    _time = 0;
  }
}

class StarParticle {
  final double x;
  final double y;
  final double size;
  final double baseOpacity;
  final int twinklePeriod;
  final double driftSpeed;

  double get currentOpacity {
    final twinklePhase = (_time % twinklePeriod) / twinklePeriod * 2 * pi;
    final twinkle = (sin(twinklePhase) + 1) / 2;
    return baseOpacity * (0.3 + twinkle * 0.7);
  }

  double get driftY => sin(_time * 0.001 + y) * 2;

  double _time = 0;

  StarParticle({
    required this.x,
    required this.y,
    required this.size,
    required this.baseOpacity,
    required this.twinklePeriod,
    required this.driftSpeed,
  });

  void update(double time) {
    _time = time;
  }
}
