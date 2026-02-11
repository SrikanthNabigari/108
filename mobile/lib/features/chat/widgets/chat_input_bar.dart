import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Glass-styled input bar with send button and remaining messages badge.
class ChatInputBar extends StatelessWidget {
  final TextEditingController controller;
  final bool isLoading;
  final int remainingMessages;
  final VoidCallback onSend;

  const ChatInputBar({
    super.key,
    required this.controller,
    required this.isLoading,
    required this.remainingMessages,
    required this.onSend,
  });

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.sm),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Remaining messages badge
            if (remainingMessages >= 0 && remainingMessages < 20)
              Padding(
                padding: const EdgeInsets.only(bottom: S.xs),
                child: Text(
                  remainingMessages == 0
                      ? 'No messages remaining today'
                      : '$remainingMessages messages remaining today',
                  style: T.caption.copyWith(
                    color: remainingMessages <= 3 ? C.warning : C.textMuted,
                  ),
                ),
              ),

            // Input row
            GlassContainer(
              borderRadius: 28,
              padding: const EdgeInsets.symmetric(
                horizontal: S.lg,
                vertical: S.xs,
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: controller,
                      style: T.body.copyWith(color: C.textPrimary),
                      decoration: InputDecoration(
                        hintText: 'Ask about your chart...',
                        hintStyle: T.body.copyWith(color: C.textMuted),
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.zero,
                        isDense: true,
                      ),
                      maxLines: 3,
                      minLines: 1,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _handleSend(),
                    ),
                  ),
                  const SizedBox(width: S.sm),
                  _SendButton(
                    isLoading: isLoading,
                    onTap: _handleSend,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _handleSend() {
    if (controller.text.trim().isNotEmpty && !isLoading) {
      onSend();
    }
  }
}

class _SendButton extends StatelessWidget {
  final bool isLoading;
  final VoidCallback onTap;

  const _SendButton({required this.isLoading, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: isLoading ? null : onTap,
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: isLoading ? C.glassBg : C.accent,
        ),
        child: Center(
          child: isLoading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: C.textMuted,
                  ),
                )
              : const Icon(
                  Icons.arrow_upward,
                  color: C.textOnAccent,
                  size: 18,
                ),
        ),
      ),
    );
  }
}
