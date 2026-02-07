import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_model.freezed.dart';
part 'user_model.g.dart';

@freezed
class UserModel with _$UserModel {
  const factory UserModel({
    required String id,
    String? email,
    String? phone,
    String? name,
    String? gender,
    String? avatarUrl,
    @Default(false) bool onboardingComplete,
    @Default('free') String subscriptionTier,
    String? lagnaRashi,
    String? moonRashi,
    String? moonNakshatra,
    DateTime? birthDatetime,
    String? placeName,
    @Default(0) int creditBalance,
  }) = _UserModel;

  factory UserModel.fromJson(Map<String, dynamic> json) =>
      _$UserModelFromJson(json);
}
