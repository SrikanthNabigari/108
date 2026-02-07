// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'event_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$EventModelImpl _$$EventModelImplFromJson(Map<String, dynamic> json) =>
    _$EventModelImpl(
      id: json['id'] as String,
      userId: json['userId'] as String,
      title: json['title'] as String,
      eventDate: DateTime.parse(json['eventDate'] as String),
      eventTime: json['eventTime'] == null
          ? null
          : DateTime.parse(json['eventTime'] as String),
      eventType: json['eventType'] as String,
      category: json['category'] as String?,
      description: json['description'] as String?,
      muhurtaScore: (json['muhurtaScore'] as num?)?.toInt(),
      correlationScore: (json['correlationScore'] as num?)?.toInt(),
      isSystemGenerated: json['isSystemGenerated'] as bool? ?? false,
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$EventModelImplToJson(_$EventModelImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'title': instance.title,
      'eventDate': instance.eventDate.toIso8601String(),
      'eventTime': instance.eventTime?.toIso8601String(),
      'eventType': instance.eventType,
      'category': instance.category,
      'description': instance.description,
      'muhurtaScore': instance.muhurtaScore,
      'correlationScore': instance.correlationScore,
      'isSystemGenerated': instance.isSystemGenerated,
      'metadata': instance.metadata,
      'createdAt': instance.createdAt.toIso8601String(),
    };
