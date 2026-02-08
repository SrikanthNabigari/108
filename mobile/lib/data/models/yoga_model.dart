import 'package:freezed_annotation/freezed_annotation.dart';

part 'yoga_model.freezed.dart';
part 'yoga_model.g.dart';

@freezed
class YogaModel with _$YogaModel {
  const factory YogaModel({
    required String name,
    required String category,
    required double strength,
    @Default(false) bool isCancelled,
    required List<String> planets,
    required List<String> effects,
    required String formation,
    String? activationPeriod,
  }) = _YogaModel;

  factory YogaModel.fromJson(Map<String, dynamic> json) =>
      _$YogaModelFromJson(json);
}
