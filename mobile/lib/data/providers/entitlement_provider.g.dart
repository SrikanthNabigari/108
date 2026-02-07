// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'entitlement_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$initializeRevenueCatHash() =>
    r'8710f03f17af380fa71e62ea634e86c4521b07e5';

/// Initialize RevenueCat SDK
///
/// Copied from [initializeRevenueCat].
@ProviderFor(initializeRevenueCat)
final initializeRevenueCatProvider = AutoDisposeFutureProvider<void>.internal(
  initializeRevenueCat,
  name: r'initializeRevenueCatProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$initializeRevenueCatHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef InitializeRevenueCatRef = AutoDisposeFutureProviderRef<void>;
String _$customerInfoHash() => r'9c04667dc8f0e322473354492f4f863d9d92e1f1';

/// Get current customer info
///
/// Copied from [customerInfo].
@ProviderFor(customerInfo)
final customerInfoProvider = AutoDisposeStreamProvider<CustomerInfo>.internal(
  customerInfo,
  name: r'customerInfoProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$customerInfoHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef CustomerInfoRef = AutoDisposeStreamProviderRef<CustomerInfo>;
String _$hasProHash() => r'f904f4ab07ae32f063f6d9682aad2bb0b19267cf';

/// Check if user has "pro" entitlement
///
/// Copied from [hasPro].
@ProviderFor(hasPro)
final hasProProvider = AutoDisposeFutureProvider<bool>.internal(
  hasPro,
  name: r'hasProProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$hasProHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef HasProRef = AutoDisposeFutureProviderRef<bool>;
String _$hasPremiumHash() => r'11ba12ad5b0eac1f60c6db349ece0d1a50b042d9';

/// Check if user has "premium" entitlement
///
/// Copied from [hasPremium].
@ProviderFor(hasPremium)
final hasPremiumProvider = AutoDisposeFutureProvider<bool>.internal(
  hasPremium,
  name: r'hasPremiumProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$hasPremiumHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef HasPremiumRef = AutoDisposeFutureProviderRef<bool>;
String _$offeringsHash() => r'b181ffdb23467ae0e72c93303a63bec1d6dff605';

/// Get available offerings
///
/// Copied from [offerings].
@ProviderFor(offerings)
final offeringsProvider = AutoDisposeFutureProvider<Offerings?>.internal(
  offerings,
  name: r'offeringsProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$offeringsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef OfferingsRef = AutoDisposeFutureProviderRef<Offerings?>;
String _$purchasePackageHash() => r'17c584911ff646e10684fd8d099555c0e6d106c6';

/// Purchase a package
///
/// Copied from [PurchasePackage].
@ProviderFor(PurchasePackage)
final purchasePackageProvider =
    AutoDisposeAsyncNotifierProvider<PurchasePackage, void>.internal(
  PurchasePackage.new,
  name: r'purchasePackageProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$purchasePackageHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$PurchasePackage = AutoDisposeAsyncNotifier<void>;
String _$purchaseSubscriptionHash() =>
    r'e28c49d68b449c3a8c7bb692c348904574a1b987';

/// Purchase a subscription
///
/// Copied from [PurchaseSubscription].
@ProviderFor(PurchaseSubscription)
final purchaseSubscriptionProvider =
    AutoDisposeAsyncNotifierProvider<PurchaseSubscription, void>.internal(
  PurchaseSubscription.new,
  name: r'purchaseSubscriptionProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$purchaseSubscriptionHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$PurchaseSubscription = AutoDisposeAsyncNotifier<void>;
String _$restorePurchasesHash() => r'd539f971768776952043cf92c02a3a142c2e0a5e';

/// Restore purchases
///
/// Copied from [RestorePurchases].
@ProviderFor(RestorePurchases)
final restorePurchasesProvider =
    AutoDisposeAsyncNotifierProvider<RestorePurchases, void>.internal(
  RestorePurchases.new,
  name: r'restorePurchasesProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$restorePurchasesHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$RestorePurchases = AutoDisposeAsyncNotifier<void>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
