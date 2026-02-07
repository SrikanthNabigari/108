import 'package:freezed_annotation/freezed_annotation.dart';

part 'config_model.freezed.dart';
part 'config_model.g.dart';

@freezed
class SubscriptionTier with _$SubscriptionTier {
  const factory SubscriptionTier({
    required String id, // 'free', 'pro', 'premium'
    required String name,
    double? priceMonthly,
    double? priceYearly,
    required List<String> features,
  }) = _SubscriptionTier;

  factory SubscriptionTier.fromJson(Map<String, dynamic> json) =>
      _$SubscriptionTierFromJson(json);
}

@freezed
class CreditPack with _$CreditPack {
  const factory CreditPack({
    required int credits,
    required double price,
    required String label,
    String? badge, // 'best_value', etc.
  }) = _CreditPack;

  factory CreditPack.fromJson(Map<String, dynamic> json) =>
      _$CreditPackFromJson(json);
}

@freezed
class ReportPrice with _$ReportPrice {
  const factory ReportPrice({
    required String reportType,
    required int credits,
    required double money,
    required String title,
  }) = _ReportPrice;

  factory ReportPrice.fromJson(Map<String, dynamic> json) =>
      _$ReportPriceFromJson(json);
}

@freezed
class FeatureGates with _$FeatureGates {
  const factory FeatureGates({
    required Map<String, bool> free,
    required Map<String, bool> pro,
    required Map<String, bool> premium,
  }) = _FeatureGates;

  factory FeatureGates.fromJson(Map<String, dynamic> json) =>
      _$FeatureGatesFromJson(json);
}

@freezed
class AppConfigModel with _$AppConfigModel {
  const factory AppConfigModel({
    required Map<String, int> chatLimits, // 'free': 5, 'pro': 30, 'premium': -1
    required Map<String, SubscriptionTier> subscriptionTiers,
    required List<CreditPack> creditPacks,
    required List<ReportPrice> reportPrices,
    required FeatureGates featureGates,
  }) = _AppConfigModel;

  factory AppConfigModel.fromJson(Map<String, dynamic> json) =>
      _$AppConfigModelFromJson(json);
}
