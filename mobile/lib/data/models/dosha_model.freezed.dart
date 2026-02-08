// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dosha_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

CancellationCondition _$CancellationConditionFromJson(
    Map<String, dynamic> json) {
  return _CancellationCondition.fromJson(json);
}

/// @nodoc
mixin _$CancellationCondition {
  String get description => throw _privateConstructorUsedError;
  bool get isMet => throw _privateConstructorUsedError;

  /// Serializes this CancellationCondition to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CancellationCondition
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CancellationConditionCopyWith<CancellationCondition> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CancellationConditionCopyWith<$Res> {
  factory $CancellationConditionCopyWith(CancellationCondition value,
          $Res Function(CancellationCondition) then) =
      _$CancellationConditionCopyWithImpl<$Res, CancellationCondition>;
  @useResult
  $Res call({String description, bool isMet});
}

/// @nodoc
class _$CancellationConditionCopyWithImpl<$Res,
        $Val extends CancellationCondition>
    implements $CancellationConditionCopyWith<$Res> {
  _$CancellationConditionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CancellationCondition
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? description = null,
    Object? isMet = null,
  }) {
    return _then(_value.copyWith(
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      isMet: null == isMet
          ? _value.isMet
          : isMet // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CancellationConditionImplCopyWith<$Res>
    implements $CancellationConditionCopyWith<$Res> {
  factory _$$CancellationConditionImplCopyWith(
          _$CancellationConditionImpl value,
          $Res Function(_$CancellationConditionImpl) then) =
      __$$CancellationConditionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String description, bool isMet});
}

/// @nodoc
class __$$CancellationConditionImplCopyWithImpl<$Res>
    extends _$CancellationConditionCopyWithImpl<$Res,
        _$CancellationConditionImpl>
    implements _$$CancellationConditionImplCopyWith<$Res> {
  __$$CancellationConditionImplCopyWithImpl(_$CancellationConditionImpl _value,
      $Res Function(_$CancellationConditionImpl) _then)
      : super(_value, _then);

  /// Create a copy of CancellationCondition
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? description = null,
    Object? isMet = null,
  }) {
    return _then(_$CancellationConditionImpl(
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      isMet: null == isMet
          ? _value.isMet
          : isMet // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CancellationConditionImpl implements _CancellationCondition {
  const _$CancellationConditionImpl(
      {required this.description, required this.isMet});

  factory _$CancellationConditionImpl.fromJson(Map<String, dynamic> json) =>
      _$$CancellationConditionImplFromJson(json);

  @override
  final String description;
  @override
  final bool isMet;

  @override
  String toString() {
    return 'CancellationCondition(description: $description, isMet: $isMet)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CancellationConditionImpl &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.isMet, isMet) || other.isMet == isMet));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, description, isMet);

  /// Create a copy of CancellationCondition
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CancellationConditionImplCopyWith<_$CancellationConditionImpl>
      get copyWith => __$$CancellationConditionImplCopyWithImpl<
          _$CancellationConditionImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CancellationConditionImplToJson(
      this,
    );
  }
}

abstract class _CancellationCondition implements CancellationCondition {
  const factory _CancellationCondition(
      {required final String description,
      required final bool isMet}) = _$CancellationConditionImpl;

  factory _CancellationCondition.fromJson(Map<String, dynamic> json) =
      _$CancellationConditionImpl.fromJson;

  @override
  String get description;
  @override
  bool get isMet;

  /// Create a copy of CancellationCondition
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CancellationConditionImplCopyWith<_$CancellationConditionImpl>
      get copyWith => throw _privateConstructorUsedError;
}

DoshaModel _$DoshaModelFromJson(Map<String, dynamic> json) {
  return _DoshaModel.fromJson(json);
}

/// @nodoc
mixin _$DoshaModel {
  String get name => throw _privateConstructorUsedError;
  String get severity => throw _privateConstructorUsedError;
  List<String> get planets => throw _privateConstructorUsedError;
  List<String> get effects => throw _privateConstructorUsedError;
  List<CancellationCondition> get cancellationConditions =>
      throw _privateConstructorUsedError;
  List<String> get remedies => throw _privateConstructorUsedError;
  bool get isActive => throw _privateConstructorUsedError;

  /// Serializes this DoshaModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DoshaModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DoshaModelCopyWith<DoshaModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DoshaModelCopyWith<$Res> {
  factory $DoshaModelCopyWith(
          DoshaModel value, $Res Function(DoshaModel) then) =
      _$DoshaModelCopyWithImpl<$Res, DoshaModel>;
  @useResult
  $Res call(
      {String name,
      String severity,
      List<String> planets,
      List<String> effects,
      List<CancellationCondition> cancellationConditions,
      List<String> remedies,
      bool isActive});
}

/// @nodoc
class _$DoshaModelCopyWithImpl<$Res, $Val extends DoshaModel>
    implements $DoshaModelCopyWith<$Res> {
  _$DoshaModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DoshaModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? severity = null,
    Object? planets = null,
    Object? effects = null,
    Object? cancellationConditions = null,
    Object? remedies = null,
    Object? isActive = null,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as String,
      planets: null == planets
          ? _value.planets
          : planets // ignore: cast_nullable_to_non_nullable
              as List<String>,
      effects: null == effects
          ? _value.effects
          : effects // ignore: cast_nullable_to_non_nullable
              as List<String>,
      cancellationConditions: null == cancellationConditions
          ? _value.cancellationConditions
          : cancellationConditions // ignore: cast_nullable_to_non_nullable
              as List<CancellationCondition>,
      remedies: null == remedies
          ? _value.remedies
          : remedies // ignore: cast_nullable_to_non_nullable
              as List<String>,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DoshaModelImplCopyWith<$Res>
    implements $DoshaModelCopyWith<$Res> {
  factory _$$DoshaModelImplCopyWith(
          _$DoshaModelImpl value, $Res Function(_$DoshaModelImpl) then) =
      __$$DoshaModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name,
      String severity,
      List<String> planets,
      List<String> effects,
      List<CancellationCondition> cancellationConditions,
      List<String> remedies,
      bool isActive});
}

/// @nodoc
class __$$DoshaModelImplCopyWithImpl<$Res>
    extends _$DoshaModelCopyWithImpl<$Res, _$DoshaModelImpl>
    implements _$$DoshaModelImplCopyWith<$Res> {
  __$$DoshaModelImplCopyWithImpl(
      _$DoshaModelImpl _value, $Res Function(_$DoshaModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of DoshaModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? severity = null,
    Object? planets = null,
    Object? effects = null,
    Object? cancellationConditions = null,
    Object? remedies = null,
    Object? isActive = null,
  }) {
    return _then(_$DoshaModelImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as String,
      planets: null == planets
          ? _value._planets
          : planets // ignore: cast_nullable_to_non_nullable
              as List<String>,
      effects: null == effects
          ? _value._effects
          : effects // ignore: cast_nullable_to_non_nullable
              as List<String>,
      cancellationConditions: null == cancellationConditions
          ? _value._cancellationConditions
          : cancellationConditions // ignore: cast_nullable_to_non_nullable
              as List<CancellationCondition>,
      remedies: null == remedies
          ? _value._remedies
          : remedies // ignore: cast_nullable_to_non_nullable
              as List<String>,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DoshaModelImpl implements _DoshaModel {
  const _$DoshaModelImpl(
      {required this.name,
      required this.severity,
      required final List<String> planets,
      required final List<String> effects,
      required final List<CancellationCondition> cancellationConditions,
      required final List<String> remedies,
      this.isActive = true})
      : _planets = planets,
        _effects = effects,
        _cancellationConditions = cancellationConditions,
        _remedies = remedies;

  factory _$DoshaModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$DoshaModelImplFromJson(json);

  @override
  final String name;
  @override
  final String severity;
  final List<String> _planets;
  @override
  List<String> get planets {
    if (_planets is EqualUnmodifiableListView) return _planets;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_planets);
  }

  final List<String> _effects;
  @override
  List<String> get effects {
    if (_effects is EqualUnmodifiableListView) return _effects;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_effects);
  }

  final List<CancellationCondition> _cancellationConditions;
  @override
  List<CancellationCondition> get cancellationConditions {
    if (_cancellationConditions is EqualUnmodifiableListView)
      return _cancellationConditions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_cancellationConditions);
  }

  final List<String> _remedies;
  @override
  List<String> get remedies {
    if (_remedies is EqualUnmodifiableListView) return _remedies;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_remedies);
  }

  @override
  @JsonKey()
  final bool isActive;

  @override
  String toString() {
    return 'DoshaModel(name: $name, severity: $severity, planets: $planets, effects: $effects, cancellationConditions: $cancellationConditions, remedies: $remedies, isActive: $isActive)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DoshaModelImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.severity, severity) ||
                other.severity == severity) &&
            const DeepCollectionEquality().equals(other._planets, _planets) &&
            const DeepCollectionEquality().equals(other._effects, _effects) &&
            const DeepCollectionEquality().equals(
                other._cancellationConditions, _cancellationConditions) &&
            const DeepCollectionEquality().equals(other._remedies, _remedies) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      name,
      severity,
      const DeepCollectionEquality().hash(_planets),
      const DeepCollectionEquality().hash(_effects),
      const DeepCollectionEquality().hash(_cancellationConditions),
      const DeepCollectionEquality().hash(_remedies),
      isActive);

  /// Create a copy of DoshaModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DoshaModelImplCopyWith<_$DoshaModelImpl> get copyWith =>
      __$$DoshaModelImplCopyWithImpl<_$DoshaModelImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DoshaModelImplToJson(
      this,
    );
  }
}

abstract class _DoshaModel implements DoshaModel {
  const factory _DoshaModel(
      {required final String name,
      required final String severity,
      required final List<String> planets,
      required final List<String> effects,
      required final List<CancellationCondition> cancellationConditions,
      required final List<String> remedies,
      final bool isActive}) = _$DoshaModelImpl;

  factory _DoshaModel.fromJson(Map<String, dynamic> json) =
      _$DoshaModelImpl.fromJson;

  @override
  String get name;
  @override
  String get severity;
  @override
  List<String> get planets;
  @override
  List<String> get effects;
  @override
  List<CancellationCondition> get cancellationConditions;
  @override
  List<String> get remedies;
  @override
  bool get isActive;

  /// Create a copy of DoshaModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DoshaModelImplCopyWith<_$DoshaModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
