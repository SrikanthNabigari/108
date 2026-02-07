import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/models/birth_chart_model.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

part 'chart_provider.g.dart';

/// Get full birth chart from /api/v1/chart/full
@riverpod
Future<BirthChartModel> birthChart(BirthChartRef ref) async {
  final response = await ApiService().get(
    ApiConstants.chartFull,
    fromJson: (json) => BirthChartModel.fromJson(json),
  );
  return response;
}

/// Get chart summary (lightweight version)
@riverpod
Future<BirthChartModel> chartSummary(ChartSummaryRef ref) async {
  final response = await ApiService().get(
    ApiConstants.chartSummary,
    fromJson: (json) => BirthChartModel.fromJson(json),
  );
  return response;
}

/// Get divisional chart (D2-D60)
@riverpod
Future<BirthChartModel> divisionalChart(DivisionalChartRef ref, String d) async {
  final response = await ApiService().get(
    ApiConstants.chartDivisional(d),
    fromJson: (json) => BirthChartModel.fromJson(json),
  );
  return response;
}

/// Get D9 (Navamsha) chart
@riverpod
Future<BirthChartModel> d9Chart(D9ChartRef ref) async {
  return ref.watch(divisionalChartProvider('D9').future);
}

/// Get D10 (Dasamsha) chart
@riverpod
Future<BirthChartModel> d10Chart(D10ChartRef ref) async {
  return ref.watch(divisionalChartProvider('D10').future);
}

/// Refresh birth chart data
@riverpod
class RefreshBirthChart extends _$RefreshBirthChart {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call() async {
    ref.invalidate(birthChartProvider);
    ref.invalidate(chartSummaryProvider);
  }
}
