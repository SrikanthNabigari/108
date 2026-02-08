import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_model.freezed.dart';
part 'user_model.g.dart';

@Freezed(fromJson: true, toJson: true)
class UserModel with _$UserModel {
  const UserModel._();

  // ignore: invalid_annotation_target
  @JsonSerializable(fieldRename: FieldRename.snake)
  const factory UserModel({
    required String id,
    String? email,
    String? phone,
    String? name,
    String? gender,
    String? avatarUrl,
    @Default('free') String subscriptionTier,
    DateTime? birthDatetime,
    double? birthLatitude,
    double? birthLongitude,
    double? timezoneOffset,
    String? placeName,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) = _UserModel;

  factory UserModel.fromJson(Map<String, dynamic> json) =>
      _$UserModelFromJson(json);

  /// Whether user has completed the onboarding flow
  bool get onboardingComplete => name != null && birthDatetime != null;

  /// Whether user has set their profile (name)
  bool get hasProfile => name != null && name!.isNotEmpty;

  /// Whether user has entered birth details
  bool get hasBirthDetails => birthDatetime != null;
}
