// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'remedies_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$remediesListHash() => r'fefa1b903f11f4274b318a70bc8ed90ca56b48b4';

/// Get all remedies from /api/v1/remedies
///
/// Copied from [remediesList].
@ProviderFor(remediesList)
final remediesListProvider =
    AutoDisposeFutureProvider<List<RemedyModel>>.internal(
  remediesList,
  name: r'remediesListProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$remediesListHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef RemediesListRef = AutoDisposeFutureProviderRef<List<RemedyModel>>;
String _$gemsHash() => r'abf05fac2a745b4f683224618f466b2a239dbe02';

/// Get gem recommendations from /api/v1/remedies/gems
///
/// Copied from [gems].
@ProviderFor(gems)
final gemsProvider = AutoDisposeFutureProvider<List<GemstoneRemedy>>.internal(
  gems,
  name: r'gemsProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$gemsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef GemsRef = AutoDisposeFutureProviderRef<List<GemstoneRemedy>>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
