import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService;
  static const String webClientId =
      '28959632040-oi3m6ho9mdbmue9t25d3590bjaorl2rb.apps.googleusercontent.com';
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    clientId: kIsWeb ? webClientId : null,
    serverClientId: webClientId,
    scopes: ['email', 'profile'],
  );

  bool _isLoading = false;
  bool _isInitialized = false;
  String? _token;
  Map<String, dynamic>? _currentUser;
  String? _errorMessage;

  String? _pendingOtpTarget;
  String? _pendingOtpType;
  String? _devOtpCode;

  AuthProvider(this._apiService) {
    _initAuth();
  }

  bool get isLoading => _isLoading;
  bool get isInitialized => _isInitialized;
  bool get isAuthenticated => _token != null && _currentUser != null;
  String? get token => _token;
  Map<String, dynamic>? get currentUser => _currentUser;
  String? get errorMessage => _errorMessage;
  String? get pendingOtpTarget => _pendingOtpTarget;
  String? get pendingOtpType => _pendingOtpType;
  String? get devOtpCode => _devOtpCode;

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  Future<void> _initAuth() async {
    _isLoading = true;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString('auth_token');
      if (_token != null) {
        _apiService.setAuthToken(_token);
        try {
          _currentUser = await _apiService.getProfile();
        } catch (e) {
          // Token expired or invalid
          await logout();
        }
      }
    } catch (e) {
      debugPrint('Auth initialization error: $e');
    } finally {
      _isLoading = false;
      _isInitialized = true;
      notifyListeners();
    }
  }

  Future<bool> register({
    required String email,
    String? password,
    String? fullName,
  }) async {
    _setLoading(true);
    _errorMessage = null;
    try {
      final res = await _apiService.register(
        email: email,
        password: password,
        fullName: fullName,
      );
      _token = res['access_token'];
      _currentUser = res['user'];
      await _saveToken(_token!);
      _pendingOtpTarget = email;
      _pendingOtpType = 'email_verification';
      _devOtpCode = res['dev_otp_code'];
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> login({required String email, required String password}) async {
    _setLoading(true);
    _errorMessage = null;
    try {
      final res = await _apiService.login(email: email, password: password);
      _token = res['access_token'];
      _currentUser = res['user'];
      await _saveToken(_token!);
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> requestOtp({
    required String target,
    String otpType = 'email_verification',
  }) async {
    _setLoading(true);
    _errorMessage = null;
    try {
      final res = await _apiService.requestOtp(
        target: target,
        otpType: otpType,
      );
      _pendingOtpTarget = target;
      _pendingOtpType = otpType;
      _devOtpCode = res['dev_otp_code'];
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> verifyOtp({
    required String target,
    required String otpCode,
    String otpType = 'email_verification',
  }) async {
    _setLoading(true);
    _errorMessage = null;
    try {
      final res = await _apiService.verifyOtp(
        target: target,
        otpCode: otpCode,
        otpType: otpType,
      );
      _token = res['access_token'];
      _currentUser = res['user'];
      await _saveToken(_token!);
      _pendingOtpTarget = null;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> signInWithGoogle() async {
    _setLoading(true);
    _errorMessage = null;
    try {
      final googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        // User canceled login
        _setLoading(false);
        return false;
      }

      final googleAuth = await googleUser.authentication;
      final idToken = googleAuth.idToken ?? googleAuth.accessToken;

      if (idToken == null) {
        throw Exception('Failed to obtain Google ID Token.');
      }

      final res = await _apiService.googleAuth(idToken: idToken);
      _token = res['access_token'];
      _currentUser = res['user'];
      await _saveToken(_token!);
      notifyListeners();
      return true;
    } catch (e) {
      final errStr = e.toString();
      if (errStr.contains('appClientId != null') ||
          errStr.contains('ClientID not set') ||
          errStr.contains('invalid_client')) {
        _errorMessage = 'Google OAuth Client ID is invalid or missing origin setup. Please ensure your Client ID and Authorized JavaScript Origins are set in Google Cloud Console.';
      } else {
        _errorMessage = errStr
            .replaceAll('Exception: ', '')
            .replaceAll('Assertion failed: ', '');
      }
      notifyListeners();
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> logout() async {
    _token = null;
    _currentUser = null;
    _pendingOtpTarget = null;
    _apiService.setAuthToken(null);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    try {
      await _googleSignIn.signOut();
    } catch (_) {}
    notifyListeners();
  }

  Future<void> _saveToken(String token) async {
    _apiService.setAuthToken(token);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}
