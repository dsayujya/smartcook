import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_provider.dart';
import 'camera_screen.dart';
import 'ingredient_confirmation_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final auth = Provider.of<AuthProvider>(context);
    final user = auth.currentUser;
    final fullName = user?['full_name'] ?? user?['username'] ?? 'Chef';
    final avatarUrl = user?['avatar_url'];

    final List<Widget> pages = [
      _buildHomeExploreView(context, colorScheme, textTheme, fullName, avatarUrl),
      const CameraScreen(),
      const ProfileScreen(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: pages,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() => _currentIndex = index);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.explore_outlined),
            selectedIcon: Icon(Icons.explore_rounded),
            label: 'Explore',
          ),
          NavigationDestination(
            icon: Icon(Icons.camera_alt_outlined),
            selectedIcon: Icon(Icons.camera_alt_rounded),
            label: 'Scan AI',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline_rounded),
            selectedIcon: Icon(Icons.person_rounded),
            label: 'Profile',
          ),
        ],
      ),
    );
  }

  Widget _buildHomeExploreView(
    BuildContext context,
    ColorScheme colorScheme,
    TextTheme textTheme,
    String fullName,
    String? avatarUrl,
  ) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top App Greeting Row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Hello, $fullName! 👨‍🍳',
                        style: textTheme.titleMedium?.copyWith(
                          color: colorScheme.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'What ingredients do\nyou have today?',
                        style: textTheme.displayMedium?.copyWith(height: 1.2),
                      ),
                    ],
                  ),
                ),
                GestureDetector(
                  onTap: () {
                    setState(() => _currentIndex = 2); // Navigate to Profile
                  },
                  child: CircleAvatar(
                    radius: 26,
                    backgroundColor: colorScheme.primaryContainer,
                    backgroundImage: avatarUrl != null ? NetworkImage(avatarUrl) : null,
                    child: avatarUrl == null
                        ? Text(
                            fullName.isNotEmpty ? fullName[0].toUpperCase() : 'U',
                            style: TextStyle(
                              color: colorScheme.onPrimaryContainer,
                              fontWeight: FontWeight.bold,
                              fontSize: 18,
                            ),
                          )
                        : null,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 32),

            // Main AI Scan Card (Material 3 Tonal Card)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(28),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    colorScheme.primaryContainer,
                    colorScheme.surfaceContainerHighest,
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(28),
                boxShadow: [
                  BoxShadow(
                    color: colorScheme.primary.withOpacity(0.08),
                    blurRadius: 16,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: colorScheme.primary,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.camera_rounded,
                      color: colorScheme.onPrimary,
                      size: 40,
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    'Scan Fridge Ingredients',
                    style: textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: colorScheme.onSurface,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Snap a photo of your fridge or counter. SmartCook AI detects ingredients automatically.',
                    textAlign: TextAlign.center,
                    style: textTheme.bodyMedium?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 24),
                  FilledButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const CameraScreen()),
                      );
                    },
                    icon: const Icon(Icons.photo_camera_rounded),
                    label: const Text('Open AI Camera'),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Secondary Action: Add Ingredients Manually
            Card(
              child: ListTile(
                contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                leading: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: colorScheme.secondaryContainer,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(Icons.edit_note_rounded, color: colorScheme.onSecondaryContainer),
                ),
                title: Text(
                  'Add Manually',
                  style: textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
                subtitle: const Text('Type out your available ingredients'),
                trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 18),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const IngredientConfirmationScreen(
                        detectedIngredients: [],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
