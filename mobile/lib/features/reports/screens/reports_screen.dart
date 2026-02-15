import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import '../widgets/report_viewer.dart';

// -- Report type configs ---------------------------------------------------

const _kReportTypes = [
  {
    'type': 'annual_report',
    'title': 'Annual Forecast',
    'desc': 'Comprehensive 12-month outlook covering career, relationships, '
        'health, and spiritual growth based on your dasha and transits.',
    'icon': Icons.calendar_today,
    'color': 'jupiter',
    'credits': 50,
  },
  {
    'type': 'career_report',
    'title': 'Career Blueprint',
    'desc': 'Professional strengths, ideal career paths, and upcoming '
        'opportunities based on your 10th house and current dasha.',
    'icon': Icons.work,
    'color': 'saturn',
    'credits': 40,
  },
  {
    'type': 'health_report',
    'title': 'Health & Wellness',
    'desc': 'Health indicators, Ayurvedic constitution, and preventive '
        'measures based on your 6th and 8th house analysis.',
    'icon': Icons.favorite,
    'color': 'mars',
    'credits': 30,
  },
  {
    'type': 'relationship_report',
    'title': 'Relationship Insights',
    'desc': 'Love, marriage indicators, and partnership dynamics from '
        'your 7th house, Venus, and Navamsa chart.',
    'icon': Icons.people,
    'color': 'venus',
    'credits': 30,
  },
];

// -- Mock data -------------------------------------------------------------

final _kMockReports = <Map<String, dynamic>>[
  {
    'id': '1',
    'report_type': 'annual_report',
    'title': 'Annual Forecast Report',
    'status': 'completed',
    'created_at': '2026-02-10',
    'credit_cost': 50,
    'content': {
      'title': 'Annual Forecast Report',
      'summary': 'A comprehensive overview of your year ahead based on '
          'Mercury Mahadasha and Jupiter transit through your 9th house.',
      'sections': [
        {
          'heading': 'Overview',
          'content': 'This year brings significant growth opportunities as '
              'Jupiter transits your 9th house of fortune.',
          'highlights': [
            '**Jupiter transit** through 9th house brings expansion',
            '**Mercury Mahadasha** favors intellectual pursuits',
          ],
        },
        {
          'heading': 'Career & Finance',
          'content': 'The 10th house lord receives strong aspects, indicating '
              'professional advancement in the coming months.',
          'highlights': [
            '**Saturn transit** stabilizes career foundation',
            '**Rahu in 11th** amplifies gains and networking',
          ],
        },
      ],
      'generated_at': '2026-02-10T08:00:00Z',
    },
  },
  {
    'id': '2',
    'report_type': 'career_report',
    'title': 'Career Blueprint Report',
    'status': 'completed',
    'created_at': '2026-02-08',
    'credit_cost': 40,
    'content': {
      'title': 'Career Blueprint Report',
      'summary': 'Your career analysis based on the 10th house in Cancer '
          'with Mars (retrograde) providing Neecha Bhanga Raja Yoga.',
      'sections': [
        {
          'heading': 'Career Overview',
          'content': 'With Libra Lagna and Mars in the 10th house (Cancer), '
              'your career path involves leadership through emotional '
              'intelligence and strategic action.',
          'highlights': [
            '**Neecha Bhanga** Mars gives resilience in career',
            '**Mercury MD** period favors communication roles',
          ],
        },
      ],
      'generated_at': '2026-02-08T12:00:00Z',
    },
  },
];

// -- Color helper ----------------------------------------------------------

Color _colorForType(String colorName) {
  switch (colorName) {
    case 'jupiter':
      return C.jupiter;
    case 'saturn':
      return C.saturn;
    case 'mars':
      return C.mars;
    case 'venus':
      return C.venus;
    case 'sun':
      return C.sun;
    case 'moon':
      return C.moon;
    default:
      return C.accent;
  }
}

// ==========================================================================
// Reports Screen
// ==========================================================================

class ReportsScreen extends ConsumerStatefulWidget {
  const ReportsScreen({super.key});

  @override
  ConsumerState<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends ConsumerState<ReportsScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  List<Map<String, dynamic>> _myReports = [];
  bool _loading = true;
  String? _generatingType; // which report type is currently generating

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetchMyReports();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchMyReports() async {
    try {
      final data = await ApiService().get<List<dynamic>>(
        ApiConstants.reports,
        fromJson: (json) => json as List<dynamic>,
      );
      if (!mounted) return;
      setState(() {
        _myReports = data.cast<Map<String, dynamic>>();
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _myReports = _kMockReports;
        _loading = false;
      });
    }
  }

  Future<void> _generateReport(Map<String, dynamic> reportType) async {
    final type = reportType['type'] as String;
    final credits = reportType['credits'] as int;
    final title = reportType['title'] as String;

    // Confirmation dialog
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: C.surface,
        shape: RoundedRectangleBorder(borderRadius: R.lgBr),
        title: Text('Generate $title?', style: T.h3),
        content: Text(
          'This will use $credits credits from your balance.',
          style: T.bodySm,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Generate'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    setState(() => _generatingType = type);

    try {
      await ApiService().post<Map<String, dynamic>>(
        ApiConstants.reports,
        body: {'report_type': type},
        fromJson: (json) => json as Map<String, dynamic>,
      );

      if (!mounted) return;

      // Refresh reports and switch to My Reports tab
      await _fetchMyReports();
      _tabController.animateTo(1);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$title generated successfully')),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to generate report: $e'),
          backgroundColor: C.negative,
        ),
      );
    } finally {
      if (mounted) setState(() => _generatingType = null);
    }
  }

  void _viewReport(Map<String, dynamic> report) {
    final content = report['content'];
    if (content == null || content is! Map<String, dynamic>) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Report content not available')),
      );
      return;
    }

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ReportViewer(reportData: report),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: C.bg,
      body: AmbientBackground(
        child: SafeArea(
          bottom: false,
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.lg, vertical: S.sm),
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
                    Text('Reports', style: T.h3),
                  ],
                ),
              ),

              // Tab bar
              Container(
                margin: const EdgeInsets.symmetric(horizontal: S.lg),
                decoration: BoxDecoration(
                  color: C.glassBg,
                  borderRadius: R.lgBr,
                  border: Border.all(color: C.glassBorder),
                ),
                child: TabBar(
                  controller: _tabController,
                  indicator: BoxDecoration(
                    color: C.accent.withValues(alpha: 0.15),
                    borderRadius: R.lgBr,
                  ),
                  indicatorSize: TabBarIndicatorSize.tab,
                  labelColor: C.textPrimary,
                  unselectedLabelColor: C.textMuted,
                  labelStyle: T.bodySm.copyWith(fontWeight: FontWeight.w600),
                  unselectedLabelStyle: T.bodySm,
                  dividerHeight: 0,
                  tabs: const [
                    Tab(text: 'Browse'),
                    Tab(text: 'My Reports'),
                  ],
                ),
              ),

              const SizedBox(height: S.md),

              // Tab views
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildBrowseTab(),
                    _buildMyReportsTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // -- Browse Tab ----------------------------------------------------------

  Widget _buildBrowseTab() {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: S.lg),
      itemCount: _kReportTypes.length,
      itemBuilder: (context, index) {
        final rt = _kReportTypes[index];
        return _buildReportTypeCard(rt);
      },
    );
  }

  Widget _buildReportTypeCard(Map<String, dynamic> rt) {
    final type = rt['type'] as String;
    final title = rt['title'] as String;
    final desc = rt['desc'] as String;
    final icon = rt['icon'] as IconData;
    final color = _colorForType(rt['color'] as String);
    final credits = rt['credits'] as int;
    final isGenerating = _generatingType == type;

    return Padding(
      padding: const EdgeInsets.only(bottom: S.md),
      child: GlassContainer(
        borderColor: color.withValues(alpha: 0.3),
        padding: const EdgeInsets.all(S.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon + title row
            Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: color.withValues(alpha: 0.12),
                  ),
                  child: Icon(icon, color: color, size: 20),
                ),
                const SizedBox(width: S.md),
                Expanded(
                  child: Text(title,
                      style: T.h3.copyWith(fontSize: 16, color: color)),
                ),
                // Credit badge
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: S.sm, vertical: S.xs),
                  decoration: BoxDecoration(
                    color: C.jupiter.withValues(alpha: 0.12),
                    borderRadius: R.smBr,
                  ),
                  child: Text(
                    '$credits credits',
                    style: T.caption.copyWith(
                      color: C.jupiter,
                      fontWeight: FontWeight.w600,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: S.md),

            // Description
            Text(desc, style: T.bodySm.copyWith(height: 1.5)),
            const SizedBox(height: S.lg),

            // Generate button
            SizedBox(
              width: double.infinity,
              height: 44,
              child: ElevatedButton(
                onPressed: isGenerating ? null : () => _generateReport(rt),
                style: ElevatedButton.styleFrom(
                  backgroundColor: color.withValues(alpha: 0.15),
                  foregroundColor: color,
                  disabledBackgroundColor: C.glassBg,
                  elevation: 0,
                  shape:
                      RoundedRectangleBorder(borderRadius: R.mdBr),
                ),
                child: isGenerating
                    ? SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: color),
                      )
                    : Text('Generate',
                        style: T.bodySm.copyWith(
                            color: color, fontWeight: FontWeight.w600)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // -- My Reports Tab ------------------------------------------------------

  Widget _buildMyReportsTab() {
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(strokeWidth: 2, color: C.accent),
      );
    }

    if (_myReports.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.description_outlined,
                color: C.textMuted, size: 48),
            const SizedBox(height: S.md),
            Text('No reports yet', style: T.bodySm),
            const SizedBox(height: S.sm),
            Text('Browse and generate your first report',
                style: T.caption),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: S.lg),
      itemCount: _myReports.length,
      itemBuilder: (context, index) {
        final report = _myReports[index];
        return _buildMyReportCard(report);
      },
    );
  }

  Widget _buildMyReportCard(Map<String, dynamic> report) {
    final title = report['title'] as String? ?? 'Report';
    final reportStatus = report['status'] as String? ?? 'pending';
    final date = report['created_at'] as String? ?? '';
    final credits = report['credit_cost'] as int? ?? 0;

    Color statusColor;
    String statusLabel;
    switch (reportStatus) {
      case 'completed':
        statusColor = C.positive;
        statusLabel = 'Completed';
        break;
      case 'pending':
      case 'generating':
        statusColor = C.warning;
        statusLabel = 'Generating';
        break;
      case 'failed':
        statusColor = C.negative;
        statusLabel = 'Failed';
        break;
      default:
        statusColor = C.textMuted;
        statusLabel = reportStatus;
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: GestureDetector(
        onTap: reportStatus == 'completed' ? () => _viewReport(report) : null,
        child: GlassContainer(
          padding:
              const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
          child: Row(
            children: [
              // Report icon
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: statusColor.withValues(alpha: 0.12),
                ),
                child: Icon(
                  reportStatus == 'completed'
                      ? Icons.description
                      : reportStatus == 'failed'
                          ? Icons.error_outline
                          : Icons.hourglass_empty,
                  color: statusColor,
                  size: 20,
                ),
              ),
              const SizedBox(width: S.md),

              // Title + date
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title,
                        style:
                            T.bodySm.copyWith(color: C.textPrimary)),
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        Text(date, style: T.caption),
                        const SizedBox(width: S.sm),
                        Text('$credits credits',
                            style: T.caption.copyWith(
                                color: C.jupiter, fontSize: 10)),
                      ],
                    ),
                  ],
                ),
              ),

              // Status badge
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.sm, vertical: S.xs),
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.12),
                  borderRadius: R.smBr,
                ),
                child: Text(
                  statusLabel,
                  style: T.caption.copyWith(
                    color: statusColor,
                    fontWeight: FontWeight.w600,
                    fontSize: 10,
                  ),
                ),
              ),

              if (reportStatus == 'completed') ...[
                const SizedBox(width: S.sm),
                Icon(Icons.chevron_right, color: C.textMuted, size: 20),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
