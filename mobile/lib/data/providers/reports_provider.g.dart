// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'reports_provider.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ReportInfoImpl _$$ReportInfoImplFromJson(Map<String, dynamic> json) =>
    _$ReportInfoImpl(
      reportType: json['reportType'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      credits: (json['credits'] as num).toInt(),
      money: (json['money'] as num).toDouble(),
    );

Map<String, dynamic> _$$ReportInfoImplToJson(_$ReportInfoImpl instance) =>
    <String, dynamic>{
      'reportType': instance.reportType,
      'title': instance.title,
      'description': instance.description,
      'credits': instance.credits,
      'money': instance.money,
    };

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$availableReportsHash() => r'0077268c39d2c9931119936c48312da460c5710c';

/// Get list of available reports with prices
///
/// Copied from [availableReports].
@ProviderFor(availableReports)
final availableReportsProvider =
    AutoDisposeFutureProvider<List<ReportInfo>>.internal(
  availableReports,
  name: r'availableReportsProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$availableReportsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef AvailableReportsRef = AutoDisposeFutureProviderRef<List<ReportInfo>>;
String _$userReportsHash() => r'49e5a4b497b245af4db38e5b103b29985fe1819f';

/// Get user's generated reports
///
/// Copied from [userReports].
@ProviderFor(userReports)
final userReportsProvider =
    AutoDisposeFutureProvider<List<ReportModel>>.internal(
  userReports,
  name: r'userReportsProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$userReportsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef UserReportsRef = AutoDisposeFutureProviderRef<List<ReportModel>>;
String _$reportDetailHash() => r'70663aba0794155ecfdd248399c31837bd7c0823';

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

/// Get specific report details
///
/// Copied from [reportDetail].
@ProviderFor(reportDetail)
const reportDetailProvider = ReportDetailFamily();

/// Get specific report details
///
/// Copied from [reportDetail].
class ReportDetailFamily extends Family<AsyncValue<ReportModel>> {
  /// Get specific report details
  ///
  /// Copied from [reportDetail].
  const ReportDetailFamily();

  /// Get specific report details
  ///
  /// Copied from [reportDetail].
  ReportDetailProvider call(
    String reportId,
  ) {
    return ReportDetailProvider(
      reportId,
    );
  }

  @override
  ReportDetailProvider getProviderOverride(
    covariant ReportDetailProvider provider,
  ) {
    return call(
      provider.reportId,
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
  String? get name => r'reportDetailProvider';
}

/// Get specific report details
///
/// Copied from [reportDetail].
class ReportDetailProvider extends AutoDisposeFutureProvider<ReportModel> {
  /// Get specific report details
  ///
  /// Copied from [reportDetail].
  ReportDetailProvider(
    String reportId,
  ) : this._internal(
          (ref) => reportDetail(
            ref as ReportDetailRef,
            reportId,
          ),
          from: reportDetailProvider,
          name: r'reportDetailProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$reportDetailHash,
          dependencies: ReportDetailFamily._dependencies,
          allTransitiveDependencies:
              ReportDetailFamily._allTransitiveDependencies,
          reportId: reportId,
        );

  ReportDetailProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.reportId,
  }) : super.internal();

  final String reportId;

  @override
  Override overrideWith(
    FutureOr<ReportModel> Function(ReportDetailRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: ReportDetailProvider._internal(
        (ref) => create(ref as ReportDetailRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        reportId: reportId,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<ReportModel> createElement() {
    return _ReportDetailProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is ReportDetailProvider && other.reportId == reportId;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, reportId.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin ReportDetailRef on AutoDisposeFutureProviderRef<ReportModel> {
  /// The parameter `reportId` of this provider.
  String get reportId;
}

class _ReportDetailProviderElement
    extends AutoDisposeFutureProviderElement<ReportModel> with ReportDetailRef {
  _ReportDetailProviderElement(super.provider);

  @override
  String get reportId => (origin as ReportDetailProvider).reportId;
}

String _$reportPdfUrlHash() => r'b1df92595035864392f6765b2b4fece807567ebe';

/// Download report PDF
///
/// Copied from [reportPdfUrl].
@ProviderFor(reportPdfUrl)
const reportPdfUrlProvider = ReportPdfUrlFamily();

/// Download report PDF
///
/// Copied from [reportPdfUrl].
class ReportPdfUrlFamily extends Family<AsyncValue<String>> {
  /// Download report PDF
  ///
  /// Copied from [reportPdfUrl].
  const ReportPdfUrlFamily();

  /// Download report PDF
  ///
  /// Copied from [reportPdfUrl].
  ReportPdfUrlProvider call(
    String reportId,
  ) {
    return ReportPdfUrlProvider(
      reportId,
    );
  }

  @override
  ReportPdfUrlProvider getProviderOverride(
    covariant ReportPdfUrlProvider provider,
  ) {
    return call(
      provider.reportId,
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
  String? get name => r'reportPdfUrlProvider';
}

/// Download report PDF
///
/// Copied from [reportPdfUrl].
class ReportPdfUrlProvider extends AutoDisposeFutureProvider<String> {
  /// Download report PDF
  ///
  /// Copied from [reportPdfUrl].
  ReportPdfUrlProvider(
    String reportId,
  ) : this._internal(
          (ref) => reportPdfUrl(
            ref as ReportPdfUrlRef,
            reportId,
          ),
          from: reportPdfUrlProvider,
          name: r'reportPdfUrlProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$reportPdfUrlHash,
          dependencies: ReportPdfUrlFamily._dependencies,
          allTransitiveDependencies:
              ReportPdfUrlFamily._allTransitiveDependencies,
          reportId: reportId,
        );

  ReportPdfUrlProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.reportId,
  }) : super.internal();

  final String reportId;

  @override
  Override overrideWith(
    FutureOr<String> Function(ReportPdfUrlRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: ReportPdfUrlProvider._internal(
        (ref) => create(ref as ReportPdfUrlRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        reportId: reportId,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<String> createElement() {
    return _ReportPdfUrlProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is ReportPdfUrlProvider && other.reportId == reportId;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, reportId.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin ReportPdfUrlRef on AutoDisposeFutureProviderRef<String> {
  /// The parameter `reportId` of this provider.
  String get reportId;
}

class _ReportPdfUrlProviderElement
    extends AutoDisposeFutureProviderElement<String> with ReportPdfUrlRef {
  _ReportPdfUrlProviderElement(super.provider);

  @override
  String get reportId => (origin as ReportPdfUrlProvider).reportId;
}

String _$generateReportHash() => r'f39667e7203efbe9b6db43d51ae0a28739a0564b';

/// Generate new report
///
/// Copied from [GenerateReport].
@ProviderFor(GenerateReport)
final generateReportProvider =
    AutoDisposeAsyncNotifierProvider<GenerateReport, void>.internal(
  GenerateReport.new,
  name: r'generateReportProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$generateReportHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$GenerateReport = AutoDisposeAsyncNotifier<void>;
String _$refreshUserReportsHash() =>
    r'9e58b6a49e19210c154d29b2b30556057549ced8';

/// Refresh user reports
///
/// Copied from [RefreshUserReports].
@ProviderFor(RefreshUserReports)
final refreshUserReportsProvider =
    AutoDisposeAsyncNotifierProvider<RefreshUserReports, void>.internal(
  RefreshUserReports.new,
  name: r'refreshUserReportsProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$refreshUserReportsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$RefreshUserReports = AutoDisposeAsyncNotifier<void>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
