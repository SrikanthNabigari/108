// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'birth_chart_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$PlanetPositionImpl _$$PlanetPositionImplFromJson(Map<String, dynamic> json) =>
    _$PlanetPositionImpl(
      planet: json['planet'] as String,
      longitude: (json['longitude'] as num).toDouble(),
      sign: json['sign'] as String,
      house: (json['house'] as num).toInt(),
      nakshatra: json['nakshatra'] as String,
      nakshatraPada: (json['nakshatraPada'] as num?)?.toInt() ?? 0,
      nakshatraDegree: (json['nakshatraDegree'] as num?)?.toDouble() ?? 0,
      isRetrograde: json['isRetrograde'] as bool? ?? false,
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0,
    );

Map<String, dynamic> _$$PlanetPositionImplToJson(
        _$PlanetPositionImpl instance) =>
    <String, dynamic>{
      'planet': instance.planet,
      'longitude': instance.longitude,
      'sign': instance.sign,
      'house': instance.house,
      'nakshatra': instance.nakshatra,
      'nakshatraPada': instance.nakshatraPada,
      'nakshatraDegree': instance.nakshatraDegree,
      'isRetrograde': instance.isRetrograde,
      'latitude': instance.latitude,
    };

_$BirthChartModelImpl _$$BirthChartModelImplFromJson(
        Map<String, dynamic> json) =>
    _$BirthChartModelImpl(
      userId: json['userId'] as String,
      ascendantLongitude: (json['ascendantLongitude'] as num).toDouble(),
      ascendantSign: json['ascendantSign'] as String,
      ascendantNakshatra: json['ascendantNakshatra'] as String,
      planets: (json['planets'] as List<dynamic>)
          .map((e) => PlanetPosition.fromJson(e as Map<String, dynamic>))
          .toList(),
      houseCusps: (json['houseCusps'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(int.parse(k), (e as num).toDouble()),
      ),
      moonRashi: json['moonRashi'] as String,
      moonNakshatra: json['moonNakshatra'] as String,
      ayanamsa: json['ayanamsa'] as String? ?? 'lahiri',
    );

Map<String, dynamic> _$$BirthChartModelImplToJson(
        _$BirthChartModelImpl instance) =>
    <String, dynamic>{
      'userId': instance.userId,
      'ascendantLongitude': instance.ascendantLongitude,
      'ascendantSign': instance.ascendantSign,
      'ascendantNakshatra': instance.ascendantNakshatra,
      'planets': instance.planets,
      'houseCusps':
          instance.houseCusps.map((k, e) => MapEntry(k.toString(), e)),
      'moonRashi': instance.moonRashi,
      'moonNakshatra': instance.moonNakshatra,
      'ayanamsa': instance.ayanamsa,
    };
