// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'forecast_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AreaRatingImpl _$$AreaRatingImplFromJson(Map<String, dynamic> json) =>
    _$AreaRatingImpl(
      area: json['area'] as String,
      score: (json['score'] as num).toDouble(),
      trend: json['trend'] as String?,
    );

Map<String, dynamic> _$$AreaRatingImplToJson(_$AreaRatingImpl instance) =>
    <String, dynamic>{
      'area': instance.area,
      'score': instance.score,
      'trend': instance.trend,
    };

_$PanchangaDataImpl _$$PanchangaDataImplFromJson(Map<String, dynamic> json) =>
    _$PanchangaDataImpl(
      tithi: json['tithi'] as String?,
      nakshatra: json['nakshatra'] as String?,
      yoga: json['yoga'] as String?,
      karana: json['karana'] as String?,
      vara: json['vara'] as String?,
    );

Map<String, dynamic> _$$PanchangaDataImplToJson(_$PanchangaDataImpl instance) =>
    <String, dynamic>{
      'tithi': instance.tithi,
      'nakshatra': instance.nakshatra,
      'yoga': instance.yoga,
      'karana': instance.karana,
      'vara': instance.vara,
    };

_$ForecastModelImpl _$$ForecastModelImplFromJson(Map<String, dynamic> json) =>
    _$ForecastModelImpl(
      forecastType: json['forecastType'] as String,
      date: DateTime.parse(json['date'] as String),
      dayRating: (json['dayRating'] as num).toDouble(),
      areaRatings: (json['areaRatings'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, AreaRating.fromJson(e as Map<String, dynamic>)),
      ),
      recommendations: (json['recommendations'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      details: json['details'] as Map<String, dynamic>,
      panchanga: json['panchanga'] == null
          ? null
          : PanchangaData.fromJson(json['panchanga'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$ForecastModelImplToJson(_$ForecastModelImpl instance) =>
    <String, dynamic>{
      'forecastType': instance.forecastType,
      'date': instance.date.toIso8601String(),
      'dayRating': instance.dayRating,
      'areaRatings': instance.areaRatings,
      'recommendations': instance.recommendations,
      'details': instance.details,
      'panchanga': instance.panchanga,
    };
