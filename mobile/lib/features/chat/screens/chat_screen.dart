import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import '../widgets/chat_message_tile.dart';
import '../widgets/chat_input_bar.dart';

/// Data class for a chat message.
class _ChatMessage {
  final String id;
  final String role;
  final String content;
  final List<Map<String, dynamic>> blocks;
  final DateTime createdAt;

  _ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    this.blocks = const [],
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory _ChatMessage.fromJson(Map<String, dynamic> json) {
    // blocks may arrive as List or JSON string — handle both
    final dynamic rawBlocksValue = json['blocks'];
    List<dynamic> rawBlocks;
    if (rawBlocksValue is List) {
      rawBlocks = rawBlocksValue;
    } else {
      rawBlocks = [];
    }
    return _ChatMessage(
      id: json['id'] as String? ?? '',
      role: json['role'] as String? ?? 'assistant',
      content: json['content'] as String? ?? '',
      blocks: rawBlocks
          .whereType<Map<String, dynamic>>()
          .toList(),
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'].toString()) ?? DateTime.now()
          : DateTime.now(),
    );
  }
}

/// Main chat screen — talk to the 108 Guide.
class ChatScreen extends ConsumerStatefulWidget {
  final String? initialPrompt;

  const ChatScreen({super.key, this.initialPrompt});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _scrollController = ScrollController();
  final _messageController = TextEditingController();
  final List<_ChatMessage> _messages = [];
  bool _isLoading = false;
  bool _historyLoading = true;
  int _remainingMessages = -1; // -1 = unlimited

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _loadHistory() async {
    try {
      final result = await ApiService().get<Map<String, dynamic>>(
        ApiConstants.chatHistory,
        fromJson: (json) => json as Map<String, dynamic>,
      );
      final rawMessages = result['messages'] as List<dynamic>? ?? [];
      if (mounted) {
        setState(() {
          _messages.clear();
          // History comes DESC, reverse so oldest first
          _messages.addAll(
            rawMessages
                .whereType<Map<String, dynamic>>()
                .map(_ChatMessage.fromJson)
                .toList()
                .reversed,
          );
          _historyLoading = false;
        });
        _scrollToBottom();
      }
    } catch (e) {
      if (kDebugMode) debugPrint('[Chat] History error: $e');
      if (mounted) {
        setState(() => _historyLoading = false);
      }
    }
    // Auto-send initial prompt if provided (e.g. from detail panel "Ask about")
    if (widget.initialPrompt != null && widget.initialPrompt!.isNotEmpty) {
      _messageController.text = widget.initialPrompt!;
      _sendMessage();
    }
  }

  Future<void> _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty || _isLoading) return;

    // Add user message immediately
    final userMsg = _ChatMessage(
      id: 'local_${DateTime.now().millisecondsSinceEpoch}',
      role: 'user',
      content: text,
    );
    setState(() {
      _messages.add(userMsg);
      _isLoading = true;
    });
    _messageController.clear();
    _scrollToBottom();

    // Remember scroll position before response arrives
    final preResponseOffset = _scrollController.hasClients
        ? _scrollController.position.maxScrollExtent
        : 0.0;

    try {
      final result = await ApiService().post<Map<String, dynamic>>(
        ApiConstants.chat,
        fromJson: (json) => json as Map<String, dynamic>,
        body: {'message': text},
      );

      final msgJson = result['message'] as Map<String, dynamic>? ?? {};
      final assistantMsg = _ChatMessage.fromJson(msgJson);
      final remaining = result['remainingMessages'] as int? ?? -1;

      if (mounted) {
        setState(() {
          _messages.add(assistantMsg);
          _remainingMessages = remaining;
          _isLoading = false;
        });
        // Scroll to show start of assistant response, not the end
        _scrollToOffset(preResponseOffset);
      }
    } catch (e) {
      if (kDebugMode) debugPrint('[Chat] Send error: $e');
      if (mounted) {
        final isRateLimit = e.toString().contains('Rate limit') ||
            e.toString().contains('429');
        setState(() {
          _messages.add(_ChatMessage(
            id: 'error_${DateTime.now().millisecondsSinceEpoch}',
            role: 'assistant',
            content: isRateLimit
                ? 'You have reached your daily message limit. Please try again tomorrow.'
                : (kDebugMode
                    ? 'Something went wrong: $e'
                    : 'Something went wrong. Please try again.'),
          ));
          if (isRateLimit) _remainingMessages = 0;
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }

  void _startNewChat() {
    setState(() {
      _messages.clear();
      _remainingMessages = -1;
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _scrollToOffset(double offset) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        // Scroll to just past the user message so the response start is visible
        final target = (offset + 60).clamp(
          0.0,
          _scrollController.position.maxScrollExtent,
        );
        _scrollController.animateTo(
          target,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          bottom: false,
          child: Column(
            children: [
              // App bar
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: S.lg,
                  vertical: S.sm,
                ),
                child: Row(
                  children: [
                    GestureDetector(
                      onTap: () => context.canPop()
                          ? context.pop()
                          : context.go('/home'),
                      child: const Icon(Icons.arrow_back_ios,
                          color: C.textSecondary, size: 18),
                    ),
                    const SizedBox(width: S.sm),
                    Text('108 Guide', style: T.h3),
                    const Spacer(),
                    GestureDetector(
                      onTap: _startNewChat,
                      child: Container(
                        padding: const EdgeInsets.all(S.sm),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: C.glassBg,
                          border: Border.all(color: C.glassBorder),
                        ),
                        child: const Icon(Icons.edit_outlined,
                            color: C.textPrimary, size: 18),
                      ),
                    ),
                  ],
                ),
              ),

              const Divider(height: 1),

              // Messages list
              Expanded(
                child: _historyLoading
                    ? const Center(
                        child: CircularProgressIndicator(color: C.accent),
                      )
                    : _messages.isEmpty
                        ? _buildEmptyState()
                        : ListView.builder(
                            controller: _scrollController,
                            padding: const EdgeInsets.symmetric(
                              horizontal: S.lg,
                              vertical: S.md,
                            ),
                            itemCount:
                                _messages.length + (_isLoading ? 1 : 0),
                            itemBuilder: (context, index) {
                              if (index == _messages.length && _isLoading) {
                                return _buildTypingIndicator();
                              }
                              final msg = _messages[index];
                              return ChatMessageTile(
                                role: msg.role,
                                content: msg.content,
                                blocks: msg.blocks,
                              );
                            },
                          ),
              ),

              // Input bar
              ChatInputBar(
                controller: _messageController,
                isLoading: _isLoading,
                remainingMessages: _remainingMessages,
                onSend: _sendMessage,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(S.xxxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.auto_awesome,
              size: 48,
              color: C.accent.withValues(alpha: 0.4),
            ),
            const SizedBox(height: S.xl),
            Text(
              'Ask the Guide',
              style: T.h2.copyWith(color: C.textPrimary),
            ),
            const SizedBox(height: S.sm),
            Text(
              'Ask about your chart, career, relationships, timing, remedies, or anything about your cosmic blueprint.',
              style: T.bodySm.copyWith(color: C.textSecondary),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: S.xxl),
            // Suggestion chips
            Wrap(
              spacing: S.sm,
              runSpacing: S.sm,
              alignment: WrapAlignment.center,
              children: [
                _SuggestionChip(
                  text: 'How is my career?',
                  onTap: () {
                    _messageController.text = 'How is my career?';
                    _sendMessage();
                  },
                ),
                _SuggestionChip(
                  text: "What's happening now?",
                  onTap: () {
                    _messageController.text = "What's happening now?";
                    _sendMessage();
                  },
                ),
                _SuggestionChip(
                  text: 'Tell me about my yogas',
                  onTap: () {
                    _messageController.text = 'Tell me about my yogas';
                    _sendMessage();
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: S.sm),
      child: Row(
        children: [
          const SizedBox(width: S.sm),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
            decoration: BoxDecoration(
              color: C.glassBg,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: C.glassBorder),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (i) {
                return TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0.0, end: 1.0),
                  duration: Duration(milliseconds: 600 + i * 200),
                  builder: (_, value, child) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 2),
                      child: Opacity(
                        opacity: 0.3 + 0.7 * value,
                        child: child,
                      ),
                    );
                  },
                  child: Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: C.textMuted,
                    ),
                  ),
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
}

class _SuggestionChip extends StatelessWidget {
  final String text;
  final VoidCallback onTap;

  const _SuggestionChip({required this.text, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.sm),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          color: C.glassBg,
          border: Border.all(color: C.glassBorder),
        ),
        child: Text(
          text,
          style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 13),
        ),
      ),
    );
  }
}
