import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/data/providers/user_provider.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  final _nameController = TextEditingController();
  String _gender = 'Male';
  bool _saving = false;
  bool _checking = true;

  @override
  void initState() {
    super.initState();
    _checkExisting();
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _checkExisting() async {
    try {
      final profile = await ref.read(userProfileProvider.future);
      if (!mounted) return;

      if (profile.onboardingComplete) {
        context.go('/home');
        return;
      }
      if (profile.hasProfile) {
        context.go('/birth-details');
        return;
      }

      // Pre-fill
      if (profile.name != null && profile.name!.isNotEmpty) {
        _nameController.text = profile.name!;
      }
      if (profile.gender != null && profile.gender!.isNotEmpty) {
        _gender =
            profile.gender![0].toUpperCase() + profile.gender!.substring(1);
      }
    } catch (_) {
      // First-time user — show form
    }
    if (mounted) setState(() => _checking = false);
  }

  Future<void> _continue() async {
    final name = _nameController.text.trim();
    if (name.isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Enter your name')));
      return;
    }

    setState(() => _saving = true);
    try {
      await ApiService().put(
        ApiConstants.userMe,
        body: {
          'name': name,
          'gender': _gender.toLowerCase(),
        },
        fromJson: (json) => json,
      );
      ref.invalidate(userProfileProvider);
      if (mounted) context.go('/birth-details');
    } catch (e) {
      if (mounted) {
        setState(() => _saving = false);
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('$e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_checking) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(color: C.accent, strokeWidth: 2),
        ),
      );
    }

    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: Padding(
            padding: S.pagePadding,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: S.xl),

                // Progress
                _ProgressBar(step: 1, total: 2),

                const SizedBox(height: S.xxxl),

                Text('What should\nwe call you?', style: T.h1),
                const SizedBox(height: S.sm),
                Text(
                  'Step 1 of 2',
                  style: T.bodySm.copyWith(color: C.textMuted),
                ),

                const SizedBox(height: S.xxxl),

                // Name
                GlassContainer(
                  padding: const EdgeInsets.symmetric(horizontal: S.lg),
                  child: TextField(
                    controller: _nameController,
                    style: T.body,
                    textCapitalization: TextCapitalization.words,
                    decoration: InputDecoration(
                      hintText: 'Your name',
                      hintStyle: T.body.copyWith(color: C.textMuted),
                      border: InputBorder.none,
                      contentPadding:
                          const EdgeInsets.symmetric(vertical: S.lg),
                    ),
                  ),
                ),

                const SizedBox(height: S.xxl),

                // Gender
                Text('GENDER', style: T.label),
                const SizedBox(height: S.md),
                Row(
                  children: ['Male', 'Female', 'Other']
                      .map((g) => Expanded(
                            child: Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 4),
                              child: _GenderChip(
                                label: g,
                                selected: _gender == g,
                                onTap: () => setState(() => _gender = g),
                              ),
                            ),
                          ))
                      .toList(),
                ),

                const Spacer(),

                // Continue
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _saving ? null : _continue,
                    child: _saving
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: C.textOnAccent),
                          )
                        : const Text('Continue'),
                  ),
                ),
                const SizedBox(height: S.xxl),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ── Shared widgets ──

class _ProgressBar extends StatelessWidget {
  final int step;
  final int total;
  const _ProgressBar({required this.step, required this.total});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(
        total,
        (i) => Expanded(
          child: Container(
            height: 3,
            margin: const EdgeInsets.symmetric(horizontal: 3),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(2),
              color: i < step ? C.accent : C.glassBorder,
            ),
          ),
        ),
      ),
    );
  }
}

class _GenderChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _GenderChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: S.md + 2),
        decoration: BoxDecoration(
          borderRadius: R.mdBr,
          color: selected ? C.accentDim : C.glassBg,
          border: Border.all(
            color: selected ? C.accent : C.glassBorder,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: T.bodySm.copyWith(
              color: selected ? C.accent : C.textSecondary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    );
  }
}
