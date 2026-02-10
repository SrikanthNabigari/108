import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';

/// Timeframe toggle: Hourly | Daily | Monthly | Yearly
///
/// Glassmorphic segmented control matching the 108 design language.
class ViewToggle extends StatelessWidget {
  final String selected;
  final ValueChanged<String> onChanged;

  static const _options = ['Hourly', 'Daily', 'Monthly', 'Yearly'];

  const ViewToggle({
    super.key,
    required this.selected,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(
        borderRadius: R.lgBr,
        color: C.glassBg,
        border: Border.all(color: C.glassBorder, width: 0.5),
      ),
      child: Row(
        children: _options.map((opt) {
          final isActive = opt.toLowerCase() == selected.toLowerCase();
          return Expanded(
            child: GestureDetector(
              onTap: () => onChanged(opt.toLowerCase()),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                curve: Curves.easeInOut,
                padding: const EdgeInsets.symmetric(vertical: 8),
                decoration: BoxDecoration(
                  borderRadius: R.mdBr,
                  color: isActive ? C.accentDim : Colors.transparent,
                  border: isActive
                      ? Border.all(color: C.glassBorder)
                      : null,
                ),
                alignment: Alignment.center,
                child: Text(
                  opt,
                  style: T.label.copyWith(
                    color: isActive ? C.accent : C.textMuted,
                    fontSize: 10,
                    letterSpacing: 1.0,
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
