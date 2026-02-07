import 'package:freezed_annotation/freezed_annotation.dart';

part 'forecast_model.freezed.dart';
part 'forecast_model.g.dart';

@freezed
class AreaRating with _$AreaRating {
  const factory AreaRating({
    required String area, // 'career', 'finance', 'health', 'relationships', 'spiritual'
    required double score, // 0-10
    String? trend, // 'up', 'down', 'neutral'
  }) = _AreaRating;

  factory AreaRating.fromJson(Map<String, dynamic> json) =>
      _$AreaRatingFromJson(json);
}

@freezed
class PanchangaData with _$PanchangaData {
  const factory PanchangaData({
    String? tithi,
    String? nakshatra,
    String? yoga,
    String? karana,
    String? vara,
  }) = _PanchangaData;

  factory PanchangaData.fromJson(Map<String, dynamic> json) =>
      _$PanchangaDataFromJson(json);
}

@freezed
class ForecastModel with _$ForecastModel {
  const factory ForecastModel({
    required String forecastType, // 'daily', 'weekly', 'monthly', 'yearly'
    required DateTime date,
    required double dayRating, // 0-10
    required Map<String, AreaRating> areaRatings,
    required List<String> recommendations,
    required Map<String, dynamic> details,
    PanchangaData? panchanga,
  }) = _ForecastModel;

  factory ForecastModel.fromJson(Map<String, dynamic> json) =>
      _$ForecastModelFromJson(json);
}
