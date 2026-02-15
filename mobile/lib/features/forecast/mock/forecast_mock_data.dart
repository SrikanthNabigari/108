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
      'Wednesday favors: Education, Business, Writing.',
      'Avoid on Wednesday: Buying iron, Giving away green items.',
      'Shukla Saptami: Good for Travel, Buying vehicles, Starting journeys.',
      'Moon in Pushya: Long-term bonds, Spiritual practice.',
      'Dasha focus: Communication and intellectual pursuits thrive.',
    ],
    details: {
      'mental_state': 'Flowing',
      'composite_score': 7.3,
      'summary': 'Moon in Pushya (Aquarius, house 5): Emotional nourishment '
          'and discipline. Mercury-Ketu period sharpens intuition and '
          'spiritual inquiry.',
      'hora_lord': 'mercury',
      'is_chandrashtama': false,
      'gochara_summary': [
        {'planet': 'jupiter', 'sign': 'taurus', 'house_from_moon': 4, 'is_favorable': false, 'has_vedha': false, 'net_effect': 'unfavorable'},
        {'planet': 'saturn', 'sign': 'pisces', 'house_from_moon': 2, 'is_favorable': false, 'has_vedha': false, 'net_effect': 'unfavorable'},
        {'planet': 'mars', 'sign': 'cancer', 'house_from_moon': 6, 'is_favorable': true, 'has_vedha': false, 'net_effect': 'favorable'},
        {'planet': 'venus', 'sign': 'pisces', 'house_from_moon': 2, 'is_favorable': true, 'has_vedha': false, 'net_effect': 'favorable'},
        {'planet': 'mercury', 'sign': 'aquarius', 'house_from_moon': 1, 'is_favorable': false, 'has_vedha': false, 'net_effect': 'unfavorable'},
        {'planet': 'sun', 'sign': 'aquarius', 'house_from_moon': 1, 'is_favorable': false, 'has_vedha': false, 'net_effect': 'unfavorable'},
        {'planet': 'rahu', 'sign': 'pisces', 'house_from_moon': 2, 'is_favorable': false, 'has_vedha': false, 'net_effect': 'unfavorable'},
        {'planet': 'ketu', 'sign': 'virgo', 'house_from_moon': 8, 'is_favorable': false, 'has_vedha': false, 'net_effect': 'unfavorable'},
      ],
      'active_yogas': ['Gaja Kesari', 'Budha-Aditya'],
      'active_doshas': ['Kaal Sarp'],
      'sade_sati': {'active': false, 'phase': null},
      'upcoming_triggers': [
        {'trigger': 'Venus enters Aries', 'days_from_now': 2, 'type': 'sign_ingress'},
        {'trigger': 'Mars trine natal Jupiter', 'days_from_now': 3, 'type': 'aspect'},
      ],
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
      'This period supports: Spiritual awakening through knowledge.',
      'Career: Communication and intellectual pursuits thrive.',
      'Invest in education and skill development.',
      'Saturn trine natal Sun: Positive structural support.',
    ],
    details: {
      'mental_state': 'Steady',
      'summary': 'Mercury-Ketu dasha emphasizes intuition and spiritual inquiry. '
          'Strongest area: Relationships (8/10). '
          'Needs attention: Finance (6/10).',
      'daily_ratings': [6.2, 5.8, 7.5, 7.9, 7.1, 6.5, 6.8],
      'daily_labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      'gochara_overview': {
        'favorable_count': 3,
        'unfavorable_count': 5,
        'planets': [
          {'planet': 'mars', 'dominant_effect': 'favorable', 'favorable_days': 7, 'total_days': 7},
          {'planet': 'venus', 'dominant_effect': 'favorable', 'favorable_days': 5, 'total_days': 7},
          {'planet': 'jupiter', 'dominant_effect': 'unfavorable', 'favorable_days': 0, 'total_days': 7},
          {'planet': 'saturn', 'dominant_effect': 'unfavorable', 'favorable_days': 0, 'total_days': 7},
        ],
      },
      'active_yogas': ['Gaja Kesari', 'Budha-Aditya'],
      'active_doshas': ['Kaal Sarp'],
      'chandrashtama_days': ['2026-02-11'],
      'sade_sati': {'active': false, 'phase': null},
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
      'Invest in education and skill development.',
      'Start or expand a business venture.',
      'House 10: Major promotion or career milestone ahead.',
      'House 7: Favorable for partnerships and contracts.',
    ],
    details: {
      'mental_state': 'Steady',
      'summary': 'Mercury Mahadasha: Intelligence, communication, education. '
          'Jupiter-Saturn activate houses 10 and 7 — career and partnership '
          'themes prominent. Strongest: Spiritual. Needs care: Travel.',
      'best_area': 'spiritual',
      'weakest_area': 'travel',
      'gochara_summary': [
        {'planet': 'jupiter', 'sign': 'taurus', 'house_from_moon': 4, 'net_effect': 'unfavorable'},
        {'planet': 'saturn', 'sign': 'pisces', 'house_from_moon': 2, 'net_effect': 'unfavorable'},
        {'planet': 'mars', 'sign': 'cancer', 'house_from_moon': 6, 'net_effect': 'favorable'},
        {'planet': 'venus', 'sign': 'pisces', 'house_from_moon': 2, 'net_effect': 'favorable'},
      ],
      'active_yogas': ['Gaja Kesari', 'Budha-Aditya', 'Chandra-Mangal'],
      'active_doshas': ['Kaal Sarp'],
      'sade_sati': {'active': false, 'phase': null},
      'muhurta_dates': [
        {'date': '2026-02-04', 'abhijit_start': '11:48', 'abhijit_end': '12:36'},
        {'date': '2026-02-11', 'abhijit_start': '11:48', 'abhijit_end': '12:36'},
        {'date': '2026-02-18', 'abhijit_start': '11:47', 'abhijit_end': '12:36'},
        {'date': '2026-02-25', 'abhijit_start': '11:46', 'abhijit_end': '12:35'},
      ],
    },
  );
}
