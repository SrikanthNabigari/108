import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/models/forecast_model.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

part 'forecast_provider.g.dart';

/// Get daily forecast
@riverpod
Future<ForecastModel> dailyForecast(DailyForecastRef ref, [DateTime? date]) async {
  final queryDate = date ?? DateTime.now();
  final response = await ApiService().get(
    '${ApiConstants.forecastDaily}?date=${queryDate.toIso8601String()}',
    fromJson: (json) => ForecastModel.fromJson(json),
  );
  return response;
}

/// Get weekly forecast
@riverpod
Future<ForecastModel> weeklyForecast(WeeklyForecastRef ref, [DateTime? startDate]) async {
  final queryDate = startDate ?? DateTime.now();
  final response = await ApiService().get(
    '${ApiConstants.forecastWeekly}?start_date=${queryDate.toIso8601String()}',
    fromJson: (json) => ForecastModel.fromJson(json),
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
    fromJson: (json) => ForecastModel.fromJson(json),
  );
  return response;
}

/// Get yearly forecast
@riverpod
Future<ForecastModel> yearlyForecast(YearlyForecastRef ref, [DateTime? startDate]) async {
  final queryDate = startDate ?? DateTime.now();
  final response = await ApiService().get(
    '${ApiConstants.forecastYearly}?start_date=${queryDate.toIso8601String()}',
    fromJson: (json) => ForecastModel.fromJson(json),
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
