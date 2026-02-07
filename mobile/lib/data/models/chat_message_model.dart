import 'package:freezed_annotation/freezed_annotation.dart';

part 'chat_message_model.freezed.dart';
part 'chat_message_model.g.dart';

@freezed
class ChatBlock with _$ChatBlock {
  const factory ChatBlock({
    required String type, // 'text', 'table', 'score_card', 'alert', etc.
    String? content,
    Map<String, dynamic>? data,
  }) = _ChatBlock;

  factory ChatBlock.fromJson(Map<String, dynamic> json) =>
      _$ChatBlockFromJson(json);
}

@freezed
class ChatMessageModel with _$ChatMessageModel {
  const factory ChatMessageModel({
    required String id,
    required String userId,
    required String role, // 'user' or 'assistant'
    required String content,
    @Default('text') String contentType, // 'text', 'table', 'chart', 'card', 'report'
    @Default({}) Map<String, dynamic> metadata,
    @Default(<ChatBlock>[]) List<ChatBlock> blocks,
    @Default(0) int tokensUsed,
    required DateTime createdAt,
  }) = _ChatMessageModel;

  factory ChatMessageModel.fromJson(Map<String, dynamic> json) =>
      _$ChatMessageModelFromJson(json);
}
