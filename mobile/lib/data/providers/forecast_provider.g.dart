// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'forecast_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$dailyForecastHash() => r'5a69f3ea205f1de74d254cade888ef312c888f7c';

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

/// Get daily forecast
///
/// Copied from [dailyForecast].
@ProviderFor(dailyForecast)
const dailyForecastProvider = DailyForecastFamily();

/// Get daily forecast
///
/// Copied from [dailyForecast].
class DailyForecastFamily extends Family<AsyncValue<ForecastModel>> {
  /// Get daily forecast
  ///
  /// Copied from [dailyForecast].
  const DailyForecastFamily();

  /// Get daily forecast
  ///
  /// Copied from [dailyForecast].
  DailyForecastProvider call([
    DateTime? date,
  ]) {
    return DailyForecastProvider(
      date,
    );
  }

  @override
  DailyForecastProvider getProviderOverride(
    covariant DailyForecastProvider provider,
  ) {
    return call(
      provider.date,
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
  String? get name => r'dailyForecastProvider';
}

/// Get daily forecast
///
/// Copied from [dailyForecast].
class DailyForecastProvider extends AutoDisposeFutureProvider<ForecastModel> {
  /// Get daily forecast
  ///
  /// Copied from [dailyForecast].
  DailyForecastProvider([
    DateTime? date,
  ]) : this._internal(
          (ref) => dailyForecast(
            ref as DailyForecastRef,
            date,
          ),
          from: dailyForecastProvider,
          name: r'dailyForecastProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$dailyForecastHash,
          dependencies: DailyForecastFamily._dependencies,
          allTransitiveDependencies:
              DailyForecastFamily._allTransitiveDependencies,
          date: date,
        );

  DailyForecastProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.date,
  }) : super.internal();

  final DateTime? date;

  @override
  Override overrideWith(
    FutureOr<ForecastModel> Function(DailyForecastRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: DailyForecastProvider._internal(
        (ref) => create(ref as DailyForecastRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        date: date,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<ForecastModel> createElement() {
    return _DailyForecastProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is DailyForecastProvider && other.date == date;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, date.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin DailyForecastRef on AutoDisposeFutureProviderRef<ForecastModel> {
  /// The parameter `date` of this provider.
  DateTime? get date;
}

class _DailyForecastProviderElement
    extends AutoDisposeFutureProviderElement<ForecastModel>
    with DailyForecastRef {
  _DailyForecastProviderElement(super.provider);

  @override
  DateTime? get date => (origin as DailyForecastProvider).date;
}

String _$weeklyForecastHash() => r'f27e91c7f1bce98edcb04d463ec84ddbe7f4d134';

/// Get weekly forecast
///
/// Copied from [weeklyForecast].
@ProviderFor(weeklyForecast)
const weeklyForecastProvider = WeeklyForecastFamily();

/// Get weekly forecast
///
/// Copied from [weeklyForecast].
class WeeklyForecastFamily extends Family<AsyncValue<ForecastModel>> {
  /// Get weekly forecast
  ///
  /// Copied from [weeklyForecast].
  const WeeklyForecastFamily();

  /// Get weekly forecast
  ///
  /// Copied from [weeklyForecast].
  WeeklyForecastProvider call([
    DateTime? startDate,
  ]) {
    return WeeklyForecastProvider(
      startDate,
    );
  }

  @override
  WeeklyForecastProvider getProviderOverride(
    covariant WeeklyForecastProvider provider,
  ) {
    return call(
      provider.startDate,
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
  String? get name => r'weeklyForecastProvider';
}

/// Get weekly forecast
///
/// Copied from [weeklyForecast].
class WeeklyForecastProvider extends AutoDisposeFutureProvider<ForecastModel> {
  /// Get weekly forecast
  ///
  /// Copied from [weeklyForecast].
  WeeklyForecastProvider([
    DateTime? startDate,
  ]) : this._internal(
          (ref) => weeklyForecast(
            ref as WeeklyForecastRef,
            startDate,
          ),
          from: weeklyForecastProvider,
          name: r'weeklyForecastProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$weeklyForecastHash,
          dependencies: WeeklyForecastFamily._dependencies,
          allTransitiveDependencies:
              WeeklyForecastFamily._allTransitiveDependencies,
          startDate: startDate,
        );

  WeeklyForecastProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.startDate,
  }) : super.internal();

  final DateTime? startDate;

  @override
  Override overrideWith(
    FutureOr<ForecastModel> Function(WeeklyForecastRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: WeeklyForecastProvider._internal(
        (ref) => create(ref as WeeklyForecastRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        startDate: startDate,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<ForecastModel> createElement() {
    return _WeeklyForecastProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is WeeklyForecastProvider && other.startDate == startDate;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, startDate.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin WeeklyForecastRef on AutoDisposeFutureProviderRef<ForecastModel> {
  /// The parameter `startDate` of this provider.
  DateTime? get startDate;
}

class _WeeklyForecastProviderElement
    extends AutoDisposeFutureProviderElement<ForecastModel>
    with WeeklyForecastRef {
  _WeeklyForecastProviderElement(super.provider);

  @override
  DateTime? get startDate => (origin as WeeklyForecastProvider).startDate;
}

String _$monthlyForecastHash() => r'07c8a24c70e0098c557aca184735902da2f70a44';

/// Get monthly forecast
///
/// Copied from [monthlyForecast].
@ProviderFor(monthlyForecast)
const monthlyForecastProvider = MonthlyForecastFamily();

/// Get monthly forecast
///
/// Copied from [monthlyForecast].
class MonthlyForecastFamily extends Family<AsyncValue<ForecastModel>> {
  /// Get monthly forecast
  ///
  /// Copied from [monthlyForecast].
  const MonthlyForecastFamily();

  /// Get monthly forecast
  ///
  /// Copied from [monthlyForecast].
  MonthlyForecastProvider call([
    DateTime? startDate,
  ]) {
    return MonthlyForecastProvider(
      startDate,
    );
  }

  @override
  MonthlyForecastProvider getProviderOverride(
    covariant MonthlyForecastProvider provider,
  ) {
    return call(
      provider.startDate,
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
  String? get name => r'monthlyForecastProvider';
}

/// Get monthly forecast
///
/// Copied from [monthlyForecast].
class MonthlyForecastProvider extends AutoDisposeFutureProvider<ForecastModel> {
  /// Get monthly forecast
  ///
  /// Copied from [monthlyForecast].
  MonthlyForecastProvider([
    DateTime? startDate,
  ]) : this._internal(
          (ref) => monthlyForecast(
            ref as MonthlyForecastRef,
            startDate,
          ),
          from: monthlyForecastProvider,
          name: r'monthlyForecastProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$monthlyForecastHash,
          dependencies: MonthlyForecastFamily._dependencies,
          allTransitiveDependencies:
              MonthlyForecastFamily._allTransitiveDependencies,
          startDate: startDate,
        );

  MonthlyForecastProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.startDate,
  }) : super.internal();

  final DateTime? startDate;

  @override
  Override overrideWith(
    FutureOr<ForecastModel> Function(MonthlyForecastRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: MonthlyForecastProvider._internal(
        (ref) => create(ref as MonthlyForecastRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        startDate: startDate,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<ForecastModel> createElement() {
    return _MonthlyForecastProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is MonthlyForecastProvider && other.startDate == startDate;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, startDate.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin MonthlyForecastRef on AutoDisposeFutureProviderRef<ForecastModel> {
  /// The parameter `startDate` of this provider.
  DateTime? get startDate;
}

class _MonthlyForecastProviderElement
    extends AutoDisposeFutureProviderElement<ForecastModel>
    with MonthlyForecastRef {
  _MonthlyForecastProviderElement(super.provider);

  @override
  DateTime? get startDate => (origin as MonthlyForecastProvider).startDate;
}

String _$yearlyForecastHash() => r'ab2b6863b2486735bb6e5808167480b31f8e00e0';

/// Get yearly forecast
///
/// Copied from [yearlyForecast].
@ProviderFor(yearlyForecast)
const yearlyForecastProvider = YearlyForecastFamily();

/// Get yearly forecast
///
/// Copied from [yearlyForecast].
class YearlyForecastFamily extends Family<AsyncValue<ForecastModel>> {
  /// Get yearly forecast
  ///
  /// Copied from [yearlyForecast].
  const YearlyForecastFamily();

  /// Get yearly forecast
  ///
  /// Copied from [yearlyForecast].
  YearlyForecastProvider call([
    DateTime? startDate,
  ]) {
    return YearlyForecastProvider(
      startDate,
    );
  }

  @override
  YearlyForecastProvider getProviderOverride(
    covariant YearlyForecastProvider provider,
  ) {
    return call(
      provider.startDate,
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
  String? get name => r'yearlyForecastProvider';
}

/// Get yearly forecast
///
/// Copied from [yearlyForecast].
class YearlyForecastProvider extends AutoDisposeFutureProvider<ForecastModel> {
  /// Get yearly forecast
  ///
  /// Copied from [yearlyForecast].
  YearlyForecastProvider([
    DateTime? startDate,
  ]) : this._internal(
          (ref) => yearlyForecast(
            ref as YearlyForecastRef,
            startDate,
          ),
          from: yearlyForecastProvider,
          name: r'yearlyForecastProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$yearlyForecastHash,
          dependencies: YearlyForecastFamily._dependencies,
          allTransitiveDependencies:
              YearlyForecastFamily._allTransitiveDependencies,
          startDate: startDate,
        );

  YearlyForecastProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.startDate,
  }) : super.internal();

  final DateTime? startDate;

  @override
  Override overrideWith(
    FutureOr<ForecastModel> Function(YearlyForecastRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: YearlyForecastProvider._internal(
        (ref) => create(ref as YearlyForecastRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        startDate: startDate,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<ForecastModel> createElement() {
    return _YearlyForecastProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is YearlyForecastProvider && other.startDate == startDate;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, startDate.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin YearlyForecastRef on AutoDisposeFutureProviderRef<ForecastModel> {
  /// The parameter `startDate` of this provider.
  DateTime? get startDate;
}

class _YearlyForecastProviderElement
    extends AutoDisposeFutureProviderElement<ForecastModel>
    with YearlyForecastRef {
  _YearlyForecastProviderElement(super.provider);

  @override
  DateTime? get startDate => (origin as YearlyForecastProvider).startDate;
}

String _$refreshForecastsHash() => r'3e4899832e4dc6b4648add6b2e7f0ff64a56b533';

/// Refresh all forecasts
///
/// Copied from [RefreshForecasts].
@ProviderFor(RefreshForecasts)
final refreshForecastsProvider =
    AutoDisposeAsyncNotifierProvider<RefreshForecasts, void>.internal(
  RefreshForecasts.new,
  name: r'refreshForecastsProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$refreshForecastsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$RefreshForecasts = AutoDisposeAsyncNotifier<void>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
