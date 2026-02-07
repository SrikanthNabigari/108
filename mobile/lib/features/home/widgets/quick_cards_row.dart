import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../shared/widgets/glass_card.dart';

/// Horizontal scrolling quick action cards.
class QuickCardsRow extends StatelessWidget {
  const QuickCardsRow({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final cards = [
      _QuickCard(
        icon: Icons.access_time_rounded,
        label: 'Dasha',
        subtitle: 'Period',
        onTap: () => context.push('/timeline'),
      ),
      _QuickCard(
        icon: Icons.notifications_active_rounded,
        label: 'Transits',
        subtitle: 'Alerts',
        onTap: () => context.push('/chart'),
      ),
      _QuickCard(
        icon: Icons.stars_rounded,
        label: 'Muhurta',
        subtitle: 'Auspicious times',
        onTap: () => context.push('/muhurta'),
      ),
      _QuickCard(
        icon: Icons.healing_rounded,
        label: 'Remedies',
        subtitle: 'Personalized',
        onTap: () => context.push('/remedies'),
      ),
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          const SizedBox(width: 4),
          ...cards.map((card) {
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: card,
            );
          }),
          const SizedBox(width: 4),
        ],
      ),
    );
  }
}

class _QuickCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String subtitle;
  final VoidCallback onTap;

  const _QuickCard({
    required this.icon,
    required this.label,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      onTap: onTap,
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                colors: [Color(0xff6C63FF), Color(0xff8A84FF)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            child: Icon(
              icon,
              color: Colors.white,
              size: 20,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            subtitle,
            style: TextStyle(
              color: Colors.white54,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }
}
