import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

part 'credits_provider.freezed.dart';
part 'credits_provider.g.dart';

@freezed
class CreditTransaction with _$CreditTransaction {
  const factory CreditTransaction({
    required String id,
    required int amount,
    required int balanceAfter,
    required String transactionType, // 'purchase', 'spend', 'refund', 'bonus'
    String? description,
    String? referenceId,
    required DateTime createdAt,
  }) = _CreditTransaction;

  factory CreditTransaction.fromJson(Map<String, dynamic> json) =>
      _$CreditTransactionFromJson(json);
}

/// Get current credit balance
@riverpod
Future<int> creditBalance(CreditBalanceRef ref) async {
  final response = await ApiService().get(
    ApiConstants.creditsBalance,
    fromJson: (json) => json['balance'] as int,
  );
  return response;
}

/// Get credit transaction history
@riverpod
Future<List<CreditTransaction>> creditHistory(
  CreditHistoryRef ref, {
  int limit = 50,
  int offset = 0,
}) async {
  final response = await ApiService().get(
    '${ApiConstants.creditsHistory}?limit=$limit&offset=$offset',
    fromJson: (json) => (json['transactions'] as List)
        .map((t) => CreditTransaction.fromJson(t))
        .toList(),
  );
  return response;
}

/// Refresh credit balance
@riverpod
class RefreshCredits extends _$RefreshCredits {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call() async {
    ref.invalidate(creditBalanceProvider);
    ref.invalidate(creditHistoryProvider);
  }
}
