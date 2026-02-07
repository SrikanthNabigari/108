// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'config_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

SubscriptionTier _$SubscriptionTierFromJson(Map<String, dynamic> json) {
  return _SubscriptionTier.fromJson(json);
}

/// @nodoc
mixin _$SubscriptionTier {
  String get id =>
      throw _privateConstructorUsedError; // 'free', 'pro', 'premium'
  String get name => throw _privateConstructorUsedError;
  double? get priceMonthly => throw _privateConstructorUsedError;
  double? get priceYearly => throw _privateConstructorUsedError;
  List<String> get features => throw _privateConstructorUsedError;

  /// Serializes this SubscriptionTier to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SubscriptionTier
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SubscriptionTierCopyWith<SubscriptionTier> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SubscriptionTierCopyWith<$Res> {
  factory $SubscriptionTierCopyWith(
          SubscriptionTier value, $Res Function(SubscriptionTier) then) =
      _$SubscriptionTierCopyWithImpl<$Res, SubscriptionTier>;
  @useResult
  $Res call(
      {String id,
      String name,
      double? priceMonthly,
      double? priceYearly,
      List<String> features});
}

/// @nodoc
class _$SubscriptionTierCopyWithImpl<$Res, $Val extends SubscriptionTier>
    implements $SubscriptionTierCopyWith<$Res> {
  _$SubscriptionTierCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SubscriptionTier
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? priceMonthly = freezed,
    Object? priceYearly = freezed,
    Object? features = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      priceMonthly: freezed == priceMonthly
          ? _value.priceMonthly
          : priceMonthly // ignore: cast_nullable_to_non_nullable
              as double?,
      priceYearly: freezed == priceYearly
          ? _value.priceYearly
          : priceYearly // ignore: cast_nullable_to_non_nullable
              as double?,
      features: null == features
          ? _value.features
          : features // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SubscriptionTierImplCopyWith<$Res>
    implements $SubscriptionTierCopyWith<$Res> {
  factory _$$SubscriptionTierImplCopyWith(_$SubscriptionTierImpl value,
          $Res Function(_$SubscriptionTierImpl) then) =
      __$$SubscriptionTierImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      double? priceMonthly,
      double? priceYearly,
      List<String> features});
}

/// @nodoc
class __$$SubscriptionTierImplCopyWithImpl<$Res>
    extends _$SubscriptionTierCopyWithImpl<$Res, _$SubscriptionTierImpl>
    implements _$$SubscriptionTierImplCopyWith<$Res> {
  __$$SubscriptionTierImplCopyWithImpl(_$SubscriptionTierImpl _value,
      $Res Function(_$SubscriptionTierImpl) _then)
      : super(_value, _then);

  /// Create a copy of SubscriptionTier
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? priceMonthly = freezed,
    Object? priceYearly = freezed,
    Object? features = null,
  }) {
    return _then(_$SubscriptionTierImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      priceMonthly: freezed == priceMonthly
          ? _value.priceMonthly
          : priceMonthly // ignore: cast_nullable_to_non_nullable
              as double?,
      priceYearly: freezed == priceYearly
          ? _value.priceYearly
          : priceYearly // ignore: cast_nullable_to_non_nullable
              as double?,
      features: null == features
          ? _value._features
          : features // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SubscriptionTierImpl implements _SubscriptionTier {
  const _$SubscriptionTierImpl(
      {required this.id,
      required this.name,
      this.priceMonthly,
      this.priceYearly,
      required final List<String> features})
      : _features = features;

  factory _$SubscriptionTierImpl.fromJson(Map<String, dynamic> json) =>
      _$$SubscriptionTierImplFromJson(json);

  @override
  final String id;
// 'free', 'pro', 'premium'
  @override
  final String name;
  @override
  final double? priceMonthly;
  @override
  final double? priceYearly;
  final List<String> _features;
  @override
  List<String> get features {
    if (_features is EqualUnmodifiableListView) return _features;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_features);
  }

  @override
  String toString() {
    return 'SubscriptionTier(id: $id, name: $name, priceMonthly: $priceMonthly, priceYearly: $priceYearly, features: $features)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SubscriptionTierImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.priceMonthly, priceMonthly) ||
                other.priceMonthly == priceMonthly) &&
            (identical(other.priceYearly, priceYearly) ||
                other.priceYearly == priceYearly) &&
            const DeepCollectionEquality().equals(other._features, _features));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, name, priceMonthly,
      priceYearly, const DeepCollectionEquality().hash(_features));

  /// Create a copy of SubscriptionTier
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SubscriptionTierImplCopyWith<_$SubscriptionTierImpl> get copyWith =>
      __$$SubscriptionTierImplCopyWithImpl<_$SubscriptionTierImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SubscriptionTierImplToJson(
      this,
    );
  }
}

abstract class _SubscriptionTier implements SubscriptionTier {
  const factory _SubscriptionTier(
      {required final String id,
      required final String name,
      final double? priceMonthly,
      final double? priceYearly,
      required final List<String> features}) = _$SubscriptionTierImpl;

  factory _SubscriptionTier.fromJson(Map<String, dynamic> json) =
      _$SubscriptionTierImpl.fromJson;

  @override
  String get id; // 'free', 'pro', 'premium'
  @override
  String get name;
  @override
  double? get priceMonthly;
  @override
  double? get priceYearly;
  @override
  List<String> get features;

  /// Create a copy of SubscriptionTier
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SubscriptionTierImplCopyWith<_$SubscriptionTierImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CreditPack _$CreditPackFromJson(Map<String, dynamic> json) {
  return _CreditPack.fromJson(json);
}

/// @nodoc
mixin _$CreditPack {
  int get credits => throw _privateConstructorUsedError;
  double get price => throw _privateConstructorUsedError;
  String get label => throw _privateConstructorUsedError;
  String? get badge => throw _privateConstructorUsedError;

  /// Serializes this CreditPack to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CreditPack
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CreditPackCopyWith<CreditPack> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CreditPackCopyWith<$Res> {
  factory $CreditPackCopyWith(
          CreditPack value, $Res Function(CreditPack) then) =
      _$CreditPackCopyWithImpl<$Res, CreditPack>;
  @useResult
  $Res call({int credits, double price, String label, String? badge});
}

/// @nodoc
class _$CreditPackCopyWithImpl<$Res, $Val extends CreditPack>
    implements $CreditPackCopyWith<$Res> {
  _$CreditPackCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CreditPack
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? credits = null,
    Object? price = null,
    Object? label = null,
    Object? badge = freezed,
  }) {
    return _then(_value.copyWith(
      credits: null == credits
          ? _value.credits
          : credits // ignore: cast_nullable_to_non_nullable
              as int,
      price: null == price
          ? _value.price
          : price // ignore: cast_nullable_to_non_nullable
              as double,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      badge: freezed == badge
          ? _value.badge
          : badge // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CreditPackImplCopyWith<$Res>
    implements $CreditPackCopyWith<$Res> {
  factory _$$CreditPackImplCopyWith(
          _$CreditPackImpl value, $Res Function(_$CreditPackImpl) then) =
      __$$CreditPackImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int credits, double price, String label, String? badge});
}

/// @nodoc
class __$$CreditPackImplCopyWithImpl<$Res>
    extends _$CreditPackCopyWithImpl<$Res, _$CreditPackImpl>
    implements _$$CreditPackImplCopyWith<$Res> {
  __$$CreditPackImplCopyWithImpl(
      _$CreditPackImpl _value, $Res Function(_$CreditPackImpl) _then)
      : super(_value, _then);

  /// Create a copy of CreditPack
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? credits = null,
    Object? price = null,
    Object? label = null,
    Object? badge = freezed,
  }) {
    return _then(_$CreditPackImpl(
      credits: null == credits
          ? _value.credits
          : credits // ignore: cast_nullable_to_non_nullable
              as int,
      price: null == price
          ? _value.price
          : price // ignore: cast_nullable_to_non_nullable
              as double,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      badge: freezed == badge
          ? _value.badge
          : badge // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CreditPackImpl implements _CreditPack {
  const _$CreditPackImpl(
      {required this.credits,
      required this.price,
      required this.label,
      this.badge});

  factory _$CreditPackImpl.fromJson(Map<String, dynamic> json) =>
      _$$CreditPackImplFromJson(json);

  @override
  final int credits;
  @override
  final double price;
  @override
  final String label;
  @override
  final String? badge;

  @override
  String toString() {
    return 'CreditPack(credits: $credits, price: $price, label: $label, badge: $badge)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CreditPackImpl &&
            (identical(other.credits, credits) || other.credits == credits) &&
            (identical(other.price, price) || other.price == price) &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.badge, badge) || other.badge == badge));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, credits, price, label, badge);

  /// Create a copy of CreditPack
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CreditPackImplCopyWith<_$CreditPackImpl> get copyWith =>
      __$$CreditPackImplCopyWithImpl<_$CreditPackImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CreditPackImplToJson(
      this,
    );
  }
}

abstract class _CreditPack implements CreditPack {
  const factory _CreditPack(
      {required final int credits,
      required final double price,
      required final String label,
      final String? badge}) = _$CreditPackImpl;

  factory _CreditPack.fromJson(Map<String, dynamic> json) =
      _$CreditPackImpl.fromJson;

  @override
  int get credits;
  @override
  double get price;
  @override
  String get label;
  @override
  String? get badge;

  /// Create a copy of CreditPack
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CreditPackImplCopyWith<_$CreditPackImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ReportPrice _$ReportPriceFromJson(Map<String, dynamic> json) {
  return _ReportPrice.fromJson(json);
}

/// @nodoc
mixin _$ReportPrice {
  String get reportType => throw _privateConstructorUsedError;
  int get credits => throw _privateConstructorUsedError;
  double get money => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;

  /// Serializes this ReportPrice to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ReportPrice
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ReportPriceCopyWith<ReportPrice> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ReportPriceCopyWith<$Res> {
  factory $ReportPriceCopyWith(
          ReportPrice value, $Res Function(ReportPrice) then) =
      _$ReportPriceCopyWithImpl<$Res, ReportPrice>;
  @useResult
  $Res call({String reportType, int credits, double money, String title});
}

/// @nodoc
class _$ReportPriceCopyWithImpl<$Res, $Val extends ReportPrice>
    implements $ReportPriceCopyWith<$Res> {
  _$ReportPriceCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ReportPrice
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? reportType = null,
    Object? credits = null,
    Object? money = null,
    Object? title = null,
  }) {
    return _then(_value.copyWith(
      reportType: null == reportType
          ? _value.reportType
          : reportType // ignore: cast_nullable_to_non_nullable
              as String,
      credits: null == credits
          ? _value.credits
          : credits // ignore: cast_nullable_to_non_nullable
              as int,
      money: null == money
          ? _value.money
          : money // ignore: cast_nullable_to_non_nullable
              as double,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ReportPriceImplCopyWith<$Res>
    implements $ReportPriceCopyWith<$Res> {
  factory _$$ReportPriceImplCopyWith(
          _$ReportPriceImpl value, $Res Function(_$ReportPriceImpl) then) =
      __$$ReportPriceImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String reportType, int credits, double money, String title});
}

/// @nodoc
class __$$ReportPriceImplCopyWithImpl<$Res>
    extends _$ReportPriceCopyWithImpl<$Res, _$ReportPriceImpl>
    implements _$$ReportPriceImplCopyWith<$Res> {
  __$$ReportPriceImplCopyWithImpl(
      _$ReportPriceImpl _value, $Res Function(_$ReportPriceImpl) _then)
      : super(_value, _then);

  /// Create a copy of ReportPrice
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? reportType = null,
    Object? credits = null,
    Object? money = null,
    Object? title = null,
  }) {
    return _then(_$ReportPriceImpl(
      reportType: null == reportType
          ? _value.reportType
          : reportType // ignore: cast_nullable_to_non_nullable
              as String,
      credits: null == credits
          ? _value.credits
          : credits // ignore: cast_nullable_to_non_nullable
              as int,
      money: null == money
          ? _value.money
          : money // ignore: cast_nullable_to_non_nullable
              as double,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ReportPriceImpl implements _ReportPrice {
  const _$ReportPriceImpl(
      {required this.reportType,
      required this.credits,
      required this.money,
      required this.title});

  factory _$ReportPriceImpl.fromJson(Map<String, dynamic> json) =>
      _$$ReportPriceImplFromJson(json);

  @override
  final String reportType;
  @override
  final int credits;
  @override
  final double money;
  @override
  final String title;

  @override
  String toString() {
    return 'ReportPrice(reportType: $reportType, credits: $credits, money: $money, title: $title)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ReportPriceImpl &&
            (identical(other.reportType, reportType) ||
                other.reportType == reportType) &&
            (identical(other.credits, credits) || other.credits == credits) &&
            (identical(other.money, money) || other.money == money) &&
            (identical(other.title, title) || other.title == title));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, reportType, credits, money, title);

  /// Create a copy of ReportPrice
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ReportPriceImplCopyWith<_$ReportPriceImpl> get copyWith =>
      __$$ReportPriceImplCopyWithImpl<_$ReportPriceImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ReportPriceImplToJson(
      this,
    );
  }
}

abstract class _ReportPrice implements ReportPrice {
  const factory _ReportPrice(
      {required final String reportType,
      required final int credits,
      required final double money,
      required final String title}) = _$ReportPriceImpl;

  factory _ReportPrice.fromJson(Map<String, dynamic> json) =
      _$ReportPriceImpl.fromJson;

  @override
  String get reportType;
  @override
  int get credits;
  @override
  double get money;
  @override
  String get title;

  /// Create a copy of ReportPrice
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ReportPriceImplCopyWith<_$ReportPriceImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

FeatureGates _$FeatureGatesFromJson(Map<String, dynamic> json) {
  return _FeatureGates.fromJson(json);
}

/// @nodoc
mixin _$FeatureGates {
  Map<String, bool> get free => throw _privateConstructorUsedError;
  Map<String, bool> get pro => throw _privateConstructorUsedError;
  Map<String, bool> get premium => throw _privateConstructorUsedError;

  /// Serializes this FeatureGates to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of FeatureGates
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $FeatureGatesCopyWith<FeatureGates> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $FeatureGatesCopyWith<$Res> {
  factory $FeatureGatesCopyWith(
          FeatureGates value, $Res Function(FeatureGates) then) =
      _$FeatureGatesCopyWithImpl<$Res, FeatureGates>;
  @useResult
  $Res call(
      {Map<String, bool> free,
      Map<String, bool> pro,
      Map<String, bool> premium});
}

/// @nodoc
class _$FeatureGatesCopyWithImpl<$Res, $Val extends FeatureGates>
    implements $FeatureGatesCopyWith<$Res> {
  _$FeatureGatesCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of FeatureGates
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? free = null,
    Object? pro = null,
    Object? premium = null,
  }) {
    return _then(_value.copyWith(
      free: null == free
          ? _value.free
          : free // ignore: cast_nullable_to_non_nullable
              as Map<String, bool>,
      pro: null == pro
          ? _value.pro
          : pro // ignore: cast_nullable_to_non_nullable
              as Map<String, bool>,
      premium: null == premium
          ? _value.premium
          : premium // ignore: cast_nullable_to_non_nullable
              as Map<String, bool>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$FeatureGatesImplCopyWith<$Res>
    implements $FeatureGatesCopyWith<$Res> {
  factory _$$FeatureGatesImplCopyWith(
          _$FeatureGatesImpl value, $Res Function(_$FeatureGatesImpl) then) =
      __$$FeatureGatesImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {Map<String, bool> free,
      Map<String, bool> pro,
      Map<String, bool> premium});
}

/// @nodoc
class __$$FeatureGatesImplCopyWithImpl<$Res>
    extends _$FeatureGatesCopyWithImpl<$Res, _$FeatureGatesImpl>
    implements _$$FeatureGatesImplCopyWith<$Res> {
  __$$FeatureGatesImplCopyWithImpl(
      _$FeatureGatesImpl _value, $Res Function(_$FeatureGatesImpl) _then)
      : super(_value, _then);

  /// Create a copy of FeatureGates
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? free = null,
    Object? pro = null,
    Object? premium = null,
  }) {
    return _then(_$FeatureGatesImpl(
      free: null == free
          ? _value._free
          : free // ignore: cast_nullable_to_non_nullable
              as Map<String, bool>,
      pro: null == pro
          ? _value._pro
          : pro // ignore: cast_nullable_to_non_nullable
              as Map<String, bool>,
      premium: null == premium
          ? _value._premium
          : premium // ignore: cast_nullable_to_non_nullable
              as Map<String, bool>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$FeatureGatesImpl implements _FeatureGates {
  const _$FeatureGatesImpl(
      {required final Map<String, bool> free,
      required final Map<String, bool> pro,
      required final Map<String, bool> premium})
      : _free = free,
        _pro = pro,
        _premium = premium;

  factory _$FeatureGatesImpl.fromJson(Map<String, dynamic> json) =>
      _$$FeatureGatesImplFromJson(json);

  final Map<String, bool> _free;
  @override
  Map<String, bool> get free {
    if (_free is EqualUnmodifiableMapView) return _free;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_free);
  }

  final Map<String, bool> _pro;
  @override
  Map<String, bool> get pro {
    if (_pro is EqualUnmodifiableMapView) return _pro;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_pro);
  }

  final Map<String, bool> _premium;
  @override
  Map<String, bool> get premium {
    if (_premium is EqualUnmodifiableMapView) return _premium;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_premium);
  }

  @override
  String toString() {
    return 'FeatureGates(free: $free, pro: $pro, premium: $premium)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$FeatureGatesImpl &&
            const DeepCollectionEquality().equals(other._free, _free) &&
            const DeepCollectionEquality().equals(other._pro, _pro) &&
            const DeepCollectionEquality().equals(other._premium, _premium));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_free),
      const DeepCollectionEquality().hash(_pro),
      const DeepCollectionEquality().hash(_premium));

  /// Create a copy of FeatureGates
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$FeatureGatesImplCopyWith<_$FeatureGatesImpl> get copyWith =>
      __$$FeatureGatesImplCopyWithImpl<_$FeatureGatesImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$FeatureGatesImplToJson(
      this,
    );
  }
}

abstract class _FeatureGates implements FeatureGates {
  const factory _FeatureGates(
      {required final Map<String, bool> free,
      required final Map<String, bool> pro,
      required final Map<String, bool> premium}) = _$FeatureGatesImpl;

  factory _FeatureGates.fromJson(Map<String, dynamic> json) =
      _$FeatureGatesImpl.fromJson;

  @override
  Map<String, bool> get free;
  @override
  Map<String, bool> get pro;
  @override
  Map<String, bool> get premium;

  /// Create a copy of FeatureGates
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$FeatureGatesImplCopyWith<_$FeatureGatesImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

AppConfigModel _$AppConfigModelFromJson(Map<String, dynamic> json) {
  return _AppConfigModel.fromJson(json);
}

/// @nodoc
mixin _$AppConfigModel {
  Map<String, int> get chatLimits =>
      throw _privateConstructorUsedError; // 'free': 5, 'pro': 30, 'premium': -1
  Map<String, SubscriptionTier> get subscriptionTiers =>
      throw _privateConstructorUsedError;
  List<CreditPack> get creditPacks => throw _privateConstructorUsedError;
  List<ReportPrice> get reportPrices => throw _privateConstructorUsedError;
  FeatureGates get featureGates => throw _privateConstructorUsedError;

  /// Serializes this AppConfigModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AppConfigModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AppConfigModelCopyWith<AppConfigModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AppConfigModelCopyWith<$Res> {
  factory $AppConfigModelCopyWith(
          AppConfigModel value, $Res Function(AppConfigModel) then) =
      _$AppConfigModelCopyWithImpl<$Res, AppConfigModel>;
  @useResult
  $Res call(
      {Map<String, int> chatLimits,
      Map<String, SubscriptionTier> subscriptionTiers,
      List<CreditPack> creditPacks,
      List<ReportPrice> reportPrices,
      FeatureGates featureGates});

  $FeatureGatesCopyWith<$Res> get featureGates;
}

/// @nodoc
class _$AppConfigModelCopyWithImpl<$Res, $Val extends AppConfigModel>
    implements $AppConfigModelCopyWith<$Res> {
  _$AppConfigModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AppConfigModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? chatLimits = null,
    Object? subscriptionTiers = null,
    Object? creditPacks = null,
    Object? reportPrices = null,
    Object? featureGates = null,
  }) {
    return _then(_value.copyWith(
      chatLimits: null == chatLimits
          ? _value.chatLimits
          : chatLimits // ignore: cast_nullable_to_non_nullable
              as Map<String, int>,
      subscriptionTiers: null == subscriptionTiers
          ? _value.subscriptionTiers
          : subscriptionTiers // ignore: cast_nullable_to_non_nullable
              as Map<String, SubscriptionTier>,
      creditPacks: null == creditPacks
          ? _value.creditPacks
          : creditPacks // ignore: cast_nullable_to_non_nullable
              as List<CreditPack>,
      reportPrices: null == reportPrices
          ? _value.reportPrices
          : reportPrices // ignore: cast_nullable_to_non_nullable
              as List<ReportPrice>,
      featureGates: null == featureGates
          ? _value.featureGates
          : featureGates // ignore: cast_nullable_to_non_nullable
              as FeatureGates,
    ) as $Val);
  }

  /// Create a copy of AppConfigModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $FeatureGatesCopyWith<$Res> get featureGates {
    return $FeatureGatesCopyWith<$Res>(_value.featureGates, (value) {
      return _then(_value.copyWith(featureGates: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$AppConfigModelImplCopyWith<$Res>
    implements $AppConfigModelCopyWith<$Res> {
  factory _$$AppConfigModelImplCopyWith(_$AppConfigModelImpl value,
          $Res Function(_$AppConfigModelImpl) then) =
      __$$AppConfigModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {Map<String, int> chatLimits,
      Map<String, SubscriptionTier> subscriptionTiers,
      List<CreditPack> creditPacks,
      List<ReportPrice> reportPrices,
      FeatureGates featureGates});

  @override
  $FeatureGatesCopyWith<$Res> get featureGates;
}

/// @nodoc
class __$$AppConfigModelImplCopyWithImpl<$Res>
    extends _$AppConfigModelCopyWithImpl<$Res, _$AppConfigModelImpl>
    implements _$$AppConfigModelImplCopyWith<$Res> {
  __$$AppConfigModelImplCopyWithImpl(
      _$AppConfigModelImpl _value, $Res Function(_$AppConfigModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of AppConfigModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? chatLimits = null,
    Object? subscriptionTiers = null,
    Object? creditPacks = null,
    Object? reportPrices = null,
    Object? featureGates = null,
  }) {
    return _then(_$AppConfigModelImpl(
      chatLimits: null == chatLimits
          ? _value._chatLimits
          : chatLimits // ignore: cast_nullable_to_non_nullable
              as Map<String, int>,
      subscriptionTiers: null == subscriptionTiers
          ? _value._subscriptionTiers
          : subscriptionTiers // ignore: cast_nullable_to_non_nullable
              as Map<String, SubscriptionTier>,
      creditPacks: null == creditPacks
          ? _value._creditPacks
          : creditPacks // ignore: cast_nullable_to_non_nullable
              as List<CreditPack>,
      reportPrices: null == reportPrices
          ? _value._reportPrices
          : reportPrices // ignore: cast_nullable_to_non_nullable
              as List<ReportPrice>,
      featureGates: null == featureGates
          ? _value.featureGates
          : featureGates // ignore: cast_nullable_to_non_nullable
              as FeatureGates,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AppConfigModelImpl implements _AppConfigModel {
  const _$AppConfigModelImpl(
      {required final Map<String, int> chatLimits,
      required final Map<String, SubscriptionTier> subscriptionTiers,
      required final List<CreditPack> creditPacks,
      required final List<ReportPrice> reportPrices,
      required this.featureGates})
      : _chatLimits = chatLimits,
        _subscriptionTiers = subscriptionTiers,
        _creditPacks = creditPacks,
        _reportPrices = reportPrices;

  factory _$AppConfigModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$AppConfigModelImplFromJson(json);

  final Map<String, int> _chatLimits;
  @override
  Map<String, int> get chatLimits {
    if (_chatLimits is EqualUnmodifiableMapView) return _chatLimits;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_chatLimits);
  }

// 'free': 5, 'pro': 30, 'premium': -1
  final Map<String, SubscriptionTier> _subscriptionTiers;
// 'free': 5, 'pro': 30, 'premium': -1
  @override
  Map<String, SubscriptionTier> get subscriptionTiers {
    if (_subscriptionTiers is EqualUnmodifiableMapView)
      return _subscriptionTiers;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_subscriptionTiers);
  }

  final List<CreditPack> _creditPacks;
  @override
  List<CreditPack> get creditPacks {
    if (_creditPacks is EqualUnmodifiableListView) return _creditPacks;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_creditPacks);
  }

  final List<ReportPrice> _reportPrices;
  @override
  List<ReportPrice> get reportPrices {
    if (_reportPrices is EqualUnmodifiableListView) return _reportPrices;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_reportPrices);
  }

  @override
  final FeatureGates featureGates;

  @override
  String toString() {
    return 'AppConfigModel(chatLimits: $chatLimits, subscriptionTiers: $subscriptionTiers, creditPacks: $creditPacks, reportPrices: $reportPrices, featureGates: $featureGates)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AppConfigModelImpl &&
            const DeepCollectionEquality()
                .equals(other._chatLimits, _chatLimits) &&
            const DeepCollectionEquality()
                .equals(other._subscriptionTiers, _subscriptionTiers) &&
            const DeepCollectionEquality()
                .equals(other._creditPacks, _creditPacks) &&
            const DeepCollectionEquality()
                .equals(other._reportPrices, _reportPrices) &&
            (identical(other.featureGates, featureGates) ||
                other.featureGates == featureGates));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_chatLimits),
      const DeepCollectionEquality().hash(_subscriptionTiers),
      const DeepCollectionEquality().hash(_creditPacks),
      const DeepCollectionEquality().hash(_reportPrices),
      featureGates);

  /// Create a copy of AppConfigModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AppConfigModelImplCopyWith<_$AppConfigModelImpl> get copyWith =>
      __$$AppConfigModelImplCopyWithImpl<_$AppConfigModelImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AppConfigModelImplToJson(
      this,
    );
  }
}

abstract class _AppConfigModel implements AppConfigModel {
  const factory _AppConfigModel(
      {required final Map<String, int> chatLimits,
      required final Map<String, SubscriptionTier> subscriptionTiers,
      required final List<CreditPack> creditPacks,
      required final List<ReportPrice> reportPrices,
      required final FeatureGates featureGates}) = _$AppConfigModelImpl;

  factory _AppConfigModel.fromJson(Map<String, dynamic> json) =
      _$AppConfigModelImpl.fromJson;

  @override
  Map<String, int> get chatLimits; // 'free': 5, 'pro': 30, 'premium': -1
  @override
  Map<String, SubscriptionTier> get subscriptionTiers;
  @override
  List<CreditPack> get creditPacks;
  @override
  List<ReportPrice> get reportPrices;
  @override
  FeatureGates get featureGates;

  /// Create a copy of AppConfigModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AppConfigModelImplCopyWith<_$AppConfigModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
