import 'package:freezed_annotation/freezed_annotation.dart';

part 'dosha_model.freezed.dart';
part 'dosha_model.g.dart';

@freezed
class CancellationCondition with _$CancellationCondition {
  const factory CancellationCondition({
    required String description,
    required bool isMet,
  }) = _CancellationCondition;

  factory CancellationCondition.fromJson(Map<String, dynamic> json) =>
      _$CancellationConditionFromJson(json);
}

@freezed
class DoshaModel with _$DoshaModel {
  const factory DoshaModel({
    required String name,
    required String severity,
    required List<String> planets,
    required List<String> effects,
    required List<CancellationCondition> cancellationConditions,
    required List<String> remedies,
    @Default(true) bool isActive,
  }) = _DoshaModel;

  factory DoshaModel.fromJson(Map<String, dynamic> json) =>
      _$DoshaModelFromJson(json);
}
