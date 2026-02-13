import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/data/services/api_service.dart';

// -- Mock data ----------------------------------------------------------

const _kMockBalance = 25;
const _kMockTier = 'free';
final _kMockTransactions = <Map<String, dynamic>>[
  {
    'type': 'bonus',
    'amount': 10,
    'desc': 'Welcome bonus',
    'date': '2026-02-01',
  },
  {
    'type': 'spend',
    'amount': -5,
    'desc': 'Career Report',
    'date': '2026-02-05',
  },
  {
    'type': 'purchase',
    'amount': 50,
    'desc': 'Credit pack',
    'date': '2026-02-08',
  },
  {
    'type': 'spend',
    'amount': -30,
    'desc': 'Annual Report',
    'date': '2026-02-10',
  },
];

// -- Credit packs -------------------------------------------------------

const _kCreditPacks = [
  {'credits': 10, 'price': '\$2.99', 'label': 'Starter', 'best': false},
  {'credits': 50, 'price': '\$9.99', 'label': 'Popular', 'best': true},
  {'credits': 100, 'price': '\$14.99', 'label': 'Power User', 'best': false},
];

// -- Tier info ----------------------------------------------------------

const _kTierInfo = <String, Map<String, String>>{
  'free': {'name': 'Free', 'limit': '5'},
  'pro': {'name': 'Pro', 'limit': '25'},
  'premium': {'name': 'Premium', 'limit': 'unlimited'},
};

// =======================================================================
// Credits Screen
// =======================================================================

class CreditsScreen extends ConsumerStatefulWidget {
  const CreditsScreen({super.key});

  @override
  ConsumerState<CreditsScreen> createState() => _CreditsScreenState();
}

class _CreditsScreenState extends ConsumerState<CreditsScreen> {
  int _balance = _kMockBalance;
  String _tier = _kMockTier;
  List<Map<String, dynamic>> _transactions = _kMockTransactions;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    try {
      final balanceData = await ApiService().get<Map<String, dynamic>>(
        ApiConstants.creditsBalance,
        fromJson: (json) => json as Map<String, dynamic>,
      );
      final historyData = await ApiService().get<List<dynamic>>(
        ApiConstants.creditsHistory,
        fromJson: (json) => json as List<dynamic>,
      );
      if (!mounted) return;
      setState(() {
        _balance = (balanceData['balance'] as num?)?.toInt() ?? _kMockBalance;
        _tier = (balanceData['tier'] as String?) ?? _kMockTier;
        _transactions = historyData.cast<Map<String, dynamic>>();
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: C.bg,
      body: AmbientBackground(
        child: SafeArea(
          child: SingleChildScrollView(
            padding: S.pagePadding,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: S.sm),
                _buildHeader(context),
                const SizedBox(height: S.xl),
                _buildBalanceHero(),
                const SizedBox(height: S.lg),
                _buildTierInfo(),
                const SizedBox(height: S.xl),
                _buildCreditPacks(),
                const SizedBox(height: S.xl),
                _buildTransactionHistory(),
                const SizedBox(height: S.xxxl),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // -- Header -----------------------------------------------------------

  Widget _buildHeader(BuildContext context) {
    return Row(
      children: [
        GestureDetector(
          onTap: () => context.pop(),
          child: const Icon(Icons.arrow_back_ios_new,
              color: C.textPrimary, size: 20),
        ),
        const SizedBox(width: S.md),
        Text('Credits', style: T.h2),
      ],
    );
  }

  // -- Balance Hero -----------------------------------------------------

  Widget _buildBalanceHero() {
    return GlassContainer(
      borderColor: C.accent,
      padding: const EdgeInsets.symmetric(vertical: S.xxl, horizontal: S.xl),
      child: Center(
        child: Column(
          children: [
            _loading
                ? const SizedBox(
                    height: 48,
                    child: Center(
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: C.accent),
                    ),
                  )
                : Text(
                    '$_balance',
                    style: T.h1.copyWith(fontSize: 48, color: C.accent),
                  ),
            const SizedBox(height: S.sm),
            Text('credits available', style: T.bodySm),
          ],
        ),
      ),
    );
  }

  // -- Tier Info --------------------------------------------------------

  Widget _buildTierInfo() {
    final info = _kTierInfo[_tier] ?? _kTierInfo['free']!;
    return GlassContainer(
      padding: const EdgeInsets.all(S.lg),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            'Current Tier: ${info['name']}',
            style: T.bodySm.copyWith(color: C.textPrimary),
          ),
          Text(
            'Daily chat limit: ${info['limit']}',
            style: T.bodySm,
          ),
        ],
      ),
    );
  }

  // -- Credit Packs -----------------------------------------------------

  Widget _buildCreditPacks() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Buy Credits', style: T.h3.copyWith(fontSize: 16)),
        const SizedBox(height: S.md),
        ..._kCreditPacks.map((pack) => _buildPackCard(pack)),
      ],
    );
  }

  Widget _buildPackCard(Map<String, dynamic> pack) {
    final isBest = pack['best'] as bool;
    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: GestureDetector(
        onTap: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
                content: Text('Coming soon \u2014 RevenueCat integration')),
          );
        },
        child: GlassContainer(
          padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
          borderColor: isBest ? C.jupiter : null,
          child: Row(
            children: [
              // Left: amount + label
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          '${pack['credits']} credits',
                          style: T.body.copyWith(fontWeight: FontWeight.w600),
                        ),
                        if (isBest) ...[
                          const SizedBox(width: S.sm),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: S.sm, vertical: 2),
                            decoration: BoxDecoration(
                              color: C.jupiter,
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              'Best Value',
                              style: T.caption.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.w600,
                                fontSize: 10,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(pack['label'] as String, style: T.caption),
                  ],
                ),
              ),
              // Right: price
              Text(
                pack['price'] as String,
                style: T.h3.copyWith(color: C.accent),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // -- Transaction History ----------------------------------------------

  Widget _buildTransactionHistory() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Recent Transactions', style: T.h3.copyWith(fontSize: 16)),
        const SizedBox(height: S.md),
        if (_transactions.isEmpty)
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: S.xxl),
              child: Text('No transactions yet', style: T.bodySm),
            ),
          )
        else
          ..._transactions.map((tx) => _buildTransactionItem(tx)),
      ],
    );
  }

  Widget _buildTransactionItem(Map<String, dynamic> tx) {
    final type = tx['type'] as String;
    final amount = tx['amount'] as int;
    final desc = tx['desc'] as String;
    final date = tx['date'] as String;

    IconData icon;
    Color iconColor;
    switch (type) {
      case 'purchase':
        icon = Icons.add_circle;
        iconColor = C.positive;
        break;
      case 'spend':
        icon = Icons.remove_circle;
        iconColor = C.negative;
        break;
      case 'refund':
        icon = Icons.replay;
        iconColor = const Color(0xFF42A5F5); // blue
        break;
      case 'bonus':
        icon = Icons.card_giftcard;
        iconColor = C.jupiter;
        break;
      default:
        icon = Icons.circle;
        iconColor = C.textMuted;
    }

    final amountText = amount >= 0 ? '+$amount' : '$amount';
    final amountColor = amount >= 0 ? C.positive : C.negative;

    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: GlassContainer(
        padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
        child: Row(
          children: [
            Icon(icon, color: iconColor, size: 24),
            const SizedBox(width: S.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(desc, style: T.bodySm.copyWith(color: C.textPrimary)),
                  const SizedBox(height: 2),
                  Text(date, style: T.caption),
                ],
              ),
            ),
            Text(
              amountText,
              style: T.body.copyWith(
                color: amountColor,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
