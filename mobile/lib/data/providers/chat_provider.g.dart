// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chat_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// chatMessagesProvider is defined manually in chat_provider.dart
String _$remainingMessagesHash() => r'b54c2a22a2075d256532f36964a701f684af26fb';

/// Get remaining messages today
///
/// Copied from [remainingMessages].
@ProviderFor(remainingMessages)
final remainingMessagesProvider = AutoDisposeFutureProvider<int>.internal(
  remainingMessages,
  name: r'remainingMessagesProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$remainingMessagesHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef RemainingMessagesRef = AutoDisposeFutureProviderRef<int>;
String _$chatHistoryHash() => r'0fb9bb749836c2de29d49e097df11b46b1a05bec';

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

/// Load chat history
///
/// Copied from [chatHistory].
@ProviderFor(chatHistory)
const chatHistoryProvider = ChatHistoryFamily();

/// Load chat history
///
/// Copied from [chatHistory].
class ChatHistoryFamily extends Family<AsyncValue<List<ChatMessageModel>>> {
  /// Load chat history
  ///
  /// Copied from [chatHistory].
  const ChatHistoryFamily();

  /// Load chat history
  ///
  /// Copied from [chatHistory].
  ChatHistoryProvider call({
    int limit = 50,
    int offset = 0,
  }) {
    return ChatHistoryProvider(
      limit: limit,
      offset: offset,
    );
  }

  @override
  ChatHistoryProvider getProviderOverride(
    covariant ChatHistoryProvider provider,
  ) {
    return call(
      limit: provider.limit,
      offset: provider.offset,
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
  String? get name => r'chatHistoryProvider';
}

/// Load chat history
///
/// Copied from [chatHistory].
class ChatHistoryProvider
    extends AutoDisposeFutureProvider<List<ChatMessageModel>> {
  /// Load chat history
  ///
  /// Copied from [chatHistory].
  ChatHistoryProvider({
    int limit = 50,
    int offset = 0,
  }) : this._internal(
          (ref) => chatHistory(
            ref as ChatHistoryRef,
            limit: limit,
            offset: offset,
          ),
          from: chatHistoryProvider,
          name: r'chatHistoryProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$chatHistoryHash,
          dependencies: ChatHistoryFamily._dependencies,
          allTransitiveDependencies:
              ChatHistoryFamily._allTransitiveDependencies,
          limit: limit,
          offset: offset,
        );

  ChatHistoryProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.limit,
    required this.offset,
  }) : super.internal();

  final int limit;
  final int offset;

  @override
  Override overrideWith(
    FutureOr<List<ChatMessageModel>> Function(ChatHistoryRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: ChatHistoryProvider._internal(
        (ref) => create(ref as ChatHistoryRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        limit: limit,
        offset: offset,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<List<ChatMessageModel>> createElement() {
    return _ChatHistoryProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is ChatHistoryProvider &&
        other.limit == limit &&
        other.offset == offset;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, limit.hashCode);
    hash = _SystemHash.combine(hash, offset.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin ChatHistoryRef on AutoDisposeFutureProviderRef<List<ChatMessageModel>> {
  /// The parameter `limit` of this provider.
  int get limit;

  /// The parameter `offset` of this provider.
  int get offset;
}

class _ChatHistoryProviderElement
    extends AutoDisposeFutureProviderElement<List<ChatMessageModel>>
    with ChatHistoryRef {
  _ChatHistoryProviderElement(super.provider);

  @override
  int get limit => (origin as ChatHistoryProvider).limit;
  @override
  int get offset => (origin as ChatHistoryProvider).offset;
}

String _$sendChatMessageHash() => r'fa8b09d6c63554ab03f027e9432b8dffcfb4c155';

/// Send chat message
///
/// Copied from [SendChatMessage].
@ProviderFor(SendChatMessage)
final sendChatMessageProvider =
    AutoDisposeAsyncNotifierProvider<SendChatMessage, void>.internal(
  SendChatMessage.new,
  name: r'sendChatMessageProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$sendChatMessageHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$SendChatMessage = AutoDisposeAsyncNotifier<void>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
