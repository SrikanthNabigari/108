import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:one_zero_eight/data/models/event_model.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

part 'events_provider.g.dart';

/// Get events for a date range
@riverpod
Future<List<EventModel>> eventsForDateRange(
  EventsForDateRangeRef ref,
  DateTime startDate,
  DateTime endDate,
) async {
  final response = await ApiService().get(
    '${ApiConstants.events}?start=${startDate.toIso8601String()}&end=${endDate.toIso8601String()}',
    fromJson: (json) => (json['events'] as List)
        .map((e) => EventModel.fromJson(e))
        .toList(),
  );
  return response;
}

/// Get all user events
@riverpod
Future<List<EventModel>> allEvents(AllEventsRef ref) async {
  final response = await ApiService().get(
    ApiConstants.events,
    fromJson: (json) => (json['events'] as List)
        .map((e) => EventModel.fromJson(e))
        .toList(),
  );
  return response;
}

/// Create user event
@riverpod
class CreateEvent extends _$CreateEvent {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call(Map<String, dynamic> eventData) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      try {
        await ApiService().post(
          ApiConstants.events,
          body: eventData,
          fromJson: (json) => json,
        );
        // Invalidate cache
        ref.invalidate(allEventsProvider);
      } catch (e) {
        print('Failed to create event: $e');
        rethrow;
      }
    });
  }
}

/// Update user event
@riverpod
class UpdateEvent extends _$UpdateEvent {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call(String eventId, Map<String, dynamic> updates) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      try {
        await ApiService().put(
          '${ApiConstants.events}/$eventId',
          body: updates,
          fromJson: (json) => json,
        );
        ref.invalidate(allEventsProvider);
      } catch (e) {
        print('Failed to update event: $e');
        rethrow;
      }
    });
  }
}

/// Delete user event
@riverpod
class DeleteEvent extends _$DeleteEvent {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<void> call(String eventId) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      try {
        await ApiService().delete('${ApiConstants.events}/$eventId');
        ref.invalidate(allEventsProvider);
      } catch (e) {
        print('Failed to delete event: $e');
        rethrow;
      }
    });
  }
}

/// Correlate past event with chart
@riverpod
class CorrelateEvent extends _$CorrelateEvent {
  @override
  FutureOr<void> build() {
    // Void provider
  }

  Future<Map<String, dynamic>> call(Map<String, dynamic> eventData) async {
    final result = await AsyncValue.guard(() async {
      return await ApiService().post(
        ApiConstants.eventsCorrelate,
        body: eventData,
        fromJson: (json) => json as Map<String, dynamic>,
      );
    });

    state = result;
    return result.when(
      data: (data) => data,
      loading: () => {},
      error: (error, stack) => throw error,
    );
  }
}
