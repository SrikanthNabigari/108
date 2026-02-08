// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'yoga_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$YogaModelImpl _$$YogaModelImplFromJson(Map<String, dynamic> json) =>
    _$YogaModelImpl(
      name: json['name'] as String,
      category: json['category'] as String,
      strength: (json['strength'] as num).toDouble(),
      isCancelled: json['isCancelled'] as bool? ?? false,
      planets:
          (json['planets'] as List<dynamic>).map((e) => e as String).toList(),
      effects:
          (json['effects'] as List<dynamic>).map((e) => e as String).toList(),
      formation: json['formation'] as String,
      activationPeriod: json['activationPeriod'] as String?,
    );

Map<String, dynamic> _$$YogaModelImplToJson(_$YogaModelImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'category': instance.category,
      'strength': instance.strength,
      'isCancelled': instance.isCancelled,
      'planets': instance.planets,
      'effects': instance.effects,
      'formation': instance.formation,
      'activationPeriod': instance.activationPeriod,
    };
