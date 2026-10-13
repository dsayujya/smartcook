import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';

class RecipeDetailsScreen extends StatefulWidget {
  final Map<String, dynamic> recipe;
  final int matchPercentage;
  final List<dynamic> missingIngredients;
  final List<dynamic>? missingCoreIngredients;
  final List<dynamic>? usedIngredients;
  final bool assumePantryStaples;

  const RecipeDetailsScreen({
    super.key,
    required this.recipe,
    required this.matchPercentage,
    required this.missingIngredients,
    this.missingCoreIngredients,
    this.usedIngredients,
    this.assumePantryStaples = true,
  });

  @override
  State<RecipeDetailsScreen> createState() => _RecipeDetailsScreenState();
}

class _RecipeDetailsScreenState extends State<RecipeDetailsScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoadingTutorials = false;
  List<dynamic> _tutorials = [];
  bool _hasFetchedTutorials = false;

  Future<void> _fetchTutorials() async {
    setState(() {
      _isLoadingTutorials = true;
    });
    try {
      final ingredientsList = (widget.recipe['ingredients'] as List)
          .map((item) => item['ingredient']['name'].toString())
          .toList();
      final results = await _apiService.searchYouTube(widget.recipe['name'], ingredientsList);
      if (mounted) {
        setState(() {
          _tutorials = results;
          _hasFetchedTutorials = true;
          _isLoadingTutorials = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoadingTutorials = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load tutorials: $e')),
        );
      }
    }
  }

  Future<void> _launchUrl(String videoId) async {
    final url = Uri.parse('https://www.youtube.com/watch?v=$videoId');
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not open YouTube')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: (widget.recipe['image_url'] != null && widget.recipe['image_url'].toString().isNotEmpty) ? 280.0 : kToolbarHeight,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              titlePadding: const EdgeInsets.only(left: 16, bottom: 16, right: 16),
              title: Text(
                widget.recipe['name'] ?? 'Recipe Details',
                style: TextStyle(
                  color: (widget.recipe['image_url'] != null && widget.recipe['image_url'].toString().isNotEmpty)
                      ? Colors.white
                      : colorScheme.onSurface,
                  fontWeight: FontWeight.bold,
                  shadows: (widget.recipe['image_url'] != null && widget.recipe['image_url'].toString().isNotEmpty)
                      ? const [Shadow(color: Colors.black87, blurRadius: 8)]
                      : null,
                ),
              ),
              background: (widget.recipe['image_url'] != null && widget.recipe['image_url'].toString().isNotEmpty)
                  ? Image.network(
                      widget.recipe['image_url'],
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) => const SizedBox.shrink(),
                    )
                  : null,
            ),
          ),
          
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Badges Row
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                        decoration: BoxDecoration(
                          color: widget.matchPercentage >= 80 ? Colors.green.withOpacity(0.15) : colorScheme.tertiaryContainer,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '${widget.matchPercentage}% Match',
                          style: TextStyle(
                            color: widget.matchPercentage >= 80 ? Colors.green.shade800 : colorScheme.onTertiaryContainer,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                        decoration: BoxDecoration(
                          color: colorScheme.secondaryContainer,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.timer_outlined, size: 16, color: colorScheme.onSecondaryContainer),
                            const SizedBox(width: 4),
                            Text(
                              '${widget.recipe['cook_time'] ?? 30} min',
                              style: TextStyle(color: colorScheme.onSecondaryContainer, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  
                  // Categorized Ingredients Section
                  _buildCategorizedIngredients(context, colorScheme, textTheme),
                  
                  const SizedBox(height: 32),
                  
                  // Instructions Section
                  Text('Cooking Instructions', style: textTheme.titleLarge),
                  const SizedBox(height: 12),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(
                        widget.recipe['instructions'] ?? 'No instructions provided.',
                        style: textTheme.bodyLarge?.copyWith(height: 1.6),
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // YouTube Video Tutorials Section
                  Text('Video Tutorials', style: textTheme.titleLarge),
                  const SizedBox(height: 16),
                  
                  if (!_hasFetchedTutorials)
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: _isLoadingTutorials ? null : _fetchTutorials,
                        icon: _isLoadingTutorials 
                          ? SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: colorScheme.onPrimary, strokeWidth: 2))
                          : const Icon(Icons.play_arrow_rounded),
                        label: Text(_isLoadingTutorials ? 'Searching Tutorials...' : 'Watch Video Tutorials'),
                        style: FilledButton.styleFrom(
                          backgroundColor: Colors.red.shade700,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    )
                  else if (_tutorials.isEmpty)
                    const Text('No video tutorials found.')
                  else
                    Column(
                      children: _tutorials.map((video) {
                        return Card(
                          margin: const EdgeInsets.only(bottom: 12),
                          clipBehavior: Clip.antiAlias,
                          child: InkWell(
                            onTap: () => _launchUrl(video['video_id']),
                            child: Row(
                              children: [
                                SizedBox(
                                  width: 120,
                                  height: 80,
                                  child: Image.network(video['thumbnail'], fit: BoxFit.cover),
                                ),
                                Expanded(
                                  child: Padding(
                                    padding: const EdgeInsets.all(12.0),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          video['title'],
                                          maxLines: 2,
                                          overflow: TextOverflow.ellipsis,
                                          style: textTheme.titleMedium?.copyWith(fontSize: 14),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          video['channel'],
                                          style: textTheme.bodyMedium?.copyWith(fontSize: 12),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                                const Padding(
                                  padding: EdgeInsets.all(12.0),
                                  child: Icon(Icons.play_circle_fill_rounded, color: Colors.red, size: 32),
                                )
                              ],
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                    
                  const SizedBox(height: 40),
                ],
              ),
            ),
          )
        ],
      ),
    );
  }

  static const Set<String> _pantryKeywords = {
    'salt', 'oil', 'water', 'turmeric', 'haldi', 'chilli powder', 'pepper', 'cumin', 'jeera',
    'coriander powder', 'dhania powder', 'garam masala', 'mustard', 'rai', 'sarson',
    'asafoetida', 'hing', 'curry leaves', 'ginger', 'garlic', 'green chilli', 'lemon',
    'ghee', 'butter', 'sugar', 'jaggery', 'cloves', 'cinnamon', 'cardamom', 'bay leaf',
    'kasuri methi', 'amchur', 'chaat masala', 'baking', 'vinegar', 'oregano'
  };

  bool _isPantryItem(String name) {
    final lower = name.toLowerCase();
    return _pantryKeywords.any((k) => lower.contains(k));
  }

  Widget _buildCategorizedIngredients(BuildContext context, ColorScheme colorScheme, TextTheme textTheme) {
    final allIngredients = (widget.recipe['ingredients'] as List);
    final coreItems = widget.assumePantryStaples
        ? allIngredients.where((i) => !_isPantryItem(i['ingredient']['name'].toString())).toList()
        : allIngredients;
    final pantryItems = widget.assumePantryStaples
        ? allIngredients.where((i) => _isPantryItem(i['ingredient']['name'].toString())).toList()
        : [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Core / Main Ingredients Header
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Main Ingredients', style: textTheme.titleLarge),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '${coreItems.length} items',
                style: textTheme.labelSmall?.copyWith(fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        ...coreItems.map((item) {
          final ingredientName = item['ingredient']['name'].toString();
          final isMissing = widget.missingIngredients.contains(ingredientName.toLowerCase()) ||
              (widget.missingCoreIngredients != null &&
                  widget.missingCoreIngredients!.any((m) => m.toString().toLowerCase() == ingredientName.toLowerCase()));

          return _buildIngredientRow(
            item: item,
            name: ingredientName,
            isMissing: isMissing,
            isPantry: false,
            colorScheme: colorScheme,
            textTheme: textTheme,
          );
        }),

        if (pantryItems.isNotEmpty) ...[
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Pantry Staples & Spices', style: textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                  Text(
                    'Assumed available in kitchen',
                    style: textTheme.bodySmall?.copyWith(color: colorScheme.outline),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: colorScheme.primaryContainer.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${pantryItems.length} items',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: colorScheme.onPrimaryContainer,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          ...pantryItems.map((item) {
            final ingredientName = item['ingredient']['name'].toString();
            return _buildIngredientRow(
              item: item,
              name: ingredientName,
              isMissing: false,
              isPantry: true,
              colorScheme: colorScheme,
              textTheme: textTheme,
            );
          }),
        ],
      ],
    );
  }

  Widget _buildIngredientRow({
    required dynamic item,
    required String name,
    required bool isMissing,
    required bool isPantry,
    required ColorScheme colorScheme,
    required TextTheme textTheme,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        children: [
          Icon(
            isPantry
                ? Icons.kitchen_rounded
                : isMissing
                    ? Icons.cancel_outlined
                    : Icons.check_circle_rounded,
            color: isPantry
                ? colorScheme.primary
                : isMissing
                    ? colorScheme.error
                    : Colors.green.shade700,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              '${item['quantity'] ?? ''} ${item['unit'] ?? ''} ${name.toUpperCase()}',
              style: textTheme.bodyLarge?.copyWith(
                color: isMissing ? colorScheme.error : colorScheme.onSurface,
                fontWeight: isMissing ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ),
          if (isMissing)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: colorScheme.errorContainer,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                'MISSING',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onErrorContainer,
                ),
              ),
            )
          else if (isPantry)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                'PANTRY',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: colorScheme.outline,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

