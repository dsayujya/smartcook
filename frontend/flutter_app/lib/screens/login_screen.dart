import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/auth_provider.dart';
import '../widgets/server_config_dialog.dart';
import 'register_screen.dart';
import 'otp_verification_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _otpTargetController = TextEditingController();

  bool _useOtpLogin = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _otpTargetController.dispose();
    super.dispose();
  }

  void _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;
    final auth = Provider.of<AuthProvider>(context, listen: false);

    if (_useOtpLogin) {
      final target = _otpTargetController.text.trim();
      final success = await auth.requestOtp(target: target, otpType: 'login');
      if (success && mounted) {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => OtpVerificationScreen(
              target: target,
              otpType: 'login',
            ),
          ),
        );
      }
    } else {
      final success = await auth.login(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );
      if (!success && auth.errorMessage != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(auth.errorMessage!),
            backgroundColor: Theme.of(context).colorScheme.error,
            action: SnackBarAction(
              label: 'Settings',
              textColor: Colors.white,
              onPressed: () => ServerConfigDialog.show(context),
            ),
          ),
        );
      }
    }
  }

  void _handleGoogleSignIn() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final success = await auth.signInWithGoogle();
    if (!success && auth.errorMessage != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(auth.errorMessage!),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
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
        elevation: 0,
        backgroundColor: Colors.transparent,
        actions: [
          IconButton(
            icon: const Icon(Icons.dns_rounded),
            tooltip: 'Server Settings',
            onPressed: () => ServerConfigDialog.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Prominent Server IP Badge
                  InkWell(
                    onTap: () => ServerConfigDialog.show(context),
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: colorScheme.outlineVariant),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.dns_rounded, size: 16, color: colorScheme.primary),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Server: ${ApiService.baseUrl}',
                              style: textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w600),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          Text(
                            'Change IP',
                            style: textTheme.labelSmall?.copyWith(
                              color: colorScheme.primary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // App Brand Icon
                  Center(
                    child: Container(
                      width: 72,
                      height: 72,
                      decoration: BoxDecoration(
                        color: colorScheme.primaryContainer,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.soup_kitchen_rounded,
                        size: 40,
                        color: colorScheme.onPrimaryContainer,
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  Text(
                    'SmartCook',
                    textAlign: TextAlign.center,
                    style: textTheme.displayLarge?.copyWith(
                      color: colorScheme.primary,
                      fontSize: 32,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'AI Kitchen Assistant',
                    textAlign: TextAlign.center,
                    style: textTheme.bodyMedium?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 28),

                  // Mode Toggle Segmented Switch
                  SegmentedButton<bool>(
                    segments: const [
                      ButtonSegment(
                        value: false,
                        label: Text('Password Sign In'),
                        icon: Icon(Icons.lock_outline),
                      ),
                      ButtonSegment(
                        value: true,
                        label: Text('Email OTP'),
                        icon: Icon(Icons.mark_email_read_outlined),
                      ),
                    ],
                    selected: {_useOtpLogin},
                    onSelectionChanged: (Set<bool> selected) {
                      setState(() {
                        _useOtpLogin = selected.first;
                        auth.clearError();
                      });
                    },
                  ),
                  const SizedBox(height: 24),

                  if (!_useOtpLogin) ...[
                    // Email Field
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email Address',
                        prefixIcon: Icon(Icons.alternate_email_rounded),
                        hintText: 'user@example.com',
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Please enter your email';
                        }
                        if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value.trim())) {
                          return 'Please enter a valid email address';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),

                    // Password Field
                    TextFormField(
                      controller: _passwordController,
                      obscureText: _obscurePassword,
                      decoration: InputDecoration(
                        labelText: 'Password',
                        prefixIcon: const Icon(Icons.lock_outline_rounded),
                        suffixIcon: IconButton(
                          icon: Icon(_obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                          onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your password';
                        }
                        return null;
                      },
                    ),
                  ] else ...[
                    // Target Field (Email Only)
                    TextFormField(
                      controller: _otpTargetController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email Address for OTP',
                        prefixIcon: Icon(Icons.mark_email_read_outlined),
                        hintText: 'user@example.com',
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Please enter your email address';
                        }
                        if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value.trim())) {
                          return 'Please enter a valid email address';
                        }
                        return null;
                      },
                    ),
                  ],

                  if (auth.errorMessage != null) ...[
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: colorScheme.errorContainer,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.error_outline_rounded, color: colorScheme.onErrorContainer),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  auth.errorMessage!,
                                  style: TextStyle(color: colorScheme.onErrorContainer, fontSize: 13),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Align(
                            alignment: Alignment.centerRight,
                            child: TextButton.icon(
                              style: TextButton.styleFrom(
                                foregroundColor: colorScheme.onErrorContainer,
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              ),
                              icon: const Icon(Icons.settings_rounded, size: 16),
                              label: const Text('Change Server IP / Settings'),
                              onPressed: () => ServerConfigDialog.show(context),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],

                  const SizedBox(height: 24),

                  // Main Submit Button
                  FilledButton(
                    onPressed: auth.isLoading ? null : _handleLogin,
                    child: auth.isLoading
                        ? SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              color: colorScheme.onPrimary,
                            ),
                          )
                        : Text(_useOtpLogin ? 'Send OTP Code' : 'Sign In'),
                  ),

                  const SizedBox(height: 20),

                  // Divider
                  Row(
                    children: [
                      Expanded(child: Divider(color: colorScheme.outlineVariant)),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Text(
                          'OR',
                          style: textTheme.bodyMedium?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      Expanded(child: Divider(color: colorScheme.outlineVariant)),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Google OAuth Button
                  OutlinedButton.icon(
                    onPressed: auth.isLoading ? null : _handleGoogleSignIn,
                    icon: Image.network(
                      'https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg',
                      height: 20,
                      width: 20,
                      errorBuilder: (context, error, stackTrace) => const Icon(Icons.g_mobiledata_rounded, size: 24),
                    ),
                    label: const Text('Continue with Google'),
                  ),

                  const SizedBox(height: 28),

                  // Link to Register
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        "Don't have an account? ",
                        style: textTheme.bodyMedium,
                      ),
                      GestureDetector(
                        onTap: () {
                          auth.clearError();
                          Navigator.of(context).push(
                            MaterialPageRoute(builder: (_) => const RegisterScreen()),
                          );
                        },
                        child: Text(
                          'Sign Up',
                          style: textTheme.bodyMedium?.copyWith(
                            color: colorScheme.primary,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
