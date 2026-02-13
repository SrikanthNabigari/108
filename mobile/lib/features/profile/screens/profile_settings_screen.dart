import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/data/providers/user_provider.dart';
import 'package:one_zero_eight/data/models/user_model.dart';
import 'package:one_zero_eight/data/services/supabase_service.dart';

class ProfileSettingsScreen extends ConsumerStatefulWidget {
  const ProfileSettingsScreen({super.key});

  @override
  ConsumerState<ProfileSettingsScreen> createState() =>
      _ProfileSettingsScreenState();
}

class _ProfileSettingsScreenState extends ConsumerState<ProfileSettingsScreen> {
  bool _signingOut = false;

  // ── Helpers ──

  String _initials(String? name) {
    if (name == null || name.isEmpty) return '?';
    return name[0].toUpperCase();
  }

  Color _tierColor(String tier) {
    switch (tier.toLowerCase()) {
      case 'pro':
        return C.jupiter;
      case 'premium':
        return C.venus;
      default:
        return C.textMuted;
    }
  }

  String _tierLabel(String tier) {
    switch (tier.toLowerCase()) {
      case 'pro':
        return 'Pro';
      case 'premium':
        return 'Premium';
      default:
        return 'Free';
    }
  }

  String _formatBirthDatetime(DateTime? dt) {
    if (dt == null) return 'Not set';
    return DateFormat('dd MMM yyyy, hh:mm a').format(dt);
  }

  String _formatLatLon(double? lat, double? lon) {
    if (lat == null || lon == null) return 'Not set';
    return '${lat.toStringAsFixed(4)}, ${lon.toStringAsFixed(4)}';
  }

  // ── Sign out ──

  Future<void> _confirmSignOut() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: C.surface,
        shape: RoundedRectangleBorder(borderRadius: R.lgBr),
        title: Text('Sign Out', style: T.h3),
        content: Text(
          'Are you sure you want to sign out?',
          style: T.bodySm,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: C.negative),
            child: const Text('Sign Out'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    setState(() => _signingOut = true);
    try {
      await SupabaseService().signOut();
      if (mounted) context.go('/phone-auth');
    } catch (_) {
      if (mounted) setState(() => _signingOut = false);
    }
  }

  // ── Build ──

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(userProfileProvider);

    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: profileAsync.when(
            loading: () => const Center(
              child: CircularProgressIndicator(color: C.accent, strokeWidth: 2),
            ),
            error: (err, _) => Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Failed to load profile', style: T.bodySm),
                  const SizedBox(height: S.md),
                  TextButton(
                    onPressed: () => ref.invalidate(userProfileProvider),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
            data: (user) => _buildContent(user),
          ),
        ),
      ),
    );
  }

  Widget _buildContent(UserModel user) {
    return SingleChildScrollView(
      padding: S.pagePadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: S.xl),

          // ── Header ──
          _buildHeader(user),
          const SizedBox(height: S.xxl),

          // ── Personal Details ──
          _buildSectionTitle('Personal Details'),
          const SizedBox(height: S.sm),
          GlassContainer(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                _SettingsRow(
                  label: 'Name',
                  value: user.name ?? 'Not set',
                  onTap: () {
                    // TODO: navigate to edit name
                  },
                ),
                const Divider(height: 1, color: C.divider),
                _SettingsRow(
                  label: 'Gender',
                  value: user.gender ?? 'Not set',
                ),
                const Divider(height: 1, color: C.divider),
                _SettingsRow(
                  label: 'Phone',
                  value: user.phone ?? 'Not set',
                  trailing: user.phone != null
                      ? Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: S.sm, vertical: 2),
                          decoration: BoxDecoration(
                            borderRadius: R.smBr,
                            color: C.positive.withValues(alpha: 0.12),
                          ),
                          child: Text(
                            'verified',
                            style: T.caption.copyWith(
                                color: C.positive, fontSize: 10),
                          ),
                        )
                      : null,
                ),
              ],
            ),
          ),
          const SizedBox(height: S.xl),

          // ── Birth Details ──
          _buildSectionTitle('Birth Details'),
          const SizedBox(height: S.sm),
          GlassContainer(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                _SettingsRow(
                  label: 'Date / Time',
                  value: _formatBirthDatetime(user.birthDatetime),
                ),
                const Divider(height: 1, color: C.divider),
                _SettingsRow(
                  label: 'Place',
                  value: user.placeName ?? 'Not set',
                ),
                const Divider(height: 1, color: C.divider),
                _SettingsRow(
                  label: 'Lat / Lon',
                  value: _formatLatLon(user.birthLatitude, user.birthLongitude),
                ),
              ],
            ),
          ),
          const SizedBox(height: S.md),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () => context.push('/birth-details'),
              child: const Text('Edit Birth Details'),
            ),
          ),
          const SizedBox(height: S.xl),

          // ── Subscription ──
          _buildSectionTitle('Subscription'),
          const SizedBox(height: S.sm),
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            borderColor: _tierColor(user.subscriptionTier).withValues(alpha: 0.3),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: S.md, vertical: S.xs),
                      decoration: BoxDecoration(
                        borderRadius: R.smBr,
                        color: _tierColor(user.subscriptionTier)
                            .withValues(alpha: 0.15),
                      ),
                      child: Text(
                        _tierLabel(user.subscriptionTier),
                        style: T.label.copyWith(
                          color: _tierColor(user.subscriptionTier),
                          fontSize: 12,
                        ),
                      ),
                    ),
                    const Spacer(),
                    Text(
                      'Current Plan',
                      style: T.caption,
                    ),
                  ],
                ),
                const SizedBox(height: S.md),
                Text(
                  _tierDescription(user.subscriptionTier),
                  style: T.bodySm.copyWith(color: C.textSecondary),
                ),
                const SizedBox(height: S.lg),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton(
                    onPressed: () => context.push('/credits'),
                    child: const Text('View Credits'),
                  ),
                ),
                if (user.subscriptionTier.toLowerCase() != 'premium') ...[
                  const SizedBox(height: S.sm),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton(
                      onPressed: () {
                        // TODO: upgrade flow
                      },
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(
                            color: C.jupiter.withValues(alpha: 0.5)),
                        foregroundColor: C.jupiter,
                      ),
                      child: const Text('Upgrade'),
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: S.xl),

          // ── Quick Links ──
          _buildSectionTitle('Quick Links'),
          const SizedBox(height: S.sm),
          Row(
            children: [
              _QuickLink(
                icon: Icons.favorite_border,
                label: 'Compatibility',
                onTap: () => context.push('/compatibility'),
              ),
              const SizedBox(width: S.sm),
              _QuickLink(
                icon: Icons.description_outlined,
                label: 'Reports',
                onTap: () => context.push('/reports'),
              ),
              const SizedBox(width: S.sm),
              _QuickLink(
                icon: Icons.grid_on,
                label: 'State Map',
                onTap: () => context.push('/state-map'),
              ),
              const SizedBox(width: S.sm),
              _QuickLink(
                icon: Icons.menu_book_rounded,
                label: 'Learn',
                onTap: () => context.push('/learn'),
              ),
            ],
          ),
          const SizedBox(height: S.xxxl),

          // ── Sign Out ──
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _signingOut ? null : _confirmSignOut,
              style: ElevatedButton.styleFrom(
                backgroundColor: C.negative,
                foregroundColor: Colors.white,
              ),
              child: _signingOut
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        color: Colors.white,
                        strokeWidth: 2,
                      ),
                    )
                  : const Text('Sign Out'),
            ),
          ),
          const SizedBox(height: S.xl),

          // ── Footer ──
          Center(child: Text('v1.0', style: T.caption)),
          const SizedBox(height: S.xxl),
        ],
      ),
    );
  }

  // ── Header ──

  Widget _buildHeader(UserModel user) {
    return Center(
      child: Column(
        children: [
          // Avatar
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: C.glassBg,
              border: Border.all(color: C.accent, width: 2),
            ),
            child: Center(
              child: Text(
                _initials(user.name),
                style: T.h1.copyWith(
                  color: C.accent,
                  fontSize: 32,
                ),
              ),
            ),
          ),
          const SizedBox(height: S.md),

          // Name
          Text(user.name ?? 'Explorer', style: T.h2),
          const SizedBox(height: S.sm),

          // Tier badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.xs),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              color: _tierColor(user.subscriptionTier).withValues(alpha: 0.15),
              border: Border.all(
                color: _tierColor(user.subscriptionTier).withValues(alpha: 0.3),
              ),
            ),
            child: Text(
              _tierLabel(user.subscriptionTier),
              style: T.caption.copyWith(
                color: _tierColor(user.subscriptionTier),
                fontWeight: FontWeight.w600,
                fontSize: 11,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Section Title ──

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: T.h3.copyWith(fontSize: 16),
    );
  }

  // ── Tier Description ──

  String _tierDescription(String tier) {
    switch (tier.toLowerCase()) {
      case 'pro':
        return 'Unlimited chat, detailed reports, priority support.';
      case 'premium':
        return 'Everything in Pro plus compatibility, advanced forecasts, and more.';
      default:
        return 'Basic chart analysis with limited daily messages.';
    }
  }
}

// ════════════════════════════════════════════════════════════════
// Settings Row
// ════════════════════════════════════════════════════════════════

class _SettingsRow extends StatelessWidget {
  final String label;
  final String value;
  final VoidCallback? onTap;
  final Widget? trailing;

  const _SettingsRow({
    required this.label,
    required this.value,
    this.onTap,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
        child: Row(
          children: [
            SizedBox(
              width: 90,
              child: Text(
                label,
                style: T.bodySm.copyWith(color: C.textMuted),
              ),
            ),
            Expanded(
              child: Text(
                value,
                style: T.bodySm.copyWith(color: C.textPrimary),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            if (trailing != null) ...[
              const SizedBox(width: S.sm),
              trailing!,
            ],
            if (onTap != null)
              const Padding(
                padding: EdgeInsets.only(left: S.sm),
                child: Icon(Icons.chevron_right, color: C.textMuted, size: 18),
              ),
          ],
        ),
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════
// Quick Link
// ════════════════════════════════════════════════════════════════

class _QuickLink extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _QuickLink({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: GlassContainer(
          padding: const EdgeInsets.symmetric(vertical: S.md),
          child: Column(
            children: [
              Icon(icon, color: C.textSecondary, size: 22),
              const SizedBox(height: S.xs),
              Text(
                label,
                style: T.caption.copyWith(fontSize: 10),
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
