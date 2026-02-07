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
  bool get onboardingComplete => throw _privateConstructorUsedError;
  String get subscriptionTier => throw _privateConstructorUsedError;
  String? get lagnaRashi => throw _privateConstructorUsedError;
  String? get moonRashi => throw _privateConstructorUsedError;
  String? get moonNakshatra => throw _privateConstructorUsedError;
  DateTime? get birthDatetime => throw _privateConstructorUsedError;
  String? get placeName => throw _privateConstructorUsedError;
  int get creditBalance => throw _privateConstructorUsedError;

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
      bool onboardingComplete,
      String subscriptionTier,
      String? lagnaRashi,
      String? moonRashi,
      String? moonNakshatra,
      DateTime? birthDatetime,
      String? placeName,
      int creditBalance});
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
    Object? onboardingComplete = null,
    Object? subscriptionTier = null,
    Object? lagnaRashi = freezed,
    Object? moonRashi = freezed,
    Object? moonNakshatra = freezed,
    Object? birthDatetime = freezed,
    Object? placeName = freezed,
    Object? creditBalance = null,
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
      onboardingComplete: null == onboardingComplete
          ? _value.onboardingComplete
          : onboardingComplete // ignore: cast_nullable_to_non_nullable
              as bool,
      subscriptionTier: null == subscriptionTier
          ? _value.subscriptionTier
          : subscriptionTier // ignore: cast_nullable_to_non_nullable
              as String,
      lagnaRashi: freezed == lagnaRashi
          ? _value.lagnaRashi
          : lagnaRashi // ignore: cast_nullable_to_non_nullable
              as String?,
      moonRashi: freezed == moonRashi
          ? _value.moonRashi
          : moonRashi // ignore: cast_nullable_to_non_nullable
              as String?,
      moonNakshatra: freezed == moonNakshatra
          ? _value.moonNakshatra
          : moonNakshatra // ignore: cast_nullable_to_non_nullable
              as String?,
      birthDatetime: freezed == birthDatetime
          ? _value.birthDatetime
          : birthDatetime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      placeName: freezed == placeName
          ? _value.placeName
          : placeName // ignore: cast_nullable_to_non_nullable
              as String?,
      creditBalance: null == creditBalance
          ? _value.creditBalance
          : creditBalance // ignore: cast_nullable_to_non_nullable
              as int,
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
      bool onboardingComplete,
      String subscriptionTier,
      String? lagnaRashi,
      String? moonRashi,
      String? moonNakshatra,
      DateTime? birthDatetime,
      String? placeName,
      int creditBalance});
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
    Object? onboardingComplete = null,
    Object? subscriptionTier = null,
    Object? lagnaRashi = freezed,
    Object? moonRashi = freezed,
    Object? moonNakshatra = freezed,
    Object? birthDatetime = freezed,
    Object? placeName = freezed,
    Object? creditBalance = null,
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
      onboardingComplete: null == onboardingComplete
          ? _value.onboardingComplete
          : onboardingComplete // ignore: cast_nullable_to_non_nullable
              as bool,
      subscriptionTier: null == subscriptionTier
          ? _value.subscriptionTier
          : subscriptionTier // ignore: cast_nullable_to_non_nullable
              as String,
      lagnaRashi: freezed == lagnaRashi
          ? _value.lagnaRashi
          : lagnaRashi // ignore: cast_nullable_to_non_nullable
              as String?,
      moonRashi: freezed == moonRashi
          ? _value.moonRashi
          : moonRashi // ignore: cast_nullable_to_non_nullable
              as String?,
      moonNakshatra: freezed == moonNakshatra
          ? _value.moonNakshatra
          : moonNakshatra // ignore: cast_nullable_to_non_nullable
              as String?,
      birthDatetime: freezed == birthDatetime
          ? _value.birthDatetime
          : birthDatetime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      placeName: freezed == placeName
          ? _value.placeName
          : placeName // ignore: cast_nullable_to_non_nullable
              as String?,
      creditBalance: null == creditBalance
          ? _value.creditBalance
          : creditBalance // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UserModelImpl implements _UserModel {
  const _$UserModelImpl(
      {required this.id,
      this.email,
      this.phone,
      this.name,
      this.gender,
      this.avatarUrl,
      this.onboardingComplete = false,
      this.subscriptionTier = 'free',
      this.lagnaRashi,
      this.moonRashi,
      this.moonNakshatra,
      this.birthDatetime,
      this.placeName,
      this.creditBalance = 0});

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
  final bool onboardingComplete;
  @override
  @JsonKey()
  final String subscriptionTier;
  @override
  final String? lagnaRashi;
  @override
  final String? moonRashi;
  @override
  final String? moonNakshatra;
  @override
  final DateTime? birthDatetime;
  @override
  final String? placeName;
  @override
  @JsonKey()
  final int creditBalance;

  @override
  String toString() {
    return 'UserModel(id: $id, email: $email, phone: $phone, name: $name, gender: $gender, avatarUrl: $avatarUrl, onboardingComplete: $onboardingComplete, subscriptionTier: $subscriptionTier, lagnaRashi: $lagnaRashi, moonRashi: $moonRashi, moonNakshatra: $moonNakshatra, birthDatetime: $birthDatetime, placeName: $placeName, creditBalance: $creditBalance)';
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
            (identical(other.onboardingComplete, onboardingComplete) ||
                other.onboardingComplete == onboardingComplete) &&
            (identical(other.subscriptionTier, subscriptionTier) ||
                other.subscriptionTier == subscriptionTier) &&
            (identical(other.lagnaRashi, lagnaRashi) ||
                other.lagnaRashi == lagnaRashi) &&
            (identical(other.moonRashi, moonRashi) ||
                other.moonRashi == moonRashi) &&
            (identical(other.moonNakshatra, moonNakshatra) ||
                other.moonNakshatra == moonNakshatra) &&
            (identical(other.birthDatetime, birthDatetime) ||
                other.birthDatetime == birthDatetime) &&
            (identical(other.placeName, placeName) ||
                other.placeName == placeName) &&
            (identical(other.creditBalance, creditBalance) ||
                other.creditBalance == creditBalance));
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
      onboardingComplete,
      subscriptionTier,
      lagnaRashi,
      moonRashi,
      moonNakshatra,
      birthDatetime,
      placeName,
      creditBalance);

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

abstract class _UserModel implements UserModel {
  const factory _UserModel(
      {required final String id,
      final String? email,
      final String? phone,
      final String? name,
      final String? gender,
      final String? avatarUrl,
      final bool onboardingComplete,
      final String subscriptionTier,
      final String? lagnaRashi,
      final String? moonRashi,
      final String? moonNakshatra,
      final DateTime? birthDatetime,
      final String? placeName,
      final int creditBalance}) = _$UserModelImpl;

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
  bool get onboardingComplete;
  @override
  String get subscriptionTier;
  @override
  String? get lagnaRashi;
  @override
  String? get moonRashi;
  @override
  String? get moonNakshatra;
  @override
  DateTime? get birthDatetime;
  @override
  String? get placeName;
  @override
  int get creditBalance;

  /// Create a copy of UserModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UserModelImplCopyWith<_$UserModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
