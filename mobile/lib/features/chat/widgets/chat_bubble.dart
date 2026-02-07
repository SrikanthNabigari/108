import 'package:flutter/material.dart';
import '../../../shared/widgets/glass_card.dart';

/// User and AI message bubbles for chat UI.
class ChatBubble extends StatelessWidget {
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final List<ChatBlock> blocks;

  const ChatBubble({
    Key? key,
    required this.content,
    required this.isUser,
    required this.timestamp,
    this.blocks = const [],
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Padding(
        padding: EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 8,
        ),
        child: Column(
          crossAxisAlignment:
              isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            if (isUser)
              Container(
                constraints: BoxConstraints(
                  maxWidth: MediaQuery.of(context).size.width * 0.75,
                ),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xff6C63FF), Color(0xff8A84FF)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                padding: const EdgeInsets.all(12),
                child: Text(
                  content,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                  ),
                ),
              )
            else
              GlassCard(
                padding: const EdgeInsets.all(12),
                margin: EdgeInsets.zero,
                child: ConstrainedBox(
                  constraints: BoxConstraints(
                    maxWidth: MediaQuery.of(context).size.width * 0.75,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        content,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                        ),
                      ),
                      if (blocks.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        ..._buildBlocks(),
                      ],
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 4),
            Text(
              _formatTime(timestamp),
              style: TextStyle(
                color: Colors.white54,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildBlocks() {
    return blocks.map((block) {
      switch (block.type) {
        case 'table':
          return _buildTable(block.data);
        case 'score_card':
          return _buildScoreCard(block.data);
        default:
          return const SizedBox.shrink();
      }
    }).toList();
  }

  Widget _buildTable(Map<String, dynamic> data) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8),
        color: Colors.white.withOpacity(0.05),
      ),
      child: const Text(
        '[Table data]',
        style: TextStyle(
          color: Colors.white54,
          fontSize: 12,
        ),
      ),
    );
  }

  Widget _buildScoreCard(Map<String, dynamic> data) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8),
        color: Colors.white.withOpacity(0.05),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('Score: ', style: TextStyle(color: Colors.white54)),
          Text(
            '${data['score'] ?? 'N/A'}',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    if (now.difference(time).inHours < 1) {
      return '${now.difference(time).inMinutes}m ago';
    }
    return '${time.hour}:${time.minute.toString().padLeft(2, '0')}';
  }
}

class ChatBlock {
  final String type;
  final Map<String, dynamic> data;

  ChatBlock({
    required this.type,
    required this.data,
  });
}
