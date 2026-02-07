import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/chat_input_bar.dart';
import '../widgets/remaining_counter.dart';

/// AI chat screen with rate limiting and rich content support.
class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _messages = <_Message>[];
  bool _isLoading = false;
  int _remainingMessages = 12;
  int _totalDailyMessages = 30;

  @override
  void initState() {
    super.initState();
    _messages.add(
      _Message(
        content:
            'Welcome! I\'m your personal astrological guide. Ask me anything about your birth chart, current transits, or life timing.',
        isUser: false,
        timestamp: DateTime.now(),
      ),
    );
  }

  Future<void> _sendMessage(String text) async {
    setState(() {
      _messages.add(
        _Message(
          content: text,
          isUser: true,
          timestamp: DateTime.now(),
        ),
      );
      _isLoading = true;
    });

    // Simulate API delay
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      _messages.add(
        _Message(
          content:
              'Based on your chart, I see some fascinating patterns. Your Mercury is in Libra in the 1st house, which gives you excellent communication skills...',
          isUser: false,
          timestamp: DateTime.now(),
        ),
      );
      _isLoading = false;
      _remainingMessages--;
    });
  }

  @override
  Widget build(BuildContext context) {
    final isRateLimited = _remainingMessages <= 0;

    return StarBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: Column(
            children: [
              // Header
              Container(
                padding: const EdgeInsets.all(16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Cosmic Guide',
                      style: Theme.of(context)
                          .textTheme
                          .headlineSmall
                          ?.copyWith(
                            color: Colors.white,
                          ),
                    ),
                    RemainingCounter(
                      remaining: _remainingMessages,
                      total: _totalDailyMessages,
                    ),
                  ],
                ),
              ),
              // Messages list
              Expanded(
                child: ListView.builder(
                  reverse: true,
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final message = _messages[_messages.length - 1 - index];
                    return ChatBubble(
                      content: message.content,
                      isUser: message.isUser,
                      timestamp: message.timestamp,
                    );
                  },
                ),
              ),
              // Rate limit warning
              if (isRateLimited)
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    color: const Color(0xFFE74C3C).withOpacity(0.2),
                    border: Border.all(
                      color: const Color(0xFFE74C3C).withOpacity(0.5),
                    ),
                  ),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.info_rounded,
                        color: Color(0xFFE74C3C),
                        size: 18,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Daily limit reached. Upgrade to Pro for 30 messages/day.',
                          style: TextStyle(
                            color: const Color(0xFFE74C3C),
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              if (isRateLimited) const SizedBox(height: 12),
              // Input bar
              ChatInputBar(
                onSend: _sendMessage,
                isEnabled: !isRateLimited,
                isLoading: _isLoading,
              ),
            ],
          ),
        ),
        bottomNavigationBar: const BottomNavBar(currentIndex: 2),
      ),
    );
  }
}

class _Message {
  final String content;
  final bool isUser;
  final DateTime timestamp;

  _Message({
    required this.content,
    required this.isUser,
    required this.timestamp,
  });
}
