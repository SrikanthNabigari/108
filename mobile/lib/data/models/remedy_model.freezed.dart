// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'remedy_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

MantraRemedy _$MantraRemedyFromJson(Map<String, dynamic> json) {
  return _MantraRemedy.fromJson(json);
}

/// @nodoc
mixin _$MantraRemedy {
  String get mantra => throw _privateConstructorUsedError;
  String? get transliteration => throw _privateConstructorUsedError;
  String get repetitions => throw _privateConstructorUsedError;
  String get bestDay => throw _privateConstructorUsedError;
  String get bestTime => throw _privateConstructorUsedError;
  String get duration => throw _privateConstructorUsedError;

  /// Serializes this MantraRemedy to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of MantraRemedy
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MantraRemedyCopyWith<MantraRemedy> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MantraRemedyCopyWith<$Res> {
  factory $MantraRemedyCopyWith(
          MantraRemedy value, $Res Function(MantraRemedy) then) =
      _$MantraRemedyCopyWithImpl<$Res, MantraRemedy>;
  @useResult
  $Res call(
      {String mantra,
      String? transliteration,
      String repetitions,
      String bestDay,
      String bestTime,
      String duration});
}

/// @nodoc
class _$MantraRemedyCopyWithImpl<$Res, $Val extends MantraRemedy>
    implements $MantraRemedyCopyWith<$Res> {
  _$MantraRemedyCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of MantraRemedy
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? mantra = null,
    Object? transliteration = freezed,
    Object? repetitions = null,
    Object? bestDay = null,
    Object? bestTime = null,
    Object? duration = null,
  }) {
    return _then(_value.copyWith(
      mantra: null == mantra
          ? _value.mantra
          : mantra // ignore: cast_nullable_to_non_nullable
              as String,
      transliteration: freezed == transliteration
          ? _value.transliteration
          : transliteration // ignore: cast_nullable_to_non_nullable
              as String?,
      repetitions: null == repetitions
          ? _value.repetitions
          : repetitions // ignore: cast_nullable_to_non_nullable
              as String,
      bestDay: null == bestDay
          ? _value.bestDay
          : bestDay // ignore: cast_nullable_to_non_nullable
              as String,
      bestTime: null == bestTime
          ? _value.bestTime
          : bestTime // ignore: cast_nullable_to_non_nullable
              as String,
      duration: null == duration
          ? _value.duration
          : duration // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$MantraRemedyImplCopyWith<$Res>
    implements $MantraRemedyCopyWith<$Res> {
  factory _$$MantraRemedyImplCopyWith(
          _$MantraRemedyImpl value, $Res Function(_$MantraRemedyImpl) then) =
      __$$MantraRemedyImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String mantra,
      String? transliteration,
      String repetitions,
      String bestDay,
      String bestTime,
      String duration});
}

/// @nodoc
class __$$MantraRemedyImplCopyWithImpl<$Res>
    extends _$MantraRemedyCopyWithImpl<$Res, _$MantraRemedyImpl>
    implements _$$MantraRemedyImplCopyWith<$Res> {
  __$$MantraRemedyImplCopyWithImpl(
      _$MantraRemedyImpl _value, $Res Function(_$MantraRemedyImpl) _then)
      : super(_value, _then);

  /// Create a copy of MantraRemedy
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? mantra = null,
    Object? transliteration = freezed,
    Object? repetitions = null,
    Object? bestDay = null,
    Object? bestTime = null,
    Object? duration = null,
  }) {
    return _then(_$MantraRemedyImpl(
      mantra: null == mantra
          ? _value.mantra
          : mantra // ignore: cast_nullable_to_non_nullable
              as String,
      transliteration: freezed == transliteration
          ? _value.transliteration
          : transliteration // ignore: cast_nullable_to_non_nullable
              as String?,
      repetitions: null == repetitions
          ? _value.repetitions
          : repetitions // ignore: cast_nullable_to_non_nullable
              as String,
      bestDay: null == bestDay
          ? _value.bestDay
          : bestDay // ignore: cast_nullable_to_non_nullable
              as String,
      bestTime: null == bestTime
          ? _value.bestTime
          : bestTime // ignore: cast_nullable_to_non_nullable
              as String,
      duration: null == duration
          ? _value.duration
          : duration // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$MantraRemedyImpl implements _MantraRemedy {
  const _$MantraRemedyImpl(
      {required this.mantra,
      this.transliteration,
      required this.repetitions,
      required this.bestDay,
      required this.bestTime,
      required this.duration});

  factory _$MantraRemedyImpl.fromJson(Map<String, dynamic> json) =>
      _$$MantraRemedyImplFromJson(json);

  @override
  final String mantra;
  @override
  final String? transliteration;
  @override
  final String repetitions;
  @override
  final String bestDay;
  @override
  final String bestTime;
  @override
  final String duration;

  @override
  String toString() {
    return 'MantraRemedy(mantra: $mantra, transliteration: $transliteration, repetitions: $repetitions, bestDay: $bestDay, bestTime: $bestTime, duration: $duration)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MantraRemedyImpl &&
            (identical(other.mantra, mantra) || other.mantra == mantra) &&
            (identical(other.transliteration, transliteration) ||
                other.transliteration == transliteration) &&
            (identical(other.repetitions, repetitions) ||
                other.repetitions == repetitions) &&
            (identical(other.bestDay, bestDay) || other.bestDay == bestDay) &&
            (identical(other.bestTime, bestTime) ||
                other.bestTime == bestTime) &&
            (identical(other.duration, duration) ||
                other.duration == duration));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, mantra, transliteration,
      repetitions, bestDay, bestTime, duration);

  /// Create a copy of MantraRemedy
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MantraRemedyImplCopyWith<_$MantraRemedyImpl> get copyWith =>
      __$$MantraRemedyImplCopyWithImpl<_$MantraRemedyImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MantraRemedyImplToJson(
      this,
    );
  }
}

abstract class _MantraRemedy implements MantraRemedy {
  const factory _MantraRemedy(
      {required final String mantra,
      final String? transliteration,
      required final String repetitions,
      required final String bestDay,
      required final String bestTime,
      required final String duration}) = _$MantraRemedyImpl;

  factory _MantraRemedy.fromJson(Map<String, dynamic> json) =
      _$MantraRemedyImpl.fromJson;

  @override
  String get mantra;
  @override
  String? get transliteration;
  @override
  String get repetitions;
  @override
  String get bestDay;
  @override
  String get bestTime;
  @override
  String get duration;

  /// Create a copy of MantraRemedy
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MantraRemedyImplCopyWith<_$MantraRemedyImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

GemstoneRemedy _$GemstoneRemedyFromJson(Map<String, dynamic> json) {
  return _GemstoneRemedy.fromJson(json);
}

/// @nodoc
mixin _$GemstoneRemedy {
  String get name => throw _privateConstructorUsedError;
  String get weight => throw _privateConstructorUsedError;
  String get metal => throw _privateConstructorUsedError;
  String get finger => throw _privateConstructorUsedError;
  String get wearingDay => throw _privateConstructorUsedError;
  String get wearingTime => throw _privateConstructorUsedError;
  String? get caution => throw _privateConstructorUsedError;

  /// Serializes this GemstoneRemedy to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GemstoneRemedy
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GemstoneRemedyCopyWith<GemstoneRemedy> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GemstoneRemedyCopyWith<$Res> {
  factory $GemstoneRemedyCopyWith(
          GemstoneRemedy value, $Res Function(GemstoneRemedy) then) =
      _$GemstoneRemedyCopyWithImpl<$Res, GemstoneRemedy>;
  @useResult
  $Res call(
      {String name,
      String weight,
      String metal,
      String finger,
      String wearingDay,
      String wearingTime,
      String? caution});
}

/// @nodoc
class _$GemstoneRemedyCopyWithImpl<$Res, $Val extends GemstoneRemedy>
    implements $GemstoneRemedyCopyWith<$Res> {
  _$GemstoneRemedyCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GemstoneRemedy
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? weight = null,
    Object? metal = null,
    Object? finger = null,
    Object? wearingDay = null,
    Object? wearingTime = null,
    Object? caution = freezed,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      weight: null == weight
          ? _value.weight
          : weight // ignore: cast_nullable_to_non_nullable
              as String,
      metal: null == metal
          ? _value.metal
          : metal // ignore: cast_nullable_to_non_nullable
              as String,
      finger: null == finger
          ? _value.finger
          : finger // ignore: cast_nullable_to_non_nullable
              as String,
      wearingDay: null == wearingDay
          ? _value.wearingDay
          : wearingDay // ignore: cast_nullable_to_non_nullable
              as String,
      wearingTime: null == wearingTime
          ? _value.wearingTime
          : wearingTime // ignore: cast_nullable_to_non_nullable
              as String,
      caution: freezed == caution
          ? _value.caution
          : caution // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$GemstoneRemedyImplCopyWith<$Res>
    implements $GemstoneRemedyCopyWith<$Res> {
  factory _$$GemstoneRemedyImplCopyWith(_$GemstoneRemedyImpl value,
          $Res Function(_$GemstoneRemedyImpl) then) =
      __$$GemstoneRemedyImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name,
      String weight,
      String metal,
      String finger,
      String wearingDay,
      String wearingTime,
      String? caution});
}

/// @nodoc
class __$$GemstoneRemedyImplCopyWithImpl<$Res>
    extends _$GemstoneRemedyCopyWithImpl<$Res, _$GemstoneRemedyImpl>
    implements _$$GemstoneRemedyImplCopyWith<$Res> {
  __$$GemstoneRemedyImplCopyWithImpl(
      _$GemstoneRemedyImpl _value, $Res Function(_$GemstoneRemedyImpl) _then)
      : super(_value, _then);

  /// Create a copy of GemstoneRemedy
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? weight = null,
    Object? metal = null,
    Object? finger = null,
    Object? wearingDay = null,
    Object? wearingTime = null,
    Object? caution = freezed,
  }) {
    return _then(_$GemstoneRemedyImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      weight: null == weight
          ? _value.weight
          : weight // ignore: cast_nullable_to_non_nullable
              as String,
      metal: null == metal
          ? _value.metal
          : metal // ignore: cast_nullable_to_non_nullable
              as String,
      finger: null == finger
          ? _value.finger
          : finger // ignore: cast_nullable_to_non_nullable
              as String,
      wearingDay: null == wearingDay
          ? _value.wearingDay
          : wearingDay // ignore: cast_nullable_to_non_nullable
              as String,
      wearingTime: null == wearingTime
          ? _value.wearingTime
          : wearingTime // ignore: cast_nullable_to_non_nullable
              as String,
      caution: freezed == caution
          ? _value.caution
          : caution // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$GemstoneRemedyImpl implements _GemstoneRemedy {
  const _$GemstoneRemedyImpl(
      {required this.name,
      required this.weight,
      required this.metal,
      required this.finger,
      required this.wearingDay,
      required this.wearingTime,
      this.caution});

  factory _$GemstoneRemedyImpl.fromJson(Map<String, dynamic> json) =>
      _$$GemstoneRemedyImplFromJson(json);

  @override
  final String name;
  @override
  final String weight;
  @override
  final String metal;
  @override
  final String finger;
  @override
  final String wearingDay;
  @override
  final String wearingTime;
  @override
  final String? caution;

  @override
  String toString() {
    return 'GemstoneRemedy(name: $name, weight: $weight, metal: $metal, finger: $finger, wearingDay: $wearingDay, wearingTime: $wearingTime, caution: $caution)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GemstoneRemedyImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.weight, weight) || other.weight == weight) &&
            (identical(other.metal, metal) || other.metal == metal) &&
            (identical(other.finger, finger) || other.finger == finger) &&
            (identical(other.wearingDay, wearingDay) ||
                other.wearingDay == wearingDay) &&
            (identical(other.wearingTime, wearingTime) ||
                other.wearingTime == wearingTime) &&
            (identical(other.caution, caution) || other.caution == caution));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, name, weight, metal, finger,
      wearingDay, wearingTime, caution);

  /// Create a copy of GemstoneRemedy
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GemstoneRemedyImplCopyWith<_$GemstoneRemedyImpl> get copyWith =>
      __$$GemstoneRemedyImplCopyWithImpl<_$GemstoneRemedyImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$GemstoneRemedyImplToJson(
      this,
    );
  }
}

abstract class _GemstoneRemedy implements GemstoneRemedy {
  const factory _GemstoneRemedy(
      {required final String name,
      required final String weight,
      required final String metal,
      required final String finger,
      required final String wearingDay,
      required final String wearingTime,
      final String? caution}) = _$GemstoneRemedyImpl;

  factory _GemstoneRemedy.fromJson(Map<String, dynamic> json) =
      _$GemstoneRemedyImpl.fromJson;

  @override
  String get name;
  @override
  String get weight;
  @override
  String get metal;
  @override
  String get finger;
  @override
  String get wearingDay;
  @override
  String get wearingTime;
  @override
  String? get caution;

  /// Create a copy of GemstoneRemedy
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GemstoneRemedyImplCopyWith<_$GemstoneRemedyImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

RemedyModel _$RemedyModelFromJson(Map<String, dynamic> json) {
  return _RemedyModel.fromJson(json);
}

/// @nodoc
mixin _$RemedyModel {
  String get planet => throw _privateConstructorUsedError;
  String get reason => throw _privateConstructorUsedError;
  List<MantraRemedy> get mantras => throw _privateConstructorUsedError;
  List<GemstoneRemedy> get gemstones => throw _privateConstructorUsedError;
  List<String> get charities => throw _privateConstructorUsedError;
  List<String> get worship => throw _privateConstructorUsedError;
  List<String> get behavioral => throw _privateConstructorUsedError;

  /// Serializes this RemedyModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of RemedyModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $RemedyModelCopyWith<RemedyModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $RemedyModelCopyWith<$Res> {
  factory $RemedyModelCopyWith(
          RemedyModel value, $Res Function(RemedyModel) then) =
      _$RemedyModelCopyWithImpl<$Res, RemedyModel>;
  @useResult
  $Res call(
      {String planet,
      String reason,
      List<MantraRemedy> mantras,
      List<GemstoneRemedy> gemstones,
      List<String> charities,
      List<String> worship,
      List<String> behavioral});
}

/// @nodoc
class _$RemedyModelCopyWithImpl<$Res, $Val extends RemedyModel>
    implements $RemedyModelCopyWith<$Res> {
  _$RemedyModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of RemedyModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? planet = null,
    Object? reason = null,
    Object? mantras = null,
    Object? gemstones = null,
    Object? charities = null,
    Object? worship = null,
    Object? behavioral = null,
  }) {
    return _then(_value.copyWith(
      planet: null == planet
          ? _value.planet
          : planet // ignore: cast_nullable_to_non_nullable
              as String,
      reason: null == reason
          ? _value.reason
          : reason // ignore: cast_nullable_to_non_nullable
              as String,
      mantras: null == mantras
          ? _value.mantras
          : mantras // ignore: cast_nullable_to_non_nullable
              as List<MantraRemedy>,
      gemstones: null == gemstones
          ? _value.gemstones
          : gemstones // ignore: cast_nullable_to_non_nullable
              as List<GemstoneRemedy>,
      charities: null == charities
          ? _value.charities
          : charities // ignore: cast_nullable_to_non_nullable
              as List<String>,
      worship: null == worship
          ? _value.worship
          : worship // ignore: cast_nullable_to_non_nullable
              as List<String>,
      behavioral: null == behavioral
          ? _value.behavioral
          : behavioral // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$RemedyModelImplCopyWith<$Res>
    implements $RemedyModelCopyWith<$Res> {
  factory _$$RemedyModelImplCopyWith(
          _$RemedyModelImpl value, $Res Function(_$RemedyModelImpl) then) =
      __$$RemedyModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String planet,
      String reason,
      List<MantraRemedy> mantras,
      List<GemstoneRemedy> gemstones,
      List<String> charities,
      List<String> worship,
      List<String> behavioral});
}

/// @nodoc
class __$$RemedyModelImplCopyWithImpl<$Res>
    extends _$RemedyModelCopyWithImpl<$Res, _$RemedyModelImpl>
    implements _$$RemedyModelImplCopyWith<$Res> {
  __$$RemedyModelImplCopyWithImpl(
      _$RemedyModelImpl _value, $Res Function(_$RemedyModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of RemedyModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? planet = null,
    Object? reason = null,
    Object? mantras = null,
    Object? gemstones = null,
    Object? charities = null,
    Object? worship = null,
    Object? behavioral = null,
  }) {
    return _then(_$RemedyModelImpl(
      planet: null == planet
          ? _value.planet
          : planet // ignore: cast_nullable_to_non_nullable
              as String,
      reason: null == reason
          ? _value.reason
          : reason // ignore: cast_nullable_to_non_nullable
              as String,
      mantras: null == mantras
          ? _value._mantras
          : mantras // ignore: cast_nullable_to_non_nullable
              as List<MantraRemedy>,
      gemstones: null == gemstones
          ? _value._gemstones
          : gemstones // ignore: cast_nullable_to_non_nullable
              as List<GemstoneRemedy>,
      charities: null == charities
          ? _value._charities
          : charities // ignore: cast_nullable_to_non_nullable
              as List<String>,
      worship: null == worship
          ? _value._worship
          : worship // ignore: cast_nullable_to_non_nullable
              as List<String>,
      behavioral: null == behavioral
          ? _value._behavioral
          : behavioral // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$RemedyModelImpl implements _RemedyModel {
  const _$RemedyModelImpl(
      {required this.planet,
      required this.reason,
      required final List<MantraRemedy> mantras,
      required final List<GemstoneRemedy> gemstones,
      required final List<String> charities,
      required final List<String> worship,
      required final List<String> behavioral})
      : _mantras = mantras,
        _gemstones = gemstones,
        _charities = charities,
        _worship = worship,
        _behavioral = behavioral;

  factory _$RemedyModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$RemedyModelImplFromJson(json);

  @override
  final String planet;
  @override
  final String reason;
  final List<MantraRemedy> _mantras;
  @override
  List<MantraRemedy> get mantras {
    if (_mantras is EqualUnmodifiableListView) return _mantras;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_mantras);
  }

  final List<GemstoneRemedy> _gemstones;
  @override
  List<GemstoneRemedy> get gemstones {
    if (_gemstones is EqualUnmodifiableListView) return _gemstones;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_gemstones);
  }

  final List<String> _charities;
  @override
  List<String> get charities {
    if (_charities is EqualUnmodifiableListView) return _charities;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_charities);
  }

  final List<String> _worship;
  @override
  List<String> get worship {
    if (_worship is EqualUnmodifiableListView) return _worship;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_worship);
  }

  final List<String> _behavioral;
  @override
  List<String> get behavioral {
    if (_behavioral is EqualUnmodifiableListView) return _behavioral;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_behavioral);
  }

  @override
  String toString() {
    return 'RemedyModel(planet: $planet, reason: $reason, mantras: $mantras, gemstones: $gemstones, charities: $charities, worship: $worship, behavioral: $behavioral)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$RemedyModelImpl &&
            (identical(other.planet, planet) || other.planet == planet) &&
            (identical(other.reason, reason) || other.reason == reason) &&
            const DeepCollectionEquality().equals(other._mantras, _mantras) &&
            const DeepCollectionEquality()
                .equals(other._gemstones, _gemstones) &&
            const DeepCollectionEquality()
                .equals(other._charities, _charities) &&
            const DeepCollectionEquality().equals(other._worship, _worship) &&
            const DeepCollectionEquality()
                .equals(other._behavioral, _behavioral));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      planet,
      reason,
      const DeepCollectionEquality().hash(_mantras),
      const DeepCollectionEquality().hash(_gemstones),
      const DeepCollectionEquality().hash(_charities),
      const DeepCollectionEquality().hash(_worship),
      const DeepCollectionEquality().hash(_behavioral));

  /// Create a copy of RemedyModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$RemedyModelImplCopyWith<_$RemedyModelImpl> get copyWith =>
      __$$RemedyModelImplCopyWithImpl<_$RemedyModelImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$RemedyModelImplToJson(
      this,
    );
  }
}

abstract class _RemedyModel implements RemedyModel {
  const factory _RemedyModel(
      {required final String planet,
      required final String reason,
      required final List<MantraRemedy> mantras,
      required final List<GemstoneRemedy> gemstones,
      required final List<String> charities,
      required final List<String> worship,
      required final List<String> behavioral}) = _$RemedyModelImpl;

  factory _RemedyModel.fromJson(Map<String, dynamic> json) =
      _$RemedyModelImpl.fromJson;

  @override
  String get planet;
  @override
  String get reason;
  @override
  List<MantraRemedy> get mantras;
  @override
  List<GemstoneRemedy> get gemstones;
  @override
  List<String> get charities;
  @override
  List<String> get worship;
  @override
  List<String> get behavioral;

  /// Create a copy of RemedyModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$RemedyModelImplCopyWith<_$RemedyModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
