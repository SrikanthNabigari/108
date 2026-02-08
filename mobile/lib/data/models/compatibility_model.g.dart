// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'compatibility_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$KutaScoreImpl _$$KutaScoreImplFromJson(Map<String, dynamic> json) =>
    _$KutaScoreImpl(
      name: json['name'] as String,
      obtained: (json['obtained'] as num).toDouble(),
      maximum: (json['maximum'] as num).toDouble(),
      description: json['description'] as String?,
    );

Map<String, dynamic> _$$KutaScoreImplToJson(_$KutaScoreImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'obtained': instance.obtained,
      'maximum': instance.maximum,
      'description': instance.description,
    };

_$CompatibilityModelImpl _$$CompatibilityModelImplFromJson(
        Map<String, dynamic> json) =>
    _$CompatibilityModelImpl(
      kutaScores: (json['kutaScores'] as List<dynamic>)
          .map((e) => KutaScore.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalObtained: (json['totalObtained'] as num).toDouble(),
      totalMaximum: (json['totalMaximum'] as num).toDouble(),
      verdict: json['verdict'] as String,
      summary: json['summary'] as String?,
    );

Map<String, dynamic> _$$CompatibilityModelImplToJson(
        _$CompatibilityModelImpl instance) =>
    <String, dynamic>{
      'kutaScores': instance.kutaScores,
      'totalObtained': instance.totalObtained,
      'totalMaximum': instance.totalMaximum,
      'verdict': instance.verdict,
      'summary': instance.summary,
    };
