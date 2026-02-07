// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'credits_provider.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$CreditTransactionImpl _$$CreditTransactionImplFromJson(
        Map<String, dynamic> json) =>
    _$CreditTransactionImpl(
      id: json['id'] as String,
      amount: (json['amount'] as num).toInt(),
      balanceAfter: (json['balanceAfter'] as num).toInt(),
      transactionType: json['transactionType'] as String,
      description: json['description'] as String?,
      referenceId: json['referenceId'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$CreditTransactionImplToJson(
        _$CreditTransactionImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'amount': instance.amount,
      'balanceAfter': instance.balanceAfter,
      'transactionType': instance.transactionType,
      'description': instance.description,
      'referenceId': instance.referenceId,
      'createdAt': instance.createdAt.toIso8601String(),
    };

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$creditBalanceHash() => r'f7dc2a793b5013f5f623a3493c70e5fa2ef556b8';

/// Get current credit balance
///
/// Copied from [creditBalance].
@ProviderFor(creditBalance)
final creditBalanceProvider = AutoDisposeFutureProvider<int>.internal(
  creditBalance,
  name: r'creditBalanceProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$creditBalanceHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef CreditBalanceRef = AutoDisposeFutureProviderRef<int>;
String _$creditHistoryHash() => r'48809a93c2b0391514dbd34aa018003e5937362d';

/// Copied from Dart SDK
class _SystemHash {
  _SystemHash._();

  static int combine(int hash, int value) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + value);
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x0007ffff & hash) << 10));
    return hash ^ (hash >> 6);
  }

  static int finish(int hash) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x03ffffff & hash) << 3));
    // ignore: parameter_assignments
    hash = hash ^ (hash >> 11);
    return 0x1fffffff & (hash + ((0x00003fff & hash) << 15));
  }
}

/// Get credit transaction history
///
/// Copied from [creditHistory].
@ProviderFor(creditHistory)
const creditHistoryProvider = CreditHistoryFamily();

/// Get credit transaction history
///
/// Copied from [creditHistory].
class CreditHistoryFamily extends Family<AsyncValue<List<CreditTransaction>>> {
  /// Get credit transaction history
  ///
  /// Copied from [creditHistory].
  const CreditHistoryFamily();

  /// Get credit transaction history
  ///
  /// Copied from [creditHistory].
  CreditHistoryProvider call({
    int limit = 50,
    int offset = 0,
  }) {
    return CreditHistoryProvider(
      limit: limit,
      offset: offset,
    );
  }

  @override
  CreditHistoryProvider getProviderOverride(
    covariant CreditHistoryProvider provider,
  ) {
    return call(
      limit: provider.limit,
      offset: provider.offset,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'creditHistoryProvider';
}

/// Get credit transaction history
///
/// Copied from [creditHistory].
class CreditHistoryProvider
    extends AutoDisposeFutureProvider<List<CreditTransaction>> {
  /// Get credit transaction history
  ///
  /// Copied from [creditHistory].
  CreditHistoryProvider({
    int limit = 50,
    int offset = 0,
  }) : this._internal(
          (ref) => creditHistory(
            ref as CreditHistoryRef,
            limit: limit,
            offset: offset,
          ),
          from: creditHistoryProvider,
          name: r'creditHistoryProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$creditHistoryHash,
          dependencies: CreditHistoryFamily._dependencies,
          allTransitiveDependencies:
              CreditHistoryFamily._allTransitiveDependencies,
          limit: limit,
          offset: offset,
        );

  CreditHistoryProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.limit,
    required this.offset,
  }) : super.internal();

  final int limit;
  final int offset;

  @override
  Override overrideWith(
    FutureOr<List<CreditTransaction>> Function(CreditHistoryRef provider)
        create,
  ) {
    return ProviderOverride(
      origin: this,
      override: CreditHistoryProvider._internal(
        (ref) => create(ref as CreditHistoryRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        limit: limit,
        offset: offset,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<List<CreditTransaction>> createElement() {
    return _CreditHistoryProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is CreditHistoryProvider &&
        other.limit == limit &&
        other.offset == offset;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, limit.hashCode);
    hash = _SystemHash.combine(hash, offset.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin CreditHistoryRef
    on AutoDisposeFutureProviderRef<List<CreditTransaction>> {
  /// The parameter `limit` of this provider.
  int get limit;

  /// The parameter `offset` of this provider.
  int get offset;
}

class _CreditHistoryProviderElement
    extends AutoDisposeFutureProviderElement<List<CreditTransaction>>
    with CreditHistoryRef {
  _CreditHistoryProviderElement(super.provider);

  @override
  int get limit => (origin as CreditHistoryProvider).limit;
  @override
  int get offset => (origin as CreditHistoryProvider).offset;
}

String _$refreshCreditsHash() => r'7da74ecc13eeffec82933729ffdd060e4003cf86';

/// Refresh credit balance
///
/// Copied from [RefreshCredits].
@ProviderFor(RefreshCredits)
final refreshCreditsProvider =
    AutoDisposeAsyncNotifierProvider<RefreshCredits, void>.internal(
  RefreshCredits.new,
  name: r'refreshCreditsProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$refreshCreditsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$RefreshCredits = AutoDisposeAsyncNotifier<void>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
