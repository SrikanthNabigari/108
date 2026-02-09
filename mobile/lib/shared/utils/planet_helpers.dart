import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';

/// Shared planet display helpers used across timeline, transits, and detail panels.

String planetGlyph(String planet) {
  const glyphs = {
    'sun': '\u2609', 'moon': '\u263D', 'mars': '\u2642', 'mercury': '\u263F',
    'jupiter': '\u2643', 'venus': '\u2640', 'saturn': '\u2644',
    'rahu': '\u260A', 'ketu': '\u260B',
  };
  return glyphs[planet.toLowerCase()] ?? '?';
}

String planetName(String planet) {
  if (planet.isEmpty) return '';
  return planet[0].toUpperCase() + planet.substring(1);
}

Color planetColor(String planet) {
  const colors = {
    'sun': C.sun, 'moon': C.moon, 'mars': C.mars, 'mercury': C.mercury,
    'jupiter': C.jupiter, 'venus': C.venus, 'saturn': C.saturn,
    'rahu': C.rahu, 'ketu': C.ketu,
  };
  return colors[planet.toLowerCase()] ?? C.accent;
}

const rashiNames = [
  'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
];

const rashiAbbrev = [
  'Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir',
  'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis',
];
