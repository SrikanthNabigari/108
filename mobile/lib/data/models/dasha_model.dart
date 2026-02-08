import 'package:freezed_annotation/freezed_annotation.dart';

part 'dasha_model.freezed.dart';
part 'dasha_model.g.dart';

@freezed
class DashaPeriodModel with _$DashaPeriodModel {
  const factory DashaPeriodModel({
    required String planet,
    required String level,
    required String startDate,
    required String endDate,
    @Default(false) bool isActive,
  }) = _DashaPeriodModel;

  factory DashaPeriodModel.fromJson(Map<String, dynamic> json) =>
      _$DashaPeriodModelFromJson(json);
}

@freezed
class DashaModel with _$DashaModel {
  const factory DashaModel({
    required DashaPeriodModel currentMD,
    required DashaPeriodModel currentAD,
    required DashaPeriodModel currentPD,
    required List<DashaPeriodModel> sequence,
  }) = _DashaModel;

  factory DashaModel.fromJson(Map<String, dynamic> json) =>
      _$DashaModelFromJson(json);
}
