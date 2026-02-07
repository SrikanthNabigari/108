import 'package:flutter/material.dart';

/// South Indian chart grid widget showing 12 houses with planets.
class SouthIndianChart extends StatelessWidget {
  final Map<int, List<String>> housePlanets;
  final Map<String, String> planetSigns;
  final int ascendantHouse;

  const SouthIndianChart({
    Key? key,
    this.housePlanets = const {},
    this.planetSigns = const {},
    this.ascendantHouse = 1,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _SouthIndianChartPainter(
        housePlanets: housePlanets,
        planetSigns: planetSigns,
        ascendantHouse: ascendantHouse,
      ),
      size: const Size(300, 300),
    );
  }
}

class _SouthIndianChartPainter extends CustomPainter {
  final Map<int, List<String>> housePlanets;
  final Map<String, String> planetSigns;
  final int ascendantHouse;

  _SouthIndianChartPainter({
    required this.housePlanets,
    required this.planetSigns,
    required this.ascendantHouse,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final cellSize = size.width / 4;

    // Draw grid background
    final gridPaint = Paint()
      ..color = Colors.white.withOpacity(0.1)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    // South Indian layout: 4x4 grid with center merged
    for (int row = 0; row < 4; row++) {
      for (int col = 0; col < 4; col++) {
        final rect = Rect.fromLTWH(
          col * cellSize,
          row * cellSize,
          cellSize,
          cellSize,
        );
        canvas.drawRect(rect, gridPaint);
      }
    }

    // House numbers (South Indian order)
    const List<int> houseOrder = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1];
    int houseNum = 0;
    final housePaint = Paint()..style = PaintingStyle.fill;

    // Top row
    _drawHouse(canvas, 0, 0, houseOrder[0]);
    _drawHouse(canvas, 1, 0, houseOrder[1]);
    _drawHouse(canvas, 2, 0, houseOrder[2]);
    _drawHouse(canvas, 3, 0, houseOrder[3]);

    // Right column
    _drawHouse(canvas, 3, 1, houseOrder[4]);
    _drawHouse(canvas, 3, 2, houseOrder[5]);
    _drawHouse(canvas, 3, 3, houseOrder[6]);

    // Bottom row (right to left)
    _drawHouse(canvas, 2, 3, houseOrder[7]);
    _drawHouse(canvas, 1, 3, houseOrder[8]);
    _drawHouse(canvas, 0, 3, houseOrder[9]);

    // Left column (bottom to top)
    _drawHouse(canvas, 0, 2, houseOrder[10]);
    _drawHouse(canvas, 0, 1, houseOrder[11]);

    // Draw ascendant marker on house 1
    _drawAscendantMarker(canvas, 3, 1);
  }

  void _drawHouse(Canvas canvas, int col, int row, int houseNum) {
    final cellSize = 300 / 4;
    final x = col * cellSize;
    final y = row * cellSize;

    // House number text
    final textPainter = TextPainter(
      text: TextSpan(
        text: houseNum.toString(),
        style: const TextStyle(
          color: Colors.white54,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(x + 8, y + 8),
    );

    // Planets in house
    if (housePlanets[houseNum] != null) {
      int planetIdx = 0;
      for (final planet in housePlanets[houseNum]!) {
        final planetTextPainter = TextPainter(
          text: TextSpan(
            text: planet,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 10,
            ),
          ),
          textDirection: TextDirection.ltr,
        );
        planetTextPainter.layout();
        planetTextPainter.paint(
          canvas,
          Offset(x + 12, y + 28 + (planetIdx * 14)),
        );
        planetIdx++;
      }
    }
  }

  void _drawAscendantMarker(Canvas canvas, int col, int row) {
    final cellSize = 300 / 4;
    final x = col * cellSize + cellSize / 2;
    final y = row * cellSize + cellSize / 2;

    canvas.drawCircle(
      Offset(x, y),
      8,
      Paint()
        ..color = const Color(0xff6C63FF)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2,
    );
  }

  @override
  bool shouldRepaint(_SouthIndianChartPainter oldDelegate) => false;
}
