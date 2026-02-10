/// Data models for the State Map — prediction engine output.
///
/// The State Vector captures seven astrological prediction factors
/// (0-10 each) plus five life-area scores, a composite rating,
/// and a confluence measure.

class FactorScore {
  final String id;
  final String name;
  final String shortName;
  final double score; // 0-10
  final String dominantPlanet;
  final String description;

  const FactorScore({
    required this.id,
    required this.name,
    required this.shortName,
    required this.score,
    this.dominantPlanet = '',
    this.description = '',
  });

  factory FactorScore.fromJson(Map<String, dynamic> json) => FactorScore(
        id: json['id'] as String? ?? '',
        name: json['name'] as String? ?? '',
        shortName: json['short_name'] as String? ?? '',
        score: (json['score'] as num?)?.toDouble() ?? 0,
        dominantPlanet: json['dominant_planet'] as String? ?? '',
        description: json['description'] as String? ?? '',
      );
}

class AreaScore {
  final String id;
  final String name;
  final double score; // 0-10
  final List<int> houses;
  final String insight;
  final String dominantPlanet;

  const AreaScore({
    required this.id,
    required this.name,
    required this.score,
    this.houses = const [],
    this.insight = '',
    this.dominantPlanet = '',
  });

  factory AreaScore.fromJson(Map<String, dynamic> json) => AreaScore(
        id: json['id'] as String? ?? '',
        name: json['name'] as String? ?? '',
        score: (json['score'] as num?)?.toDouble() ?? 0,
        houses: (json['houses'] as List?)?.cast<int>() ?? [],
        insight: json['insight'] as String? ?? '',
        dominantPlanet: json['dominant_planet'] as String? ?? '',
      );
}

class StateVector {
  final DateTime date;
  final List<FactorScore> factors;
  final List<AreaScore> areas;
  final double composite; // 0-10
  final String mentalState;
  final double confluence; // 0-6
  final String horaLord;

  const StateVector({
    required this.date,
    required this.factors,
    required this.areas,
    required this.composite,
    this.mentalState = '',
    this.confluence = 0,
    this.horaLord = '',
  });

  factory StateVector.fromJson(Map<String, dynamic> json) {
    return StateVector(
      date: DateTime.tryParse(json['date'] as String? ?? '') ?? DateTime.now(),
      factors: (json['factors'] as List?)
              ?.map((f) => FactorScore.fromJson(f as Map<String, dynamic>))
              .toList() ??
          [],
      areas: (json['areas'] as List?)
              ?.map((a) => AreaScore.fromJson(a as Map<String, dynamic>))
              .toList() ??
          [],
      composite: (json['composite'] as num?)?.toDouble() ?? 0,
      mentalState: json['mental_state'] as String? ?? '',
      confluence: (json['confluence'] as num?)?.toDouble() ?? 0,
      horaLord: json['hora_lord'] as String? ?? '',
    );
  }
}

class LifeEvent {
  final String? id;
  final DateTime date;
  final String type; // career, relationship, health, finance, spiritual
  final String description;
  final double? actualRating; // user's subjective 1-10

  const LifeEvent({
    this.id,
    required this.date,
    required this.type,
    required this.description,
    this.actualRating,
  });

  factory LifeEvent.fromJson(Map<String, dynamic> json) => LifeEvent(
        id: json['id'] as String?,
        date:
            DateTime.tryParse(json['date'] as String? ?? '') ?? DateTime.now(),
        type: json['type'] as String? ?? 'career',
        description: json['description'] as String? ?? '',
        actualRating: (json['actual_rating'] as num?)?.toDouble(),
      );

  Map<String, dynamic> toJson() => {
        'date': date.toIso8601String().split('T').first,
        'type': type,
        'description': description,
        if (actualRating != null) 'actual_rating': actualRating,
      };
}

/// Batch response from range endpoint.
class StateMapData {
  final List<StateVector> vectors;
  final List<LifeEvent> events;
  final String resolution; // hourly, daily, weekly, monthly

  const StateMapData({
    required this.vectors,
    this.events = const [],
    this.resolution = 'daily',
  });

  factory StateMapData.fromJson(Map<String, dynamic> json) => StateMapData(
        vectors: (json['vectors'] as List?)
                ?.map((v) => StateVector.fromJson(v as Map<String, dynamic>))
                .toList() ??
            [],
        events: (json['events'] as List?)
                ?.map((e) => LifeEvent.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
        resolution: json['resolution'] as String? ?? 'daily',
      );
}

// ── Factor & area identifiers (stable) ──

const kFactorIds = [
  'panchanga',
  'transit_moon',
  'gochara',
  'dasha',
  'yoga_activation',
  'shadbala',
  'ashtakavarga',
];

const kFactorNames = {
  'panchanga': 'Panchanga',
  'transit_moon': 'Transit Moon',
  'gochara': 'Gochara',
  'dasha': 'Dasha',
  'yoga_activation': 'Yoga',
  'shadbala': 'Shadbala',
  'ashtakavarga': 'Ashtakavarga',
};

const kFactorShortNames = {
  'panchanga': 'PAN',
  'transit_moon': 'MON',
  'gochara': 'GOC',
  'dasha': 'DSH',
  'yoga_activation': 'YOG',
  'shadbala': 'SHD',
  'ashtakavarga': 'ASH',
};

const kAreaIds = ['career', 'relationships', 'health', 'finance', 'spiritual'];

const kAreaNames = {
  'career': 'Career',
  'relationships': 'Love',
  'health': 'Health',
  'finance': 'Money',
  'spiritual': 'Spirit',
};

const kAreaIcons = {
  'career': '💼',
  'relationships': '❤️',
  'health': '🏥',
  'finance': '💰',
  'spiritual': '🕉️',
};

const kEventTypes = [
  'career',
  'relationship',
  'health',
  'finance',
  'spiritual',
  'travel',
  'education',
  'loss',
];
