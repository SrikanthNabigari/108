import 'package:one_zero_eight/data/models/forecast_model.dart';

/// Static mock data for Forecast screens when API is unavailable.
class ForecastMockData {
  ForecastMockData._();

  static final daily = ForecastModel(
    forecastType: 'daily',
    date: DateTime.now(),
    dayRating: 7.3,
    areaRatings: {
      'career': const AreaRating(area: 'career', score: 7.8, trend: 'up'),
      'relationships': const AreaRating(area: 'relationships', score: 6.5, trend: 'neutral'),
      'health': const AreaRating(area: 'health', score: 8.1, trend: 'up'),
      'finance': const AreaRating(area: 'finance', score: 5.9, trend: 'down'),
      'spiritual': const AreaRating(area: 'spiritual', score: 7.0, trend: 'up'),
      'family': const AreaRating(area: 'family', score: 6.8, trend: 'neutral'),
      'education': const AreaRating(area: 'education', score: 7.5, trend: 'up'),
      'travel': const AreaRating(area: 'travel', score: 4.2, trend: 'down'),
    },
    recommendations: [
      'Mercury hora (9-10 AM) is ideal for important communications.',
      'Avoid major financial decisions after 4 PM today.',
      'Good day for learning and skill development.',
      'Evening meditation will be especially effective.',
    ],
    details: {
      'mental_state': 'Flowing',
      'summary': 'A productive day with strong intellectual energy. '
          'Mercury-Jupiter alignment supports career growth and learning. '
          'Be mindful of impulsive spending.',
    },
    panchanga: const PanchangaData(
      tithi: 'Shukla Saptami',
      nakshatra: 'Pushya',
      yoga: 'Siddha',
      karana: 'Balava',
      vara: 'Budhavara',
    ),
  );

  static final weekly = ForecastModel(
    forecastType: 'weekly',
    date: DateTime.now(),
    dayRating: 6.8,
    areaRatings: {
      'career': const AreaRating(area: 'career', score: 7.2, trend: 'up'),
      'relationships': const AreaRating(area: 'relationships', score: 7.5, trend: 'up'),
      'health': const AreaRating(area: 'health', score: 6.0, trend: 'neutral'),
      'finance': const AreaRating(area: 'finance', score: 5.5, trend: 'down'),
      'spiritual': const AreaRating(area: 'spiritual', score: 8.0, trend: 'up'),
      'family': const AreaRating(area: 'family', score: 6.3, trend: 'neutral'),
      'education': const AreaRating(area: 'education', score: 7.1, trend: 'up'),
      'travel': const AreaRating(area: 'travel', score: 5.0, trend: 'neutral'),
    },
    recommendations: [
      'Best days for career moves: Wednesday and Thursday.',
      'Relationship energy peaks on Friday evening.',
      'Avoid travel on Tuesday due to Mars transit.',
      'Weekend ideal for spiritual practices and family time.',
    ],
    details: {
      'mental_state': 'Steady',
      'summary': 'A balanced week with gradual improvement. '
          'Mid-week brings the strongest professional energy. '
          'Weekend favors relationships and rest.',
      'daily_ratings': [6.2, 5.8, 7.5, 7.9, 7.1, 6.5, 6.8],
      'daily_labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    },
  );

  static final monthly = ForecastModel(
    forecastType: 'monthly',
    date: DateTime.now(),
    dayRating: 6.5,
    areaRatings: {
      'career': const AreaRating(area: 'career', score: 7.0, trend: 'up'),
      'relationships': const AreaRating(area: 'relationships', score: 6.8, trend: 'neutral'),
      'health': const AreaRating(area: 'health', score: 6.2, trend: 'down'),
      'finance': const AreaRating(area: 'finance', score: 7.5, trend: 'up'),
      'spiritual': const AreaRating(area: 'spiritual', score: 7.8, trend: 'up'),
      'family': const AreaRating(area: 'family', score: 6.5, trend: 'neutral'),
      'education': const AreaRating(area: 'education', score: 6.9, trend: 'up'),
      'travel': const AreaRating(area: 'travel', score: 5.5, trend: 'neutral'),
    },
    recommendations: [
      'Jupiter transit supports financial growth after the 15th.',
      'Health needs attention during first week — avoid overexertion.',
      'Best period for career negotiations: 10th to 20th.',
      'Spiritual retreats are highly favored this month.',
    ],
    details: {
      'mental_state': 'Steady',
      'summary': 'A month of gradual consolidation. '
          'Financial prospects improve in the second half. '
          'Focus on health and rest during the opening days.',
      'best_area': 'spiritual',
      'weakest_area': 'travel',
    },
  );
}
