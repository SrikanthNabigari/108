import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';
import '../../../shared/widgets/glass_card.dart';

/// Remedies dashboard with personalized recommendations.
class RemediesScreen extends ConsumerWidget {
  const RemediesScreen({Key? key}) : super(key: key);

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
                Text(
                  'Remedies',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Colors.white,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Personalized remedies for your current chart position',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white54,
                      ),
                ),
                const SizedBox(height: 24),
                // Urgent remedies
                _SectionHeader(title: 'Urgent'),
                const SizedBox(height: 12),
                _RemedyCard(
                  title: 'Saturn Sade Sati Remedies',
                  description:
                      'Saturn is transiting over your natal Moon position. Perform Saturn remedies to ease the transition.',
                  actions: ['Chant Hanuman Chalisa', 'Wear Blue Sapphire'],
                  severity: 'high',
                ),
                const SizedBox(height: 24),
                // Recommended remedies
                _SectionHeader(title: 'Recommended'),
                const SizedBox(height: 12),
                _RemedyCard(
                  title: 'Mars Strengthening',
                  description:
                      'Mars in Cancer (debilitated) needs strengthening for career energy.',
                  actions: ['Donate red items', 'Perform Mangal mantra'],
                  severity: 'medium',
                ),
                const SizedBox(height: 12),
                _RemedyCard(
                  title: 'Mercury Puja',
                  description:
                      'Mercury is your chart ruler. Monthly puja enhances its benefits.',
                  actions: ['Visit temple on Wednesdays', 'Offer green items'],
                  severity: 'medium',
                ),
                const SizedBox(height: 24),
                // Gem recommendations
                _SectionHeader(title: 'Gemstone Recommendations'),
                const SizedBox(height: 12),
                _GemCard(
                  gemName: 'Blue Sapphire',
                  planet: 'Saturn',
                  weight: '3-5 carats',
                  finger: 'Middle finger',
                  metal: 'Silver',
                  day: 'Saturday',
                ),
                const SizedBox(height: 12),
                _GemCard(
                  gemName: 'Emerald',
                  planet: 'Mercury',
                  weight: '2-3 carats',
                  finger: 'Little finger',
                  metal: 'Gold',
                  day: 'Wednesday',
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

class _SectionHeader extends StatelessWidget {
  final String title;

  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: Theme.of(context).textTheme.labelMedium?.copyWith(
            color: Colors.white70,
          ),
    );
  }
}

class _RemedyCard extends StatelessWidget {
  final String title;
  final String description;
  final List<String> actions;
  final String severity;

  const _RemedyCard({
    required this.title,
    required this.description,
    required this.actions,
    required this.severity,
  });

  Color _getSeverityColor() {
    switch (severity) {
      case 'high':
        return const Color(0xFFE74C3C);
      case 'medium':
        return const Color(0xFFF39C12);
      default:
        return const Color(0xFF2ECC71);
    }
  }

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 4,
                height: 20,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(2),
                  color: _getSeverityColor(),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  title,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: Colors.white,
                      ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            description,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.white70,
                ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: actions
                .map(
                  (action) => Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(6),
                      color: _getSeverityColor().withOpacity(0.2),
                    ),
                    child: Text(
                      action,
                      style: TextStyle(
                        color: _getSeverityColor(),
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                )
                .toList(),
          ),
        ],
      ),
    );
  }
}

class _GemCard extends StatelessWidget {
  final String gemName;
  final String planet;
  final String weight;
  final String finger;
  final String metal;
  final String day;

  const _GemCard({
    required this.gemName,
    required this.planet,
    required this.weight,
    required this.finger,
    required this.metal,
    required this.day,
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
              Text(
                gemName,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: Colors.white,
                    ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(6),
                  color: const Color(0xff6C63FF).withOpacity(0.2),
                ),
                child: Text(
                  planet,
                  style: TextStyle(
                    color: const Color(0xff6C63FF),
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _DetailText(label: 'Weight', value: weight),
          const SizedBox(height: 6),
          _DetailText(label: 'Finger', value: finger),
          const SizedBox(height: 6),
          _DetailText(label: 'Metal', value: metal),
          const SizedBox(height: 6),
          _DetailText(label: 'Best Day', value: day),
        ],
      ),
    );
  }
}

class _DetailText extends StatelessWidget {
  final String label;
  final String value;

  const _DetailText({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Colors.white54,
              ),
        ),
        Text(
          value,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Colors.white,
              ),
        ),
      ],
    );
  }
}
