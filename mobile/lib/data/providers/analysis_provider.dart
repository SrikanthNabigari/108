import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/models/yoga_model.dart';
import 'package:one_zero_eight/data/models/dosha_model.dart';
import 'package:one_zero_eight/data/models/dasha_model.dart';
import 'package:one_zero_eight/data/models/transit_model.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

part 'analysis_provider.g.dart';

/// Get yogas analysis from /api/v1/analysis/yogas
@riverpod
Future<List<YogaModel>> yogas(YogasRef ref) async {
  final response = await ApiService().get(
    ApiConstants.analysisYogas,
    fromJson: (json) => (json as List)
        .map((e) => YogaModel.fromJson(e as Map<String, dynamic>))
        .toList(),
  );
  return response;
}

/// Get doshas analysis from /api/v1/analysis/doshas
@riverpod
Future<List<DoshaModel>> doshas(DoshasRef ref) async {
  final response = await ApiService().get(
    ApiConstants.analysisDoshas,
    fromJson: (json) => (json as List)
        .map((e) => DoshaModel.fromJson(e as Map<String, dynamic>))
        .toList(),
  );
  return response;
}

/// Get dasha periods from /api/v1/analysis/dasha
@riverpod
Future<DashaModel> dasha(DashaRef ref) async {
  final response = await ApiService().get(
    ApiConstants.analysisDasha,
    fromJson: (json) => DashaModel.fromJson(json),
  );
  return response;
}

/// Get current transits from /api/v1/analysis/transits
@riverpod
Future<TransitModel> transits(TransitsRef ref) async {
  final response = await ApiService().get(
    ApiConstants.analysisTransits,
    fromJson: (json) => TransitModel.fromJson(json),
  );
  return response;
}
