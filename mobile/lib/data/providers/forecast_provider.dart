import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/models/forecast_model.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

part 'forecast_provider.g.dart';

// ====================================================================
// Raw API → ForecastModel mappers (backend returns snake_case)
// ====================================================================

/// Map raw daily forecast API response to ForecastModel.
ForecastModel _mapDailyResponse(Map<String, dynamic> json) {
  // Area scores → AreaRating map
  final rawAreas = json['area_scores'] as Map<String, dynamic>? ?? {};
  final areaRatings = <String, AreaRating>{};
  for (final entry in rawAreas.entries) {
    final data = entry.value;
    if (data is Map<String, dynamic>) {
      areaRatings[entry.key] = AreaRating(
        area: entry.key,
        score: (data['score'] as num?)?.toDouble() ?? 5.0,
        trend: data['trend'] as String?,
      );
    }
  }

  // Panchanga
  PanchangaData? panchanga;
  final rawPan = json['panchanga'] as Map<String, dynamic>?;
  if (rawPan != null) {
    panchanga = PanchangaData(
      tithi: rawPan['tithi'] as String?,
      nakshatra: rawPan['nakshatra'] as String?,
      yoga: rawPan['yoga'] as String?,
      karana: rawPan['karana'] as String?,
      vara: rawPan['vara'] as String?,
    );
  }

  // Recommendations
  final recs = (json['recommendations'] as List?)
      ?.map((e) => e.toString()).toList() ?? [];

  // Everything else goes into details (the catch-all)
  final details = Map<String, dynamic>.from(json);

  return ForecastModel(
    forecastType: 'daily',
    date: DateTime.tryParse(json['date'] as String? ?? '') ?? DateTime.now(),
    dayRating: (json['day_rating'] as num?)?.toDouble() ?? 5.0,
    areaRatings: areaRatings,
    recommendations: recs,
    details: details,
    panchanga: panchanga,
  );
}

/// Map raw weekly forecast API response to ForecastModel.
ForecastModel _mapWeeklyResponse(Map<String, dynamic> json) {
  final rawAreas = json['areas'] as Map<String, dynamic>? ?? {};
  final areaRatings = <String, AreaRating>{};
  for (final entry in rawAreas.entries) {
    final data = entry.value;
    if (data is Map<String, dynamic>) {
      areaRatings[entry.key] = AreaRating(
        area: entry.key,
        score: (data['score'] as num?)?.toDouble() ??
            (data['rating'] as num?)?.toDouble() ?? 5.0,
        trend: data['trend'] as String?,
      );
    }
  }

  final recs = (json['recommendations'] as List?)
      ?.map((e) => e.toString()).toList() ?? [];

  return ForecastModel(
    forecastType: 'weekly',
    date: DateTime.tryParse(json['week_start'] as String? ?? '') ?? DateTime.now(),
    dayRating: (json['overall_rating'] as num?)?.toDouble() ?? 5.0,
    areaRatings: areaRatings,
    recommendations: recs,
    details: Map<String, dynamic>.from(json),
  );
}

/// Map raw monthly forecast API response to ForecastModel.
ForecastModel _mapMonthlyResponse(Map<String, dynamic> json) {
  final rawAreas = json['areas'] as Map<String, dynamic>? ?? {};
  final areaRatings = <String, AreaRating>{};
  for (final entry in rawAreas.entries) {
    final data = entry.value;
    if (data is Map<String, dynamic>) {
      areaRatings[entry.key] = AreaRating(
        area: entry.key,
        score: (data['score'] as num?)?.toDouble() ??
            (data['rating'] as num?)?.toDouble() ?? 5.0,
        trend: data['trend'] as String?,
      );
    }
  }

  final recs = (json['recommendations'] as List?)
      ?.map((e) => e.toString()).toList() ?? [];

  // Parse month/year into a date
  final year = json['year'] as int? ?? DateTime.now().year;
  final monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
  ];
  final monthStr = json['month'] as String? ?? '';
  final monthIdx = monthNames.indexOf(monthStr);
  final date = DateTime(year, monthIdx >= 0 ? monthIdx + 1 : DateTime.now().month);

  return ForecastModel(
    forecastType: 'monthly',
    date: date,
    dayRating: (json['overall_rating'] as num?)?.toDouble() ?? 5.0,
    areaRatings: areaRatings,
    recommendations: recs,
    details: Map<String, dynamic>.from(json),
  );
}

/// Map raw yearly forecast API response to ForecastModel.
ForecastModel _mapYearlyResponse(Map<String, dynamic> json) {
  final rawAreas = json['areas'] as Map<String, dynamic>? ?? {};
  final areaRatings = <String, AreaRating>{};
  for (final entry in rawAreas.entries) {
    final data = entry.value;
    if (data is Map<String, dynamic>) {
      areaRatings[entry.key] = AreaRating(
        area: entry.key,
        score: (data['score'] as num?)?.toDouble() ??
            (data['rating'] as num?)?.toDouble() ?? 5.0,
        trend: data['trend'] as String?,
      );
    }
  }

  final recs = (json['recommendations'] as List?)
      ?.map((e) => e.toString()).toList() ?? [];

  return ForecastModel(
    forecastType: 'yearly',
    date: DateTime(json['year'] as int? ?? DateTime.now().year),
    dayRating: (json['overall_rating'] as num?)?.toDouble() ?? 5.0,
    areaRatings: areaRatings,
    recommendations: recs,
    details: Map<String, dynamic>.from(json),
  );
}

// ====================================================================
// Riverpod providers
// ====================================================================

/// Get daily forecast
@riverpod
Future<ForecastModel> dailyForecast(DailyForecastRef ref, [DateTime? date]) async {
  final queryDate = date ?? DateTime.now();
  final response = await ApiService().get(
    '${ApiConstants.forecastDaily}?date=${queryDate.toIso8601String()}',
    fromJson: (json) => _mapDailyResponse(json as Map<String, dynamic>),
  );
  return response;
}

/// Get weekly forecast
@riverpod
Future<ForecastModel> weeklyForecast(WeeklyForecastRef ref, [DateTime? startDate]) async {
  final queryDate = startDate ?? DateTime.now();
  final response = await ApiService().get(
    '${ApiConstants.forecastWeekly}?start_date=${queryDate.toIso8601String()}',
    fromJson: (json) => _mapWeeklyResponse(json as Map<String, dynamic>),
  );
  return response;
}

/// Get monthly forecast
@riverpod
Future<ForecastModel> monthlyForecast(
  MonthlyForecastRef ref, [
  DateTime? startDate,
]) async {
  final queryDate = startDate ?? DateTime.now();
  final response = await ApiService().get(
    '${ApiConstants.forecastMonthly}?start_date=${queryDate.toIso8601String()}',
    fromJson: (json) => _mapMonthlyResponse(json as Map<String, dynamic>),
  );
  return response;
}

/// Get yearly forecast
@riverpod
Future<ForecastModel> yearlyForecast(YearlyForecastRef ref, [DateTime? startDate]) async {
  final queryDate = startDate ?? DateTime.now();
  final response = await ApiService().get(
    '${ApiConstants.forecastYearly}?start_date=${queryDate.toIso8601String()}',
    fromJson: (json) => _mapYearlyResponse(json as Map<String, dynamic>),
  );
  return response;
}

/// Refresh all forecasts
@riverpod
class RefreshForecasts extends _$RefreshForecasts {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call() async {
    ref.invalidate(dailyForecastProvider);
    ref.invalidate(weeklyForecastProvider);
    ref.invalidate(monthlyForecastProvider);
    ref.invalidate(yearlyForecastProvider);
  }
}
