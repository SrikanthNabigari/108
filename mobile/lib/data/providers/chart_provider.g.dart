// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chart_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$birthChartHash() => r'3025b1ce986ceea766f375092ffbb5105444a45b';

/// Get full birth chart from /api/v1/chart/full
///
/// Copied from [birthChart].
@ProviderFor(birthChart)
final birthChartProvider = AutoDisposeFutureProvider<BirthChartModel>.internal(
  birthChart,
  name: r'birthChartProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$birthChartHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef BirthChartRef = AutoDisposeFutureProviderRef<BirthChartModel>;
String _$chartSummaryHash() => r'000a00cae60776dbf6ed7e04d6c0bbe5a0427fbc';

/// Get chart summary (lightweight version)
///
/// Copied from [chartSummary].
@ProviderFor(chartSummary)
final chartSummaryProvider =
    AutoDisposeFutureProvider<BirthChartModel>.internal(
  chartSummary,
  name: r'chartSummaryProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$chartSummaryHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef ChartSummaryRef = AutoDisposeFutureProviderRef<BirthChartModel>;
String _$divisionalChartHash() => r'02800e41f9f74a2a0da2c1e26c915da97a7b53c3';

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

/// Get divisional chart (D2-D60)
///
/// Copied from [divisionalChart].
@ProviderFor(divisionalChart)
const divisionalChartProvider = DivisionalChartFamily();

/// Get divisional chart (D2-D60)
///
/// Copied from [divisionalChart].
class DivisionalChartFamily extends Family<AsyncValue<BirthChartModel>> {
  /// Get divisional chart (D2-D60)
  ///
  /// Copied from [divisionalChart].
  const DivisionalChartFamily();

  /// Get divisional chart (D2-D60)
  ///
  /// Copied from [divisionalChart].
  DivisionalChartProvider call(
    String d,
  ) {
    return DivisionalChartProvider(
      d,
    );
  }

  @override
  DivisionalChartProvider getProviderOverride(
    covariant DivisionalChartProvider provider,
  ) {
    return call(
      provider.d,
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
  String? get name => r'divisionalChartProvider';
}

/// Get divisional chart (D2-D60)
///
/// Copied from [divisionalChart].
class DivisionalChartProvider
    extends AutoDisposeFutureProvider<BirthChartModel> {
  /// Get divisional chart (D2-D60)
  ///
  /// Copied from [divisionalChart].
  DivisionalChartProvider(
    String d,
  ) : this._internal(
          (ref) => divisionalChart(
            ref as DivisionalChartRef,
            d,
          ),
          from: divisionalChartProvider,
          name: r'divisionalChartProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$divisionalChartHash,
          dependencies: DivisionalChartFamily._dependencies,
          allTransitiveDependencies:
              DivisionalChartFamily._allTransitiveDependencies,
          d: d,
        );

  DivisionalChartProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.d,
  }) : super.internal();

  final String d;

  @override
  Override overrideWith(
    FutureOr<BirthChartModel> Function(DivisionalChartRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: DivisionalChartProvider._internal(
        (ref) => create(ref as DivisionalChartRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        d: d,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<BirthChartModel> createElement() {
    return _DivisionalChartProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is DivisionalChartProvider && other.d == d;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, d.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin DivisionalChartRef on AutoDisposeFutureProviderRef<BirthChartModel> {
  /// The parameter `d` of this provider.
  String get d;
}

class _DivisionalChartProviderElement
    extends AutoDisposeFutureProviderElement<BirthChartModel>
    with DivisionalChartRef {
  _DivisionalChartProviderElement(super.provider);

  @override
  String get d => (origin as DivisionalChartProvider).d;
}

String _$d9ChartHash() => r'2cb4a3ab1ebdac9f95c8802481df547a0728727f';

/// Get D9 (Navamsha) chart
///
/// Copied from [d9Chart].
@ProviderFor(d9Chart)
final d9ChartProvider = AutoDisposeFutureProvider<BirthChartModel>.internal(
  d9Chart,
  name: r'd9ChartProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$d9ChartHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef D9ChartRef = AutoDisposeFutureProviderRef<BirthChartModel>;
String _$d10ChartHash() => r'aee73e349173152ced81483c69fcf0d92862bf58';

/// Get D10 (Dasamsha) chart
///
/// Copied from [d10Chart].
@ProviderFor(d10Chart)
final d10ChartProvider = AutoDisposeFutureProvider<BirthChartModel>.internal(
  d10Chart,
  name: r'd10ChartProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$d10ChartHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef D10ChartRef = AutoDisposeFutureProviderRef<BirthChartModel>;
String _$refreshBirthChartHash() => r'05d4cf177eb184a9de78b4850fad21d8e8e0e8dc';

/// Refresh birth chart data
///
/// Copied from [RefreshBirthChart].
@ProviderFor(RefreshBirthChart)
final refreshBirthChartProvider =
    AutoDisposeAsyncNotifierProvider<RefreshBirthChart, void>.internal(
  RefreshBirthChart.new,
  name: r'refreshBirthChartProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$refreshBirthChartHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$RefreshBirthChart = AutoDisposeAsyncNotifier<void>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
