import 'package:freezed_annotation/freezed_annotation.dart';

part 'event_model.freezed.dart';
part 'event_model.g.dart';

@freezed
class EventModel with _$EventModel {
  const factory EventModel({
    required String id,
    required String userId,
    required String title,
    required DateTime eventDate,
    DateTime? eventTime,
    required String eventType, // 'personal', 'cosmic', 'muhurta', 'reminder'
    String? category, // 'career', 'marriage', 'health', 'travel', etc.
    String? description,
    int? muhurtaScore, // 0-100 if muhurta was checked
    int? correlationScore, // 0-100 if past event was correlated
    @Default(false) bool isSystemGenerated,
    @Default({}) Map<String, dynamic> metadata,
    required DateTime createdAt,
  }) = _EventModel;

  factory EventModel.fromJson(Map<String, dynamic> json) =>
      _$EventModelFromJson(json);
}
