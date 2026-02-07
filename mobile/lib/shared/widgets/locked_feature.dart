import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'dart:ui';
import 'glass_card.dart';

/// Lock overlay for gated/premium features.
class LockedFeature extends StatelessWidget {
  final Widget child;
  final bool isLocked;
  final String requiredTier;

  const LockedFeature({
    Key? key,
    required this.child,
    this.isLocked = false,
    this.requiredTier = 'Pro',
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (!isLocked) return child;

    return Stack(
      children: [
        Opacity(
          opacity: 0.4,
          child: child,
        ),
        GestureDetector(
          onTap: () => context.push('/paywall'),
          child: Container(
            color: Colors.black.withOpacity(0.4),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 4, sigmaY: 4),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xff6C63FF).withOpacity(0.2),
                      ),
                      child: const Icon(
                        Icons.lock_rounded,
                        color: Color(0xff6C63FF),
                        size: 32,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Unlock with $requiredTier',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: Colors.white,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Upgrade your subscription',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.white70,
                          ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
