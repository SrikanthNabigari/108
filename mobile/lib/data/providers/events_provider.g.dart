// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'events_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$eventsForDateRangeHash() =>
    r'2dc84df7121706b09a498a5751e38adfdd61e8aa';

/// Copied from Dart SDK
class _SystemHash {
  _SystemHash._();

  static int combine(int hash, int value) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + value);
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x0007ffff & hash) << 10));
    return hash ^ (hash >> 6);
  }

  static int finish(int hash) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x03ffffff & hash) << 3));
    // ignore: parameter_assignments
    hash = hash ^ (hash >> 11);
    return 0x1fffffff & (hash + ((0x00003fff & hash) << 15));
  }
}

/// Get events for a date range
///
/// Copied from [eventsForDateRange].
@ProviderFor(eventsForDateRange)
const eventsForDateRangeProvider = EventsForDateRangeFamily();

/// Get events for a date range
///
/// Copied from [eventsForDateRange].
class EventsForDateRangeFamily extends Family<AsyncValue<List<EventModel>>> {
  /// Get events for a date range
  ///
  /// Copied from [eventsForDateRange].
  const EventsForDateRangeFamily();

  /// Get events for a date range
  ///
  /// Copied from [eventsForDateRange].
  EventsForDateRangeProvider call(
    DateTime startDate,
    DateTime endDate,
  ) {
    return EventsForDateRangeProvider(
      startDate,
      endDate,
    );
  }

  @override
  EventsForDateRangeProvider getProviderOverride(
    covariant EventsForDateRangeProvider provider,
  ) {
    return call(
      provider.startDate,
      provider.endDate,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'eventsForDateRangeProvider';
}

/// Get events for a date range
///
/// Copied from [eventsForDateRange].
class EventsForDateRangeProvider
    extends AutoDisposeFutureProvider<List<EventModel>> {
  /// Get events for a date range
  ///
  /// Copied from [eventsForDateRange].
  EventsForDateRangeProvider(
    DateTime startDate,
    DateTime endDate,
  ) : this._internal(
          (ref) => eventsForDateRange(
            ref as EventsForDateRangeRef,
            startDate,
            endDate,
          ),
          from: eventsForDateRangeProvider,
          name: r'eventsForDateRangeProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$eventsForDateRangeHash,
          dependencies: EventsForDateRangeFamily._dependencies,
          allTransitiveDependencies:
              EventsForDateRangeFamily._allTransitiveDependencies,
          startDate: startDate,
          endDate: endDate,
        );

  EventsForDateRangeProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.startDate,
    required this.endDate,
  }) : super.internal();

  final DateTime startDate;
  final DateTime endDate;

  @override
  Override overrideWith(
    FutureOr<List<EventModel>> Function(EventsForDateRangeRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: EventsForDateRangeProvider._internal(
        (ref) => create(ref as EventsForDateRangeRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        startDate: startDate,
        endDate: endDate,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<List<EventModel>> createElement() {
    return _EventsForDateRangeProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is EventsForDateRangeProvider &&
        other.startDate == startDate &&
        other.endDate == endDate;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, startDate.hashCode);
    hash = _SystemHash.combine(hash, endDate.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin EventsForDateRangeRef on AutoDisposeFutureProviderRef<List<EventModel>> {
  /// The parameter `startDate` of this provider.
  DateTime get startDate;

  /// The parameter `endDate` of this provider.
  DateTime get endDate;
}

class _EventsForDateRangeProviderElement
    extends AutoDisposeFutureProviderElement<List<EventModel>>
    with EventsForDateRangeRef {
  _EventsForDateRangeProviderElement(super.provider);

  @override
  DateTime get startDate => (origin as EventsForDateRangeProvider).startDate;
  @override
  DateTime get endDate => (origin as EventsForDateRangeProvider).endDate;
}

String _$allEventsHash() => r'73172f0aad295f121a9993c23d24e8a7c5c1e1b4';

/// Get all user events
///
/// Copied from [allEvents].
@ProviderFor(allEvents)
final allEventsProvider = AutoDisposeFutureProvider<List<EventModel>>.internal(
  allEvents,
  name: r'allEventsProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$allEventsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef AllEventsRef = AutoDisposeFutureProviderRef<List<EventModel>>;
String _$createEventHash() => r'490c989efbe09b038918cdff567a3a3127d1980a';

/// Create user event
///
/// Copied from [CreateEvent].
@ProviderFor(CreateEvent)
final createEventProvider =
    AutoDisposeAsyncNotifierProvider<CreateEvent, void>.internal(
  CreateEvent.new,
  name: r'createEventProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$createEventHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$CreateEvent = AutoDisposeAsyncNotifier<void>;
String _$updateEventHash() => r'7ca0ea5c29c907a1ae01b6dc1bf275a0977518b0';

/// Update user event
///
/// Copied from [UpdateEvent].
@ProviderFor(UpdateEvent)
final updateEventProvider =
    AutoDisposeAsyncNotifierProvider<UpdateEvent, void>.internal(
  UpdateEvent.new,
  name: r'updateEventProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$updateEventHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$UpdateEvent = AutoDisposeAsyncNotifier<void>;
String _$deleteEventHash() => r'2e868ce33eb3803e0585a36ec41b44f3efd428cc';

/// Delete user event
///
/// Copied from [DeleteEvent].
@ProviderFor(DeleteEvent)
final deleteEventProvider =
    AutoDisposeAsyncNotifierProvider<DeleteEvent, void>.internal(
  DeleteEvent.new,
  name: r'deleteEventProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$deleteEventHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$DeleteEvent = AutoDisposeAsyncNotifier<void>;
String _$correlateEventHash() => r'6952f6af0573f837576750babb0b195bd9712cd9';

/// Correlate past event with chart
///
/// Copied from [CorrelateEvent].
@ProviderFor(CorrelateEvent)
final correlateEventProvider =
    AutoDisposeAsyncNotifierProvider<CorrelateEvent, void>.internal(
  CorrelateEvent.new,
  name: r'correlateEventProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$correlateEventHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$CorrelateEvent = AutoDisposeAsyncNotifier<void>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
