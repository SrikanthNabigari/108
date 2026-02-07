import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/colors.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../data/services/api_service.dart';
import '../../../core/constants/api_constants.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  final _nameController = TextEditingController();
  String _selectedGender = 'Male';
  bool _isLoading = false;

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _continue() async {
    if (_nameController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter your name')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      // Save profile to gateway
      await ApiService().put(
        ApiConstants.userMe,
        body: {
          'name': _nameController.text.trim(),
          'gender': _selectedGender.toLowerCase(),
        },
        fromJson: (json) => json,
      );
    } catch (e) {
      // Gateway might not be running — continue anyway for dev
      debugPrint('Profile save failed (continuing): $e');
    }

    if (mounted) {
      setState(() => _isLoading = false);
      context.push('/birth-details');
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
                const SizedBox(height: 24),

                // Progress indicator
                Row(
                  children: List.generate(
                    2,
                    (index) => Expanded(
                      child: Container(
                        height: 3,
                        margin: const EdgeInsets.symmetric(horizontal: 3),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(2),
                          color: index == 0
                              ? CosmicColors.accentPurple
                              : CosmicColors.glassBorder,
                        ),
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 48),

                // Header
                Text(
                  'Tell us about\nyourself',
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: CosmicColors.textPrimary,
                    height: 1.15,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Step 1 of 2',
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 14,
                    color: CosmicColors.textMuted,
                  ),
                ),

                const SizedBox(height: 40),

                // Name input
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
                  child: TextField(
                    controller: _nameController,
                    style: GoogleFonts.spaceGrotesk(
                      fontSize: 16,
                      color: CosmicColors.textPrimary,
                    ),
                    decoration: InputDecoration(
                      hintText: 'Your name',
                      hintStyle: GoogleFonts.spaceGrotesk(
                        fontSize: 16,
                        color: CosmicColors.textSubtle,
                      ),
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 16,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 32),

                // Gender selection
                Text(
                  'Gender',
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 13,
                    color: CosmicColors.textMuted,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: ['Male', 'Female', 'Other']
                      .map(
                        (gender) => Expanded(
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 4),
                            child: GestureDetector(
                              onTap: () =>
                                  setState(() => _selectedGender = gender),
                              child: Container(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 14),
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(12),
                                  color: _selectedGender == gender
                                      ? CosmicColors.accentPurple
                                      : CosmicColors.glass,
                                  border: Border.all(
                                    color: _selectedGender == gender
                                        ? CosmicColors.accentPurple
                                        : CosmicColors.glassBorder,
                                  ),
                                ),
                                child: Center(
                                  child: Text(
                                    gender,
                                    style: GoogleFonts.spaceGrotesk(
                                      color: _selectedGender == gender
                                          ? Colors.white
                                          : CosmicColors.textDim,
                                      fontWeight: FontWeight.w600,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                      )
                      .toList(),
                ),

                const Spacer(),

                // Continue button
                Padding(
                  padding: const EdgeInsets.only(bottom: 32),
                  child: SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _continue,
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
                              'Continue',
                              style: GoogleFonts.spaceGrotesk(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
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
