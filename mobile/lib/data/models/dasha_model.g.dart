// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dasha_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$DashaPeriodModelImpl _$$DashaPeriodModelImplFromJson(
        Map<String, dynamic> json) =>
    _$DashaPeriodModelImpl(
      planet: json['planet'] as String,
      level: json['level'] as String,
      startDate: json['startDate'] as String,
      endDate: json['endDate'] as String,
      isActive: json['isActive'] as bool? ?? false,
    );

Map<String, dynamic> _$$DashaPeriodModelImplToJson(
        _$DashaPeriodModelImpl instance) =>
    <String, dynamic>{
      'planet': instance.planet,
      'level': instance.level,
      'startDate': instance.startDate,
      'endDate': instance.endDate,
      'isActive': instance.isActive,
    };

_$DashaModelImpl _$$DashaModelImplFromJson(Map<String, dynamic> json) =>
    _$DashaModelImpl(
      currentMD:
          DashaPeriodModel.fromJson(json['currentMD'] as Map<String, dynamic>),
      currentAD:
          DashaPeriodModel.fromJson(json['currentAD'] as Map<String, dynamic>),
      currentPD:
          DashaPeriodModel.fromJson(json['currentPD'] as Map<String, dynamic>),
      sequence: (json['sequence'] as List<dynamic>)
          .map((e) => DashaPeriodModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$$DashaModelImplToJson(_$DashaModelImpl instance) =>
    <String, dynamic>{
      'currentMD': instance.currentMD,
      'currentAD': instance.currentAD,
      'currentPD': instance.currentPD,
      'sequence': instance.sequence,
    };
