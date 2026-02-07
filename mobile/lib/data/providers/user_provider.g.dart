// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$userProfileHash() => r'414f65161e4c4ca7969531fef04cbcae06f98db3';

/// Get user profile from /api/v1/me
///
/// Copied from [userProfile].
@ProviderFor(userProfile)
final userProfileProvider = AutoDisposeFutureProvider<UserModel>.internal(
  userProfile,
  name: r'userProfileProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$userProfileHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef UserProfileRef = AutoDisposeFutureProviderRef<UserModel>;
String _$updateUserProfileHash() => r'325bd693c497018b02d430058dae378ebb86c538';

/// Update user profile
///
/// Copied from [UpdateUserProfile].
@ProviderFor(UpdateUserProfile)
final updateUserProfileProvider =
    AutoDisposeAsyncNotifierProvider<UpdateUserProfile, void>.internal(
  UpdateUserProfile.new,
  name: r'updateUserProfileProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$updateUserProfileHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$UpdateUserProfile = AutoDisposeAsyncNotifier<void>;
String _$updateBirthDetailsHash() =>
    r'c3e083e9721fa15523816fa7c19f3c4dd624049a';

/// Update birth details
///
/// Copied from [UpdateBirthDetails].
@ProviderFor(UpdateBirthDetails)
final updateBirthDetailsProvider =
    AutoDisposeAsyncNotifierProvider<UpdateBirthDetails, void>.internal(
  UpdateBirthDetails.new,
  name: r'updateBirthDetailsProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$updateBirthDetailsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$UpdateBirthDetails = AutoDisposeAsyncNotifier<void>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
