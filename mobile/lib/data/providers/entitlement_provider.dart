import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

part 'entitlement_provider.g.dart';

/// Initialize RevenueCat SDK
@riverpod
Future<void> initializeRevenueCat(InitializeRevenueCatRef ref) async {
  await Purchases.configure(
    PurchasesConfiguration(
      'goog_BKPYwBfdQGVDvLJsYYhBKvLhWKG', // Placeholder API key
    ),
  );
}

/// Get current customer info
@riverpod
Stream<CustomerInfo> customerInfo(CustomerInfoRef ref) async* {
  await ref.watch(initializeRevenueCatProvider.future);

  // Initial fetch
  try {
    final info = await Purchases.getCustomerInfo();
    yield info;
  } catch (e) {
    print('Error fetching customer info: $e');
  }

  // Listen for updates
  Purchases.addCustomerInfoUpdateListener((info) {
    ref.state = AsyncValue.data(info);
  });
}

/// Check if user has "pro" entitlement
@riverpod
Future<bool> hasPro(HasProRef ref) async {
  final info = await ref.watch(customerInfoProvider.future);
  return info.entitlements.active.containsKey('pro');
}

/// Check if user has "premium" entitlement
@riverpod
Future<bool> hasPremium(HasPremiumRef ref) async {
  final info = await ref.watch(customerInfoProvider.future);
  return info.entitlements.active.containsKey('premium');
}

/// Purchase a package
@riverpod
class PurchasePackage extends _$PurchasePackage {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call(Package package) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      try {
        await Purchases.purchasePackage(package);
        // Refresh customer info
        ref.invalidate(customerInfoProvider);
      } catch (e) {
        print('Purchase failed: $e');
        rethrow;
      }
    });
  }
}

/// Purchase a subscription
@riverpod
class PurchaseSubscription extends _$PurchaseSubscription {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call(String productId) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      try {
        final offerings = await Purchases.getOfferings();
        final package = offerings.current?.getPackage(productId);

        if (package != null) {
          await Purchases.purchasePackage(package);
          ref.invalidate(customerInfoProvider);
        } else {
          throw Exception('Package not found: $productId');
        }
      } catch (e) {
        print('Subscription purchase failed: $e');
        rethrow;
      }
    });
  }
}

/// Restore purchases
@riverpod
class RestorePurchases extends _$RestorePurchases {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      try {
        await Purchases.restorePurchases();
        ref.invalidate(customerInfoProvider);
      } catch (e) {
        print('Restore failed: $e');
        rethrow;
      }
    });
  }
}

/// Get available offerings
@riverpod
Future<Offerings?> offerings(OfferingsRef ref) async {
  await ref.watch(initializeRevenueCatProvider.future);
  try {
    return await Purchases.getOfferings();
  } catch (e) {
    print('Error fetching offerings: $e');
    return null;
  }
}
