// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'compatibility_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

KutaScore _$KutaScoreFromJson(Map<String, dynamic> json) {
  return _KutaScore.fromJson(json);
}

/// @nodoc
mixin _$KutaScore {
  String get name => throw _privateConstructorUsedError;
  double get obtained => throw _privateConstructorUsedError;
  double get maximum => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;

  /// Serializes this KutaScore to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of KutaScore
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $KutaScoreCopyWith<KutaScore> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $KutaScoreCopyWith<$Res> {
  factory $KutaScoreCopyWith(KutaScore value, $Res Function(KutaScore) then) =
      _$KutaScoreCopyWithImpl<$Res, KutaScore>;
  @useResult
  $Res call(
      {String name, double obtained, double maximum, String? description});
}

/// @nodoc
class _$KutaScoreCopyWithImpl<$Res, $Val extends KutaScore>
    implements $KutaScoreCopyWith<$Res> {
  _$KutaScoreCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of KutaScore
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? obtained = null,
    Object? maximum = null,
    Object? description = freezed,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      obtained: null == obtained
          ? _value.obtained
          : obtained // ignore: cast_nullable_to_non_nullable
              as double,
      maximum: null == maximum
          ? _value.maximum
          : maximum // ignore: cast_nullable_to_non_nullable
              as double,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$KutaScoreImplCopyWith<$Res>
    implements $KutaScoreCopyWith<$Res> {
  factory _$$KutaScoreImplCopyWith(
          _$KutaScoreImpl value, $Res Function(_$KutaScoreImpl) then) =
      __$$KutaScoreImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name, double obtained, double maximum, String? description});
}

/// @nodoc
class __$$KutaScoreImplCopyWithImpl<$Res>
    extends _$KutaScoreCopyWithImpl<$Res, _$KutaScoreImpl>
    implements _$$KutaScoreImplCopyWith<$Res> {
  __$$KutaScoreImplCopyWithImpl(
      _$KutaScoreImpl _value, $Res Function(_$KutaScoreImpl) _then)
      : super(_value, _then);

  /// Create a copy of KutaScore
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? obtained = null,
    Object? maximum = null,
    Object? description = freezed,
  }) {
    return _then(_$KutaScoreImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      obtained: null == obtained
          ? _value.obtained
          : obtained // ignore: cast_nullable_to_non_nullable
              as double,
      maximum: null == maximum
          ? _value.maximum
          : maximum // ignore: cast_nullable_to_non_nullable
              as double,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$KutaScoreImpl implements _KutaScore {
  const _$KutaScoreImpl(
      {required this.name,
      required this.obtained,
      required this.maximum,
      this.description});

  factory _$KutaScoreImpl.fromJson(Map<String, dynamic> json) =>
      _$$KutaScoreImplFromJson(json);

  @override
  final String name;
  @override
  final double obtained;
  @override
  final double maximum;
  @override
  final String? description;

  @override
  String toString() {
    return 'KutaScore(name: $name, obtained: $obtained, maximum: $maximum, description: $description)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$KutaScoreImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.obtained, obtained) ||
                other.obtained == obtained) &&
            (identical(other.maximum, maximum) || other.maximum == maximum) &&
            (identical(other.description, description) ||
                other.description == description));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, name, obtained, maximum, description);

  /// Create a copy of KutaScore
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$KutaScoreImplCopyWith<_$KutaScoreImpl> get copyWith =>
      __$$KutaScoreImplCopyWithImpl<_$KutaScoreImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$KutaScoreImplToJson(
      this,
    );
  }
}

abstract class _KutaScore implements KutaScore {
  const factory _KutaScore(
      {required final String name,
      required final double obtained,
      required final double maximum,
      final String? description}) = _$KutaScoreImpl;

  factory _KutaScore.fromJson(Map<String, dynamic> json) =
      _$KutaScoreImpl.fromJson;

  @override
  String get name;
  @override
  double get obtained;
  @override
  double get maximum;
  @override
  String? get description;

  /// Create a copy of KutaScore
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$KutaScoreImplCopyWith<_$KutaScoreImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CompatibilityModel _$CompatibilityModelFromJson(Map<String, dynamic> json) {
  return _CompatibilityModel.fromJson(json);
}

/// @nodoc
mixin _$CompatibilityModel {
  List<KutaScore> get kutaScores => throw _privateConstructorUsedError;
  double get totalObtained => throw _privateConstructorUsedError;
  double get totalMaximum => throw _privateConstructorUsedError;
  String get verdict => throw _privateConstructorUsedError;
  String? get summary => throw _privateConstructorUsedError;

  /// Serializes this CompatibilityModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CompatibilityModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CompatibilityModelCopyWith<CompatibilityModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CompatibilityModelCopyWith<$Res> {
  factory $CompatibilityModelCopyWith(
          CompatibilityModel value, $Res Function(CompatibilityModel) then) =
      _$CompatibilityModelCopyWithImpl<$Res, CompatibilityModel>;
  @useResult
  $Res call(
      {List<KutaScore> kutaScores,
      double totalObtained,
      double totalMaximum,
      String verdict,
      String? summary});
}

/// @nodoc
class _$CompatibilityModelCopyWithImpl<$Res, $Val extends CompatibilityModel>
    implements $CompatibilityModelCopyWith<$Res> {
  _$CompatibilityModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CompatibilityModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? kutaScores = null,
    Object? totalObtained = null,
    Object? totalMaximum = null,
    Object? verdict = null,
    Object? summary = freezed,
  }) {
    return _then(_value.copyWith(
      kutaScores: null == kutaScores
          ? _value.kutaScores
          : kutaScores // ignore: cast_nullable_to_non_nullable
              as List<KutaScore>,
      totalObtained: null == totalObtained
          ? _value.totalObtained
          : totalObtained // ignore: cast_nullable_to_non_nullable
              as double,
      totalMaximum: null == totalMaximum
          ? _value.totalMaximum
          : totalMaximum // ignore: cast_nullable_to_non_nullable
              as double,
      verdict: null == verdict
          ? _value.verdict
          : verdict // ignore: cast_nullable_to_non_nullable
              as String,
      summary: freezed == summary
          ? _value.summary
          : summary // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CompatibilityModelImplCopyWith<$Res>
    implements $CompatibilityModelCopyWith<$Res> {
  factory _$$CompatibilityModelImplCopyWith(_$CompatibilityModelImpl value,
          $Res Function(_$CompatibilityModelImpl) then) =
      __$$CompatibilityModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<KutaScore> kutaScores,
      double totalObtained,
      double totalMaximum,
      String verdict,
      String? summary});
}

/// @nodoc
class __$$CompatibilityModelImplCopyWithImpl<$Res>
    extends _$CompatibilityModelCopyWithImpl<$Res, _$CompatibilityModelImpl>
    implements _$$CompatibilityModelImplCopyWith<$Res> {
  __$$CompatibilityModelImplCopyWithImpl(_$CompatibilityModelImpl _value,
      $Res Function(_$CompatibilityModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of CompatibilityModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? kutaScores = null,
    Object? totalObtained = null,
    Object? totalMaximum = null,
    Object? verdict = null,
    Object? summary = freezed,
  }) {
    return _then(_$CompatibilityModelImpl(
      kutaScores: null == kutaScores
          ? _value._kutaScores
          : kutaScores // ignore: cast_nullable_to_non_nullable
              as List<KutaScore>,
      totalObtained: null == totalObtained
          ? _value.totalObtained
          : totalObtained // ignore: cast_nullable_to_non_nullable
              as double,
      totalMaximum: null == totalMaximum
          ? _value.totalMaximum
          : totalMaximum // ignore: cast_nullable_to_non_nullable
              as double,
      verdict: null == verdict
          ? _value.verdict
          : verdict // ignore: cast_nullable_to_non_nullable
              as String,
      summary: freezed == summary
          ? _value.summary
          : summary // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CompatibilityModelImpl implements _CompatibilityModel {
  const _$CompatibilityModelImpl(
      {required final List<KutaScore> kutaScores,
      required this.totalObtained,
      required this.totalMaximum,
      required this.verdict,
      this.summary})
      : _kutaScores = kutaScores;

  factory _$CompatibilityModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$CompatibilityModelImplFromJson(json);

  final List<KutaScore> _kutaScores;
  @override
  List<KutaScore> get kutaScores {
    if (_kutaScores is EqualUnmodifiableListView) return _kutaScores;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_kutaScores);
  }

  @override
  final double totalObtained;
  @override
  final double totalMaximum;
  @override
  final String verdict;
  @override
  final String? summary;

  @override
  String toString() {
    return 'CompatibilityModel(kutaScores: $kutaScores, totalObtained: $totalObtained, totalMaximum: $totalMaximum, verdict: $verdict, summary: $summary)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CompatibilityModelImpl &&
            const DeepCollectionEquality()
                .equals(other._kutaScores, _kutaScores) &&
            (identical(other.totalObtained, totalObtained) ||
                other.totalObtained == totalObtained) &&
            (identical(other.totalMaximum, totalMaximum) ||
                other.totalMaximum == totalMaximum) &&
            (identical(other.verdict, verdict) || other.verdict == verdict) &&
            (identical(other.summary, summary) || other.summary == summary));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_kutaScores),
      totalObtained,
      totalMaximum,
      verdict,
      summary);

  /// Create a copy of CompatibilityModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CompatibilityModelImplCopyWith<_$CompatibilityModelImpl> get copyWith =>
      __$$CompatibilityModelImplCopyWithImpl<_$CompatibilityModelImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CompatibilityModelImplToJson(
      this,
    );
  }
}

abstract class _CompatibilityModel implements CompatibilityModel {
  const factory _CompatibilityModel(
      {required final List<KutaScore> kutaScores,
      required final double totalObtained,
      required final double totalMaximum,
      required final String verdict,
      final String? summary}) = _$CompatibilityModelImpl;

  factory _CompatibilityModel.fromJson(Map<String, dynamic> json) =
      _$CompatibilityModelImpl.fromJson;

  @override
  List<KutaScore> get kutaScores;
  @override
  double get totalObtained;
  @override
  double get totalMaximum;
  @override
  String get verdict;
  @override
  String? get summary;

  /// Create a copy of CompatibilityModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CompatibilityModelImplCopyWith<_$CompatibilityModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
