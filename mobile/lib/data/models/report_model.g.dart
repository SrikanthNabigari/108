// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ReportModelImpl _$$ReportModelImplFromJson(Map<String, dynamic> json) =>
    _$ReportModelImpl(
      id: json['id'] as String,
      userId: json['userId'] as String,
      reportType: json['reportType'] as String,
      title: json['title'] as String,
      content: json['content'] as Map<String, dynamic>,
      pdfUrl: json['pdfUrl'] as String?,
      creditsCharged: (json['creditsCharged'] as num?)?.toInt() ?? 0,
      status: json['status'] as String? ?? 'completed',
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$ReportModelImplToJson(_$ReportModelImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'reportType': instance.reportType,
      'title': instance.title,
      'content': instance.content,
      'pdfUrl': instance.pdfUrl,
      'creditsCharged': instance.creditsCharged,
      'status': instance.status,
      'createdAt': instance.createdAt.toIso8601String(),
    };
