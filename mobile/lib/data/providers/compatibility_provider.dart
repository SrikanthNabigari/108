import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/models/compatibility_model.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

part 'compatibility_provider.g.dart';

@riverpod
class CheckCompatibility extends _$CheckCompatibility {
  @override
  FutureOr<CompatibilityModel?> build() => null;

  Future<CompatibilityModel> call({
    required String partnerName,
    required DateTime partnerBirthDatetime,
    required double partnerLatitude,
    required double partnerLongitude,
    required double partnerTimezoneOffset,
  }) async {
    state = const AsyncValue.loading();
    final result = await AsyncValue.guard(() async {
      return await ApiService().post(
        ApiConstants.compatibilityQuick,
        body: {
          'partner_name': partnerName,
          'partner_birth_datetime': partnerBirthDatetime.toIso8601String(),
          'partner_latitude': partnerLatitude,
          'partner_longitude': partnerLongitude,
          'partner_timezone_offset': partnerTimezoneOffset,
        },
        fromJson: (json) => CompatibilityModel.fromJson(json),
      );
    });
    state = result;
    return result.value!;
  }
}
