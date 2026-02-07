import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/glass_card.dart';

/// Credit store for purchasing report credits.
class CreditStoreScreen extends ConsumerWidget {
  const CreditStoreScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final packs = [
      _CreditPack(
        credits: 50,
        price: '\$2.99',
        label: 'Starter',
        costPerCredit: 0.06,
      ),
      _CreditPack(
        credits: 200,
        price: '\$9.99',
        label: 'Popular',
        costPerCredit: 0.05,
        badge: 'Best Value',
      ),
      _CreditPack(
        credits: 500,
        price: '\$19.99',
        label: 'Power User',
        costPerCredit: 0.04,
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
                  'Buy Credits',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Colors.white,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Use credits to purchase detailed reports',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white54,
                      ),
                ),
                const SizedBox(height: 24),
                // Current balance
                GlassCard(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Current Balance',
                            style: Theme.of(context)
                                .textTheme
                                .labelMedium
                                ?.copyWith(
                                  color: Colors.white70,
                                ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '45 Credits',
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  color: const Color(0xff6C63FF),
                                ),
                          ),
                        ],
                      ),
                      Container(
                        width: 60,
                        height: 60,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: const Color(0xff6C63FF).withOpacity(0.2),
                        ),
                        child: const Icon(
                          Icons.stars_rounded,
                          color: Color(0xff6C63FF),
                          size: 32,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
                // Credit packs
                Text(
                  'Credit Packs',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Colors.white70,
                      ),
                ),
                const SizedBox(height: 12),
                ...packs.map((pack) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: _PackCard(pack: pack),
                  );
                }).toList(),
                const SizedBox(height: 24),
                // Report prices reference
                Text(
                  'Report Prices',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Colors.white70,
                      ),
                ),
                const SizedBox(height: 12),
                GlassCard(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _PriceRow('Year Ahead', '40 credits'),
                      const SizedBox(height: 10),
                      _PriceRow('Career Blueprint', '40 credits'),
                      const SizedBox(height: 10),
                      _PriceRow('Marriage Report', '40 credits'),
                      const SizedBox(height: 10),
                      _PriceRow('Soul Purpose', '30 credits'),
                      const SizedBox(height: 10),
                      _PriceRow('Birth Chart Full', '50 credits'),
                    ],
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

class _CreditPack {
  final int credits;
  final String price;
  final String label;
  final double costPerCredit;
  final String? badge;

  _CreditPack({
    required this.credits,
    required this.price,
    required this.label,
    required this.costPerCredit,
    this.badge,
  });
}

class _PackCard extends StatelessWidget {
  final _CreditPack pack;

  const _PackCard({required this.pack});

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      onTap: () {},
      padding: const EdgeInsets.all(16),
      border: pack.badge != null
          ? Border.all(
              color: const Color(0xff6C63FF),
              width: 1.5,
            )
          : null,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        '${pack.credits}',
                        style:
                            Theme.of(context).textTheme.titleSmall?.copyWith(
                                  color: Colors.white,
                                ),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        'Credits',
                        style:
                            Theme.of(context).textTheme.labelSmall?.copyWith(
                                  color: Colors.white54,
                                ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    pack.label,
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: Colors.white70,
                        ),
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    pack.price,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: const Color(0xff6C63FF),
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${pack.costPerCredit.toStringAsFixed(3)}/credit',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: Colors.white54,
                        ),
                  ),
                ],
              ),
            ],
          ),
          if (pack.badge != null) ...[
            const SizedBox(height: 12),
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
                pack.badge!,
                style: TextStyle(
                  color: const Color(0xff6C63FF),
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _PriceRow extends StatelessWidget {
  final String label;
  final String price;

  const _PriceRow(this.label, this.price);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Colors.white70,
              ),
        ),
        Text(
          price,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.w600,
              ),
        ),
      ],
    );
  }
}
