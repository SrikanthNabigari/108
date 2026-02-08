// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'remedy_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$MantraRemedyImpl _$$MantraRemedyImplFromJson(Map<String, dynamic> json) =>
    _$MantraRemedyImpl(
      mantra: json['mantra'] as String,
      transliteration: json['transliteration'] as String?,
      repetitions: json['repetitions'] as String,
      bestDay: json['bestDay'] as String,
      bestTime: json['bestTime'] as String,
      duration: json['duration'] as String,
    );

Map<String, dynamic> _$$MantraRemedyImplToJson(_$MantraRemedyImpl instance) =>
    <String, dynamic>{
      'mantra': instance.mantra,
      'transliteration': instance.transliteration,
      'repetitions': instance.repetitions,
      'bestDay': instance.bestDay,
      'bestTime': instance.bestTime,
      'duration': instance.duration,
    };

_$GemstoneRemedyImpl _$$GemstoneRemedyImplFromJson(Map<String, dynamic> json) =>
    _$GemstoneRemedyImpl(
      name: json['name'] as String,
      weight: json['weight'] as String,
      metal: json['metal'] as String,
      finger: json['finger'] as String,
      wearingDay: json['wearingDay'] as String,
      wearingTime: json['wearingTime'] as String,
      caution: json['caution'] as String?,
    );

Map<String, dynamic> _$$GemstoneRemedyImplToJson(
        _$GemstoneRemedyImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'weight': instance.weight,
      'metal': instance.metal,
      'finger': instance.finger,
      'wearingDay': instance.wearingDay,
      'wearingTime': instance.wearingTime,
      'caution': instance.caution,
    };

_$RemedyModelImpl _$$RemedyModelImplFromJson(Map<String, dynamic> json) =>
    _$RemedyModelImpl(
      planet: json['planet'] as String,
      reason: json['reason'] as String,
      mantras: (json['mantras'] as List<dynamic>)
          .map((e) => MantraRemedy.fromJson(e as Map<String, dynamic>))
          .toList(),
      gemstones: (json['gemstones'] as List<dynamic>)
          .map((e) => GemstoneRemedy.fromJson(e as Map<String, dynamic>))
          .toList(),
      charities:
          (json['charities'] as List<dynamic>).map((e) => e as String).toList(),
      worship:
          (json['worship'] as List<dynamic>).map((e) => e as String).toList(),
      behavioral: (json['behavioral'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$$RemedyModelImplToJson(_$RemedyModelImpl instance) =>
    <String, dynamic>{
      'planet': instance.planet,
      'reason': instance.reason,
      'mantras': instance.mantras,
      'gemstones': instance.gemstones,
      'charities': instance.charities,
      'worship': instance.worship,
      'behavioral': instance.behavioral,
    };
