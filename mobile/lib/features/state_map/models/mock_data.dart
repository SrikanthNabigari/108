import 'dart:math';
import 'state_vector.dart';

/// Generates realistic-looking mock state vectors until the backend
/// endpoints are ready. Uses planetary cycle patterns to create
/// plausible-looking data rather than pure random noise.

class MockStateData {
  static final _rng = Random(42); // fixed seed for consistency

  /// Generate vectors for a date range at the given resolution.
  static StateMapData generate({
    required DateTime start,
    required DateTime end,
    String resolution = 'daily',
  }) {
    final vectors = <StateVector>[];
    final step = _stepForResolution(resolution);
    var current = start;

    while (current.isBefore(end) || current.isAtSameMomentAs(end)) {
      vectors.add(_vectorForDate(current));
      current = current.add(step);
    }

    return StateMapData(
      vectors: vectors,
      events: _sampleEvents(start, end),
      resolution: resolution,
    );
  }

  /// Single "now" vector.
  static StateVector now() => _vectorForDate(DateTime.now());

  // ── Internal ──

  static Duration _stepForResolution(String res) {
    switch (res) {
      case 'hourly':
        return const Duration(hours: 1);
      case 'weekly':
        return const Duration(days: 7);
      case 'monthly':
        return const Duration(days: 30);
      default:
        return const Duration(days: 1);
    }
  }

  static StateVector _vectorForDate(DateTime dt) {
    // Use day-of-year as seed offset for deterministic but varied data
    final dayOffset = dt.difference(DateTime(dt.year, 1, 1)).inDays;
    final hourOffset = dt.hour;

    // Simulate slow-moving factors (dasha) with long-period sine
    final dashaWave = (sin(dayOffset / 120 * 2 * pi) + 1) / 2; // 120-day cycle
    // Medium cycle for transits
    final transitWave =
        (sin(dayOffset / 27.3 * 2 * pi) + 1) / 2; // lunar month
    // Fast cycle for panchanga (daily tithi)
    final panchaWave = (sin(dayOffset / 15 * 2 * pi) + 1) / 2; // half-month
    // Hourly hora variation
    final horaWave =
        (sin(hourOffset / 24 * 2 * pi + dayOffset) + 1) / 2;

    final factors = <FactorScore>[
      FactorScore(
        id: 'panchanga',
        name: 'Panchanga',
        shortName: 'PAN',
        score: _clamp(3 + panchaWave * 6 + _noise(0.8)),
        dominantPlanet: _horaLordForDay(dt.weekday),
        description: 'Tithi, Vara, Yoga, Karana quality',
      ),
      FactorScore(
        id: 'transit_moon',
        name: 'Transit Moon',
        shortName: 'MON',
        score: _clamp(2.5 + transitWave * 6.5 + _noise(1.0)),
        dominantPlanet: 'moon',
        description: 'Moon nakshatra & Ashtakavarga bindus',
      ),
      FactorScore(
        id: 'gochara',
        name: 'Gochara',
        shortName: 'GOC',
        score: _clamp(4 + transitWave * 4 + _noise(0.6)),
        dominantPlanet: _slowPlanetForDay(dayOffset),
        description: 'Favorable vs unfavorable transits from Moon',
      ),
      FactorScore(
        id: 'dasha',
        name: 'Dasha',
        shortName: 'DSH',
        score: _clamp(5 + dashaWave * 4 + _noise(0.3)),
        dominantPlanet: 'mercury', // would come from actual dasha
        description: 'MD-AD-PD lord nature & dignity',
      ),
      FactorScore(
        id: 'yoga_activation',
        name: 'Yoga',
        shortName: 'YOG',
        score: _clamp(3.5 + dashaWave * 3 + transitWave * 2.5 + _noise(0.5)),
        dominantPlanet: 'jupiter',
        description: 'Natal yogas activated by current transits',
      ),
      FactorScore(
        id: 'shadbala',
        name: 'Shadbala',
        shortName: 'SHD',
        score: _clamp(4 + horaWave * 3 + dashaWave * 2 + _noise(0.4)),
        dominantPlanet: _horaLordForDay(dt.weekday),
        description: 'Six-fold strength of dominant planet',
      ),
      FactorScore(
        id: 'ashtakavarga',
        name: 'Ashtakavarga',
        shortName: 'ASH',
        score: _clamp(3 + transitWave * 5 + _noise(0.7)),
        dominantPlanet: 'saturn',
        description: 'SAV score for current transit sign',
      ),
    ];

    final composite =
        factors.fold(0.0, (sum, f) => sum + f.score) / factors.length;

    final areas = <AreaScore>[
      AreaScore(
        id: 'career',
        name: 'Career',
        score:
            _clamp(composite + _noise(1.5) + (dashaWave > 0.6 ? 1.0 : -0.5)),
        houses: const [10, 6, 2],
        insight: dashaWave > 0.6
            ? 'Strong period for professional growth'
            : 'Patience needed at work',
        dominantPlanet: 'saturn',
      ),
      AreaScore(
        id: 'relationships',
        name: 'Love',
        score:
            _clamp(composite + _noise(1.2) + (transitWave > 0.5 ? 1.2 : -0.8)),
        houses: const [7, 5, 11],
        insight: transitWave > 0.5
            ? 'Harmonious connections ahead'
            : 'Reflect on relationship needs',
        dominantPlanet: 'venus',
      ),
      AreaScore(
        id: 'health',
        name: 'Health',
        score:
            _clamp(composite + _noise(1.0) + (panchaWave > 0.4 ? 0.8 : -0.5)),
        houses: const [1, 6, 8],
        insight:
            panchaWave > 0.4 ? 'Good vitality' : 'Rest and recover',
        dominantPlanet: 'sun',
      ),
      AreaScore(
        id: 'finance',
        name: 'Money',
        score:
            _clamp(composite + _noise(1.3) + (dashaWave > 0.5 ? 0.5 : -0.3)),
        houses: const [2, 11, 5],
        insight:
            dashaWave > 0.5 ? 'Gains possible' : 'Avoid risky investments',
        dominantPlanet: 'jupiter',
      ),
      AreaScore(
        id: 'spiritual',
        name: 'Spirit',
        score:
            _clamp(composite + _noise(0.8) + (horaWave > 0.5 ? 1.5 : 0)),
        houses: const [9, 12, 5],
        insight: horaWave > 0.5
            ? 'Inner clarity and insight'
            : 'Steady contemplation',
        dominantPlanet: 'ketu',
      ),
      AreaScore(
        id: 'family',
        name: 'Family',
        score:
            _clamp(composite + _noise(1.0) + (transitWave > 0.4 ? 0.8 : -0.4)),
        houses: const [4, 2, 1],
        insight: transitWave > 0.4
            ? 'Harmonious home environment'
            : 'Family matters need attention',
        dominantPlanet: 'moon',
        doubleTransit: transitWave > 0.7 && dashaWave > 0.6,
        activeYogas: transitWave > 0.6 ? const ['Gajakesari'] : const [],
        lordshipQuality: transitWave > 0.5 ? 'benefic' : 'neutral',
      ),
      AreaScore(
        id: 'education',
        name: 'Education',
        score:
            _clamp(composite + _noise(0.9) + (dashaWave > 0.4 ? 0.7 : -0.3)),
        houses: const [4, 5, 9],
        insight: dashaWave > 0.4
            ? 'Good period for learning'
            : 'Focus on revision over new topics',
        dominantPlanet: 'mercury',
      ),
      AreaScore(
        id: 'travel',
        name: 'Travel',
        score:
            _clamp(composite + _noise(1.1) + (horaWave > 0.6 ? 1.2 : -0.6)),
        houses: const [3, 9, 12],
        insight: horaWave > 0.6
            ? 'Favorable for journeys'
            : 'Postpone long-distance travel',
        dominantPlanet: 'rahu',
      ),
    ];

    // Confluence: how many factors agree (above or below 5)
    final aboveCount = factors.where((f) => f.score >= 5).length;
    final belowCount = factors.where((f) => f.score < 5).length;
    final agreement = max(aboveCount, belowCount);
    final confluence = (agreement / factors.length * 6).clamp(0.0, 6.0);

    // Mental state from composite
    final mentalState = _mentalStateFromScore(composite);

    return StateVector(
      date: dt,
      factors: factors,
      areas: areas,
      composite: double.parse(composite.toStringAsFixed(1)),
      mentalState: mentalState,
      confluence: double.parse(confluence.toStringAsFixed(1)),
      horaLord: _horaLordForDay(dt.weekday),
    );
  }

  static double _clamp(double v) => v.clamp(0.0, 10.0);
  static double _noise(double amplitude) =>
      (_rng.nextDouble() - 0.5) * 2 * amplitude;

  static String _horaLordForDay(int weekday) {
    // Classical: Sun Mon Tue Wed Thu Fri Sat → day lord
    const lords = [
      'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'sun'
    ];
    return lords[(weekday - 1) % 7];
  }

  static String _slowPlanetForDay(int dayOffset) {
    const slow = ['saturn', 'jupiter', 'rahu'];
    return slow[dayOffset % slow.length];
  }

  static String _mentalStateFromScore(double score) {
    if (score >= 8) return 'Thriving';
    if (score >= 6.5) return 'Flowing';
    if (score >= 5) return 'Steady';
    if (score >= 3.5) return 'Challenged';
    if (score >= 2) return 'Struggling';
    return 'Turbulent';
  }

  static List<LifeEvent> _sampleEvents(DateTime start, DateTime end) {
    final days = end.difference(start).inDays;
    if (days < 7) return [];
    // Sprinkle a few sample events
    return [
      LifeEvent(
        date: start.add(Duration(days: (days * 0.2).round())),
        type: 'career',
        description: 'Important meeting',
        actualRating: 7,
      ),
      LifeEvent(
        date: start.add(Duration(days: (days * 0.5).round())),
        type: 'health',
        description: 'Felt low energy',
        actualRating: 4,
      ),
      LifeEvent(
        date: start.add(Duration(days: (days * 0.8).round())),
        type: 'spiritual',
        description: 'Deep meditation session',
        actualRating: 9,
      ),
    ];
  }
}
