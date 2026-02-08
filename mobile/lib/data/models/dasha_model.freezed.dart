// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dasha_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

DashaPeriodModel _$DashaPeriodModelFromJson(Map<String, dynamic> json) {
  return _DashaPeriodModel.fromJson(json);
}

/// @nodoc
mixin _$DashaPeriodModel {
  String get planet => throw _privateConstructorUsedError;
  String get level => throw _privateConstructorUsedError;
  String get startDate => throw _privateConstructorUsedError;
  String get endDate => throw _privateConstructorUsedError;
  bool get isActive => throw _privateConstructorUsedError;

  /// Serializes this DashaPeriodModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DashaPeriodModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DashaPeriodModelCopyWith<DashaPeriodModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DashaPeriodModelCopyWith<$Res> {
  factory $DashaPeriodModelCopyWith(
          DashaPeriodModel value, $Res Function(DashaPeriodModel) then) =
      _$DashaPeriodModelCopyWithImpl<$Res, DashaPeriodModel>;
  @useResult
  $Res call(
      {String planet,
      String level,
      String startDate,
      String endDate,
      bool isActive});
}

/// @nodoc
class _$DashaPeriodModelCopyWithImpl<$Res, $Val extends DashaPeriodModel>
    implements $DashaPeriodModelCopyWith<$Res> {
  _$DashaPeriodModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DashaPeriodModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? planet = null,
    Object? level = null,
    Object? startDate = null,
    Object? endDate = null,
    Object? isActive = null,
  }) {
    return _then(_value.copyWith(
      planet: null == planet
          ? _value.planet
          : planet // ignore: cast_nullable_to_non_nullable
              as String,
      level: null == level
          ? _value.level
          : level // ignore: cast_nullable_to_non_nullable
              as String,
      startDate: null == startDate
          ? _value.startDate
          : startDate // ignore: cast_nullable_to_non_nullable
              as String,
      endDate: null == endDate
          ? _value.endDate
          : endDate // ignore: cast_nullable_to_non_nullable
              as String,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DashaPeriodModelImplCopyWith<$Res>
    implements $DashaPeriodModelCopyWith<$Res> {
  factory _$$DashaPeriodModelImplCopyWith(_$DashaPeriodModelImpl value,
          $Res Function(_$DashaPeriodModelImpl) then) =
      __$$DashaPeriodModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String planet,
      String level,
      String startDate,
      String endDate,
      bool isActive});
}

/// @nodoc
class __$$DashaPeriodModelImplCopyWithImpl<$Res>
    extends _$DashaPeriodModelCopyWithImpl<$Res, _$DashaPeriodModelImpl>
    implements _$$DashaPeriodModelImplCopyWith<$Res> {
  __$$DashaPeriodModelImplCopyWithImpl(_$DashaPeriodModelImpl _value,
      $Res Function(_$DashaPeriodModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of DashaPeriodModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? planet = null,
    Object? level = null,
    Object? startDate = null,
    Object? endDate = null,
    Object? isActive = null,
  }) {
    return _then(_$DashaPeriodModelImpl(
      planet: null == planet
          ? _value.planet
          : planet // ignore: cast_nullable_to_non_nullable
              as String,
      level: null == level
          ? _value.level
          : level // ignore: cast_nullable_to_non_nullable
              as String,
      startDate: null == startDate
          ? _value.startDate
          : startDate // ignore: cast_nullable_to_non_nullable
              as String,
      endDate: null == endDate
          ? _value.endDate
          : endDate // ignore: cast_nullable_to_non_nullable
              as String,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DashaPeriodModelImpl implements _DashaPeriodModel {
  const _$DashaPeriodModelImpl(
      {required this.planet,
      required this.level,
      required this.startDate,
      required this.endDate,
      this.isActive = false});

  factory _$DashaPeriodModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$DashaPeriodModelImplFromJson(json);

  @override
  final String planet;
  @override
  final String level;
  @override
  final String startDate;
  @override
  final String endDate;
  @override
  @JsonKey()
  final bool isActive;

  @override
  String toString() {
    return 'DashaPeriodModel(planet: $planet, level: $level, startDate: $startDate, endDate: $endDate, isActive: $isActive)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DashaPeriodModelImpl &&
            (identical(other.planet, planet) || other.planet == planet) &&
            (identical(other.level, level) || other.level == level) &&
            (identical(other.startDate, startDate) ||
                other.startDate == startDate) &&
            (identical(other.endDate, endDate) || other.endDate == endDate) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, planet, level, startDate, endDate, isActive);

  /// Create a copy of DashaPeriodModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DashaPeriodModelImplCopyWith<_$DashaPeriodModelImpl> get copyWith =>
      __$$DashaPeriodModelImplCopyWithImpl<_$DashaPeriodModelImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DashaPeriodModelImplToJson(
      this,
    );
  }
}

abstract class _DashaPeriodModel implements DashaPeriodModel {
  const factory _DashaPeriodModel(
      {required final String planet,
      required final String level,
      required final String startDate,
      required final String endDate,
      final bool isActive}) = _$DashaPeriodModelImpl;

  factory _DashaPeriodModel.fromJson(Map<String, dynamic> json) =
      _$DashaPeriodModelImpl.fromJson;

  @override
  String get planet;
  @override
  String get level;
  @override
  String get startDate;
  @override
  String get endDate;
  @override
  bool get isActive;

  /// Create a copy of DashaPeriodModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DashaPeriodModelImplCopyWith<_$DashaPeriodModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DashaModel _$DashaModelFromJson(Map<String, dynamic> json) {
  return _DashaModel.fromJson(json);
}

/// @nodoc
mixin _$DashaModel {
  DashaPeriodModel get currentMD => throw _privateConstructorUsedError;
  DashaPeriodModel get currentAD => throw _privateConstructorUsedError;
  DashaPeriodModel get currentPD => throw _privateConstructorUsedError;
  List<DashaPeriodModel> get sequence => throw _privateConstructorUsedError;

  /// Serializes this DashaModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DashaModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DashaModelCopyWith<DashaModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DashaModelCopyWith<$Res> {
  factory $DashaModelCopyWith(
          DashaModel value, $Res Function(DashaModel) then) =
      _$DashaModelCopyWithImpl<$Res, DashaModel>;
  @useResult
  $Res call(
      {DashaPeriodModel currentMD,
      DashaPeriodModel currentAD,
      DashaPeriodModel currentPD,
      List<DashaPeriodModel> sequence});

  $DashaPeriodModelCopyWith<$Res> get currentMD;
  $DashaPeriodModelCopyWith<$Res> get currentAD;
  $DashaPeriodModelCopyWith<$Res> get currentPD;
}

/// @nodoc
class _$DashaModelCopyWithImpl<$Res, $Val extends DashaModel>
    implements $DashaModelCopyWith<$Res> {
  _$DashaModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DashaModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentMD = null,
    Object? currentAD = null,
    Object? currentPD = null,
    Object? sequence = null,
  }) {
    return _then(_value.copyWith(
      currentMD: null == currentMD
          ? _value.currentMD
          : currentMD // ignore: cast_nullable_to_non_nullable
              as DashaPeriodModel,
      currentAD: null == currentAD
          ? _value.currentAD
          : currentAD // ignore: cast_nullable_to_non_nullable
              as DashaPeriodModel,
      currentPD: null == currentPD
          ? _value.currentPD
          : currentPD // ignore: cast_nullable_to_non_nullable
              as DashaPeriodModel,
      sequence: null == sequence
          ? _value.sequence
          : sequence // ignore: cast_nullable_to_non_nullable
              as List<DashaPeriodModel>,
    ) as $Val);
  }

  /// Create a copy of DashaModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $DashaPeriodModelCopyWith<$Res> get currentMD {
    return $DashaPeriodModelCopyWith<$Res>(_value.currentMD, (value) {
      return _then(_value.copyWith(currentMD: value) as $Val);
    });
  }

  /// Create a copy of DashaModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $DashaPeriodModelCopyWith<$Res> get currentAD {
    return $DashaPeriodModelCopyWith<$Res>(_value.currentAD, (value) {
      return _then(_value.copyWith(currentAD: value) as $Val);
    });
  }

  /// Create a copy of DashaModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $DashaPeriodModelCopyWith<$Res> get currentPD {
    return $DashaPeriodModelCopyWith<$Res>(_value.currentPD, (value) {
      return _then(_value.copyWith(currentPD: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$DashaModelImplCopyWith<$Res>
    implements $DashaModelCopyWith<$Res> {
  factory _$$DashaModelImplCopyWith(
          _$DashaModelImpl value, $Res Function(_$DashaModelImpl) then) =
      __$$DashaModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {DashaPeriodModel currentMD,
      DashaPeriodModel currentAD,
      DashaPeriodModel currentPD,
      List<DashaPeriodModel> sequence});

  @override
  $DashaPeriodModelCopyWith<$Res> get currentMD;
  @override
  $DashaPeriodModelCopyWith<$Res> get currentAD;
  @override
  $DashaPeriodModelCopyWith<$Res> get currentPD;
}

/// @nodoc
class __$$DashaModelImplCopyWithImpl<$Res>
    extends _$DashaModelCopyWithImpl<$Res, _$DashaModelImpl>
    implements _$$DashaModelImplCopyWith<$Res> {
  __$$DashaModelImplCopyWithImpl(
      _$DashaModelImpl _value, $Res Function(_$DashaModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of DashaModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentMD = null,
    Object? currentAD = null,
    Object? currentPD = null,
    Object? sequence = null,
  }) {
    return _then(_$DashaModelImpl(
      currentMD: null == currentMD
          ? _value.currentMD
          : currentMD // ignore: cast_nullable_to_non_nullable
              as DashaPeriodModel,
      currentAD: null == currentAD
          ? _value.currentAD
          : currentAD // ignore: cast_nullable_to_non_nullable
              as DashaPeriodModel,
      currentPD: null == currentPD
          ? _value.currentPD
          : currentPD // ignore: cast_nullable_to_non_nullable
              as DashaPeriodModel,
      sequence: null == sequence
          ? _value._sequence
          : sequence // ignore: cast_nullable_to_non_nullable
              as List<DashaPeriodModel>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DashaModelImpl implements _DashaModel {
  const _$DashaModelImpl(
      {required this.currentMD,
      required this.currentAD,
      required this.currentPD,
      required final List<DashaPeriodModel> sequence})
      : _sequence = sequence;

  factory _$DashaModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$DashaModelImplFromJson(json);

  @override
  final DashaPeriodModel currentMD;
  @override
  final DashaPeriodModel currentAD;
  @override
  final DashaPeriodModel currentPD;
  final List<DashaPeriodModel> _sequence;
  @override
  List<DashaPeriodModel> get sequence {
    if (_sequence is EqualUnmodifiableListView) return _sequence;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_sequence);
  }

  @override
  String toString() {
    return 'DashaModel(currentMD: $currentMD, currentAD: $currentAD, currentPD: $currentPD, sequence: $sequence)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DashaModelImpl &&
            (identical(other.currentMD, currentMD) ||
                other.currentMD == currentMD) &&
            (identical(other.currentAD, currentAD) ||
                other.currentAD == currentAD) &&
            (identical(other.currentPD, currentPD) ||
                other.currentPD == currentPD) &&
            const DeepCollectionEquality().equals(other._sequence, _sequence));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, currentMD, currentAD, currentPD,
      const DeepCollectionEquality().hash(_sequence));

  /// Create a copy of DashaModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DashaModelImplCopyWith<_$DashaModelImpl> get copyWith =>
      __$$DashaModelImplCopyWithImpl<_$DashaModelImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DashaModelImplToJson(
      this,
    );
  }
}

abstract class _DashaModel implements DashaModel {
  const factory _DashaModel(
      {required final DashaPeriodModel currentMD,
      required final DashaPeriodModel currentAD,
      required final DashaPeriodModel currentPD,
      required final List<DashaPeriodModel> sequence}) = _$DashaModelImpl;

  factory _DashaModel.fromJson(Map<String, dynamic> json) =
      _$DashaModelImpl.fromJson;

  @override
  DashaPeriodModel get currentMD;
  @override
  DashaPeriodModel get currentAD;
  @override
  DashaPeriodModel get currentPD;
  @override
  List<DashaPeriodModel> get sequence;

  /// Create a copy of DashaModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DashaModelImplCopyWith<_$DashaModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
