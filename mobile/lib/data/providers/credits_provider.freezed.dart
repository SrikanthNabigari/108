// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'credits_provider.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

CreditTransaction _$CreditTransactionFromJson(Map<String, dynamic> json) {
  return _CreditTransaction.fromJson(json);
}

/// @nodoc
mixin _$CreditTransaction {
  String get id => throw _privateConstructorUsedError;
  int get amount => throw _privateConstructorUsedError;
  int get balanceAfter => throw _privateConstructorUsedError;
  String get transactionType =>
      throw _privateConstructorUsedError; // 'purchase', 'spend', 'refund', 'bonus'
  String? get description => throw _privateConstructorUsedError;
  String? get referenceId => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;

  /// Serializes this CreditTransaction to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CreditTransaction
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CreditTransactionCopyWith<CreditTransaction> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CreditTransactionCopyWith<$Res> {
  factory $CreditTransactionCopyWith(
          CreditTransaction value, $Res Function(CreditTransaction) then) =
      _$CreditTransactionCopyWithImpl<$Res, CreditTransaction>;
  @useResult
  $Res call(
      {String id,
      int amount,
      int balanceAfter,
      String transactionType,
      String? description,
      String? referenceId,
      DateTime createdAt});
}

/// @nodoc
class _$CreditTransactionCopyWithImpl<$Res, $Val extends CreditTransaction>
    implements $CreditTransactionCopyWith<$Res> {
  _$CreditTransactionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CreditTransaction
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? amount = null,
    Object? balanceAfter = null,
    Object? transactionType = null,
    Object? description = freezed,
    Object? referenceId = freezed,
    Object? createdAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      amount: null == amount
          ? _value.amount
          : amount // ignore: cast_nullable_to_non_nullable
              as int,
      balanceAfter: null == balanceAfter
          ? _value.balanceAfter
          : balanceAfter // ignore: cast_nullable_to_non_nullable
              as int,
      transactionType: null == transactionType
          ? _value.transactionType
          : transactionType // ignore: cast_nullable_to_non_nullable
              as String,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      referenceId: freezed == referenceId
          ? _value.referenceId
          : referenceId // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CreditTransactionImplCopyWith<$Res>
    implements $CreditTransactionCopyWith<$Res> {
  factory _$$CreditTransactionImplCopyWith(_$CreditTransactionImpl value,
          $Res Function(_$CreditTransactionImpl) then) =
      __$$CreditTransactionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      int amount,
      int balanceAfter,
      String transactionType,
      String? description,
      String? referenceId,
      DateTime createdAt});
}

/// @nodoc
class __$$CreditTransactionImplCopyWithImpl<$Res>
    extends _$CreditTransactionCopyWithImpl<$Res, _$CreditTransactionImpl>
    implements _$$CreditTransactionImplCopyWith<$Res> {
  __$$CreditTransactionImplCopyWithImpl(_$CreditTransactionImpl _value,
      $Res Function(_$CreditTransactionImpl) _then)
      : super(_value, _then);

  /// Create a copy of CreditTransaction
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? amount = null,
    Object? balanceAfter = null,
    Object? transactionType = null,
    Object? description = freezed,
    Object? referenceId = freezed,
    Object? createdAt = null,
  }) {
    return _then(_$CreditTransactionImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      amount: null == amount
          ? _value.amount
          : amount // ignore: cast_nullable_to_non_nullable
              as int,
      balanceAfter: null == balanceAfter
          ? _value.balanceAfter
          : balanceAfter // ignore: cast_nullable_to_non_nullable
              as int,
      transactionType: null == transactionType
          ? _value.transactionType
          : transactionType // ignore: cast_nullable_to_non_nullable
              as String,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      referenceId: freezed == referenceId
          ? _value.referenceId
          : referenceId // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CreditTransactionImpl implements _CreditTransaction {
  const _$CreditTransactionImpl(
      {required this.id,
      required this.amount,
      required this.balanceAfter,
      required this.transactionType,
      this.description,
      this.referenceId,
      required this.createdAt});

  factory _$CreditTransactionImpl.fromJson(Map<String, dynamic> json) =>
      _$$CreditTransactionImplFromJson(json);

  @override
  final String id;
  @override
  final int amount;
  @override
  final int balanceAfter;
  @override
  final String transactionType;
// 'purchase', 'spend', 'refund', 'bonus'
  @override
  final String? description;
  @override
  final String? referenceId;
  @override
  final DateTime createdAt;

  @override
  String toString() {
    return 'CreditTransaction(id: $id, amount: $amount, balanceAfter: $balanceAfter, transactionType: $transactionType, description: $description, referenceId: $referenceId, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CreditTransactionImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.amount, amount) || other.amount == amount) &&
            (identical(other.balanceAfter, balanceAfter) ||
                other.balanceAfter == balanceAfter) &&
            (identical(other.transactionType, transactionType) ||
                other.transactionType == transactionType) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.referenceId, referenceId) ||
                other.referenceId == referenceId) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, amount, balanceAfter,
      transactionType, description, referenceId, createdAt);

  /// Create a copy of CreditTransaction
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CreditTransactionImplCopyWith<_$CreditTransactionImpl> get copyWith =>
      __$$CreditTransactionImplCopyWithImpl<_$CreditTransactionImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CreditTransactionImplToJson(
      this,
    );
  }
}

abstract class _CreditTransaction implements CreditTransaction {
  const factory _CreditTransaction(
      {required final String id,
      required final int amount,
      required final int balanceAfter,
      required final String transactionType,
      final String? description,
      final String? referenceId,
      required final DateTime createdAt}) = _$CreditTransactionImpl;

  factory _CreditTransaction.fromJson(Map<String, dynamic> json) =
      _$CreditTransactionImpl.fromJson;

  @override
  String get id;
  @override
  int get amount;
  @override
  int get balanceAfter;
  @override
  String get transactionType; // 'purchase', 'spend', 'refund', 'bonus'
  @override
  String? get description;
  @override
  String? get referenceId;
  @override
  DateTime get createdAt;

  /// Create a copy of CreditTransaction
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CreditTransactionImplCopyWith<_$CreditTransactionImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
