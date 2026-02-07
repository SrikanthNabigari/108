// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'event_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

EventModel _$EventModelFromJson(Map<String, dynamic> json) {
  return _EventModel.fromJson(json);
}

/// @nodoc
mixin _$EventModel {
  String get id => throw _privateConstructorUsedError;
  String get userId => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  DateTime get eventDate => throw _privateConstructorUsedError;
  DateTime? get eventTime => throw _privateConstructorUsedError;
  String get eventType =>
      throw _privateConstructorUsedError; // 'personal', 'cosmic', 'muhurta', 'reminder'
  String? get category =>
      throw _privateConstructorUsedError; // 'career', 'marriage', 'health', 'travel', etc.
  String? get description => throw _privateConstructorUsedError;
  int? get muhurtaScore =>
      throw _privateConstructorUsedError; // 0-100 if muhurta was checked
  int? get correlationScore =>
      throw _privateConstructorUsedError; // 0-100 if past event was correlated
  bool get isSystemGenerated => throw _privateConstructorUsedError;
  Map<String, dynamic> get metadata => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;

  /// Serializes this EventModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of EventModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $EventModelCopyWith<EventModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $EventModelCopyWith<$Res> {
  factory $EventModelCopyWith(
          EventModel value, $Res Function(EventModel) then) =
      _$EventModelCopyWithImpl<$Res, EventModel>;
  @useResult
  $Res call(
      {String id,
      String userId,
      String title,
      DateTime eventDate,
      DateTime? eventTime,
      String eventType,
      String? category,
      String? description,
      int? muhurtaScore,
      int? correlationScore,
      bool isSystemGenerated,
      Map<String, dynamic> metadata,
      DateTime createdAt});
}

/// @nodoc
class _$EventModelCopyWithImpl<$Res, $Val extends EventModel>
    implements $EventModelCopyWith<$Res> {
  _$EventModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of EventModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? title = null,
    Object? eventDate = null,
    Object? eventTime = freezed,
    Object? eventType = null,
    Object? category = freezed,
    Object? description = freezed,
    Object? muhurtaScore = freezed,
    Object? correlationScore = freezed,
    Object? isSystemGenerated = null,
    Object? metadata = null,
    Object? createdAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      userId: null == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      eventDate: null == eventDate
          ? _value.eventDate
          : eventDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      eventTime: freezed == eventTime
          ? _value.eventTime
          : eventTime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      eventType: null == eventType
          ? _value.eventType
          : eventType // ignore: cast_nullable_to_non_nullable
              as String,
      category: freezed == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      muhurtaScore: freezed == muhurtaScore
          ? _value.muhurtaScore
          : muhurtaScore // ignore: cast_nullable_to_non_nullable
              as int?,
      correlationScore: freezed == correlationScore
          ? _value.correlationScore
          : correlationScore // ignore: cast_nullable_to_non_nullable
              as int?,
      isSystemGenerated: null == isSystemGenerated
          ? _value.isSystemGenerated
          : isSystemGenerated // ignore: cast_nullable_to_non_nullable
              as bool,
      metadata: null == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$EventModelImplCopyWith<$Res>
    implements $EventModelCopyWith<$Res> {
  factory _$$EventModelImplCopyWith(
          _$EventModelImpl value, $Res Function(_$EventModelImpl) then) =
      __$$EventModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String userId,
      String title,
      DateTime eventDate,
      DateTime? eventTime,
      String eventType,
      String? category,
      String? description,
      int? muhurtaScore,
      int? correlationScore,
      bool isSystemGenerated,
      Map<String, dynamic> metadata,
      DateTime createdAt});
}

/// @nodoc
class __$$EventModelImplCopyWithImpl<$Res>
    extends _$EventModelCopyWithImpl<$Res, _$EventModelImpl>
    implements _$$EventModelImplCopyWith<$Res> {
  __$$EventModelImplCopyWithImpl(
      _$EventModelImpl _value, $Res Function(_$EventModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of EventModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? title = null,
    Object? eventDate = null,
    Object? eventTime = freezed,
    Object? eventType = null,
    Object? category = freezed,
    Object? description = freezed,
    Object? muhurtaScore = freezed,
    Object? correlationScore = freezed,
    Object? isSystemGenerated = null,
    Object? metadata = null,
    Object? createdAt = null,
  }) {
    return _then(_$EventModelImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      userId: null == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      eventDate: null == eventDate
          ? _value.eventDate
          : eventDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      eventTime: freezed == eventTime
          ? _value.eventTime
          : eventTime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      eventType: null == eventType
          ? _value.eventType
          : eventType // ignore: cast_nullable_to_non_nullable
              as String,
      category: freezed == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      muhurtaScore: freezed == muhurtaScore
          ? _value.muhurtaScore
          : muhurtaScore // ignore: cast_nullable_to_non_nullable
              as int?,
      correlationScore: freezed == correlationScore
          ? _value.correlationScore
          : correlationScore // ignore: cast_nullable_to_non_nullable
              as int?,
      isSystemGenerated: null == isSystemGenerated
          ? _value.isSystemGenerated
          : isSystemGenerated // ignore: cast_nullable_to_non_nullable
              as bool,
      metadata: null == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$EventModelImpl implements _EventModel {
  const _$EventModelImpl(
      {required this.id,
      required this.userId,
      required this.title,
      required this.eventDate,
      this.eventTime,
      required this.eventType,
      this.category,
      this.description,
      this.muhurtaScore,
      this.correlationScore,
      this.isSystemGenerated = false,
      final Map<String, dynamic> metadata = const {},
      required this.createdAt})
      : _metadata = metadata;

  factory _$EventModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$EventModelImplFromJson(json);

  @override
  final String id;
  @override
  final String userId;
  @override
  final String title;
  @override
  final DateTime eventDate;
  @override
  final DateTime? eventTime;
  @override
  final String eventType;
// 'personal', 'cosmic', 'muhurta', 'reminder'
  @override
  final String? category;
// 'career', 'marriage', 'health', 'travel', etc.
  @override
  final String? description;
  @override
  final int? muhurtaScore;
// 0-100 if muhurta was checked
  @override
  final int? correlationScore;
// 0-100 if past event was correlated
  @override
  @JsonKey()
  final bool isSystemGenerated;
  final Map<String, dynamic> _metadata;
  @override
  @JsonKey()
  Map<String, dynamic> get metadata {
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_metadata);
  }

  @override
  final DateTime createdAt;

  @override
  String toString() {
    return 'EventModel(id: $id, userId: $userId, title: $title, eventDate: $eventDate, eventTime: $eventTime, eventType: $eventType, category: $category, description: $description, muhurtaScore: $muhurtaScore, correlationScore: $correlationScore, isSystemGenerated: $isSystemGenerated, metadata: $metadata, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$EventModelImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.eventDate, eventDate) ||
                other.eventDate == eventDate) &&
            (identical(other.eventTime, eventTime) ||
                other.eventTime == eventTime) &&
            (identical(other.eventType, eventType) ||
                other.eventType == eventType) &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.muhurtaScore, muhurtaScore) ||
                other.muhurtaScore == muhurtaScore) &&
            (identical(other.correlationScore, correlationScore) ||
                other.correlationScore == correlationScore) &&
            (identical(other.isSystemGenerated, isSystemGenerated) ||
                other.isSystemGenerated == isSystemGenerated) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      userId,
      title,
      eventDate,
      eventTime,
      eventType,
      category,
      description,
      muhurtaScore,
      correlationScore,
      isSystemGenerated,
      const DeepCollectionEquality().hash(_metadata),
      createdAt);

  /// Create a copy of EventModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$EventModelImplCopyWith<_$EventModelImpl> get copyWith =>
      __$$EventModelImplCopyWithImpl<_$EventModelImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$EventModelImplToJson(
      this,
    );
  }
}

abstract class _EventModel implements EventModel {
  const factory _EventModel(
      {required final String id,
      required final String userId,
      required final String title,
      required final DateTime eventDate,
      final DateTime? eventTime,
      required final String eventType,
      final String? category,
      final String? description,
      final int? muhurtaScore,
      final int? correlationScore,
      final bool isSystemGenerated,
      final Map<String, dynamic> metadata,
      required final DateTime createdAt}) = _$EventModelImpl;

  factory _EventModel.fromJson(Map<String, dynamic> json) =
      _$EventModelImpl.fromJson;

  @override
  String get id;
  @override
  String get userId;
  @override
  String get title;
  @override
  DateTime get eventDate;
  @override
  DateTime? get eventTime;
  @override
  String get eventType; // 'personal', 'cosmic', 'muhurta', 'reminder'
  @override
  String? get category; // 'career', 'marriage', 'health', 'travel', etc.
  @override
  String? get description;
  @override
  int? get muhurtaScore; // 0-100 if muhurta was checked
  @override
  int? get correlationScore; // 0-100 if past event was correlated
  @override
  bool get isSystemGenerated;
  @override
  Map<String, dynamic> get metadata;
  @override
  DateTime get createdAt;

  /// Create a copy of EventModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$EventModelImplCopyWith<_$EventModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
