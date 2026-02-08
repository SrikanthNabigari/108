import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/models/remedy_model.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

part 'remedies_provider.g.dart';

/// Get all remedies from /api/v1/remedies
@riverpod
Future<List<RemedyModel>> remediesList(RemediesListRef ref) async {
  final response = await ApiService().get(
    ApiConstants.remedies,
    fromJson: (json) => (json as List)
        .map((e) => RemedyModel.fromJson(e as Map<String, dynamic>))
        .toList(),
  );
  return response;
}

/// Get gem recommendations from /api/v1/remedies/gems
@riverpod
Future<List<GemstoneRemedy>> gems(GemsRef ref) async {
  final response = await ApiService().get(
    ApiConstants.remediesGems,
    fromJson: (json) => (json as List)
        .map((e) => GemstoneRemedy.fromJson(e as Map<String, dynamic>))
        .toList(),
  );
  return response;
}
