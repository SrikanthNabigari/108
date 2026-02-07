import 'package:freezed_annotation/freezed_annotation.dart';

part 'report_model.freezed.dart';
part 'report_model.g.dart';

@freezed
class ReportModel with _$ReportModel {
  const factory ReportModel({
    required String id,
    required String userId,
    required String reportType, // 'year_ahead', 'career_blueprint', 'birth_chart_full', etc.
    required String title,
    required Map<String, dynamic> content, // structured report data
    String? pdfUrl, // Supabase Storage URL
    @Default(0) int creditsCharged,
    @Default('completed') String status, // 'generating', 'completed', 'failed'
    required DateTime createdAt,
  }) = _ReportModel;

  factory ReportModel.fromJson(Map<String, dynamic> json) =>
      _$ReportModelFromJson(json);
}
