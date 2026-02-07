import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/colors.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../data/services/supabase_service.dart';

class PhoneAuthScreen extends ConsumerStatefulWidget {
  const PhoneAuthScreen({super.key});

  @override
  ConsumerState<PhoneAuthScreen> createState() => _PhoneAuthScreenState();
}

class _PhoneAuthScreenState extends ConsumerState<PhoneAuthScreen> {
  final _phoneController = TextEditingController();
  String _countryCode = '+91';
  bool _isLoading = false;

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    if (_phoneController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter your phone number')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final phoneNumber = '$_countryCode${_phoneController.text}';
      await SupabaseService().signInWithPhone(phoneNumber);
      if (mounted) {
        context.push('/otp-verify', extra: phoneNumber);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error sending OTP: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
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
                const SizedBox(height: 80),

                // Header
                Text(
                  'Enter your\nphone number',
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: CosmicColors.textPrimary,
                    height: 1.15,
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  "We'll use this to identify you and keep\nyour chart secure.",
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 15,
                    color: CosmicColors.textMuted,
                    height: 1.5,
                  ),
                ),

                const SizedBox(height: 48),

                // Phone input row
                Container(
                  height: 56,
                  decoration: BoxDecoration(
                    color: CosmicColors.glass,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: CosmicColors.glassBorder,
                      width: 1,
                    ),
                  ),
                  child: Row(
                    children: [
                      // Country code
                      GestureDetector(
                        onTap: () {
                          // TODO: Country picker
                        },
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                _countryCode,
                                style: GoogleFonts.spaceGrotesk(
                                  fontSize: 16,
                                  color: CosmicColors.textPrimary,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              const SizedBox(width: 4),
                              Icon(
                                Icons.keyboard_arrow_down_rounded,
                                color: CosmicColors.textMuted,
                                size: 18,
                              ),
                            ],
                          ),
                        ),
                      ),
                      Container(
                        width: 1,
                        height: 24,
                        color: CosmicColors.glassBorder,
                      ),
                      // Phone field
                      Expanded(
                        child: TextField(
                          controller: _phoneController,
                          keyboardType: TextInputType.phone,
                          style: GoogleFonts.spaceGrotesk(
                            fontSize: 16,
                            color: CosmicColors.textPrimary,
                          ),
                          decoration: InputDecoration(
                            hintText: 'Phone number',
                            hintStyle: GoogleFonts.spaceGrotesk(
                              fontSize: 16,
                              color: CosmicColors.textSubtle,
                            ),
                            border: InputBorder.none,
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 16,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                // Send OTP button — white on black
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _sendOtp,
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
                            'Send OTP',
                            style: GoogleFonts.spaceGrotesk(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                  ),
                ),

                const SizedBox(height: 20),

                // Skip for now → dev bypass to onboarding
                Center(
                  child: TextButton(
                    onPressed: () {
                      context.go('/profile');
                    },
                    child: Text(
                      'Skip for now',
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 14,
                        color: CosmicColors.textMuted,
                      ),
                    ),
                  ),
                ),

                const Spacer(),

                // Privacy note
                Padding(
                  padding: const EdgeInsets.only(bottom: 32),
                  child: Center(
                    child: Text(
                      'Your phone number is only used for account verification\nand will never be shared.',
                      textAlign: TextAlign.center,
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 12,
                        color: CosmicColors.textSubtle,
                        height: 1.5,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
