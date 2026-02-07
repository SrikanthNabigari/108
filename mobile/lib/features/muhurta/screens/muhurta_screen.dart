import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';
import '../../../shared/widgets/glass_card.dart';

/// Muhurta finder for checking auspicious times.
class MuhurtaScreen extends ConsumerStatefulWidget {
  const MuhurtaScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<MuhurtaScreen> createState() => _MuhurtaScreenState();
}

class _MuhurtaScreenState extends ConsumerState<MuhurtaScreen> {
  String _selectedActivity = 'marriage';
  DateTime? _selectedDate;
  bool _showResults = false;

  @override
  Widget build(BuildContext context) {
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
                  'Muhurta Finder',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Colors.white,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Find auspicious times for important events',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white54,
                      ),
                ),
                const SizedBox(height: 24),
                // Activity picker
                Text(
                  'Activity Type',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Colors.white70,
                      ),
                ),
                const SizedBox(height: 12),
                GlassCard(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: _selectedActivity,
                      isExpanded: true,
                      style: const TextStyle(color: Colors.white),
                      dropdownColor: const Color(0x1aFFFFFF),
                      items: [
                        'marriage',
                        'business_start',
                        'travel',
                        'surgery',
                        'new_job',
                        'house_warming',
                      ]
                          .map(
                            (activity) => DropdownMenuItem(
                              value: activity,
                              child: Text(
                                activity
                                    .replaceAll('_', ' ')
                                    .toUpperCase(),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 14,
                                ),
                              ),
                            ),
                          )
                          .toList(),
                      onChanged: (value) {
                        if (value != null) {
                          setState(() => _selectedActivity = value);
                        }
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                // Date picker
                Text(
                  'Select Date Range',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Colors.white70,
                      ),
                ),
                const SizedBox(height: 12),
                GlassCard(
                  onTap: () async {
                    final date = await showDatePicker(
                      context: context,
                      initialDate: DateTime.now(),
                      firstDate: DateTime.now(),
                      lastDate: DateTime.now().add(const Duration(days: 180)),
                      builder: (context, child) => Theme(
                        data: ThemeData.dark().copyWith(
                          primaryColor: const Color(0xff6C63FF),
                        ),
                        child: child!,
                      ),
                    );
                    if (date != null) {
                      setState(() => _selectedDate = date);
                    }
                  },
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 16,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _selectedDate != null
                            ? '${_selectedDate!.day}/${_selectedDate!.month}/${_selectedDate!.year}'
                            : 'Pick a start date',
                        style: TextStyle(
                          color: _selectedDate != null
                              ? Colors.white
                              : Colors.white54,
                          fontSize: 14,
                        ),
                      ),
                      Icon(
                        Icons.calendar_today_rounded,
                        color: Colors.white54,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
                // Check button
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xff6C63FF), Color(0xff8A84FF)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: ElevatedButton(
                      onPressed: () => setState(() => _showResults = true),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.transparent,
                        shadowColor: Colors.transparent,
                      ),
                      child: const Text('Check Muhurta'),
                    ),
                  ),
                ),
                if (_showResults) ...[
                  const SizedBox(height: 32),
                  Text(
                    'Auspicious Times',
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                          color: Colors.white70,
                        ),
                  ),
                  const SizedBox(height: 12),
                  _ResultCard(
                    date: 'Feb 18, 2026',
                    time: '10:30 AM - 12:00 PM',
                    score: 9.2,
                    reason: 'Excellent time. Abhijit Muhurta window.',
                  ),
                  const SizedBox(height: 8),
                  _ResultCard(
                    date: 'Feb 22, 2026',
                    time: '2:45 PM - 4:30 PM',
                    score: 8.5,
                    reason: 'Very good. Moon waxing in Pushya nakshatra.',
                  ),
                  const SizedBox(height: 8),
                  _ResultCard(
                    date: 'Feb 25, 2026',
                    time: '6:00 AM - 7:15 AM',
                    score: 7.8,
                    reason: 'Good. Early morning Brahma Muhurta.',
                  ),
                  const SizedBox(height: 24),
                ],
              ],
            ),
          ),
        ),
        bottomNavigationBar: const BottomNavBar(currentIndex: -1),
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  final String date;
  final String time;
  final double score;
  final String reason;

  const _ResultCard({
    required this.date,
    required this.time,
    required this.score,
    required this.reason,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    date,
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                          color: Colors.white,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    time,
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: Colors.white70,
                        ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  color: const Color(0xff6C63FF).withOpacity(0.2),
                ),
                child: Text(
                  score.toStringAsFixed(1),
                  style: const TextStyle(
                    color: Color(0xff6C63FF),
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            reason,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.white70,
                ),
          ),
        ],
      ),
    );
  }
}
