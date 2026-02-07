// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'config_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$SubscriptionTierImpl _$$SubscriptionTierImplFromJson(
        Map<String, dynamic> json) =>
    _$SubscriptionTierImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      priceMonthly: (json['priceMonthly'] as num?)?.toDouble(),
      priceYearly: (json['priceYearly'] as num?)?.toDouble(),
      features:
          (json['features'] as List<dynamic>).map((e) => e as String).toList(),
    );

Map<String, dynamic> _$$SubscriptionTierImplToJson(
        _$SubscriptionTierImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'priceMonthly': instance.priceMonthly,
      'priceYearly': instance.priceYearly,
      'features': instance.features,
    };

_$CreditPackImpl _$$CreditPackImplFromJson(Map<String, dynamic> json) =>
    _$CreditPackImpl(
      credits: (json['credits'] as num).toInt(),
      price: (json['price'] as num).toDouble(),
      label: json['label'] as String,
      badge: json['badge'] as String?,
    );

Map<String, dynamic> _$$CreditPackImplToJson(_$CreditPackImpl instance) =>
    <String, dynamic>{
      'credits': instance.credits,
      'price': instance.price,
      'label': instance.label,
      'badge': instance.badge,
    };

_$ReportPriceImpl _$$ReportPriceImplFromJson(Map<String, dynamic> json) =>
    _$ReportPriceImpl(
      reportType: json['reportType'] as String,
      credits: (json['credits'] as num).toInt(),
      money: (json['money'] as num).toDouble(),
      title: json['title'] as String,
    );

Map<String, dynamic> _$$ReportPriceImplToJson(_$ReportPriceImpl instance) =>
    <String, dynamic>{
      'reportType': instance.reportType,
      'credits': instance.credits,
      'money': instance.money,
      'title': instance.title,
    };

_$FeatureGatesImpl _$$FeatureGatesImplFromJson(Map<String, dynamic> json) =>
    _$FeatureGatesImpl(
      free: Map<String, bool>.from(json['free'] as Map),
      pro: Map<String, bool>.from(json['pro'] as Map),
      premium: Map<String, bool>.from(json['premium'] as Map),
    );

Map<String, dynamic> _$$FeatureGatesImplToJson(_$FeatureGatesImpl instance) =>
    <String, dynamic>{
      'free': instance.free,
      'pro': instance.pro,
      'premium': instance.premium,
    };

_$AppConfigModelImpl _$$AppConfigModelImplFromJson(Map<String, dynamic> json) =>
    _$AppConfigModelImpl(
      chatLimits: Map<String, int>.from(json['chatLimits'] as Map),
      subscriptionTiers:
          (json['subscriptionTiers'] as Map<String, dynamic>).map(
        (k, e) =>
            MapEntry(k, SubscriptionTier.fromJson(e as Map<String, dynamic>)),
      ),
      creditPacks: (json['creditPacks'] as List<dynamic>)
          .map((e) => CreditPack.fromJson(e as Map<String, dynamic>))
          .toList(),
      reportPrices: (json['reportPrices'] as List<dynamic>)
          .map((e) => ReportPrice.fromJson(e as Map<String, dynamic>))
          .toList(),
      featureGates:
          FeatureGates.fromJson(json['featureGates'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$AppConfigModelImplToJson(
        _$AppConfigModelImpl instance) =>
    <String, dynamic>{
      'chatLimits': instance.chatLimits,
      'subscriptionTiers': instance.subscriptionTiers,
      'creditPacks': instance.creditPacks,
      'reportPrices': instance.reportPrices,
      'featureGates': instance.featureGates,
    };
