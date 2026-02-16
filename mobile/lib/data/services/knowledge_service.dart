import 'dart:convert';
import 'package:flutter/services.dart';

/// Singleton service for loading bundled Jyotish knowledge JSON files.
///
/// Loads planets, rashis, nakshatras, and houses definitions from
/// bundled assets with in-memory caching.
class KnowledgeService {
  KnowledgeService._();
  static final instance = KnowledgeService._();

  Map<String, Map<String, dynamic>>? _planetsCache;
  Map<String, Map<String, dynamic>>? _rashisCache;
  Map<String, Map<String, dynamic>>? _nakshatrasCache;
  Map<String, Map<String, dynamic>>? _housesCache;

  /// Load and parse a JSON asset file.
  Future<Map<String, dynamic>> _loadJson(String filename) async {
    final raw = await rootBundle.loadString('assets/knowledge/$filename');
    return json.decode(raw) as Map<String, dynamic>;
  }

  // ── Planets ──

  Future<void> _ensurePlanets() async {
    if (_planetsCache != null) return;
    final data = await _loadJson('planets.json');
    final planetsMap = data['planets'] as Map<String, dynamic>;
    _planetsCache = planetsMap.map(
      (key, value) => MapEntry(key, value as Map<String, dynamic>),
    );
  }

  Future<Map<String, dynamic>?> getPlanet(String id) async {
    await _ensurePlanets();
    return _planetsCache![id.toLowerCase()];
  }

  Future<List<Map<String, dynamic>>> getAllPlanets() async {
    await _ensurePlanets();
    return _planetsCache!.values.toList();
  }

  // ── Rashis ──

  Future<void> _ensureRashis() async {
    if (_rashisCache != null) return;
    final data = await _loadJson('rashis.json');
    final rashisMap = data['rashis'] as Map<String, dynamic>;
    _rashisCache = rashisMap.map(
      (key, value) => MapEntry(key, value as Map<String, dynamic>),
    );
  }

  Future<Map<String, dynamic>?> getRashi(String id) async {
    await _ensureRashis();
    return _rashisCache![id.toLowerCase()];
  }

  Future<List<Map<String, dynamic>>> getAllRashis() async {
    await _ensureRashis();
    return _rashisCache!.values.toList();
  }

  // ── Nakshatras ──

  Future<void> _ensureNakshatras() async {
    if (_nakshatrasCache != null) return;
    final data = await _loadJson('nakshatras.json');
    final nakshatrasList = data['nakshatras'] as List;
    _nakshatrasCache = {
      for (final n in nakshatrasList)
        (n as Map<String, dynamic>)['id'] as String: n,
    };
  }

  Future<Map<String, dynamic>?> getNakshatra(String id) async {
    await _ensureNakshatras();
    return _nakshatrasCache![id.toLowerCase()];
  }

  Future<List<Map<String, dynamic>>> getAllNakshatras() async {
    await _ensureNakshatras();
    // Return sorted by number
    final list = _nakshatrasCache!.values.toList();
    list.sort((a, b) =>
        (a['number'] as int? ?? 0).compareTo(b['number'] as int? ?? 0));
    return list;
  }

  // ── Houses ──

  Future<void> _ensureHouses() async {
    if (_housesCache != null) return;
    final data = await _loadJson('houses.json');
    final housesMap = data['houses'] as Map<String, dynamic>;
    _housesCache = housesMap.map(
      (key, value) => MapEntry(key, value as Map<String, dynamic>),
    );
  }

  Future<Map<String, dynamic>?> getHouse(int number) async {
    await _ensureHouses();
    return _housesCache!['$number'];
  }

  Future<List<Map<String, dynamic>>> getAllHouses() async {
    await _ensureHouses();
    final list = _housesCache!.values.toList();
    list.sort((a, b) =>
        (a['number'] as int? ?? 0).compareTo(b['number'] as int? ?? 0));
    return list;
  }
}
