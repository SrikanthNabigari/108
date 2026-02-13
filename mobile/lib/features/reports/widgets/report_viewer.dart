import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Full-screen viewer for a generated report.
///
/// Accepts either a full reportData map (from route extra) or individual
/// title/content/createdAt params (from direct navigation).
class ReportViewer extends StatelessWidget {
  final Map<String, dynamic> reportData;

  const ReportViewer({
    super.key,
    required this.reportData,
  });

  @override
  Widget build(BuildContext context) {
    final title = reportData['title'] as String? ?? 'Report';
    final content =
        reportData['content'] as Map<String, dynamic>? ?? reportData;
    final createdAt = reportData['created_at'] as String?;
    final summary = content['summary'] as String?;
    final sections = (content['sections'] as List<dynamic>?) ?? [];

    return Scaffold(
      backgroundColor: C.bg,
      body: AmbientBackground(
        child: SafeArea(
          bottom: false,
          child: Column(
            children: [
              // App bar
              Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.lg, vertical: S.sm),
                child: Row(
                  children: [
                    GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Container(
                        padding: const EdgeInsets.all(S.sm),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: C.glassBg,
                          border: Border.all(color: C.glassBorder),
                        ),
                        child: const Icon(Icons.arrow_back,
                            color: C.textPrimary, size: 18),
                      ),
                    ),
                    const Spacer(),
                    Flexible(
                      child: Text(
                        title,
                        style: T.h3.copyWith(fontSize: 16),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const Spacer(),
                    // Share button (placeholder)
                    GestureDetector(
                      onTap: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Sharing coming soon')),
                        );
                      },
                      child: Container(
                        padding: const EdgeInsets.all(S.sm),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: C.glassBg,
                          border: Border.all(color: C.glassBorder),
                        ),
                        child: const Icon(Icons.share,
                            color: C.textPrimary, size: 18),
                      ),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1),

              // Content
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(
                      horizontal: S.lg, vertical: S.md),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Generated date
                      if (createdAt != null) ...[
                        Text(
                          'Generated: $createdAt',
                          style: T.caption,
                        ),
                        const SizedBox(height: S.md),
                      ],

                      // Summary
                      if (summary != null && summary.isNotEmpty) ...[
                        GlassContainer(
                          borderColor: C.accent.withValues(alpha: 0.2),
                          padding: const EdgeInsets.all(S.lg),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Summary',
                                  style: T.label.copyWith(
                                      color: C.accent, letterSpacing: 1.2)),
                              const SizedBox(height: S.sm),
                              Text(summary,
                                  style: T.bodySm.copyWith(
                                      color: C.textPrimary, height: 1.6)),
                            ],
                          ),
                        ),
                        const SizedBox(height: S.xl),
                      ],

                      // Sections
                      ...sections.asMap().entries.map((entry) {
                        final index = entry.key;
                        final section = entry.value;
                        if (section is! Map<String, dynamic>) {
                          return const SizedBox.shrink();
                        }
                        return _buildSection(section, index, sections.length);
                      }),

                      const SizedBox(height: S.xl),

                      // Download PDF button (placeholder)
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton.icon(
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                  content:
                                      Text('PDF download coming soon')),
                            );
                          },
                          icon: const Icon(Icons.picture_as_pdf, size: 18),
                          label: const Text('Download PDF'),
                        ),
                      ),

                      const SizedBox(height: S.xxxl),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSection(
      Map<String, dynamic> section, int index, int totalSections) {
    final heading = section['heading'] as String? ?? 'Section';
    final sectionContent = section['content'] as String? ?? '';
    final highlights =
        (section['highlights'] as List<dynamic>?)?.cast<String>() ?? [];

    return Padding(
      padding: const EdgeInsets.only(bottom: S.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Section heading
          Row(
            children: [
              Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: C.accent.withValues(alpha: 0.1),
                ),
                child: Center(
                  child: Text(
                    '${index + 1}',
                    style: T.caption.copyWith(
                        color: C.accent, fontSize: 10),
                  ),
                ),
              ),
              const SizedBox(width: S.sm),
              Expanded(
                child: Text(heading,
                    style: T.h3.copyWith(fontSize: 16)),
              ),
            ],
          ),
          const SizedBox(height: S.md),

          // Section content
          if (sectionContent.isNotEmpty)
            Text(sectionContent,
                style: T.bodySm.copyWith(
                    color: C.textSecondary, height: 1.6)),

          // Highlights as accent chips
          if (highlights.isNotEmpty) ...[
            const SizedBox(height: S.md),
            Wrap(
              spacing: S.sm,
              runSpacing: S.sm,
              children: highlights.map((h) => _buildHighlightChip(h)).toList(),
            ),
          ],

          // Divider (except last)
          if (index < totalSections - 1) ...[
            const SizedBox(height: S.lg),
            Divider(color: C.glassBorder, height: 1),
          ],
        ],
      ),
    );
  }

  Widget _buildHighlightChip(String text) {
    return Container(
      padding:
          const EdgeInsets.symmetric(horizontal: S.md, vertical: S.xs),
      decoration: BoxDecoration(
        color: C.accent.withValues(alpha: 0.06),
        borderRadius: R.smBr,
        border: Border.all(color: C.accent.withValues(alpha: 0.12)),
      ),
      child: Text(
        text.replaceAll('**', ''),
        style: T.caption.copyWith(
          color: C.textPrimary,
          fontSize: 11,
          height: 1.3,
        ),
      ),
    );
  }
}
