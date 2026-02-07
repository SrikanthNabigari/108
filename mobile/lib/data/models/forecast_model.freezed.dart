// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'forecast_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

AreaRating _$AreaRatingFromJson(Map<String, dynamic> json) {
  return _AreaRating.fromJson(json);
}

/// @nodoc
mixin _$AreaRating {
  String get area =>
      throw _privateConstructorUsedError; // 'career', 'finance', 'health', 'relationships', 'spiritual'
  double get score => throw _privateConstructorUsedError; // 0-10
  String? get trend => throw _privateConstructorUsedError;

  /// Serializes this AreaRating to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AreaRating
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AreaRatingCopyWith<AreaRating> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AreaRatingCopyWith<$Res> {
  factory $AreaRatingCopyWith(
          AreaRating value, $Res Function(AreaRating) then) =
      _$AreaRatingCopyWithImpl<$Res, AreaRating>;
  @useResult
  $Res call({String area, double score, String? trend});
}

/// @nodoc
class _$AreaRatingCopyWithImpl<$Res, $Val extends AreaRating>
    implements $AreaRatingCopyWith<$Res> {
  _$AreaRatingCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AreaRating
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? area = null,
    Object? score = null,
    Object? trend = freezed,
  }) {
    return _then(_value.copyWith(
      area: null == area
          ? _value.area
          : area // ignore: cast_nullable_to_non_nullable
              as String,
      score: null == score
          ? _value.score
          : score // ignore: cast_nullable_to_non_nullable
              as double,
      trend: freezed == trend
          ? _value.trend
          : trend // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AreaRatingImplCopyWith<$Res>
    implements $AreaRatingCopyWith<$Res> {
  factory _$$AreaRatingImplCopyWith(
          _$AreaRatingImpl value, $Res Function(_$AreaRatingImpl) then) =
      __$$AreaRatingImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String area, double score, String? trend});
}

/// @nodoc
class __$$AreaRatingImplCopyWithImpl<$Res>
    extends _$AreaRatingCopyWithImpl<$Res, _$AreaRatingImpl>
    implements _$$AreaRatingImplCopyWith<$Res> {
  __$$AreaRatingImplCopyWithImpl(
      _$AreaRatingImpl _value, $Res Function(_$AreaRatingImpl) _then)
      : super(_value, _then);

  /// Create a copy of AreaRating
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? area = null,
    Object? score = null,
    Object? trend = freezed,
  }) {
    return _then(_$AreaRatingImpl(
      area: null == area
          ? _value.area
          : area // ignore: cast_nullable_to_non_nullable
              as String,
      score: null == score
          ? _value.score
          : score // ignore: cast_nullable_to_non_nullable
              as double,
      trend: freezed == trend
          ? _value.trend
          : trend // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AreaRatingImpl implements _AreaRating {
  const _$AreaRatingImpl({required this.area, required this.score, this.trend});

  factory _$AreaRatingImpl.fromJson(Map<String, dynamic> json) =>
      _$$AreaRatingImplFromJson(json);

  @override
  final String area;
// 'career', 'finance', 'health', 'relationships', 'spiritual'
  @override
  final double score;
// 0-10
  @override
  final String? trend;

  @override
  String toString() {
    return 'AreaRating(area: $area, score: $score, trend: $trend)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AreaRatingImpl &&
            (identical(other.area, area) || other.area == area) &&
            (identical(other.score, score) || other.score == score) &&
            (identical(other.trend, trend) || other.trend == trend));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, area, score, trend);

  /// Create a copy of AreaRating
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AreaRatingImplCopyWith<_$AreaRatingImpl> get copyWith =>
      __$$AreaRatingImplCopyWithImpl<_$AreaRatingImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AreaRatingImplToJson(
      this,
    );
  }
}

abstract class _AreaRating implements AreaRating {
  const factory _AreaRating(
      {required final String area,
      required final double score,
      final String? trend}) = _$AreaRatingImpl;

  factory _AreaRating.fromJson(Map<String, dynamic> json) =
      _$AreaRatingImpl.fromJson;

  @override
  String
      get area; // 'career', 'finance', 'health', 'relationships', 'spiritual'
  @override
  double get score; // 0-10
  @override
  String? get trend;

  /// Create a copy of AreaRating
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AreaRatingImplCopyWith<_$AreaRatingImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PanchangaData _$PanchangaDataFromJson(Map<String, dynamic> json) {
  return _PanchangaData.fromJson(json);
}

/// @nodoc
mixin _$PanchangaData {
  String? get tithi => throw _privateConstructorUsedError;
  String? get nakshatra => throw _privateConstructorUsedError;
  String? get yoga => throw _privateConstructorUsedError;
  String? get karana => throw _privateConstructorUsedError;
  String? get vara => throw _privateConstructorUsedError;

  /// Serializes this PanchangaData to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PanchangaData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PanchangaDataCopyWith<PanchangaData> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PanchangaDataCopyWith<$Res> {
  factory $PanchangaDataCopyWith(
          PanchangaData value, $Res Function(PanchangaData) then) =
      _$PanchangaDataCopyWithImpl<$Res, PanchangaData>;
  @useResult
  $Res call(
      {String? tithi,
      String? nakshatra,
      String? yoga,
      String? karana,
      String? vara});
}

/// @nodoc
class _$PanchangaDataCopyWithImpl<$Res, $Val extends PanchangaData>
    implements $PanchangaDataCopyWith<$Res> {
  _$PanchangaDataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PanchangaData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? tithi = freezed,
    Object? nakshatra = freezed,
    Object? yoga = freezed,
    Object? karana = freezed,
    Object? vara = freezed,
  }) {
    return _then(_value.copyWith(
      tithi: freezed == tithi
          ? _value.tithi
          : tithi // ignore: cast_nullable_to_non_nullable
              as String?,
      nakshatra: freezed == nakshatra
          ? _value.nakshatra
          : nakshatra // ignore: cast_nullable_to_non_nullable
              as String?,
      yoga: freezed == yoga
          ? _value.yoga
          : yoga // ignore: cast_nullable_to_non_nullable
              as String?,
      karana: freezed == karana
          ? _value.karana
          : karana // ignore: cast_nullable_to_non_nullable
              as String?,
      vara: freezed == vara
          ? _value.vara
          : vara // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PanchangaDataImplCopyWith<$Res>
    implements $PanchangaDataCopyWith<$Res> {
  factory _$$PanchangaDataImplCopyWith(
          _$PanchangaDataImpl value, $Res Function(_$PanchangaDataImpl) then) =
      __$$PanchangaDataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String? tithi,
      String? nakshatra,
      String? yoga,
      String? karana,
      String? vara});
}

/// @nodoc
class __$$PanchangaDataImplCopyWithImpl<$Res>
    extends _$PanchangaDataCopyWithImpl<$Res, _$PanchangaDataImpl>
    implements _$$PanchangaDataImplCopyWith<$Res> {
  __$$PanchangaDataImplCopyWithImpl(
      _$PanchangaDataImpl _value, $Res Function(_$PanchangaDataImpl) _then)
      : super(_value, _then);

  /// Create a copy of PanchangaData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? tithi = freezed,
    Object? nakshatra = freezed,
    Object? yoga = freezed,
    Object? karana = freezed,
    Object? vara = freezed,
  }) {
    return _then(_$PanchangaDataImpl(
      tithi: freezed == tithi
          ? _value.tithi
          : tithi // ignore: cast_nullable_to_non_nullable
              as String?,
      nakshatra: freezed == nakshatra
          ? _value.nakshatra
          : nakshatra // ignore: cast_nullable_to_non_nullable
              as String?,
      yoga: freezed == yoga
          ? _value.yoga
          : yoga // ignore: cast_nullable_to_non_nullable
              as String?,
      karana: freezed == karana
          ? _value.karana
          : karana // ignore: cast_nullable_to_non_nullable
              as String?,
      vara: freezed == vara
          ? _value.vara
          : vara // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PanchangaDataImpl implements _PanchangaData {
  const _$PanchangaDataImpl(
      {this.tithi, this.nakshatra, this.yoga, this.karana, this.vara});

  factory _$PanchangaDataImpl.fromJson(Map<String, dynamic> json) =>
      _$$PanchangaDataImplFromJson(json);

  @override
  final String? tithi;
  @override
  final String? nakshatra;
  @override
  final String? yoga;
  @override
  final String? karana;
  @override
  final String? vara;

  @override
  String toString() {
    return 'PanchangaData(tithi: $tithi, nakshatra: $nakshatra, yoga: $yoga, karana: $karana, vara: $vara)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PanchangaDataImpl &&
            (identical(other.tithi, tithi) || other.tithi == tithi) &&
            (identical(other.nakshatra, nakshatra) ||
                other.nakshatra == nakshatra) &&
            (identical(other.yoga, yoga) || other.yoga == yoga) &&
            (identical(other.karana, karana) || other.karana == karana) &&
            (identical(other.vara, vara) || other.vara == vara));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, tithi, nakshatra, yoga, karana, vara);

  /// Create a copy of PanchangaData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PanchangaDataImplCopyWith<_$PanchangaDataImpl> get copyWith =>
      __$$PanchangaDataImplCopyWithImpl<_$PanchangaDataImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PanchangaDataImplToJson(
      this,
    );
  }
}

abstract class _PanchangaData implements PanchangaData {
  const factory _PanchangaData(
      {final String? tithi,
      final String? nakshatra,
      final String? yoga,
      final String? karana,
      final String? vara}) = _$PanchangaDataImpl;

  factory _PanchangaData.fromJson(Map<String, dynamic> json) =
      _$PanchangaDataImpl.fromJson;

  @override
  String? get tithi;
  @override
  String? get nakshatra;
  @override
  String? get yoga;
  @override
  String? get karana;
  @override
  String? get vara;

  /// Create a copy of PanchangaData
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PanchangaDataImplCopyWith<_$PanchangaDataImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ForecastModel _$ForecastModelFromJson(Map<String, dynamic> json) {
  return _ForecastModel.fromJson(json);
}

/// @nodoc
mixin _$ForecastModel {
  String get forecastType =>
      throw _privateConstructorUsedError; // 'daily', 'weekly', 'monthly', 'yearly'
  DateTime get date => throw _privateConstructorUsedError;
  double get dayRating => throw _privateConstructorUsedError; // 0-10
  Map<String, AreaRating> get areaRatings => throw _privateConstructorUsedError;
  List<String> get recommendations => throw _privateConstructorUsedError;
  Map<String, dynamic> get details => throw _privateConstructorUsedError;
  PanchangaData? get panchanga => throw _privateConstructorUsedError;

  /// Serializes this ForecastModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ForecastModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ForecastModelCopyWith<ForecastModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ForecastModelCopyWith<$Res> {
  factory $ForecastModelCopyWith(
          ForecastModel value, $Res Function(ForecastModel) then) =
      _$ForecastModelCopyWithImpl<$Res, ForecastModel>;
  @useResult
  $Res call(
      {String forecastType,
      DateTime date,
      double dayRating,
      Map<String, AreaRating> areaRatings,
      List<String> recommendations,
      Map<String, dynamic> details,
      PanchangaData? panchanga});

  $PanchangaDataCopyWith<$Res>? get panchanga;
}

/// @nodoc
class _$ForecastModelCopyWithImpl<$Res, $Val extends ForecastModel>
    implements $ForecastModelCopyWith<$Res> {
  _$ForecastModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ForecastModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? forecastType = null,
    Object? date = null,
    Object? dayRating = null,
    Object? areaRatings = null,
    Object? recommendations = null,
    Object? details = null,
    Object? panchanga = freezed,
  }) {
    return _then(_value.copyWith(
      forecastType: null == forecastType
          ? _value.forecastType
          : forecastType // ignore: cast_nullable_to_non_nullable
              as String,
      date: null == date
          ? _value.date
          : date // ignore: cast_nullable_to_non_nullable
              as DateTime,
      dayRating: null == dayRating
          ? _value.dayRating
          : dayRating // ignore: cast_nullable_to_non_nullable
              as double,
      areaRatings: null == areaRatings
          ? _value.areaRatings
          : areaRatings // ignore: cast_nullable_to_non_nullable
              as Map<String, AreaRating>,
      recommendations: null == recommendations
          ? _value.recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as List<String>,
      details: null == details
          ? _value.details
          : details // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      panchanga: freezed == panchanga
          ? _value.panchanga
          : panchanga // ignore: cast_nullable_to_non_nullable
              as PanchangaData?,
    ) as $Val);
  }

  /// Create a copy of ForecastModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $PanchangaDataCopyWith<$Res>? get panchanga {
    if (_value.panchanga == null) {
      return null;
    }

    return $PanchangaDataCopyWith<$Res>(_value.panchanga!, (value) {
      return _then(_value.copyWith(panchanga: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$ForecastModelImplCopyWith<$Res>
    implements $ForecastModelCopyWith<$Res> {
  factory _$$ForecastModelImplCopyWith(
          _$ForecastModelImpl value, $Res Function(_$ForecastModelImpl) then) =
      __$$ForecastModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String forecastType,
      DateTime date,
      double dayRating,
      Map<String, AreaRating> areaRatings,
      List<String> recommendations,
      Map<String, dynamic> details,
      PanchangaData? panchanga});

  @override
  $PanchangaDataCopyWith<$Res>? get panchanga;
}

/// @nodoc
class __$$ForecastModelImplCopyWithImpl<$Res>
    extends _$ForecastModelCopyWithImpl<$Res, _$ForecastModelImpl>
    implements _$$ForecastModelImplCopyWith<$Res> {
  __$$ForecastModelImplCopyWithImpl(
      _$ForecastModelImpl _value, $Res Function(_$ForecastModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of ForecastModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? forecastType = null,
    Object? date = null,
    Object? dayRating = null,
    Object? areaRatings = null,
    Object? recommendations = null,
    Object? details = null,
    Object? panchanga = freezed,
  }) {
    return _then(_$ForecastModelImpl(
      forecastType: null == forecastType
          ? _value.forecastType
          : forecastType // ignore: cast_nullable_to_non_nullable
              as String,
      date: null == date
          ? _value.date
          : date // ignore: cast_nullable_to_non_nullable
              as DateTime,
      dayRating: null == dayRating
          ? _value.dayRating
          : dayRating // ignore: cast_nullable_to_non_nullable
              as double,
      areaRatings: null == areaRatings
          ? _value._areaRatings
          : areaRatings // ignore: cast_nullable_to_non_nullable
              as Map<String, AreaRating>,
      recommendations: null == recommendations
          ? _value._recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as List<String>,
      details: null == details
          ? _value._details
          : details // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      panchanga: freezed == panchanga
          ? _value.panchanga
          : panchanga // ignore: cast_nullable_to_non_nullable
              as PanchangaData?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ForecastModelImpl implements _ForecastModel {
  const _$ForecastModelImpl(
      {required this.forecastType,
      required this.date,
      required this.dayRating,
      required final Map<String, AreaRating> areaRatings,
      required final List<String> recommendations,
      required final Map<String, dynamic> details,
      this.panchanga})
      : _areaRatings = areaRatings,
        _recommendations = recommendations,
        _details = details;

  factory _$ForecastModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$ForecastModelImplFromJson(json);

  @override
  final String forecastType;
// 'daily', 'weekly', 'monthly', 'yearly'
  @override
  final DateTime date;
  @override
  final double dayRating;
// 0-10
  final Map<String, AreaRating> _areaRatings;
// 0-10
  @override
  Map<String, AreaRating> get areaRatings {
    if (_areaRatings is EqualUnmodifiableMapView) return _areaRatings;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_areaRatings);
  }

  final List<String> _recommendations;
  @override
  List<String> get recommendations {
    if (_recommendations is EqualUnmodifiableListView) return _recommendations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_recommendations);
  }

  final Map<String, dynamic> _details;
  @override
  Map<String, dynamic> get details {
    if (_details is EqualUnmodifiableMapView) return _details;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_details);
  }

  @override
  final PanchangaData? panchanga;

  @override
  String toString() {
    return 'ForecastModel(forecastType: $forecastType, date: $date, dayRating: $dayRating, areaRatings: $areaRatings, recommendations: $recommendations, details: $details, panchanga: $panchanga)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ForecastModelImpl &&
            (identical(other.forecastType, forecastType) ||
                other.forecastType == forecastType) &&
            (identical(other.date, date) || other.date == date) &&
            (identical(other.dayRating, dayRating) ||
                other.dayRating == dayRating) &&
            const DeepCollectionEquality()
                .equals(other._areaRatings, _areaRatings) &&
            const DeepCollectionEquality()
                .equals(other._recommendations, _recommendations) &&
            const DeepCollectionEquality().equals(other._details, _details) &&
            (identical(other.panchanga, panchanga) ||
                other.panchanga == panchanga));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      forecastType,
      date,
      dayRating,
      const DeepCollectionEquality().hash(_areaRatings),
      const DeepCollectionEquality().hash(_recommendations),
      const DeepCollectionEquality().hash(_details),
      panchanga);

  /// Create a copy of ForecastModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ForecastModelImplCopyWith<_$ForecastModelImpl> get copyWith =>
      __$$ForecastModelImplCopyWithImpl<_$ForecastModelImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ForecastModelImplToJson(
      this,
    );
  }
}

abstract class _ForecastModel implements ForecastModel {
  const factory _ForecastModel(
      {required final String forecastType,
      required final DateTime date,
      required final double dayRating,
      required final Map<String, AreaRating> areaRatings,
      required final List<String> recommendations,
      required final Map<String, dynamic> details,
      final PanchangaData? panchanga}) = _$ForecastModelImpl;

  factory _ForecastModel.fromJson(Map<String, dynamic> json) =
      _$ForecastModelImpl.fromJson;

  @override
  String get forecastType; // 'daily', 'weekly', 'monthly', 'yearly'
  @override
  DateTime get date;
  @override
  double get dayRating; // 0-10
  @override
  Map<String, AreaRating> get areaRatings;
  @override
  List<String> get recommendations;
  @override
  Map<String, dynamic> get details;
  @override
  PanchangaData? get panchanga;

  /// Create a copy of ForecastModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ForecastModelImplCopyWith<_$ForecastModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
