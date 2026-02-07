import 'package:flutter/material.dart';

/// Messages remaining badge showing usage and warning state.
class RemainingCounter extends StatelessWidget {
  final int remaining;
  final int total;

  const RemainingCounter({
    Key? key,
    required this.remaining,
    required this.total,
  }) : super(key: key);

  Color _getColor() {
    final percentage = remaining / total;
    if (percentage <= 0.1) return const Color(0xFFE74C3C); // Red
    if (percentage <= 0.3) return const Color(0xFFF39C12); // Orange
    return Colors.white70;
  }

  bool _showWarning() => remaining <= 3;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        color: _getColor().withOpacity(0.2),
        border: Border.all(
          color: _getColor().withOpacity(0.5),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (_showWarning())
            Padding(
              padding: const EdgeInsets.only(right: 6),
              child: Icon(
                Icons.warning_rounded,
                size: 14,
                color: const Color(0xFFF39C12),
              ),
            ),
          Text(
            '$remaining/$total',
            style: TextStyle(
              color: _getColor(),
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
