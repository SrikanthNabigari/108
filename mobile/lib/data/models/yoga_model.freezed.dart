// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'yoga_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

YogaModel _$YogaModelFromJson(Map<String, dynamic> json) {
  return _YogaModel.fromJson(json);
}

/// @nodoc
mixin _$YogaModel {
  String get name => throw _privateConstructorUsedError;
  String get category => throw _privateConstructorUsedError;
  double get strength => throw _privateConstructorUsedError;
  bool get isCancelled => throw _privateConstructorUsedError;
  List<String> get planets => throw _privateConstructorUsedError;
  List<String> get effects => throw _privateConstructorUsedError;
  String get formation => throw _privateConstructorUsedError;
  String? get activationPeriod => throw _privateConstructorUsedError;

  /// Serializes this YogaModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of YogaModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $YogaModelCopyWith<YogaModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $YogaModelCopyWith<$Res> {
  factory $YogaModelCopyWith(YogaModel value, $Res Function(YogaModel) then) =
      _$YogaModelCopyWithImpl<$Res, YogaModel>;
  @useResult
  $Res call(
      {String name,
      String category,
      double strength,
      bool isCancelled,
      List<String> planets,
      List<String> effects,
      String formation,
      String? activationPeriod});
}

/// @nodoc
class _$YogaModelCopyWithImpl<$Res, $Val extends YogaModel>
    implements $YogaModelCopyWith<$Res> {
  _$YogaModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of YogaModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? category = null,
    Object? strength = null,
    Object? isCancelled = null,
    Object? planets = null,
    Object? effects = null,
    Object? formation = null,
    Object? activationPeriod = freezed,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      category: null == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      strength: null == strength
          ? _value.strength
          : strength // ignore: cast_nullable_to_non_nullable
              as double,
      isCancelled: null == isCancelled
          ? _value.isCancelled
          : isCancelled // ignore: cast_nullable_to_non_nullable
              as bool,
      planets: null == planets
          ? _value.planets
          : planets // ignore: cast_nullable_to_non_nullable
              as List<String>,
      effects: null == effects
          ? _value.effects
          : effects // ignore: cast_nullable_to_non_nullable
              as List<String>,
      formation: null == formation
          ? _value.formation
          : formation // ignore: cast_nullable_to_non_nullable
              as String,
      activationPeriod: freezed == activationPeriod
          ? _value.activationPeriod
          : activationPeriod // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$YogaModelImplCopyWith<$Res>
    implements $YogaModelCopyWith<$Res> {
  factory _$$YogaModelImplCopyWith(
          _$YogaModelImpl value, $Res Function(_$YogaModelImpl) then) =
      __$$YogaModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name,
      String category,
      double strength,
      bool isCancelled,
      List<String> planets,
      List<String> effects,
      String formation,
      String? activationPeriod});
}

/// @nodoc
class __$$YogaModelImplCopyWithImpl<$Res>
    extends _$YogaModelCopyWithImpl<$Res, _$YogaModelImpl>
    implements _$$YogaModelImplCopyWith<$Res> {
  __$$YogaModelImplCopyWithImpl(
      _$YogaModelImpl _value, $Res Function(_$YogaModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of YogaModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? category = null,
    Object? strength = null,
    Object? isCancelled = null,
    Object? planets = null,
    Object? effects = null,
    Object? formation = null,
    Object? activationPeriod = freezed,
  }) {
    return _then(_$YogaModelImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      category: null == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      strength: null == strength
          ? _value.strength
          : strength // ignore: cast_nullable_to_non_nullable
              as double,
      isCancelled: null == isCancelled
          ? _value.isCancelled
          : isCancelled // ignore: cast_nullable_to_non_nullable
              as bool,
      planets: null == planets
          ? _value._planets
          : planets // ignore: cast_nullable_to_non_nullable
              as List<String>,
      effects: null == effects
          ? _value._effects
          : effects // ignore: cast_nullable_to_non_nullable
              as List<String>,
      formation: null == formation
          ? _value.formation
          : formation // ignore: cast_nullable_to_non_nullable
              as String,
      activationPeriod: freezed == activationPeriod
          ? _value.activationPeriod
          : activationPeriod // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$YogaModelImpl implements _YogaModel {
  const _$YogaModelImpl(
      {required this.name,
      required this.category,
      required this.strength,
      this.isCancelled = false,
      required final List<String> planets,
      required final List<String> effects,
      required this.formation,
      this.activationPeriod})
      : _planets = planets,
        _effects = effects;

  factory _$YogaModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$YogaModelImplFromJson(json);

  @override
  final String name;
  @override
  final String category;
  @override
  final double strength;
  @override
  @JsonKey()
  final bool isCancelled;
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

  @override
  final String formation;
  @override
  final String? activationPeriod;

  @override
  String toString() {
    return 'YogaModel(name: $name, category: $category, strength: $strength, isCancelled: $isCancelled, planets: $planets, effects: $effects, formation: $formation, activationPeriod: $activationPeriod)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$YogaModelImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.strength, strength) ||
                other.strength == strength) &&
            (identical(other.isCancelled, isCancelled) ||
                other.isCancelled == isCancelled) &&
            const DeepCollectionEquality().equals(other._planets, _planets) &&
            const DeepCollectionEquality().equals(other._effects, _effects) &&
            (identical(other.formation, formation) ||
                other.formation == formation) &&
            (identical(other.activationPeriod, activationPeriod) ||
                other.activationPeriod == activationPeriod));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      name,
      category,
      strength,
      isCancelled,
      const DeepCollectionEquality().hash(_planets),
      const DeepCollectionEquality().hash(_effects),
      formation,
      activationPeriod);

  /// Create a copy of YogaModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$YogaModelImplCopyWith<_$YogaModelImpl> get copyWith =>
      __$$YogaModelImplCopyWithImpl<_$YogaModelImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$YogaModelImplToJson(
      this,
    );
  }
}

abstract class _YogaModel implements YogaModel {
  const factory _YogaModel(
      {required final String name,
      required final String category,
      required final double strength,
      final bool isCancelled,
      required final List<String> planets,
      required final List<String> effects,
      required final String formation,
      final String? activationPeriod}) = _$YogaModelImpl;

  factory _YogaModel.fromJson(Map<String, dynamic> json) =
      _$YogaModelImpl.fromJson;

  @override
  String get name;
  @override
  String get category;
  @override
  double get strength;
  @override
  bool get isCancelled;
  @override
  List<String> get planets;
  @override
  List<String> get effects;
  @override
  String get formation;
  @override
  String? get activationPeriod;

  /// Create a copy of YogaModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$YogaModelImplCopyWith<_$YogaModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
