import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/data/services/supabase_service.dart';

/// Custom exception for API errors
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic originalError;

  ApiException({
    required this.message,
    this.statusCode,
    this.originalError,
  });

  @override
  String toString() => 'ApiException: $message (status: $statusCode)';
}

/// HTTP client wrapper with auth token injection from Supabase session
class ApiService {
  static final ApiService _instance = ApiService._internal();

  final http.Client _client = http.Client();
  String? _manualToken;

  factory ApiService() {
    return _instance;
  }

  ApiService._internal();

  /// Set auth token manually (fallback)
  void setAuthToken(String token) {
    _manualToken = token;
  }

  /// Clear auth token
  void clearAuthToken() {
    _manualToken = null;
  }

  /// Get current auth token — prefers Supabase session, falls back to manual
  String? get _authToken {
    final supabaseToken = SupabaseService().accessToken;
    return supabaseToken ?? _manualToken;
  }

  /// Build headers with auth token
  Map<String, String> _buildHeaders({bool needsAuth = true}) {
    final headers = Map<String, String>.from(ApiConstants.defaultHeaders);
    if (needsAuth) {
      final token = _authToken;
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  /// GET request
  Future<T> get<T>(
    String path, {
    required T Function(dynamic) fromJson,
    bool needsAuth = true,
  }) async {
    try {
      final url = Uri.parse('${ApiConstants.baseUrl}$path');
      if (kDebugMode) {
        debugPrint('[API] GET $path');
      }
      final response = await _client.get(
        url,
        headers: _buildHeaders(needsAuth: needsAuth),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final json = jsonDecode(response.body);
        return fromJson(json);
      } else {
        if (kDebugMode) {
          debugPrint('[API] GET $path → ${response.statusCode}: ${response.body}');
        }
        throw ApiException(
          message: _extractErrorMessage(response),
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Network error: ${e.toString()}',
        originalError: e,
      );
    }
  }

  /// POST request
  Future<T> post<T>(
    String path, {
    required T Function(dynamic) fromJson,
    Map<String, dynamic>? body,
    bool needsAuth = true,
  }) async {
    try {
      final url = Uri.parse('${ApiConstants.baseUrl}$path');
      if (kDebugMode) {
        debugPrint('[API] POST $path');
      }
      final response = await _client.post(
        url,
        headers: _buildHeaders(needsAuth: needsAuth),
        body: body != null ? jsonEncode(body) : null,
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final json = jsonDecode(response.body);
        return fromJson(json);
      } else if (response.statusCode == 429) {
        throw ApiException(
          message: 'Rate limit exceeded',
          statusCode: response.statusCode,
        );
      } else {
        throw ApiException(
          message: _extractErrorMessage(response),
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Network error: ${e.toString()}',
        originalError: e,
      );
    }
  }

  /// PUT request
  Future<T> put<T>(
    String path, {
    required T Function(dynamic) fromJson,
    Map<String, dynamic>? body,
    bool needsAuth = true,
  }) async {
    try {
      final url = Uri.parse('${ApiConstants.baseUrl}$path');
      if (kDebugMode) {
        debugPrint('[API] PUT $path');
      }
      final response = await _client.put(
        url,
        headers: _buildHeaders(needsAuth: needsAuth),
        body: body != null ? jsonEncode(body) : null,
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final json = jsonDecode(response.body);
        return fromJson(json);
      } else {
        if (kDebugMode) {
          debugPrint('[API] PUT $path → ${response.statusCode}: ${response.body}');
        }
        throw ApiException(
          message: _extractErrorMessage(response),
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Network error: ${e.toString()}',
        originalError: e,
      );
    }
  }

  /// DELETE request
  Future<void> delete(
    String path, {
    bool needsAuth = true,
  }) async {
    try {
      final url = Uri.parse('${ApiConstants.baseUrl}$path');
      final response = await _client.delete(
        url,
        headers: _buildHeaders(needsAuth: needsAuth),
      );

      if (response.statusCode != 200 && response.statusCode != 204) {
        throw ApiException(
          message: _extractErrorMessage(response),
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Network error: ${e.toString()}',
        originalError: e,
      );
    }
  }

  /// Extract error message from response body
  String _extractErrorMessage(http.Response response) {
    try {
      final json = jsonDecode(response.body);
      return json['detail'] ?? json['message'] ?? 'Request failed';
    } catch (_) {
      return 'Request failed (${response.statusCode})';
    }
  }
}
