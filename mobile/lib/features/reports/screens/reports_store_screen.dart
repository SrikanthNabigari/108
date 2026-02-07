import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';
import '../../../shared/widgets/glass_card.dart';

/// Browse and purchase available astrology reports.
class ReportsStoreScreen extends ConsumerWidget {
  const ReportsStoreScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reports = [
      _Report(
        title: 'Year Ahead Reading',
        subtitle: '2026 Forecast & Timeline',
        price: '\$4.99',
        credits: '40',
        icon: Icons.calendar_today_rounded,
      ),
      _Report(
        title: 'Career Blueprint',
        subtitle: 'Life Direction & Timing',
        price: '\$5.99',
        credits: '40',
        icon: Icons.trending_up_rounded,
      ),
      _Report(
        title: 'Marriage & Partner Report',
        subtitle: 'Relationship Analysis',
        price: '\$5.99',
        credits: '40',
        icon: Icons.favorite_rounded,
      ),
      _Report(
        title: 'Soul Purpose Guide',
        subtitle: 'Life Mission & Spiritual Path',
        price: '\$3.99',
        credits: '30',
        icon: Icons.favorite_rounded,
      ),
      _Report(
        title: 'Complete Birth Chart',
        subtitle: 'Full Planetary Analysis',
        price: '\$7.99',
        credits: '50',
        icon: Icons.stars_rounded,
      ),
      _Report(
        title: 'Gem Prescription',
        subtitle: 'Recommended Gemstones',
        price: '\$2.99',
        credits: '20',
        icon: Icons.diamond_rounded,
      ),
    ];

    return StarBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Reports & Insights',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Colors.white,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Detailed astrological reports personalized to your chart',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white54,
                      ),
                ),
                const SizedBox(height: 24),
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    childAspectRatio: 0.85,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                  ),
                  itemCount: reports.length,
                  itemBuilder: (context, index) {
                    final report = reports[index];
                    return _ReportCard(report: report);
                  },
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
        bottomNavigationBar: const BottomNavBar(currentIndex: -1),
      ),
    );
  }
}

class _Report {
  final String title;
  final String subtitle;
  final String price;
  final String credits;
  final IconData icon;

  _Report({
    required this.title,
    required this.subtitle,
    required this.price,
    required this.credits,
    required this.icon,
  });
}

class _ReportCard extends StatelessWidget {
  final _Report report;

  const _ReportCard({required this.report});

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      onTap: () {},
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xff6C63FF).withOpacity(0.2),
            ),
            child: Icon(
              report.icon,
              color: const Color(0xff6C63FF),
              size: 20,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            report.title,
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  color: Colors.white,
                ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            report.subtitle,
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: Colors.white54,
                ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const Spacer(),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                report.price,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                '${report.credits} credits',
                style: TextStyle(
                  color: Colors.white54,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
