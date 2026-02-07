import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/glass_card.dart';

/// Subscription paywall with tier comparison.
class PaywallScreen extends ConsumerWidget {
  const PaywallScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return StarBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_rounded),
            onPressed: () => context.pop(),
          ),
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Unlock Premium',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Colors.white,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Access your complete cosmic blueprint',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white54,
                      ),
                ),
                const SizedBox(height: 32),
                // Tier cards
                _TierCard(
                  name: 'Nakshatra',
                  subtitle: 'Free',
                  price: '\$0',
                  period: 'Forever',
                  features: [
                    'Birth chart (D1)',
                    'Today\'s forecast',
                    'Basic yoga list',
                    '5 chat messages/day',
                  ],
                  isSelected: false,
                  onTap: () {},
                ),
                const SizedBox(height: 12),
                _TierCard(
                  name: 'Graha',
                  subtitle: 'Most Popular',
                  price: '\$6.99',
                  period: '/month',
                  features: [
                    'All Free features',
                    'Full forecasts (Daily/Weekly/Monthly)',
                    'D9 & D10 charts',
                    'Muhurta finder',
                    'Yoga interpretations',
                    '30 chat messages/day',
                    'Event calendar',
                    'Compatibility Ashta Kuta',
                  ],
                  isSelected: true,
                  onTap: () {},
                ),
                const SizedBox(height: 12),
                _TierCard(
                  name: 'Rishi',
                  subtitle: 'Premium',
                  price: '\$14.99',
                  period: '/month',
                  features: [
                    'All Graha features',
                    'Yearly forecast',
                    'Full synastry analysis',
                    'Atmakaraka analysis',
                    'All divisional charts',
                    'Unlimited chat',
                    'KP predictions',
                    'Priority support',
                  ],
                  isSelected: false,
                  onTap: () {},
                ),
                const SizedBox(height: 32),
                // Subscribe button
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
                      onPressed: () {},
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.transparent,
                        shadowColor: Colors.transparent,
                      ),
                      child: const Text('Subscribe to Graha'),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                // Restore purchases
                Center(
                  child: TextButton(
                    onPressed: () {},
                    child: const Text(
                      'Restore Purchases',
                      style: TextStyle(
                        color: Color(0xff6C63FF),
                        fontSize: 14,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _TierCard extends StatelessWidget {
  final String name;
  final String subtitle;
  final String price;
  final String period;
  final List<String> features;
  final bool isSelected;
  final VoidCallback onTap;

  const _TierCard({
    required this.name,
    required this.subtitle,
    required this.price,
    required this.period,
    required this.features,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      onTap: onTap,
      border: isSelected
          ? Border.all(
              color: const Color(0xff6C63FF),
              width: 2,
            )
          : null,
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
                    name,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: Colors.white,
                        ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: isSelected
                              ? const Color(0xff6C63FF)
                              : Colors.white54,
                        ),
                  ),
                ],
              ),
              if (isSelected)
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
                    'Selected',
                    style: TextStyle(
                      color: const Color(0xff6C63FF),
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            textBaseline: TextBaseline.alphabetic,
            crossAxisAlignment: CrossAxisAlignment.baseline,
            children: [
              Text(
                price,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 4),
              Text(
                period,
                style: TextStyle(
                  color: Colors.white54,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: features
                .map(
                  (feature) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.check_circle_rounded,
                          size: 16,
                          color: Color(0xff6C63FF),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            feature,
                            style: Theme.of(context)
                                .textTheme
                                .labelSmall
                                ?.copyWith(
                                  color: Colors.white70,
                                ),
                          ),
                        ),
                      ],
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
