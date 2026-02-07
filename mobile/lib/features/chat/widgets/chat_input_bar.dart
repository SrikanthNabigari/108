import 'package:flutter/material.dart';
import '../../../shared/widgets/glass_card.dart';

/// Chat message input bar with send button.
class ChatInputBar extends StatefulWidget {
  final Function(String) onSend;
  final bool isEnabled;
  final bool isLoading;

  const ChatInputBar({
    Key? key,
    required this.onSend,
    this.isEnabled = true,
    this.isLoading = false,
  }) : super(key: key);

  @override
  State<ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends State<ChatInputBar> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _send() {
    if (_controller.text.isNotEmpty && widget.isEnabled && !widget.isLoading) {
      widget.onSend(_controller.text);
      _controller.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: GlassCard(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        margin: EdgeInsets.zero,
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                enabled: widget.isEnabled && !widget.isLoading,
                maxLines: null,
                textCapitalization: TextCapitalization.sentences,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  hintText: 'Ask about your chart...',
                  hintStyle: TextStyle(color: Colors.white38),
                  border: InputBorder.none,
                ),
                onSubmitted: (_) => _send(),
              ),
            ),
            const SizedBox(width: 8),
            GestureDetector(
              onTap: widget.isEnabled && !widget.isLoading ? _send : null,
              child: Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: (widget.isEnabled && !widget.isLoading)
                      ? const LinearGradient(
                          colors: [Color(0xff6C63FF), Color(0xff8A84FF)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        )
                      : null,
                  color: (widget.isEnabled && !widget.isLoading)
                      ? null
                      : Colors.white.withOpacity(0.1),
                ),
                child: widget.isLoading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : Icon(
                        Icons.send_rounded,
                        color: (widget.isEnabled && !widget.isLoading)
                            ? Colors.white
                            : Colors.white54,
                        size: 18,
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
