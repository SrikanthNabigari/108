import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/models/user_model.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'auth_provider.dart';

part 'user_provider.g.dart';

/// Get user profile from /api/v1/me
@riverpod
Future<UserModel> userProfile(UserProfileRef ref) async {
  final user = await ref.watch(currentUserProvider.future);
  if (user == null) throw Exception('Not authenticated');

  final response = await ApiService().get(
    ApiConstants.userMe,
    fromJson: (json) => UserModel.fromJson(json),
  );
  return response;
}

/// Update user profile
@riverpod
class UpdateUserProfile extends _$UpdateUserProfile {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call(Map<String, dynamic> updates) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await ApiService().put(
        ApiConstants.userMe,
        body: updates,
        fromJson: (json) => json,
      );
      // Invalidate cache
      ref.invalidate(userProfileProvider);
    });
  }
}

/// Update birth details
@riverpod
class UpdateBirthDetails extends _$UpdateBirthDetails {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call(Map<String, dynamic> birthData) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await ApiService().put(
        ApiConstants.userBirthDetails,
        body: birthData,
        fromJson: (json) => json,
      );
      // Invalidate caches
      ref.invalidate(userProfileProvider);
    });
  }
}
