// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'transit_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$PlanetTransitImpl _$$PlanetTransitImplFromJson(Map<String, dynamic> json) =>
    _$PlanetTransitImpl(
      planet: json['planet'] as String,
      sign: json['sign'] as String,
      house: (json['house'] as num).toInt(),
      degree: (json['degree'] as num).toDouble(),
      nakshatra: json['nakshatra'] as String,
      isRetrograde: json['isRetrograde'] as bool? ?? false,
      enteredDate: json['enteredDate'] as String?,
      exitsDate: json['exitsDate'] as String?,
    );

Map<String, dynamic> _$$PlanetTransitImplToJson(_$PlanetTransitImpl instance) =>
    <String, dynamic>{
      'planet': instance.planet,
      'sign': instance.sign,
      'house': instance.house,
      'degree': instance.degree,
      'nakshatra': instance.nakshatra,
      'isRetrograde': instance.isRetrograde,
      'enteredDate': instance.enteredDate,
      'exitsDate': instance.exitsDate,
    };

_$GocharaResultImpl _$$GocharaResultImplFromJson(Map<String, dynamic> json) =>
    _$GocharaResultImpl(
      planet: json['planet'] as String,
      houseFromMoon: (json['houseFromMoon'] as num).toInt(),
      isFavorable: json['isFavorable'] as bool,
      description: json['description'] as String,
    );

Map<String, dynamic> _$$GocharaResultImplToJson(_$GocharaResultImpl instance) =>
    <String, dynamic>{
      'planet': instance.planet,
      'houseFromMoon': instance.houseFromMoon,
      'isFavorable': instance.isFavorable,
      'description': instance.description,
    };

_$TransitModelImpl _$$TransitModelImplFromJson(Map<String, dynamic> json) =>
    _$TransitModelImpl(
      transits: (json['transits'] as List<dynamic>)
          .map((e) => PlanetTransit.fromJson(e as Map<String, dynamic>))
          .toList(),
      gochara: (json['gochara'] as List<dynamic>)
          .map((e) => GocharaResult.fromJson(e as Map<String, dynamic>))
          .toList(),
      isSadeSatiActive: json['isSadeSatiActive'] as bool? ?? false,
      sadeSatiPhase: json['sadeSatiPhase'] as String?,
    );

Map<String, dynamic> _$$TransitModelImplToJson(_$TransitModelImpl instance) =>
    <String, dynamic>{
      'transits': instance.transits,
      'gochara': instance.gochara,
      'isSadeSatiActive': instance.isSadeSatiActive,
      'sadeSatiPhase': instance.sadeSatiPhase,
    };
