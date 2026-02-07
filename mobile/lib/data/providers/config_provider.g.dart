// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'config_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$appConfigHash() => r'264a8ef47b834ebad115183e96ffe3bb876c4dfb';

/// Get app config from /api/v1/config
/// Cached for 5 minutes by the backend
///
/// Copied from [appConfig].
@ProviderFor(appConfig)
final appConfigProvider = AutoDisposeFutureProvider<AppConfigModel>.internal(
  appConfig,
  name: r'appConfigProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$appConfigHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef AppConfigRef = AutoDisposeFutureProviderRef<AppConfigModel>;
String _$chatMessageLimitHash() => r'eaaaa58bde378ca116029e2cd26048ad3e1bfcf1';

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

/// Get chat message limit for current tier
///
/// Copied from [chatMessageLimit].
@ProviderFor(chatMessageLimit)
const chatMessageLimitProvider = ChatMessageLimitFamily();

/// Get chat message limit for current tier
///
/// Copied from [chatMessageLimit].
class ChatMessageLimitFamily extends Family<AsyncValue<int>> {
  /// Get chat message limit for current tier
  ///
  /// Copied from [chatMessageLimit].
  const ChatMessageLimitFamily();

  /// Get chat message limit for current tier
  ///
  /// Copied from [chatMessageLimit].
  ChatMessageLimitProvider call(
    String tier,
  ) {
    return ChatMessageLimitProvider(
      tier,
    );
  }

  @override
  ChatMessageLimitProvider getProviderOverride(
    covariant ChatMessageLimitProvider provider,
  ) {
    return call(
      provider.tier,
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
  String? get name => r'chatMessageLimitProvider';
}

/// Get chat message limit for current tier
///
/// Copied from [chatMessageLimit].
class ChatMessageLimitProvider extends AutoDisposeFutureProvider<int> {
  /// Get chat message limit for current tier
  ///
  /// Copied from [chatMessageLimit].
  ChatMessageLimitProvider(
    String tier,
  ) : this._internal(
          (ref) => chatMessageLimit(
            ref as ChatMessageLimitRef,
            tier,
          ),
          from: chatMessageLimitProvider,
          name: r'chatMessageLimitProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$chatMessageLimitHash,
          dependencies: ChatMessageLimitFamily._dependencies,
          allTransitiveDependencies:
              ChatMessageLimitFamily._allTransitiveDependencies,
          tier: tier,
        );

  ChatMessageLimitProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.tier,
  }) : super.internal();

  final String tier;

  @override
  Override overrideWith(
    FutureOr<int> Function(ChatMessageLimitRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: ChatMessageLimitProvider._internal(
        (ref) => create(ref as ChatMessageLimitRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        tier: tier,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<int> createElement() {
    return _ChatMessageLimitProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is ChatMessageLimitProvider && other.tier == tier;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, tier.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin ChatMessageLimitRef on AutoDisposeFutureProviderRef<int> {
  /// The parameter `tier` of this provider.
  String get tier;
}

class _ChatMessageLimitProviderElement
    extends AutoDisposeFutureProviderElement<int> with ChatMessageLimitRef {
  _ChatMessageLimitProviderElement(super.provider);

  @override
  String get tier => (origin as ChatMessageLimitProvider).tier;
}

String _$isFeatureEnabledHash() => r'a8fb8b50fdea1c1dff1a77ebd767b664d8062d1f';

/// Get feature gate status
///
/// Copied from [isFeatureEnabled].
@ProviderFor(isFeatureEnabled)
const isFeatureEnabledProvider = IsFeatureEnabledFamily();

/// Get feature gate status
///
/// Copied from [isFeatureEnabled].
class IsFeatureEnabledFamily extends Family<AsyncValue<bool>> {
  /// Get feature gate status
  ///
  /// Copied from [isFeatureEnabled].
  const IsFeatureEnabledFamily();

  /// Get feature gate status
  ///
  /// Copied from [isFeatureEnabled].
  IsFeatureEnabledProvider call({
    required String feature,
    required String tier,
  }) {
    return IsFeatureEnabledProvider(
      feature: feature,
      tier: tier,
    );
  }

  @override
  IsFeatureEnabledProvider getProviderOverride(
    covariant IsFeatureEnabledProvider provider,
  ) {
    return call(
      feature: provider.feature,
      tier: provider.tier,
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
  String? get name => r'isFeatureEnabledProvider';
}

/// Get feature gate status
///
/// Copied from [isFeatureEnabled].
class IsFeatureEnabledProvider extends AutoDisposeFutureProvider<bool> {
  /// Get feature gate status
  ///
  /// Copied from [isFeatureEnabled].
  IsFeatureEnabledProvider({
    required String feature,
    required String tier,
  }) : this._internal(
          (ref) => isFeatureEnabled(
            ref as IsFeatureEnabledRef,
            feature: feature,
            tier: tier,
          ),
          from: isFeatureEnabledProvider,
          name: r'isFeatureEnabledProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$isFeatureEnabledHash,
          dependencies: IsFeatureEnabledFamily._dependencies,
          allTransitiveDependencies:
              IsFeatureEnabledFamily._allTransitiveDependencies,
          feature: feature,
          tier: tier,
        );

  IsFeatureEnabledProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.feature,
    required this.tier,
  }) : super.internal();

  final String feature;
  final String tier;

  @override
  Override overrideWith(
    FutureOr<bool> Function(IsFeatureEnabledRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: IsFeatureEnabledProvider._internal(
        (ref) => create(ref as IsFeatureEnabledRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        feature: feature,
        tier: tier,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<bool> createElement() {
    return _IsFeatureEnabledProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is IsFeatureEnabledProvider &&
        other.feature == feature &&
        other.tier == tier;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, feature.hashCode);
    hash = _SystemHash.combine(hash, tier.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin IsFeatureEnabledRef on AutoDisposeFutureProviderRef<bool> {
  /// The parameter `feature` of this provider.
  String get feature;

  /// The parameter `tier` of this provider.
  String get tier;
}

class _IsFeatureEnabledProviderElement
    extends AutoDisposeFutureProviderElement<bool> with IsFeatureEnabledRef {
  _IsFeatureEnabledProviderElement(super.provider);

  @override
  String get feature => (origin as IsFeatureEnabledProvider).feature;
  @override
  String get tier => (origin as IsFeatureEnabledProvider).tier;
}

String _$reportPriceHash() => r'10667d31608e9574a8ec08a34d48ec244f8f4dc8';

/// Get report price
///
/// Copied from [reportPrice].
@ProviderFor(reportPrice)
const reportPriceProvider = ReportPriceFamily();

/// Get report price
///
/// Copied from [reportPrice].
class ReportPriceFamily extends Family<AsyncValue<ReportPrice?>> {
  /// Get report price
  ///
  /// Copied from [reportPrice].
  const ReportPriceFamily();

  /// Get report price
  ///
  /// Copied from [reportPrice].
  ReportPriceProvider call(
    String reportType,
  ) {
    return ReportPriceProvider(
      reportType,
    );
  }

  @override
  ReportPriceProvider getProviderOverride(
    covariant ReportPriceProvider provider,
  ) {
    return call(
      provider.reportType,
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
  String? get name => r'reportPriceProvider';
}

/// Get report price
///
/// Copied from [reportPrice].
class ReportPriceProvider extends AutoDisposeFutureProvider<ReportPrice?> {
  /// Get report price
  ///
  /// Copied from [reportPrice].
  ReportPriceProvider(
    String reportType,
  ) : this._internal(
          (ref) => reportPrice(
            ref as ReportPriceRef,
            reportType,
          ),
          from: reportPriceProvider,
          name: r'reportPriceProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$reportPriceHash,
          dependencies: ReportPriceFamily._dependencies,
          allTransitiveDependencies:
              ReportPriceFamily._allTransitiveDependencies,
          reportType: reportType,
        );

  ReportPriceProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.reportType,
  }) : super.internal();

  final String reportType;

  @override
  Override overrideWith(
    FutureOr<ReportPrice?> Function(ReportPriceRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: ReportPriceProvider._internal(
        (ref) => create(ref as ReportPriceRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        reportType: reportType,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<ReportPrice?> createElement() {
    return _ReportPriceProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is ReportPriceProvider && other.reportType == reportType;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, reportType.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin ReportPriceRef on AutoDisposeFutureProviderRef<ReportPrice?> {
  /// The parameter `reportType` of this provider.
  String get reportType;
}

class _ReportPriceProviderElement
    extends AutoDisposeFutureProviderElement<ReportPrice?> with ReportPriceRef {
  _ReportPriceProviderElement(super.provider);

  @override
  String get reportType => (origin as ReportPriceProvider).reportType;
}

String _$creditPacksHash() => r'b1537202626523ecb8456d683b14ddd0ffc8f4fa';

/// Get all available credit packs
///
/// Copied from [creditPacks].
@ProviderFor(creditPacks)
final creditPacksProvider =
    AutoDisposeFutureProvider<List<CreditPack>>.internal(
  creditPacks,
  name: r'creditPacksProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$creditPacksHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef CreditPacksRef = AutoDisposeFutureProviderRef<List<CreditPack>>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
