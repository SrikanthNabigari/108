import 'package:freezed_annotation/freezed_annotation.dart';

part 'remedy_model.freezed.dart';
part 'remedy_model.g.dart';

@freezed
class MantraRemedy with _$MantraRemedy {
  const factory MantraRemedy({
    required String mantra,
    String? transliteration,
    required String repetitions,
    required String bestDay,
    required String bestTime,
    required String duration,
  }) = _MantraRemedy;

  factory MantraRemedy.fromJson(Map<String, dynamic> json) =>
      _$MantraRemedyFromJson(json);
}

@freezed
class GemstoneRemedy with _$GemstoneRemedy {
  const factory GemstoneRemedy({
    required String name,
    required String weight,
    required String metal,
    required String finger,
    required String wearingDay,
    required String wearingTime,
    String? caution,
  }) = _GemstoneRemedy;

  factory GemstoneRemedy.fromJson(Map<String, dynamic> json) =>
      _$GemstoneRemedyFromJson(json);
}

@freezed
class RemedyModel with _$RemedyModel {
  const factory RemedyModel({
    required String planet,
    required String reason,
    required List<MantraRemedy> mantras,
    required List<GemstoneRemedy> gemstones,
    required List<String> charities,
    required List<String> worship,
    required List<String> behavioral,
  }) = _RemedyModel;

  factory RemedyModel.fromJson(Map<String, dynamic> json) =>
      _$RemedyModelFromJson(json);
}
