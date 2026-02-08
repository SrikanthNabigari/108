import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/data/services/supabase_service.dart';

class OtpVerifyScreen extends ConsumerStatefulWidget {
  final String phoneNumber;
  const OtpVerifyScreen({super.key, required this.phoneNumber});

  @override
  ConsumerState<OtpVerifyScreen> createState() => _OtpVerifyScreenState();
}

class _OtpVerifyScreenState extends ConsumerState<OtpVerifyScreen> {
  final _otpController = TextEditingController();
  bool _isVerifying = false;

  @override
  void dispose() {
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _verify() async {
    final code = _otpController.text.trim();
    if (code.length != 6) {
      _showSnack('Enter the 6-digit code');
      return;
    }

    setState(() => _isVerifying = true);
    try {
      await SupabaseService().verifyOtp(
        phone: widget.phoneNumber,
        token: code,
      );
      // Auth listener in GoRouter will redirect to /profile
    } catch (e) {
      _showSnack('Verification failed: $e');
      if (mounted) setState(() => _isVerifying = false);
    }
  }

  Future<void> _resend() async {
    try {
      await SupabaseService().signInWithPhone(widget.phoneNumber);
      _showSnack('Code resent');
    } catch (e) {
      _showSnack('Failed to resend: $e');
    }
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
                const SizedBox(height: S.lg),

                // Back
                GestureDetector(
                  onTap: () => context.pop(),
                  child: const Icon(Icons.arrow_back_ios,
                      color: C.textSecondary, size: 20),
                ),

                const SizedBox(height: S.xxxl),

                Text('Verify your\nnumber', style: T.h1),
                const SizedBox(height: S.sm),
                Text(
                  'Enter the 6-digit code sent to\n${widget.phoneNumber}',
                  style: T.bodySm.copyWith(color: C.textMuted),
                ),

                const SizedBox(height: S.xxxl),

                // OTP input
                GlassContainer(
                  padding: const EdgeInsets.symmetric(horizontal: S.xl),
                  child: TextField(
                    controller: _otpController,
                    keyboardType: TextInputType.number,
                    textAlign: TextAlign.center,
                    maxLength: 6,
                    style: T.h2.copyWith(
                      letterSpacing: 12,
                      fontWeight: FontWeight.w700,
                    ),
                    decoration: InputDecoration(
                      hintText: '------',
                      hintStyle: T.h2.copyWith(
                        color: C.textMuted,
                        letterSpacing: 12,
                      ),
                      border: InputBorder.none,
                      counterText: '',
                      contentPadding:
                          const EdgeInsets.symmetric(vertical: S.lg),
                    ),
                  ),
                ),

                const SizedBox(height: S.xl),

                // Verify button
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _isVerifying ? null : _verify,
                    child: _isVerifying
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: C.textOnAccent,
                            ),
                          )
                        : const Text('Verify'),
                  ),
                ),

                const SizedBox(height: S.xl),

                // Resend
                Center(
                  child: TextButton(
                    onPressed: _resend,
                    child: const Text("Didn't receive it? Resend"),
                  ),
                ),

                const Spacer(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
