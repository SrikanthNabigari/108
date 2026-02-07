import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';
import '../../../shared/widgets/glass_card.dart';

/// Event calendar with muhurta and personal event tracking.
class CalendarScreen extends ConsumerWidget {
  const CalendarScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return StarBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Calendar',
                      style: Theme.of(context)
                          .textTheme
                          .headlineSmall
                          ?.copyWith(
                            color: Colors.white,
                          ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.add_rounded),
                      onPressed: () {},
                      color: const Color(0xff6C63FF),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // Month selector
                GlassCard(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.chevron_left_rounded),
                        onPressed: () {},
                        color: Colors.white70,
                      ),
                      Text(
                        'February 2026',
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              color: Colors.white,
                            ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.chevron_right_rounded),
                        onPressed: () {},
                        color: Colors.white70,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                // Calendar grid
                GlassCard(
                  padding: const EdgeInsets.all(16),
                  child: _buildCalendarGrid(),
                ),
                const SizedBox(height: 24),
                // Upcoming events
                Text(
                  'Upcoming Events',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Colors.white70,
                      ),
                ),
                const SizedBox(height: 12),
                _EventItem(
                  title: 'Full Moon in Virgo',
                  date: 'Feb 14',
                  type: 'cosmic',
                ),
                const SizedBox(height: 8),
                _EventItem(
                  title: 'Auspicious time for interviews',
                  date: 'Feb 18',
                  type: 'muhurta',
                ),
                const SizedBox(height: 8),
                _EventItem(
                  title: 'Mercury Retrograde Ends',
                  date: 'Feb 22',
                  type: 'transit',
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
        bottomNavigationBar: const BottomNavBar(currentIndex: 3),
      ),
    );
  }

  Widget _buildCalendarGrid() {
    final days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    final dates = List.generate(28, (i) => i + 1);

    return Column(
      children: [
        // Day headers
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: days.map((day) {
            return SizedBox(
              width: 40,
              child: Center(
                child: Text(
                  day,
                  style: const TextStyle(
                    color: Colors.white54,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 12),
        // Date grid
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 7,
            childAspectRatio: 1,
            mainAxisSpacing: 4,
            crossAxisSpacing: 4,
          ),
          itemCount: 28,
          itemBuilder: (context, index) {
            final date = dates[index];
            final hasEvent = date == 14 || date == 18 || date == 22;

            return Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8),
                color: hasEvent
                    ? const Color(0xff6C63FF).withOpacity(0.2)
                    : Colors.white.withOpacity(0.05),
                border: Border.all(
                  color: hasEvent
                      ? const Color(0xff6C63FF).withOpacity(0.5)
                      : Colors.white.withOpacity(0.1),
                ),
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  Text(
                    date.toString(),
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (hasEvent)
                    Positioned(
                      bottom: 2,
                      child: Container(
                        width: 4,
                        height: 4,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: Color(0xff6C63FF),
                        ),
                      ),
                    ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }
}

class _EventItem extends StatelessWidget {
  final String title;
  final String date;
  final String type;

  const _EventItem({
    required this.title,
    required this.date,
    required this.type,
  });

  Color _getTypeColor() {
    switch (type) {
      case 'cosmic':
        return const Color(0xff6C63FF);
      case 'muhurta':
        return const Color(0xFF2ECC71);
      case 'transit':
        return const Color(0xFFF39C12);
      default:
        return Colors.white54;
    }
  }

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          Container(
            width: 4,
            height: 40,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(2),
              color: _getTypeColor(),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Colors.white,
                      ),
                ),
                const SizedBox(height: 2),
                Text(
                  date,
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: Colors.white54,
                      ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
