import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/colors.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../data/services/supabase_service.dart';

class OtpVerifyScreen extends ConsumerStatefulWidget {
  final String phoneNumber;

  const OtpVerifyScreen({
    Key? key,
    required this.phoneNumber,
  }) : super(key: key);

  @override
  ConsumerState<OtpVerifyScreen> createState() => _OtpVerifyScreenState();
}

class _OtpVerifyScreenState extends ConsumerState<OtpVerifyScreen> {
  late List<TextEditingController> _otpControllers;
  final _focusNodes = List<FocusNode>.generate(6, (_) => FocusNode());
  int _resendTimer = 30;
  bool _canResend = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _otpControllers = List<TextEditingController>.generate(
      6,
      (_) => TextEditingController(),
    );
    _startResendTimer();
  }

  void _startResendTimer() {
    setState(() {
      _resendTimer = 30;
      _canResend = false;
    });
    _tick();
  }

  void _tick() {
    Future.delayed(const Duration(seconds: 1), () {
      if (!mounted) return;
      setState(() => _resendTimer--);
      if (_resendTimer > 0) {
        _tick();
      } else {
        setState(() => _canResend = true);
      }
    });
  }

  Future<void> _resendOtp() async {
    try {
      await SupabaseService().signInWithPhone(widget.phoneNumber);
      _startResendTimer();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('OTP resent')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to resend: $e')),
        );
      }
    }
  }

  Future<void> _verifyOtp() async {
    final otp = _otpControllers.map((c) => c.text).join();
    if (otp.length != 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter all 6 digits')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final response = await SupabaseService().verifyOtp(
        phone: widget.phoneNumber,
        token: otp,
      );

      if (mounted) {
        if (response.session != null) {
          // Auth successful — navigate to onboarding
          context.go('/profile');
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Verification failed. Please try again.')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Invalid OTP: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _onChanged(String value, int index) {
    if (value.length == 1 && index < 5) {
      _focusNodes[index + 1].requestFocus();
    }
    if (value.isEmpty && index > 0) {
      _focusNodes[index - 1].requestFocus();
    }
    if (_otpControllers.every((c) => c.text.isNotEmpty) && !_isLoading) {
      _verifyOtp();
    }
  }

  @override
  void dispose() {
    for (var controller in _otpControllers) {
      controller.dispose();
    }
    for (var node in _focusNodes) {
      node.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return StarBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        resizeToAvoidBottomInset: false,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 28),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 24),
                // Back button
                IconButton(
                  icon: const Icon(Icons.arrow_back_rounded),
                  onPressed: () => context.pop(),
                  color: CosmicColors.textPrimary,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
                const SizedBox(height: 40),

                // Header
                Text(
                  'Enter verification\ncode',
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: CosmicColors.textPrimary,
                    height: 1.15,
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  'We sent a 6-digit code to\n${widget.phoneNumber}',
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 15,
                    color: CosmicColors.textMuted,
                    height: 1.5,
                  ),
                ),

                const SizedBox(height: 48),

                // OTP input fields
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: List.generate(
                    6,
                    (index) => SizedBox(
                      width: 48,
                      height: 56,
                      child: Container(
                        decoration: BoxDecoration(
                          color: CosmicColors.glass,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: _otpControllers[index].text.isNotEmpty
                                ? CosmicColors.textDim
                                : CosmicColors.glassBorder,
                            width: 1,
                          ),
                        ),
                        child: TextField(
                          controller: _otpControllers[index],
                          focusNode: _focusNodes[index],
                          keyboardType: TextInputType.number,
                          textAlign: TextAlign.center,
                          maxLength: 1,
                          style: GoogleFonts.spaceGrotesk(
                            color: CosmicColors.textPrimary,
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                          decoration: const InputDecoration(
                            counter: SizedBox.shrink(),
                            border: InputBorder.none,
                          ),
                          onChanged: (value) => _onChanged(value, index),
                        ),
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 32),

                // Resend timer
                Center(
                  child: _canResend
                      ? GestureDetector(
                          onTap: _resendOtp,
                          child: Text(
                            'Resend code',
                            style: GoogleFonts.spaceGrotesk(
                              fontSize: 14,
                              color: CosmicColors.accentPurple,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        )
                      : Text(
                          'Resend code in ${_resendTimer}s',
                          style: GoogleFonts.spaceGrotesk(
                            fontSize: 14,
                            color: CosmicColors.textMuted,
                          ),
                        ),
                ),

                const SizedBox(height: 40),

                // Verify button
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _verifyOtp,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black,
                      disabledBackgroundColor: Colors.white24,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.black,
                            ),
                          )
                        : Text(
                            'Verify',
                            style: GoogleFonts.spaceGrotesk(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
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
