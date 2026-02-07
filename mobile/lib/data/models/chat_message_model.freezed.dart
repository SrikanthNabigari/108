// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'chat_message_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

ChatBlock _$ChatBlockFromJson(Map<String, dynamic> json) {
  return _ChatBlock.fromJson(json);
}

/// @nodoc
mixin _$ChatBlock {
  String get type =>
      throw _privateConstructorUsedError; // 'text', 'table', 'score_card', 'alert', etc.
  String? get content => throw _privateConstructorUsedError;
  Map<String, dynamic>? get data => throw _privateConstructorUsedError;

  /// Serializes this ChatBlock to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ChatBlock
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ChatBlockCopyWith<ChatBlock> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChatBlockCopyWith<$Res> {
  factory $ChatBlockCopyWith(ChatBlock value, $Res Function(ChatBlock) then) =
      _$ChatBlockCopyWithImpl<$Res, ChatBlock>;
  @useResult
  $Res call({String type, String? content, Map<String, dynamic>? data});
}

/// @nodoc
class _$ChatBlockCopyWithImpl<$Res, $Val extends ChatBlock>
    implements $ChatBlockCopyWith<$Res> {
  _$ChatBlockCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ChatBlock
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? type = null,
    Object? content = freezed,
    Object? data = freezed,
  }) {
    return _then(_value.copyWith(
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      content: freezed == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String?,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChatBlockImplCopyWith<$Res>
    implements $ChatBlockCopyWith<$Res> {
  factory _$$ChatBlockImplCopyWith(
          _$ChatBlockImpl value, $Res Function(_$ChatBlockImpl) then) =
      __$$ChatBlockImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String type, String? content, Map<String, dynamic>? data});
}

/// @nodoc
class __$$ChatBlockImplCopyWithImpl<$Res>
    extends _$ChatBlockCopyWithImpl<$Res, _$ChatBlockImpl>
    implements _$$ChatBlockImplCopyWith<$Res> {
  __$$ChatBlockImplCopyWithImpl(
      _$ChatBlockImpl _value, $Res Function(_$ChatBlockImpl) _then)
      : super(_value, _then);

  /// Create a copy of ChatBlock
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? type = null,
    Object? content = freezed,
    Object? data = freezed,
  }) {
    return _then(_$ChatBlockImpl(
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      content: freezed == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String?,
      data: freezed == data
          ? _value._data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChatBlockImpl implements _ChatBlock {
  const _$ChatBlockImpl(
      {required this.type, this.content, final Map<String, dynamic>? data})
      : _data = data;

  factory _$ChatBlockImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChatBlockImplFromJson(json);

  @override
  final String type;
// 'text', 'table', 'score_card', 'alert', etc.
  @override
  final String? content;
  final Map<String, dynamic>? _data;
  @override
  Map<String, dynamic>? get data {
    final value = _data;
    if (value == null) return null;
    if (_data is EqualUnmodifiableMapView) return _data;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'ChatBlock(type: $type, content: $content, data: $data)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChatBlockImpl &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.content, content) || other.content == content) &&
            const DeepCollectionEquality().equals(other._data, _data));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, type, content, const DeepCollectionEquality().hash(_data));

  /// Create a copy of ChatBlock
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ChatBlockImplCopyWith<_$ChatBlockImpl> get copyWith =>
      __$$ChatBlockImplCopyWithImpl<_$ChatBlockImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChatBlockImplToJson(
      this,
    );
  }
}

abstract class _ChatBlock implements ChatBlock {
  const factory _ChatBlock(
      {required final String type,
      final String? content,
      final Map<String, dynamic>? data}) = _$ChatBlockImpl;

  factory _ChatBlock.fromJson(Map<String, dynamic> json) =
      _$ChatBlockImpl.fromJson;

  @override
  String get type; // 'text', 'table', 'score_card', 'alert', etc.
  @override
  String? get content;
  @override
  Map<String, dynamic>? get data;

  /// Create a copy of ChatBlock
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ChatBlockImplCopyWith<_$ChatBlockImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ChatMessageModel _$ChatMessageModelFromJson(Map<String, dynamic> json) {
  return _ChatMessageModel.fromJson(json);
}

/// @nodoc
mixin _$ChatMessageModel {
  String get id => throw _privateConstructorUsedError;
  String get userId => throw _privateConstructorUsedError;
  String get role =>
      throw _privateConstructorUsedError; // 'user' or 'assistant'
  String get content => throw _privateConstructorUsedError;
  String get contentType =>
      throw _privateConstructorUsedError; // 'text', 'table', 'chart', 'card', 'report'
  Map<String, dynamic> get metadata => throw _privateConstructorUsedError;
  List<ChatBlock> get blocks => throw _privateConstructorUsedError;
  int get tokensUsed => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;

  /// Serializes this ChatMessageModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ChatMessageModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ChatMessageModelCopyWith<ChatMessageModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChatMessageModelCopyWith<$Res> {
  factory $ChatMessageModelCopyWith(
          ChatMessageModel value, $Res Function(ChatMessageModel) then) =
      _$ChatMessageModelCopyWithImpl<$Res, ChatMessageModel>;
  @useResult
  $Res call(
      {String id,
      String userId,
      String role,
      String content,
      String contentType,
      Map<String, dynamic> metadata,
      List<ChatBlock> blocks,
      int tokensUsed,
      DateTime createdAt});
}

/// @nodoc
class _$ChatMessageModelCopyWithImpl<$Res, $Val extends ChatMessageModel>
    implements $ChatMessageModelCopyWith<$Res> {
  _$ChatMessageModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ChatMessageModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? role = null,
    Object? content = null,
    Object? contentType = null,
    Object? metadata = null,
    Object? blocks = null,
    Object? tokensUsed = null,
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
      role: null == role
          ? _value.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      content: null == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String,
      contentType: null == contentType
          ? _value.contentType
          : contentType // ignore: cast_nullable_to_non_nullable
              as String,
      metadata: null == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      blocks: null == blocks
          ? _value.blocks
          : blocks // ignore: cast_nullable_to_non_nullable
              as List<ChatBlock>,
      tokensUsed: null == tokensUsed
          ? _value.tokensUsed
          : tokensUsed // ignore: cast_nullable_to_non_nullable
              as int,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChatMessageModelImplCopyWith<$Res>
    implements $ChatMessageModelCopyWith<$Res> {
  factory _$$ChatMessageModelImplCopyWith(_$ChatMessageModelImpl value,
          $Res Function(_$ChatMessageModelImpl) then) =
      __$$ChatMessageModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String userId,
      String role,
      String content,
      String contentType,
      Map<String, dynamic> metadata,
      List<ChatBlock> blocks,
      int tokensUsed,
      DateTime createdAt});
}

/// @nodoc
class __$$ChatMessageModelImplCopyWithImpl<$Res>
    extends _$ChatMessageModelCopyWithImpl<$Res, _$ChatMessageModelImpl>
    implements _$$ChatMessageModelImplCopyWith<$Res> {
  __$$ChatMessageModelImplCopyWithImpl(_$ChatMessageModelImpl _value,
      $Res Function(_$ChatMessageModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of ChatMessageModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? role = null,
    Object? content = null,
    Object? contentType = null,
    Object? metadata = null,
    Object? blocks = null,
    Object? tokensUsed = null,
    Object? createdAt = null,
  }) {
    return _then(_$ChatMessageModelImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      userId: null == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      role: null == role
          ? _value.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      content: null == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String,
      contentType: null == contentType
          ? _value.contentType
          : contentType // ignore: cast_nullable_to_non_nullable
              as String,
      metadata: null == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      blocks: null == blocks
          ? _value._blocks
          : blocks // ignore: cast_nullable_to_non_nullable
              as List<ChatBlock>,
      tokensUsed: null == tokensUsed
          ? _value.tokensUsed
          : tokensUsed // ignore: cast_nullable_to_non_nullable
              as int,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChatMessageModelImpl implements _ChatMessageModel {
  const _$ChatMessageModelImpl(
      {required this.id,
      required this.userId,
      required this.role,
      required this.content,
      this.contentType = 'text',
      final Map<String, dynamic> metadata = const {},
      final List<ChatBlock> blocks = const <ChatBlock>[],
      this.tokensUsed = 0,
      required this.createdAt})
      : _metadata = metadata,
        _blocks = blocks;

  factory _$ChatMessageModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChatMessageModelImplFromJson(json);

  @override
  final String id;
  @override
  final String userId;
  @override
  final String role;
// 'user' or 'assistant'
  @override
  final String content;
  @override
  @JsonKey()
  final String contentType;
// 'text', 'table', 'chart', 'card', 'report'
  final Map<String, dynamic> _metadata;
// 'text', 'table', 'chart', 'card', 'report'
  @override
  @JsonKey()
  Map<String, dynamic> get metadata {
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_metadata);
  }

  final List<ChatBlock> _blocks;
  @override
  @JsonKey()
  List<ChatBlock> get blocks {
    if (_blocks is EqualUnmodifiableListView) return _blocks;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_blocks);
  }

  @override
  @JsonKey()
  final int tokensUsed;
  @override
  final DateTime createdAt;

  @override
  String toString() {
    return 'ChatMessageModel(id: $id, userId: $userId, role: $role, content: $content, contentType: $contentType, metadata: $metadata, blocks: $blocks, tokensUsed: $tokensUsed, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChatMessageModelImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.content, content) || other.content == content) &&
            (identical(other.contentType, contentType) ||
                other.contentType == contentType) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            const DeepCollectionEquality().equals(other._blocks, _blocks) &&
            (identical(other.tokensUsed, tokensUsed) ||
                other.tokensUsed == tokensUsed) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      userId,
      role,
      content,
      contentType,
      const DeepCollectionEquality().hash(_metadata),
      const DeepCollectionEquality().hash(_blocks),
      tokensUsed,
      createdAt);

  /// Create a copy of ChatMessageModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ChatMessageModelImplCopyWith<_$ChatMessageModelImpl> get copyWith =>
      __$$ChatMessageModelImplCopyWithImpl<_$ChatMessageModelImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChatMessageModelImplToJson(
      this,
    );
  }
}

abstract class _ChatMessageModel implements ChatMessageModel {
  const factory _ChatMessageModel(
      {required final String id,
      required final String userId,
      required final String role,
      required final String content,
      final String contentType,
      final Map<String, dynamic> metadata,
      final List<ChatBlock> blocks,
      final int tokensUsed,
      required final DateTime createdAt}) = _$ChatMessageModelImpl;

  factory _ChatMessageModel.fromJson(Map<String, dynamic> json) =
      _$ChatMessageModelImpl.fromJson;

  @override
  String get id;
  @override
  String get userId;
  @override
  String get role; // 'user' or 'assistant'
  @override
  String get content;
  @override
  String get contentType; // 'text', 'table', 'chart', 'card', 'report'
  @override
  Map<String, dynamic> get metadata;
  @override
  List<ChatBlock> get blocks;
  @override
  int get tokensUsed;
  @override
  DateTime get createdAt;

  /// Create a copy of ChatMessageModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ChatMessageModelImplCopyWith<_$ChatMessageModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
