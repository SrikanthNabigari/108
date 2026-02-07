import 'package:freezed_annotation/freezed_annotation.dart';

part 'birth_chart_model.freezed.dart';
part 'birth_chart_model.g.dart';

@freezed
class PlanetPosition with _$PlanetPosition {
  const factory PlanetPosition({
    required String planet,
    required double longitude,
    required String sign,
    required int house,
    required String nakshatra,
    @Default(0) int nakshatraPada,
    @Default(0) double nakshatraDegree,
    @Default(false) bool isRetrograde,
    @Default(0) double latitude,
  }) = _PlanetPosition;

  factory PlanetPosition.fromJson(Map<String, dynamic> json) =>
      _$PlanetPositionFromJson(json);
}

@freezed
class BirthChartModel with _$BirthChartModel {
  const factory BirthChartModel({
    required String userId,
    required double ascendantLongitude,
    required String ascendantSign,
    required String ascendantNakshatra,
    required List<PlanetPosition> planets,
    required Map<int, double> houseCusps,
    required String moonRashi,
    required String moonNakshatra,
    @Default('lahiri') String ayanamsa,
  }) = _BirthChartModel;

  factory BirthChartModel.fromJson(Map<String, dynamic> json) =>
      _$BirthChartModelFromJson(json);
}
