// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$UserModelImpl _$$UserModelImplFromJson(Map<String, dynamic> json) =>
    _$UserModelImpl(
      id: json['id'] as String,
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      name: json['name'] as String?,
      gender: json['gender'] as String?,
      avatarUrl: json['avatarUrl'] as String?,
      onboardingComplete: json['onboardingComplete'] as bool? ?? false,
      subscriptionTier: json['subscriptionTier'] as String? ?? 'free',
      lagnaRashi: json['lagnaRashi'] as String?,
      moonRashi: json['moonRashi'] as String?,
      moonNakshatra: json['moonNakshatra'] as String?,
      birthDatetime: json['birthDatetime'] == null
          ? null
          : DateTime.parse(json['birthDatetime'] as String),
      placeName: json['placeName'] as String?,
      creditBalance: (json['creditBalance'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$$UserModelImplToJson(_$UserModelImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'email': instance.email,
      'phone': instance.phone,
      'name': instance.name,
      'gender': instance.gender,
      'avatarUrl': instance.avatarUrl,
      'onboardingComplete': instance.onboardingComplete,
      'subscriptionTier': instance.subscriptionTier,
      'lagnaRashi': instance.lagnaRashi,
      'moonRashi': instance.moonRashi,
      'moonNakshatra': instance.moonNakshatra,
      'birthDatetime': instance.birthDatetime?.toIso8601String(),
      'placeName': instance.placeName,
      'creditBalance': instance.creditBalance,
    };
