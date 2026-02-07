// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'reports_provider.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

ReportInfo _$ReportInfoFromJson(Map<String, dynamic> json) {
  return _ReportInfo.fromJson(json);
}

/// @nodoc
mixin _$ReportInfo {
  String get reportType => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  int get credits => throw _privateConstructorUsedError;
  double get money => throw _privateConstructorUsedError;

  /// Serializes this ReportInfo to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ReportInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ReportInfoCopyWith<ReportInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ReportInfoCopyWith<$Res> {
  factory $ReportInfoCopyWith(
          ReportInfo value, $Res Function(ReportInfo) then) =
      _$ReportInfoCopyWithImpl<$Res, ReportInfo>;
  @useResult
  $Res call(
      {String reportType,
      String title,
      String? description,
      int credits,
      double money});
}

/// @nodoc
class _$ReportInfoCopyWithImpl<$Res, $Val extends ReportInfo>
    implements $ReportInfoCopyWith<$Res> {
  _$ReportInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ReportInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? reportType = null,
    Object? title = null,
    Object? description = freezed,
    Object? credits = null,
    Object? money = null,
  }) {
    return _then(_value.copyWith(
      reportType: null == reportType
          ? _value.reportType
          : reportType // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      credits: null == credits
          ? _value.credits
          : credits // ignore: cast_nullable_to_non_nullable
              as int,
      money: null == money
          ? _value.money
          : money // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ReportInfoImplCopyWith<$Res>
    implements $ReportInfoCopyWith<$Res> {
  factory _$$ReportInfoImplCopyWith(
          _$ReportInfoImpl value, $Res Function(_$ReportInfoImpl) then) =
      __$$ReportInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String reportType,
      String title,
      String? description,
      int credits,
      double money});
}

/// @nodoc
class __$$ReportInfoImplCopyWithImpl<$Res>
    extends _$ReportInfoCopyWithImpl<$Res, _$ReportInfoImpl>
    implements _$$ReportInfoImplCopyWith<$Res> {
  __$$ReportInfoImplCopyWithImpl(
      _$ReportInfoImpl _value, $Res Function(_$ReportInfoImpl) _then)
      : super(_value, _then);

  /// Create a copy of ReportInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? reportType = null,
    Object? title = null,
    Object? description = freezed,
    Object? credits = null,
    Object? money = null,
  }) {
    return _then(_$ReportInfoImpl(
      reportType: null == reportType
          ? _value.reportType
          : reportType // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      credits: null == credits
          ? _value.credits
          : credits // ignore: cast_nullable_to_non_nullable
              as int,
      money: null == money
          ? _value.money
          : money // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ReportInfoImpl implements _ReportInfo {
  const _$ReportInfoImpl(
      {required this.reportType,
      required this.title,
      this.description,
      required this.credits,
      required this.money});

  factory _$ReportInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$ReportInfoImplFromJson(json);

  @override
  final String reportType;
  @override
  final String title;
  @override
  final String? description;
  @override
  final int credits;
  @override
  final double money;

  @override
  String toString() {
    return 'ReportInfo(reportType: $reportType, title: $title, description: $description, credits: $credits, money: $money)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ReportInfoImpl &&
            (identical(other.reportType, reportType) ||
                other.reportType == reportType) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.credits, credits) || other.credits == credits) &&
            (identical(other.money, money) || other.money == money));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, reportType, title, description, credits, money);

  /// Create a copy of ReportInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ReportInfoImplCopyWith<_$ReportInfoImpl> get copyWith =>
      __$$ReportInfoImplCopyWithImpl<_$ReportInfoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ReportInfoImplToJson(
      this,
    );
  }
}

abstract class _ReportInfo implements ReportInfo {
  const factory _ReportInfo(
      {required final String reportType,
      required final String title,
      final String? description,
      required final int credits,
      required final double money}) = _$ReportInfoImpl;

  factory _ReportInfo.fromJson(Map<String, dynamic> json) =
      _$ReportInfoImpl.fromJson;

  @override
  String get reportType;
  @override
  String get title;
  @override
  String? get description;
  @override
  int get credits;
  @override
  double get money;

  /// Create a copy of ReportInfo
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ReportInfoImplCopyWith<_$ReportInfoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
