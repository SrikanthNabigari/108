// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'user_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

UserModel _$UserModelFromJson(Map<String, dynamic> json) {
  return _UserModel.fromJson(json);
}

/// @nodoc
mixin _$UserModel {
  String get id => throw _privateConstructorUsedError;
  String? get email => throw _privateConstructorUsedError;
  String? get phone => throw _privateConstructorUsedError;
  String? get name => throw _privateConstructorUsedError;
  String? get gender => throw _privateConstructorUsedError;
  String? get avatarUrl => throw _privateConstructorUsedError;
  String get subscriptionTier => throw _privateConstructorUsedError;
  DateTime? get birthDatetime => throw _privateConstructorUsedError;
  double? get birthLatitude => throw _privateConstructorUsedError;
  double? get birthLongitude => throw _privateConstructorUsedError;
  double? get timezoneOffset => throw _privateConstructorUsedError;
  String? get placeName => throw _privateConstructorUsedError;
  DateTime? get createdAt => throw _privateConstructorUsedError;
  DateTime? get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this UserModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UserModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UserModelCopyWith<UserModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UserModelCopyWith<$Res> {
  factory $UserModelCopyWith(UserModel value, $Res Function(UserModel) then) =
      _$UserModelCopyWithImpl<$Res, UserModel>;
  @useResult
  $Res call(
      {String id,
      String? email,
      String? phone,
      String? name,
      String? gender,
      String? avatarUrl,
      String subscriptionTier,
      DateTime? birthDatetime,
      double? birthLatitude,
      double? birthLongitude,
      double? timezoneOffset,
      String? placeName,
      DateTime? createdAt,
      DateTime? updatedAt});
}

/// @nodoc
class _$UserModelCopyWithImpl<$Res, $Val extends UserModel>
    implements $UserModelCopyWith<$Res> {
  _$UserModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UserModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? email = freezed,
    Object? phone = freezed,
    Object? name = freezed,
    Object? gender = freezed,
    Object? avatarUrl = freezed,
    Object? subscriptionTier = null,
    Object? birthDatetime = freezed,
    Object? birthLatitude = freezed,
    Object? birthLongitude = freezed,
    Object? timezoneOffset = freezed,
    Object? placeName = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      email: freezed == email
          ? _value.email
          : email // ignore: cast_nullable_to_non_nullable
              as String?,
      phone: freezed == phone
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as String?,
      name: freezed == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String?,
      gender: freezed == gender
          ? _value.gender
          : gender // ignore: cast_nullable_to_non_nullable
              as String?,
      avatarUrl: freezed == avatarUrl
          ? _value.avatarUrl
          : avatarUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      subscriptionTier: null == subscriptionTier
          ? _value.subscriptionTier
          : subscriptionTier // ignore: cast_nullable_to_non_nullable
              as String,
      birthDatetime: freezed == birthDatetime
          ? _value.birthDatetime
          : birthDatetime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      birthLatitude: freezed == birthLatitude
          ? _value.birthLatitude
          : birthLatitude // ignore: cast_nullable_to_non_nullable
              as double?,
      birthLongitude: freezed == birthLongitude
          ? _value.birthLongitude
          : birthLongitude // ignore: cast_nullable_to_non_nullable
              as double?,
      timezoneOffset: freezed == timezoneOffset
          ? _value.timezoneOffset
          : timezoneOffset // ignore: cast_nullable_to_non_nullable
              as double?,
      placeName: freezed == placeName
          ? _value.placeName
          : placeName // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UserModelImplCopyWith<$Res>
    implements $UserModelCopyWith<$Res> {
  factory _$$UserModelImplCopyWith(
          _$UserModelImpl value, $Res Function(_$UserModelImpl) then) =
      __$$UserModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String? email,
      String? phone,
      String? name,
      String? gender,
      String? avatarUrl,
      String subscriptionTier,
      DateTime? birthDatetime,
      double? birthLatitude,
      double? birthLongitude,
      double? timezoneOffset,
      String? placeName,
      DateTime? createdAt,
      DateTime? updatedAt});
}

/// @nodoc
class __$$UserModelImplCopyWithImpl<$Res>
    extends _$UserModelCopyWithImpl<$Res, _$UserModelImpl>
    implements _$$UserModelImplCopyWith<$Res> {
  __$$UserModelImplCopyWithImpl(
      _$UserModelImpl _value, $Res Function(_$UserModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of UserModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? email = freezed,
    Object? phone = freezed,
    Object? name = freezed,
    Object? gender = freezed,
    Object? avatarUrl = freezed,
    Object? subscriptionTier = null,
    Object? birthDatetime = freezed,
    Object? birthLatitude = freezed,
    Object? birthLongitude = freezed,
    Object? timezoneOffset = freezed,
    Object? placeName = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
  }) {
    return _then(_$UserModelImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      email: freezed == email
          ? _value.email
          : email // ignore: cast_nullable_to_non_nullable
              as String?,
      phone: freezed == phone
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as String?,
      name: freezed == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String?,
      gender: freezed == gender
          ? _value.gender
          : gender // ignore: cast_nullable_to_non_nullable
              as String?,
      avatarUrl: freezed == avatarUrl
          ? _value.avatarUrl
          : avatarUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      subscriptionTier: null == subscriptionTier
          ? _value.subscriptionTier
          : subscriptionTier // ignore: cast_nullable_to_non_nullable
              as String,
      birthDatetime: freezed == birthDatetime
          ? _value.birthDatetime
          : birthDatetime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      birthLatitude: freezed == birthLatitude
          ? _value.birthLatitude
          : birthLatitude // ignore: cast_nullable_to_non_nullable
              as double?,
      birthLongitude: freezed == birthLongitude
          ? _value.birthLongitude
          : birthLongitude // ignore: cast_nullable_to_non_nullable
              as double?,
      timezoneOffset: freezed == timezoneOffset
          ? _value.timezoneOffset
          : timezoneOffset // ignore: cast_nullable_to_non_nullable
              as double?,
      placeName: freezed == placeName
          ? _value.placeName
          : placeName // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc

@JsonSerializable(fieldRename: FieldRename.snake)
class _$UserModelImpl extends _UserModel {
  const _$UserModelImpl(
      {required this.id,
      this.email,
      this.phone,
      this.name,
      this.gender,
      this.avatarUrl,
      this.subscriptionTier = 'free',
      this.birthDatetime,
      this.birthLatitude,
      this.birthLongitude,
      this.timezoneOffset,
      this.placeName,
      this.createdAt,
      this.updatedAt})
      : super._();

  factory _$UserModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$UserModelImplFromJson(json);

  @override
  final String id;
  @override
  final String? email;
  @override
  final String? phone;
  @override
  final String? name;
  @override
  final String? gender;
  @override
  final String? avatarUrl;
  @override
  @JsonKey()
  final String subscriptionTier;
  @override
  final DateTime? birthDatetime;
  @override
  final double? birthLatitude;
  @override
  final double? birthLongitude;
  @override
  final double? timezoneOffset;
  @override
  final String? placeName;
  @override
  final DateTime? createdAt;
  @override
  final DateTime? updatedAt;

  @override
  String toString() {
    return 'UserModel(id: $id, email: $email, phone: $phone, name: $name, gender: $gender, avatarUrl: $avatarUrl, subscriptionTier: $subscriptionTier, birthDatetime: $birthDatetime, birthLatitude: $birthLatitude, birthLongitude: $birthLongitude, timezoneOffset: $timezoneOffset, placeName: $placeName, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UserModelImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.phone, phone) || other.phone == phone) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.gender, gender) || other.gender == gender) &&
            (identical(other.avatarUrl, avatarUrl) ||
                other.avatarUrl == avatarUrl) &&
            (identical(other.subscriptionTier, subscriptionTier) ||
                other.subscriptionTier == subscriptionTier) &&
            (identical(other.birthDatetime, birthDatetime) ||
                other.birthDatetime == birthDatetime) &&
            (identical(other.birthLatitude, birthLatitude) ||
                other.birthLatitude == birthLatitude) &&
            (identical(other.birthLongitude, birthLongitude) ||
                other.birthLongitude == birthLongitude) &&
            (identical(other.timezoneOffset, timezoneOffset) ||
                other.timezoneOffset == timezoneOffset) &&
            (identical(other.placeName, placeName) ||
                other.placeName == placeName) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      email,
      phone,
      name,
      gender,
      avatarUrl,
      subscriptionTier,
      birthDatetime,
      birthLatitude,
      birthLongitude,
      timezoneOffset,
      placeName,
      createdAt,
      updatedAt);

  /// Create a copy of UserModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UserModelImplCopyWith<_$UserModelImpl> get copyWith =>
      __$$UserModelImplCopyWithImpl<_$UserModelImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UserModelImplToJson(
      this,
    );
  }
}

abstract class _UserModel extends UserModel {
  const factory _UserModel(
      {required final String id,
      final String? email,
      final String? phone,
      final String? name,
      final String? gender,
      final String? avatarUrl,
      final String subscriptionTier,
      final DateTime? birthDatetime,
      final double? birthLatitude,
      final double? birthLongitude,
      final double? timezoneOffset,
      final String? placeName,
      final DateTime? createdAt,
      final DateTime? updatedAt}) = _$UserModelImpl;
  const _UserModel._() : super._();

  factory _UserModel.fromJson(Map<String, dynamic> json) =
      _$UserModelImpl.fromJson;

  @override
  String get id;
  @override
  String? get email;
  @override
  String? get phone;
  @override
  String? get name;
  @override
  String? get gender;
  @override
  String? get avatarUrl;
  @override
  String get subscriptionTier;
  @override
  DateTime? get birthDatetime;
  @override
  double? get birthLatitude;
  @override
  double? get birthLongitude;
  @override
  double? get timezoneOffset;
  @override
  String? get placeName;
  @override
  DateTime? get createdAt;
  @override
  DateTime? get updatedAt;

  /// Create a copy of UserModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UserModelImplCopyWith<_$UserModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
