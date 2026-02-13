import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/data/services/supabase_service.dart';

class PhoneAuthScreen extends ConsumerStatefulWidget {
  const PhoneAuthScreen({super.key});

  @override
  ConsumerState<PhoneAuthScreen> createState() => _PhoneAuthScreenState();
}

class _PhoneAuthScreenState extends ConsumerState<PhoneAuthScreen> {
  final _phoneController = TextEditingController();
  bool _isSending = false;
  String _countryCode = '+91';

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    final phone = _phoneController.text.trim();
    if (phone.length < 10) {
      _showSnack('Enter a valid phone number');
      return;
    }

    setState(() => _isSending = true);
    try {
      final fullPhone = '$_countryCode$phone';
      await SupabaseService().signInWithPhone(fullPhone);
      if (mounted) context.push('/otp-verify', extra: fullPhone);
    } catch (e) {
      _showSnack('Failed to send OTP: $e');
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  Future<void> _devSignIn() async {
    setState(() => _isSending = true);
    try {
      await SupabaseService().signInAnonymously();
      // Auth listener in GoRouter will redirect to /profile
    } catch (e) {
      _showSnack('Anonymous sign-in failed: $e');
      if (mounted) setState(() => _isSending = false);
    }
  }

  static const _countries = [
    ('+91', 'IN', 'India'),
    ('+1', 'US', 'United States'),
    ('+44', 'GB', 'United Kingdom'),
    ('+61', 'AU', 'Australia'),
    ('+971', 'AE', 'UAE'),
    ('+65', 'SG', 'Singapore'),
    ('+60', 'MY', 'Malaysia'),
    ('+977', 'NP', 'Nepal'),
    ('+94', 'LK', 'Sri Lanka'),
    ('+880', 'BD', 'Bangladesh'),
  ];

  void _showCountryPicker() {
    showModalBottomSheet(
      context: context,
      backgroundColor: C.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(R.xl)),
      ),
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: S.lg),
            Text('Select Country', style: T.h3),
            const SizedBox(height: S.lg),
            ..._countries.map((c) => ListTile(
              leading: Text(c.$2, style: T.body),
              title: Text(c.$3, style: T.bodySm.copyWith(color: C.textPrimary)),
              trailing: Text(c.$1, style: T.bodySm.copyWith(color: C.textSecondary)),
              onTap: () {
                setState(() => _countryCode = c.$1);
                Navigator.pop(context);
              },
            )),
            const SizedBox(height: S.lg),
          ],
        ),
      ),
    );
  }

  void _showSnack(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: Padding(
            padding: S.pagePadding,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Spacer(flex: 2),

                // Logo
                Center(
                  child: Text(
                    '108',
                    style: T.h1.copyWith(
                      fontSize: 48,
                      fontWeight: FontWeight.w800,
                      color: C.accent,
                      letterSpacing: 4,
                    ),
                  ),
                ),
                const SizedBox(height: S.sm),
                Center(
                  child: Text(
                    'Your cosmic operating system',
                    style: T.bodySm.copyWith(color: C.textMuted),
                  ),
                ),

                const Spacer(flex: 2),

                // Phone input
                GlassContainer(
                  padding: const EdgeInsets.symmetric(horizontal: S.lg),
                  child: Row(
                    children: [
                      // Country code
                      GestureDetector(
                        onTap: () {
                          _showCountryPicker();
                        },
                        child: Row(
                          children: [
                            Text(
                              _countryCode,
                              style: T.body.copyWith(color: C.textPrimary),
                            ),
                            const SizedBox(width: S.xs),
                            const Icon(Icons.keyboard_arrow_down,
                                color: C.textMuted, size: 18),
                          ],
                        ),
                      ),
                      Container(
                        width: 1,
                        height: 24,
                        margin: const EdgeInsets.symmetric(horizontal: S.md),
                        color: C.glassBorder,
                      ),
                      Expanded(
                        child: TextField(
                          controller: _phoneController,
                          keyboardType: TextInputType.phone,
                          style: T.body,
                          decoration: InputDecoration(
                            hintText: 'Phone number',
                            hintStyle: T.body.copyWith(color: C.textMuted),
                            border: InputBorder.none,
                            contentPadding: const EdgeInsets.symmetric(
                                vertical: S.lg),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: S.lg),

                // Send OTP button
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _isSending ? null : _sendOtp,
                    child: _isSending
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: C.textOnAccent,
                            ),
                          )
                        : const Text('Send OTP'),
                  ),
                ),

                const SizedBox(height: S.xl),

                // Divider
                Row(
                  children: [
                    const Expanded(child: Divider(color: C.divider)),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: S.lg),
                      child: Text('or', style: T.caption),
                    ),
                    const Expanded(child: Divider(color: C.divider)),
                  ],
                ),

                const SizedBox(height: S.xl),

                // Dev anonymous sign-in
                if (kDebugMode)
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: OutlinedButton(
                      onPressed: _isSending ? null : _devSignIn,
                      child: const Text('Continue as Guest (Dev)'),
                    ),
                  ),

                const Spacer(flex: 3),

                // Footer
                Center(
                  child: Text(
                    'By continuing, you agree to our Terms of Service',
                    style: T.caption,
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: S.lg),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
