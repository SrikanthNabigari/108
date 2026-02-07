import 'package:flutter/material.dart';
import 'dart:ui';

/// Glassmorphic card widget with blur backdrop and semi-transparent styling.
class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final VoidCallback? onTap;
  final BorderRadius borderRadius;
  final double blurAmount;
  final Color backgroundColor;
  final Border? border;

  const GlassCard({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.borderRadius = const BorderRadius.all(Radius.circular(16)),
    this.blurAmount = 10,
    this.backgroundColor = const Color(0x1aFFFFFF),
    this.border,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin ?? EdgeInsets.zero,
      decoration: BoxDecoration(
        borderRadius: borderRadius,
        border: border ??
            Border.all(
              color: Colors.white.withOpacity(0.2),
              width: 1,
            ),
      ),
      child: ClipRRect(
        borderRadius: borderRadius,
        child: BackdropFilter(
          filter: ImageFilter.blur(
            sigmaX: blurAmount,
            sigmaY: blurAmount,
          ),
          child: Container(
            decoration: BoxDecoration(
              color: backgroundColor,
              borderRadius: borderRadius,
            ),
            child: GestureDetector(
              onTap: onTap,
              child: Padding(
                padding: padding ?? const EdgeInsets.all(16),
                child: child,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
