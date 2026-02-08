import 'package:freezed_annotation/freezed_annotation.dart';

part 'compatibility_model.freezed.dart';
part 'compatibility_model.g.dart';

@freezed
class KutaScore with _$KutaScore {
  const factory KutaScore({
    required String name,
    required double obtained,
    required double maximum,
    String? description,
  }) = _KutaScore;

  factory KutaScore.fromJson(Map<String, dynamic> json) =>
      _$KutaScoreFromJson(json);
}

@freezed
class CompatibilityModel with _$CompatibilityModel {
  const factory CompatibilityModel({
    required List<KutaScore> kutaScores,
    required double totalObtained,
    required double totalMaximum,
    required String verdict,
    String? summary,
  }) = _CompatibilityModel;

  factory CompatibilityModel.fromJson(Map<String, dynamic> json) =>
      _$CompatibilityModelFromJson(json);
}
