import 'package:freezed_annotation/freezed_annotation.dart';

part 'transit_model.freezed.dart';
part 'transit_model.g.dart';

@freezed
class PlanetTransit with _$PlanetTransit {
  const factory PlanetTransit({
    required String planet,
    required String sign,
    required int house,
    required double degree,
    required String nakshatra,
    @Default(false) bool isRetrograde,
    String? enteredDate,
    String? exitsDate,
  }) = _PlanetTransit;

  factory PlanetTransit.fromJson(Map<String, dynamic> json) =>
      _$PlanetTransitFromJson(json);
}

@freezed
class GocharaResult with _$GocharaResult {
  const factory GocharaResult({
    required String planet,
    required int houseFromMoon,
    required bool isFavorable,
    required String description,
  }) = _GocharaResult;

  factory GocharaResult.fromJson(Map<String, dynamic> json) =>
      _$GocharaResultFromJson(json);
}

@freezed
class TransitModel with _$TransitModel {
  const factory TransitModel({
    required List<PlanetTransit> transits,
    required List<GocharaResult> gochara,
    @Default(false) bool isSadeSatiActive,
    String? sadeSatiPhase,
  }) = _TransitModel;

  factory TransitModel.fromJson(Map<String, dynamic> json) =>
      _$TransitModelFromJson(json);
}
