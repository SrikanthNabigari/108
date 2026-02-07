import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/models/config_model.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

part 'config_provider.g.dart';

/// Get app config from /api/v1/config
/// Cached for 5 minutes by the backend
@riverpod
Future<AppConfigModel> appConfig(AppConfigRef ref) async {
  final response = await ApiService().get(
    ApiConstants.config,
    fromJson: (json) => AppConfigModel.fromJson(json),
    needsAuth: false, // Config is public
  );
  return response;
}

/// Get chat message limit for current tier
@riverpod
Future<int> chatMessageLimit(ChatMessageLimitRef ref, String tier) async {
  final config = await ref.watch(appConfigProvider.future);
  return config.chatLimits[tier] ?? 5;
}

/// Get feature gate status
@riverpod
Future<bool> isFeatureEnabled(IsFeatureEnabledRef ref, {
  required String feature,
  required String tier,
}) async {
  final config = await ref.watch(appConfigProvider.future);

  switch (tier) {
    case 'free':
      return config.featureGates.free[feature] ?? false;
    case 'pro':
      return config.featureGates.pro[feature] ?? false;
    case 'premium':
      return config.featureGates.premium[feature] ?? false;
    default:
      return false;
  }
}

/// Get report price
@riverpod
Future<ReportPrice?> reportPrice(ReportPriceRef ref, String reportType) async {
  final config = await ref.watch(appConfigProvider.future);
  try {
    return config.reportPrices.firstWhere(
      (p) => p.reportType == reportType,
    );
  } catch (e) {
    return null;
  }
}

/// Get all available credit packs
@riverpod
Future<List<CreditPack>> creditPacks(CreditPacksRef ref) async {
  final config = await ref.watch(appConfigProvider.future);
  return config.creditPacks;
}
