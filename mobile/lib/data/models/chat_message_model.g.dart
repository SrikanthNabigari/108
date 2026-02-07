// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chat_message_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ChatBlockImpl _$$ChatBlockImplFromJson(Map<String, dynamic> json) =>
    _$ChatBlockImpl(
      type: json['type'] as String,
      content: json['content'] as String?,
      data: json['data'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$ChatBlockImplToJson(_$ChatBlockImpl instance) =>
    <String, dynamic>{
      'type': instance.type,
      'content': instance.content,
      'data': instance.data,
    };

_$ChatMessageModelImpl _$$ChatMessageModelImplFromJson(
        Map<String, dynamic> json) =>
    _$ChatMessageModelImpl(
      id: json['id'] as String,
      userId: json['userId'] as String,
      role: json['role'] as String,
      content: json['content'] as String,
      contentType: json['contentType'] as String? ?? 'text',
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
      blocks: (json['blocks'] as List<dynamic>?)
              ?.map((e) => ChatBlock.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <ChatBlock>[],
      tokensUsed: (json['tokensUsed'] as num?)?.toInt() ?? 0,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$ChatMessageModelImplToJson(
        _$ChatMessageModelImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'role': instance.role,
      'content': instance.content,
      'contentType': instance.contentType,
      'metadata': instance.metadata,
      'blocks': instance.blocks,
      'tokensUsed': instance.tokensUsed,
      'createdAt': instance.createdAt.toIso8601String(),
    };
