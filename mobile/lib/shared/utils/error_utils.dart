import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';

/// Show a styled error snackbar.
void showErrorSnackbar(BuildContext context, String message) {
  if (!context.mounted) return;
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Row(
        children: [
          const Icon(Icons.error_outline, color: C.negative, size: 18),
          const SizedBox(width: S.sm),
          Expanded(
            child: Text(
              message,
              style: T.bodySm.copyWith(color: C.textPrimary),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
      backgroundColor: C.surface,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: R.mdBr),
      duration: const Duration(seconds: 4),
    ),
  );
}

/// Show a styled success snackbar.
void showSuccessSnackbar(BuildContext context, String message) {
  if (!context.mounted) return;
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Row(
        children: [
          const Icon(Icons.check_circle_outline, color: C.positive, size: 18),
          const SizedBox(width: S.sm),
          Expanded(
            child: Text(
              message,
              style: T.bodySm.copyWith(color: C.textPrimary),
            ),
          ),
        ],
      ),
      backgroundColor: C.surface,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: R.mdBr),
      duration: const Duration(seconds: 3),
    ),
  );
}
