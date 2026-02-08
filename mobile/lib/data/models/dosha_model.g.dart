// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dosha_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$CancellationConditionImpl _$$CancellationConditionImplFromJson(
        Map<String, dynamic> json) =>
    _$CancellationConditionImpl(
      description: json['description'] as String,
      isMet: json['isMet'] as bool,
    );

Map<String, dynamic> _$$CancellationConditionImplToJson(
        _$CancellationConditionImpl instance) =>
    <String, dynamic>{
      'description': instance.description,
      'isMet': instance.isMet,
    };

_$DoshaModelImpl _$$DoshaModelImplFromJson(Map<String, dynamic> json) =>
    _$DoshaModelImpl(
      name: json['name'] as String,
      severity: json['severity'] as String,
      planets:
          (json['planets'] as List<dynamic>).map((e) => e as String).toList(),
      effects:
          (json['effects'] as List<dynamic>).map((e) => e as String).toList(),
      cancellationConditions: (json['cancellationConditions'] as List<dynamic>)
          .map((e) => CancellationCondition.fromJson(e as Map<String, dynamic>))
          .toList(),
      remedies:
          (json['remedies'] as List<dynamic>).map((e) => e as String).toList(),
      isActive: json['isActive'] as bool? ?? true,
    );

Map<String, dynamic> _$$DoshaModelImplToJson(_$DoshaModelImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'severity': instance.severity,
      'planets': instance.planets,
      'effects': instance.effects,
      'cancellationConditions': instance.cancellationConditions,
      'remedies': instance.remedies,
      'isActive': instance.isActive,
    };
