import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'chat_block_renderer.dart';

/// A single chat bubble — user (right) or assistant (left).
class ChatMessageTile extends StatelessWidget {
  final String role;
  final String content;
  final List<Map<String, dynamic>> blocks;
  final String? timestamp;

  const ChatMessageTile({
    super.key,
    required this.role,
    required this.content,
    this.blocks = const [],
    this.timestamp,
  });

  bool get _isUser => role == 'user';

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: S.xs),
      child: Row(
        mainAxisAlignment:
            _isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!_isUser) const SizedBox(width: S.sm),
          Flexible(
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.82,
              ),
              child: _isUser ? _buildUserBubble() : _buildAssistantBubble(),
            ),
          ),
          if (_isUser) const SizedBox(width: S.sm),
        ],
      ),
    );
  }

  Widget _buildUserBubble() {
    return GlassContainer(
      borderColor: C.accent.withValues(alpha: 0.3),
      backgroundColor: C.accent.withValues(alpha: 0.08),
      borderRadius: 20,
      padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
      child: Text(
        content,
        style: T.body.copyWith(color: C.textPrimary),
      ),
    );
  }

  Widget _buildAssistantBubble() {
    return GlassContainer(
      borderRadius: 20,
      padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Render blocks above text
          if (blocks.isNotEmpty) ...[
            ...blocks.map(
              (block) => Padding(
                padding: const EdgeInsets.only(bottom: S.sm),
                child: ChatBlockRenderer(block: block),
              ),
            ),
            if (content.isNotEmpty) const SizedBox(height: S.xs),
          ],

          if (content.isNotEmpty)
            MarkdownBody(
              data: content,
              shrinkWrap: true,
              selectable: true,
              styleSheet: MarkdownStyleSheet(
                p: T.bodySm.copyWith(color: C.textPrimary, height: 1.5),
                h1: T.h2.copyWith(color: C.textPrimary),
                h2: T.h3.copyWith(color: C.textPrimary),
                h3: T.bodySm.copyWith(
                  color: C.accent,
                  fontWeight: FontWeight.w600,
                  fontSize: 15,
                ),
                strong: T.bodySm.copyWith(
                  color: C.textPrimary,
                  fontWeight: FontWeight.w600,
                ),
                em: T.bodySm.copyWith(
                  color: C.textSecondary,
                  fontStyle: FontStyle.italic,
                ),
                listBullet: T.bodySm.copyWith(color: C.textMuted),
                blockSpacing: S.sm,
                listIndent: S.lg,
                horizontalRuleDecoration: BoxDecoration(
                  border: Border(
                    top: BorderSide(color: C.glassBorder, width: 0.5),
                  ),
                ),
                blockquoteDecoration: BoxDecoration(
                  border: Border(
                    left: BorderSide(color: C.accent.withValues(alpha: 0.3), width: 3),
                  ),
                ),
                blockquotePadding: const EdgeInsets.only(left: S.md),
                codeblockDecoration: BoxDecoration(
                  color: C.surface,
                  borderRadius: BorderRadius.circular(R.sm),
                ),
                code: T.bodySm.copyWith(
                  color: C.mercury,
                  fontFamily: 'monospace',
                  fontSize: 13,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
