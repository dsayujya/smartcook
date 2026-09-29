import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_provider.dart';

class OtpVerificationScreen extends StatefulWidget {
  final String target;
  final String otpType;

  const OtpVerificationScreen({
    super.key,
    required this.target,
    this.otpType = 'email_verification',
  });

  @override
  State<OtpVerificationScreen> createState() => _OtpVerificationScreenState();
}

class _OtpVerificationScreenState extends State<OtpVerificationScreen> {
  final List<TextEditingController> _controllers = List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _focusNodes = List.generate(6, (_) => FocusNode());

  int _resendCountdown = 30;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  @override
  void dispose() {
    _timer?.cancel();
    for (var c in _controllers) {
      c.dispose();
    }
    for (var f in _focusNodes) {
      f.dispose();
    }
    super.dispose();
  }

  void _startTimer() {
    setState(() => _resendCountdown = 30);
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_resendCountdown > 0) {
        setState(() => _resendCountdown--);
      } else {
        timer.cancel();
      }
    });
  }

  String get _otpCode => _controllers.map((c) => c.text).join();

  void _verifyOtp() async {
    if (_otpCode.length < 6) return;
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final success = await auth.verifyOtp(
      target: widget.target,
      otpCode: _otpCode,
      otpType: widget.otpType,
    );

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Account verified successfully! Welcome to SmartCook.')),
      );
      Navigator.of(context).popUntil((route) => route.isFirst);
    }
  }

  void _resendCode() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final success = await auth.requestOtp(target: widget.target, otpType: widget.otpType);
    if (success && mounted) {
      _startTimer();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('A new verification code was sent to ${widget.target}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Verify Code'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Icon(
                Icons.mark_email_read_rounded,
                size: 64,
                color: colorScheme.primary,
              ),
              const SizedBox(height: 24),
              Text(
                'Enter 6-Digit Code',
                textAlign: TextAlign.center,
                style: textTheme.displayMedium,
              ),
              const SizedBox(height: 12),
              Text(
                'We sent a 6-digit verification code to:\n${widget.target}',
                textAlign: TextAlign.center,
                style: textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant),
              ),
              const SizedBox(height: 20),

              if (auth.devOtpCode != null) ...[
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: colorScheme.tertiaryContainer,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.developer_mode_rounded, color: colorScheme.onTertiaryContainer, size: 20),
                          const SizedBox(width: 8),
                          Text(
                            'Development Mode OTP: ',
                            style: TextStyle(
                              color: colorScheme.onTertiaryContainer,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            auth.devOtpCode!,
                            style: TextStyle(
                              color: colorScheme.onTertiaryContainer,
                              fontWeight: FontWeight.w900,
                              fontSize: 18,
                              letterSpacing: 2,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      TextButton.icon(
                        onPressed: () {
                          final code = auth.devOtpCode!;
                          for (int i = 0; i < 6 && i < code.length; i++) {
                            _controllers[i].text = code[i];
                          }
                          _verifyOtp();
                        },
                        icon: const Icon(Icons.touch_app_rounded, size: 18),
                        label: const Text('Auto-Fill Code & Continue'),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
              ] else
                const SizedBox(height: 16),

              // 6 PIN digit boxes
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: List.generate(
                  6,
                  (index) => SizedBox(
                    width: 46,
                    height: 58,
                    child: TextField(
                      controller: _controllers[index],
                      focusNode: _focusNodes[index],
                      keyboardType: TextInputType.number,
                      textAlign: TextAlign.center,
                      maxLength: 1,
                      style: textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                      decoration: InputDecoration(
                        counterText: '',
                        contentPadding: EdgeInsets.zero,
                        filled: true,
                        fillColor: colorScheme.surfaceContainerHighest,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide.none,
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: colorScheme.primary, width: 2),
                        ),
                      ),
                      onChanged: (value) {
                        if (value.isNotEmpty && index < 5) {
                          _focusNodes[index + 1].requestFocus();
                        } else if (value.isEmpty && index > 0) {
                          _focusNodes[index - 1].requestFocus();
                        }
                        if (_otpCode.length == 6) {
                          _verifyOtp();
                        }
                      },
                    ),
                  ),
                ),
              ),

              if (auth.errorMessage != null) ...[
                const SizedBox(height: 20),
                Text(
                  auth.errorMessage!,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: colorScheme.error, fontWeight: FontWeight.w600),
                ),
              ],

              const SizedBox(height: 36),

              FilledButton(
                onPressed: (auth.isLoading || _otpCode.length < 6) ? null : _verifyOtp,
                child: auth.isLoading
                    ? SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: colorScheme.onPrimary,
                        ),
                      )
                    : const Text('Verify & Continue'),
              ),

              const SizedBox(height: 24),

              // Resend Timer Row
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    "Didn't get the code? ",
                    style: textTheme.bodyMedium,
                  ),
                  if (_resendCountdown > 0)
                    Text(
                      'Resend in ${_resendCountdown}s',
                      style: textTheme.bodyMedium?.copyWith(
                        color: colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    )
                  else
                    GestureDetector(
                      onTap: auth.isLoading ? null : _resendCode,
                      child: Text(
                        'Resend OTP',
                        style: textTheme.bodyMedium?.copyWith(
                          color: colorScheme.primary,
                          fontWeight: FontWeight.bold,
                          decoration: TextDecoration.underline,
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
