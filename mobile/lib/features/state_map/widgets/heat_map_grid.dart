import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import '../models/state_vector.dart';

/// Interactive heat map grid — the core State Map visualization.
///
/// Rows = 7 prediction factors + 1 composite row.
/// Columns = time periods (hours / days / weeks / months).
/// Each cell is colored green→amber→red based on its 0-10 score.
/// Tapping a cell fires [onCellTap] with factor index and column index.
class HeatMapGrid extends StatefulWidget {
  final List<StateVector> vectors;
  final String resolution;
  final List<LifeEvent> events;
  final void Function(int factorIndex, int colIndex, StateVector vector)?
      onCellTap;

  const HeatMapGrid({
    super.key,
    required this.vectors,
    required this.resolution,
    this.events = const [],
    this.onCellTap,
  });

  @override
  State<HeatMapGrid> createState() => _HeatMapGridState();
}

class _HeatMapGridState extends State<HeatMapGrid> {
  // Layout constants
  static const double _labelWidth = 36;
  static const double _cellSize = 32;
  static const double _cellGap = 2;
  static const double _headerHeight = 28;
  static const int _compositeRow = 7; // row index for composite

  @override
  Widget build(BuildContext context) {
    if (widget.vectors.isEmpty) {
      return const SizedBox(
        height: 100,
        child: Center(
          child: Text('No data for this range',
              style: TextStyle(color: C.textMuted, fontSize: 13)),
        ),
      );
    }

    final colCount = widget.vectors.length;
    final rowCount = 8; // 7 factors + 1 composite
    final totalWidth = _labelWidth + colCount * (_cellSize + _cellGap);
    final totalHeight =
        _headerHeight + rowCount * (_cellSize + _cellGap) + 8;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          height: totalHeight,
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            physics: const BouncingScrollPhysics(),
            child: SizedBox(
              width: totalWidth,
              height: totalHeight,
              child: CustomPaint(
                painter: _HeatMapPainter(
                  vectors: widget.vectors,
                  resolution: widget.resolution,
                  events: widget.events,
                  labelWidth: _labelWidth,
                  cellSize: _cellSize,
                  cellGap: _cellGap,
                  headerHeight: _headerHeight,
                ),
                child: GestureDetector(
                  onTapUp: (details) => _handleTap(details.localPosition),
                ),
              ),
            ),
          ),
        ),
        // Legend
        const SizedBox(height: S.sm),
        _Legend(),
      ],
    );
  }

  void _handleTap(Offset pos) {
    final coords = _hitTest(pos);
    if (coords != null) {
      final (row, col) = coords;
      if (col >= 0 && col < widget.vectors.length && row >= 0 && row < 8) {
        widget.onCellTap?.call(row, col, widget.vectors[col]);
      }
    }
  }

  (int, int)? _hitTest(Offset pos) {
    final col =
        ((pos.dx - _labelWidth) / (_cellSize + _cellGap)).floor();
    final row =
        ((pos.dy - _headerHeight) / (_cellSize + _cellGap)).floor();
    if (col < 0 || row < 0 || col >= widget.vectors.length || row >= 8) {
      return null;
    }
    return (row, col);
  }
}

class _HeatMapPainter extends CustomPainter {
  final List<StateVector> vectors;
  final String resolution;
  final List<LifeEvent> events;
  final double labelWidth;
  final double cellSize;
  final double cellGap;
  final double headerHeight;

  _HeatMapPainter({
    required this.vectors,
    required this.resolution,
    required this.events,
    required this.labelWidth,
    required this.cellSize,
    required this.cellGap,
    required this.headerHeight,
  });

  static const _factorLabels = ['PAN', 'MON', 'GOC', 'DSH', 'YOG', 'SHD', 'ASH', 'AVG'];

  @override
  void paint(Canvas canvas, Size size) {
    final cellTotal = cellSize + cellGap;

    // ── Row labels (left side) ──
    final labelPainter = TextPainter(textDirection: TextDirection.ltr);
    for (var r = 0; r < _factorLabels.length; r++) {
      final y = headerHeight + r * cellTotal + cellSize / 2;
      final isComposite = r == 7;
      labelPainter.text = TextSpan(
        text: _factorLabels[r],
        style: TextStyle(
          color: isComposite ? C.accent : C.textMuted,
          fontSize: 8,
          fontWeight: isComposite ? FontWeight.w700 : FontWeight.w600,
          letterSpacing: 0.8,
        ),
      );
      labelPainter.layout();
      labelPainter.paint(
          canvas, Offset(labelWidth - labelPainter.width - 4, y - labelPainter.height / 2));
    }

    // ── Column headers (top) ──
    for (var c = 0; c < vectors.length; c++) {
      final x = labelWidth + c * cellTotal + cellSize / 2;
      final label = _columnLabel(vectors[c].date);
      // Only show every N labels to avoid crowding
      if (_shouldShowLabel(c, vectors.length)) {
        labelPainter.text = TextSpan(
          text: label,
          style: const TextStyle(
            color: C.textMuted,
            fontSize: 7,
            fontWeight: FontWeight.w500,
          ),
        );
        labelPainter.layout();
        labelPainter.paint(
            canvas, Offset(x - labelPainter.width / 2, headerHeight - labelPainter.height - 2));
      }
    }

    // ── Cells ──
    final cellPaint = Paint();
    final scorePainter = TextPainter(textDirection: TextDirection.ltr);

    for (var c = 0; c < vectors.length; c++) {
      final vec = vectors[c];
      for (var r = 0; r < 8; r++) {
        final score = r < 7
            ? (r < vec.factors.length ? vec.factors[r].score : 0.0)
            : vec.composite;

        final rect = Rect.fromLTWH(
          labelWidth + c * cellTotal,
          headerHeight + r * cellTotal,
          cellSize,
          cellSize,
        );

        // Cell fill
        cellPaint.color = _colorForScore(score);
        final rRect = RRect.fromRectAndRadius(rect, const Radius.circular(4));
        canvas.drawRRect(rRect, cellPaint);

        // Today marker
        if (_isToday(vec.date) && r == 0) {
          final dotPaint = Paint()..color = C.accent;
          canvas.drawCircle(
            Offset(rect.center.dx, headerHeight - 6),
            2,
            dotPaint,
          );
        }

        // Score text (only show if cell is big enough)
        if (cellSize >= 28) {
          scorePainter.text = TextSpan(
            text: score.toStringAsFixed(0),
            style: TextStyle(
              color: score >= 4
                  ? Colors.black.withValues(alpha: 0.7)
                  : Colors.white.withValues(alpha: 0.8),
              fontSize: 8,
              fontWeight: FontWeight.w600,
            ),
          );
          scorePainter.layout();
          scorePainter.paint(
            canvas,
            Offset(
              rect.center.dx - scorePainter.width / 2,
              rect.center.dy - scorePainter.height / 2,
            ),
          );
        }
      }
    }

    // ── Event markers (diamond pins at top) ──
    for (final event in events) {
      final colIdx = _findColumnForDate(event.date);
      if (colIdx != null) {
        final x = labelWidth + colIdx * cellTotal + cellSize / 2;
        final y = headerHeight - 2;
        final path = Path()
          ..moveTo(x, y - 5)
          ..lineTo(x + 3, y)
          ..lineTo(x, y + 5)
          ..lineTo(x - 3, y)
          ..close();
        canvas.drawPath(
          path,
          Paint()..color = _eventColor(event.type),
        );
      }
    }
  }

  int? _findColumnForDate(DateTime date) {
    for (var i = 0; i < vectors.length; i++) {
      if (vectors[i].date.year == date.year &&
          vectors[i].date.month == date.month &&
          vectors[i].date.day == date.day) {
        return i;
      }
    }
    return null;
  }

  Color _eventColor(String type) {
    switch (type) {
      case 'career':
        return C.jupiter;
      case 'relationship':
        return C.venus;
      case 'health':
        return C.sun;
      case 'finance':
        return C.mercury;
      case 'spiritual':
        return C.ketu;
      default:
        return C.accent;
    }
  }

  Color _colorForScore(double score) {
    // 0 = deep red, 5 = amber, 10 = vivid green
    if (score <= 0) return const Color(0xCC8B0000);
    if (score >= 10) return const Color(0xCC00C853);

    if (score < 5) {
      final t = score / 5;
      return Color.lerp(
        const Color(0xCC8B0000), // dark red
        const Color(0xCCFF8F00), // amber
        t,
      )!;
    } else {
      final t = (score - 5) / 5;
      return Color.lerp(
        const Color(0xCCFF8F00), // amber
        const Color(0xCC00C853), // green
        t,
      )!;
    }
  }

  String _columnLabel(DateTime dt) {
    switch (resolution) {
      case 'hourly':
        return '${dt.hour}h';
      case 'monthly':
        const m = [
          '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ];
        return m[dt.month];
      case 'yearly':
        return '${dt.year}';
      default: // daily
        return '${dt.day}';
    }
  }

  bool _shouldShowLabel(int index, int total) {
    if (total <= 15) return true;
    if (total <= 31) return index % 2 == 0;
    if (total <= 90) return index % 7 == 0;
    return index % 30 == 0;
  }

  bool _isToday(DateTime dt) {
    final now = DateTime.now();
    return dt.year == now.year &&
        dt.month == now.month &&
        dt.day == now.day;
  }

  @override
  bool shouldRepaint(covariant _HeatMapPainter old) => true;
}

/// Color legend strip.
class _Legend extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text('Tough', style: T.caption.copyWith(fontSize: 9)),
        const SizedBox(width: 4),
        Container(
          width: 120,
          height: 8,
          decoration: BoxDecoration(
            borderRadius: R.smBr,
            gradient: const LinearGradient(
              colors: [
                Color(0xFF8B0000),
                Color(0xFFFF8F00),
                Color(0xFF00C853),
              ],
            ),
          ),
        ),
        const SizedBox(width: 4),
        Text('Thriving', style: T.caption.copyWith(fontSize: 9)),
      ],
    );
  }
}
