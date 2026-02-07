import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/models/report_model.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

part 'reports_provider.freezed.dart';
part 'reports_provider.g.dart';

@freezed
class ReportInfo with _$ReportInfo {
  const factory ReportInfo({
    required String reportType,
    required String title,
    String? description,
    required int credits,
    required double money,
  }) = _ReportInfo;

  factory ReportInfo.fromJson(Map<String, dynamic> json) =>
      _$ReportInfoFromJson(json);
}

/// Get list of available reports with prices
@riverpod
Future<List<ReportInfo>> availableReports(AvailableReportsRef ref) async {
  final response = await ApiService().get(
    ApiConstants.reports,
    fromJson: (json) => (json['reports'] as List)
        .map((r) => ReportInfo.fromJson(r))
        .toList(),
  );
  return response;
}

/// Get user's generated reports
@riverpod
Future<List<ReportModel>> userReports(UserReportsRef ref) async {
  final response = await ApiService().get(
    ApiConstants.reports,
    fromJson: (json) => (json['user_reports'] as List)
        .map((r) => ReportModel.fromJson(r))
        .toList(),
  );
  return response;
}

/// Get specific report details
@riverpod
Future<ReportModel> reportDetail(ReportDetailRef ref, String reportId) async {
  final response = await ApiService().get(
    ApiConstants.reportDetail(reportId),
    fromJson: (json) => ReportModel.fromJson(json),
  );
  return response;
}

/// Generate new report
@riverpod
class GenerateReport extends _$GenerateReport {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<ReportModel> call(String reportType) async {
    final result = await AsyncValue.guard(() async {
      return await ApiService().post(
        ApiConstants.reports,
        body: {'report_type': reportType},
        fromJson: (json) => ReportModel.fromJson(json),
      );
    });

    state = result.whenData((_) {});

    return result.when(
      data: (data) => data,
      loading: () => throw Exception('Loading...'),
      error: (error, stack) => throw error,
    );
  }
}

/// Download report PDF
@riverpod
Future<String> reportPdfUrl(ReportPdfUrlRef ref, String reportId) async {
  // This would typically trigger a download, for now just return the URL
  return ApiConstants.baseUrl + ApiConstants.reportPdf(reportId);
}

/// Refresh user reports
@riverpod
class RefreshUserReports extends _$RefreshUserReports {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call() async {
    ref.invalidate(userReportsProvider);
  }
}
