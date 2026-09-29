import 'dart:convert';
import 'dart:async';

import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:flutter/foundation.dart' show kIsWeb, debugPrint;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  String? _authToken;
  static const String _prefKey = 'custom_api_base_url';
  static String customBaseUrl = 'https://smartcook-api-y1sk.onrender.com';

  ApiService() {
    initBaseUrl();
  }

  void setAuthToken(String? token) {
    _authToken = token;
  }

  Future<void> initBaseUrl() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedUrl = prefs.getString(_prefKey);
      if (savedUrl != null && savedUrl.isNotEmpty) {
        customBaseUrl = savedUrl;
      }
    } catch (e) {
      debugPrint('Error loading saved base URL: $e');
    }
  }

  Future<void> setCustomBaseUrl(String newUrl) async {
    var formattedUrl = newUrl.trim();
    if (formattedUrl.endsWith('/')) {
      formattedUrl = formattedUrl.substring(0, formattedUrl.length - 1);
    }
    if (!formattedUrl.endsWith('/api') && !formattedUrl.contains('/api')) {
      formattedUrl = '$formattedUrl/api';
    }
    customBaseUrl = formattedUrl;
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_prefKey, customBaseUrl);
    } catch (e) {
      debugPrint('Error saving custom base URL: $e');
    }
  }

  static String get baseUrl {
    String url = customBaseUrl.trim();
    if (url.endsWith('/')) {
      url = url.substring(0, url.length - 1);
    }
    if (!url.endsWith('/api')) {
      url = '$url/api';
    }

    if (kIsWeb) {
      return customBaseUrl.contains('127.0.0.1') || customBaseUrl.contains('localhost')
          ? 'http://127.0.0.1:8000/api'
          : url;
    } else {
      return url;
    }
  }

  Map<String, String> get _headers {
    final headers = {'Content-Type': 'application/json'};
    if (_authToken != null && _authToken!.isNotEmpty) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    return headers;
  }

  String formatNetworkError(dynamic e) {
    final errStr = e.toString();
    if (errStr.contains('SocketException') ||
        errStr.contains('SocketConnection timed out') ||
        errStr.contains('errno = 110') ||
        errStr.contains('Connection timed out') ||
        errStr.contains('Failed host lookup') ||
        errStr.contains('Connection refused') ||
        errStr.contains('ClientException') ||
        errStr.contains('TimeoutException')) {
      return 'Connection timed out to server at "$baseUrl".\n\n'
          'Troubleshooting steps:\n'
          '• Check if uvicorn backend is running on host 0.0.0.0:8000\n'
          '• Ensure phone & PC are on the same Wi-Fi network\n'
          '• Tap "Server Settings" below to edit the server IP.';
    }
    return errStr.replaceAll('Exception: ', '');
  }

  Future<bool> testConnection({String? testUrl}) async {
    final target = testUrl ?? baseUrl;
    final rootTarget = target.replaceAll(RegExp(r'/api/?$'), '');
    try {
      final response = await http
          .get(Uri.parse('$rootTarget/'))
          .timeout(const Duration(seconds: 4));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // --- Auth APIs ---

  Future<Map<String, dynamic>> register({
    required String email,
    String? password,
    String? fullName,
  }) async {
    final uri = Uri.parse('$baseUrl/auth/register');
    try {
      final response = await http
          .post(
            uri,
            headers: _headers,
            body: jsonEncode({
              'email': email,
              'password': password,
              'full_name': fullName,
            }),
          )
          .timeout(const Duration(seconds: 45));
      return _parseResponse(response);
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }

  Future<Map<String, dynamic>> requestOtp({
    required String target,
    String otpType = 'email_verification',
  }) async {
    final uri = Uri.parse('$baseUrl/auth/request-otp');
    try {
      final response = await http
          .post(
            uri,
            headers: _headers,
            body: jsonEncode({'target': target, 'otp_type': otpType}),
          )
          .timeout(const Duration(seconds: 45));
      return _parseResponse(response);
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }

  Future<Map<String, dynamic>> verifyOtp({
    required String target,
    required String otpCode,
    String otpType = 'email_verification',
  }) async {
    final uri = Uri.parse('$baseUrl/auth/verify-otp');
    try {
      final response = await http
          .post(
            uri,
            headers: _headers,
            body: jsonEncode({
              'target': target,
              'otp_code': otpCode,
              'otp_type': otpType,
            }),
          )
          .timeout(const Duration(seconds: 45));
      return _parseResponse(response);
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final uri = Uri.parse('$baseUrl/auth/login');
    try {
      final response = await http
          .post(
            uri,
            headers: _headers,
            body: jsonEncode({'email': email, 'password': password}),
          )
          .timeout(const Duration(seconds: 45));
      return _parseResponse(response);
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }

  Future<Map<String, dynamic>> googleAuth({required String idToken}) async {
    final uri = Uri.parse('$baseUrl/auth/google');
    try {
      final response = await http
          .post(uri, headers: _headers, body: jsonEncode({'id_token': idToken}))
          .timeout(const Duration(seconds: 45));
      return _parseResponse(response);
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }

  Future<Map<String, dynamic>> getProfile() async {
    final uri = Uri.parse('$baseUrl/auth/me');
    try {
      final response = await http
          .get(uri, headers: _headers)
          .timeout(const Duration(seconds: 30));
      return _parseResponse(response);
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }

  Map<String, dynamic> _parseResponse(http.Response response) {
    final body = jsonDecode(response.body);
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return body is Map<String, dynamic> ? body : {'data': body};
    } else {
      final detail = body is Map && body.containsKey('detail')
          ? body['detail']
          : 'Request failed with status ${response.statusCode}';
      throw Exception(detail);
    }
  }

  // --- Recipes & Ingredients APIs ---

  Future<List<Map<String, dynamic>>> detectIngredients(XFile imageFile) async {
    final uri = Uri.parse('$baseUrl/ingredients/detect');
    var request = http.MultipartRequest('POST', uri);

    if (_authToken != null) {
      request.headers['Authorization'] = 'Bearer $_authToken';
    }

    if (kIsWeb) {
      final bytes = await imageFile.readAsBytes();
      request.files.add(
        http.MultipartFile.fromBytes('image', bytes, filename: imageFile.name),
      );
    } else {
      request.files.add(
        await http.MultipartFile.fromPath('image', imageFile.path),
      );
    }

    try {
      var response = await request.send().timeout(const Duration(seconds: 60));
      var responseData = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        final decoded = jsonDecode(responseData);
        final ingredientsList = decoded['ingredients'] as List;
        return List<Map<String, dynamic>>.from(ingredientsList);
      } else {
        throw Exception('Failed to detect ingredients: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }

  Future<List<String>> normalizeIngredients(List<String> rawIngredients) async {
    final uri = Uri.parse('$baseUrl/ingredients/normalize');
    try {
      final response = await http
          .post(uri, headers: _headers, body: jsonEncode(rawIngredients))
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        final normalized = decoded['normalized_ingredients'] as List;
        return List<String>.from(normalized);
      } else {
        throw Exception('Failed to normalize ingredients');
      }
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }

  Future<List<dynamic>> recommendRecipes(
    List<String> ingredients, {
    String? cuisine,
    String? mealType,
    int? maxCookTime,
  }) async {
    final queryParams = <String, String>{};
    if (cuisine != null && cuisine.isNotEmpty) {
      queryParams['cuisine'] = cuisine;
    }
    if (mealType != null && mealType.isNotEmpty) {
      queryParams['meal_type'] = mealType;
    }
    if (maxCookTime != null) {
      queryParams['max_cooking_time'] = maxCookTime.toString();
    }

    final uri = Uri.parse('$baseUrl/recipes/recommend')
        .replace(queryParameters: queryParams.isNotEmpty ? queryParams : null);

    try {
      final response = await http
          .post(uri, headers: _headers, body: jsonEncode(ingredients))
          .timeout(const Duration(seconds: 45));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load recipes: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }

  Future<Map<String, dynamic>> getRecipeDetails(int recipeId) async {
    final uri = Uri.parse('$baseUrl/recipes/$recipeId');
    try {
      final response = await http
          .get(uri, headers: _headers)
          .timeout(const Duration(seconds: 10));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load recipe details');
      }
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }

  Future<List<dynamic>> searchYouTube(
    String recipeName,
    List<String> ingredients,
  ) async {
    final queryParams = ['recipe_name=${Uri.encodeComponent(recipeName)}'];
    for (var ing in ingredients) {
      queryParams.add('ingredients=${Uri.encodeComponent(ing)}');
    }
    final uri = Uri.parse('$baseUrl/youtube/search?${queryParams.join('&')}');
    try {
      final response = await http
          .get(uri, headers: _headers)
          .timeout(const Duration(seconds: 10));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load YouTube tutorials');
      }
    } catch (e) {
      throw Exception(formatNetworkError(e));
    }
  }
}
