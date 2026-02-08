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
      avatarUrl: json['avatar_url'] as String?,
      subscriptionTier: json['subscription_tier'] as String? ?? 'free',
      birthDatetime: json['birth_datetime'] == null
          ? null
          : DateTime.parse(json['birth_datetime'] as String),
      birthLatitude: (json['birth_latitude'] as num?)?.toDouble(),
      birthLongitude: (json['birth_longitude'] as num?)?.toDouble(),
      timezoneOffset: (json['timezone_offset'] as num?)?.toDouble(),
      placeName: json['place_name'] as String?,
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] == null
          ? null
          : DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$$UserModelImplToJson(_$UserModelImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'email': instance.email,
      'phone': instance.phone,
      'name': instance.name,
      'gender': instance.gender,
      'avatar_url': instance.avatarUrl,
      'subscription_tier': instance.subscriptionTier,
      'birth_datetime': instance.birthDatetime?.toIso8601String(),
      'birth_latitude': instance.birthLatitude,
      'birth_longitude': instance.birthLongitude,
      'timezone_offset': instance.timezoneOffset,
      'place_name': instance.placeName,
      'created_at': instance.createdAt?.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };
