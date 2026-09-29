import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_provider.dart';
import '../widgets/server_config_dialog.dart';
import 'login_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final auth = Provider.of<AuthProvider>(context);
    final user = auth.currentUser;

    if (!auth.isAuthenticated || user == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Profile'),
          actions: [
            IconButton(
              icon: const Icon(Icons.settings_ethernet_rounded),
              tooltip: 'Server Settings',
              onPressed: () => ServerConfigDialog.show(context),
            ),
          ],
        ),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.account_circle_outlined, size: 80, color: colorScheme.primary),
                const SizedBox(height: 16),
                Text('Sign in to access your profile', style: textTheme.titleLarge),
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const LoginScreen()),
                    );
                  },
                  child: const Text('Sign In / Register'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final email = user['email'] ?? '';
    final fullName = user['full_name'] ?? user['username'] ?? 'Chef';
    final isEmailVerified = user['is_email_verified'] == true;
    final isPhoneVerified = user['is_phone_verified'] == true;
    final googleId = user['google_id'];
    final avatarUrl = user['avatar_url'];

    return Scaffold(
      appBar: AppBar(
        title: const Text('User Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_ethernet_rounded),
            tooltip: 'Server Settings',
            onPressed: () => ServerConfigDialog.show(context),
          ),
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            tooltip: 'Sign Out',
            onPressed: () async {
              await auth.logout();
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Avatar Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 36,
                      backgroundColor: colorScheme.primaryContainer,
                      backgroundImage: avatarUrl != null ? NetworkImage(avatarUrl) : null,
                      child: avatarUrl == null
                          ? Text(
                              fullName.isNotEmpty ? fullName[0].toUpperCase() : 'U',
                              style: textTheme.displayMedium?.copyWith(
                                color: colorScheme.onPrimaryContainer,
                              ),
                            )
                          : null,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(fullName, style: textTheme.titleLarge),
                          const SizedBox(height: 4),
                          Text(email, style: textTheme.bodyMedium),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Account Verification Status Section
            Text('Account Security & Verification', style: textTheme.titleMedium),
            const SizedBox(height: 12),

            Card(
              child: Column(
                children: [
                  ListTile(
                    leading: Icon(
                      isEmailVerified ? Icons.verified_user_rounded : Icons.mark_email_unread_rounded,
                      color: isEmailVerified ? Colors.green : Colors.amber.shade800,
                    ),
                    title: const Text('Email Verification'),
                    subtitle: Text(email),
                    trailing: Chip(
                      label: Text(isEmailVerified ? 'Verified' : 'Pending'),
                      backgroundColor: isEmailVerified ? Colors.green.withOpacity(0.15) : Colors.amber.withOpacity(0.15),
                      labelStyle: TextStyle(
                        color: isEmailVerified ? Colors.green.shade800 : Colors.amber.shade900,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const Divider(height: 1, indent: 16, endIndent: 16),
                  ListTile(
                    leading: Icon(
                      isPhoneVerified ? Icons.phone_android_rounded : Icons.phone_missed_rounded,
                      color: isPhoneVerified ? Colors.green : colorScheme.outline,
                    ),
                    title: const Text('Mobile Verification'),
                    subtitle: Text(user['phone_number'] ?? 'Not linked'),
                    trailing: Chip(
                      label: Text(isPhoneVerified ? 'Verified' : 'Unlinked'),
                      backgroundColor: isPhoneVerified ? Colors.green.withOpacity(0.15) : colorScheme.surfaceContainerHighest,
                    ),
                  ),
                  const Divider(height: 1, indent: 16, endIndent: 16),
                  ListTile(
                    leading: const Icon(Icons.g_mobiledata_rounded, size: 28, color: Colors.blue),
                    title: const Text('Google Sign-In'),
                    subtitle: Text(googleId != null ? 'Account Linked' : 'Not linked'),
                    trailing: Chip(
                      label: Text(googleId != null ? 'Linked' : 'Optional'),
                      backgroundColor: googleId != null ? Colors.blue.withOpacity(0.15) : colorScheme.surfaceContainerHighest,
                    ),
                  ),
                  const Divider(height: 1, indent: 16, endIndent: 16),
                  ListTile(
                    leading: Icon(Icons.dns_rounded, color: colorScheme.primary),
                    title: const Text('Backend Server Settings'),
                    subtitle: const Text('Configure PC IP address & connection'),
                    trailing: const Icon(Icons.chevron_right_rounded),
                    onTap: () => ServerConfigDialog.show(context),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Sign Out Button
            OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                foregroundColor: colorScheme.error,
                side: BorderSide(color: colorScheme.error),
                minimumSize: const Size.fromHeight(50),
              ),
              onPressed: () async {
                await auth.logout();
              },
              icon: const Icon(Icons.logout_rounded),
              label: const Text('Sign Out'),
            ),
          ],
        ),
      ),
    );
  }
}
