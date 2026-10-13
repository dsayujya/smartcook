import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'recipe_details_screen.dart';

class RecommendationScreen extends StatefulWidget {
  final List<String> ingredients;
  final String? cuisine;
  final String? mealType;
  final int? maxCookTime;
  final bool assumePantryStaples;
  final String rankingMode;

  const RecommendationScreen({
    super.key,
    required this.ingredients,
    this.cuisine,
    this.mealType,
    this.maxCookTime,
    this.assumePantryStaples = true,
    this.rankingMode = 'basket_use',
  });

  @override
  State<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends State<RecommendationScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  List<dynamic> _recipes = [];
  String? _error;

  late bool _assumePantryStaples;
  late String _rankingMode;

  @override
  void initState() {
    super.initState();
    _assumePantryStaples = widget.assumePantryStaples;
    _rankingMode = widget.rankingMode;
    _fetchRecommendations();
  }

  Future<void> _fetchRecommendations() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final results = await _apiService.recommendRecipes(
        widget.ingredients,
        cuisine: widget.cuisine,
        mealType: widget.mealType,
        maxCookTime: widget.maxCookTime,
        assumePantryStaples: _assumePantryStaples,
        rankingMode: _rankingMode,
      );

      if (!mounted) return;
      setState(() {
        _recipes = results;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  String get _subtitle {
    final parts = <String>[];
    if (widget.cuisine != null && widget.cuisine!.isNotEmpty) parts.add(widget.cuisine!);
    if (widget.mealType != null && widget.mealType!.isNotEmpty) {
      parts.add(widget.mealType == 'sweet' ? '🍰 Sweet' : '🍲 Savoury');
    }
    if (widget.maxCookTime != null) parts.add('≤${widget.maxCookTime} min');
    return parts.isEmpty ? '' : parts.join(' · ');
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Recommended Recipes'),
            if (_subtitle.isNotEmpty)
              Text(
                _subtitle,
                style: textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
          ],
        ),
      ),
      body: Column(
        children: [
          // Interactive Quick Controls Bar
          _buildQuickControlsBar(colorScheme, textTheme),
          
          Expanded(
            child: _isLoading
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        CircularProgressIndicator(color: colorScheme.primary),
                        const SizedBox(height: 16),
                        Text(
                          'Matching recipes against your ingredients...',
                          style: textTheme.bodyMedium?.copyWith(color: colorScheme.outline),
                        ),
                      ],
                    ),
                  )
                : _error != null
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(24.0),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.error_outline_rounded, size: 48, color: colorScheme.error),
                              const SizedBox(height: 12),
                              Text('Error: $_error', style: TextStyle(color: colorScheme.error), textAlign: TextAlign.center),
                              const SizedBox(height: 16),
                              FilledButton.tonal(
                                onPressed: _fetchRecommendations,
                                child: const Text('Try Again'),
                              ),
                            ],
                          ),
                        ),
                      )
                    : _recipes.isEmpty
                        ? _buildEmptyState(colorScheme, textTheme)
                        : ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: _recipes.length,
                            itemBuilder: (context, index) {
                              final rec = _recipes[index];
                              return _buildRecipeCard(context, colorScheme, textTheme, rec);
                            },
                          ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickControlsBar(ColorScheme colorScheme, TextTheme textTheme) {
    final isBasketMode = _rankingMode == 'basket_use';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLow,
        border: Border(
          bottom: BorderSide(color: colorScheme.outlineVariant.withOpacity(0.5)),
        ),
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            // Mode Toggle
            FilterChip(
              avatar: Icon(
                isBasketMode ? Icons.shopping_basket_rounded : Icons.check_circle_rounded,
                size: 16,
                color: isBasketMode ? colorScheme.onPrimary : colorScheme.onSurfaceVariant,
              ),
              label: Text(isBasketMode ? '🎯 Maximize Basket' : '🍳 Ready to Cook'),
              selected: true,
              selectedColor: isBasketMode ? colorScheme.primary : colorScheme.tertiaryContainer,
              labelStyle: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: isBasketMode ? colorScheme.onPrimary : colorScheme.onTertiaryContainer,
              ),
              onSelected: (_) {
                setState(() {
                  _rankingMode = isBasketMode ? 'ready_to_cook' : 'basket_use';
                });
                _fetchRecommendations();
              },
            ),
            const SizedBox(width: 8),

            // Pantry Staples Toggle
            FilterChip(
              avatar: Icon(
                Icons.kitchen_rounded,
                size: 16,
                color: _assumePantryStaples ? colorScheme.primary : colorScheme.outline,
              ),
              label: Text(
                _assumePantryStaples ? '🧂 Pantry Staples: ON' : '🧂 Pantry Staples: OFF',
              ),
              selected: _assumePantryStaples,
              selectedColor: colorScheme.primaryContainer,
              labelStyle: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: _assumePantryStaples ? colorScheme.onPrimaryContainer : colorScheme.outline,
              ),
              onSelected: (val) {
                setState(() {
                  _assumePantryStaples = val;
                });
                _fetchRecommendations();
              },
            ),
            const SizedBox(width: 8),

            // Recipe count badge
            if (!_isLoading && _recipes.isNotEmpty)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  '${_recipes.length} found',
                  style: textTheme.labelSmall?.copyWith(color: colorScheme.outline),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState(ColorScheme colorScheme, TextTheme textTheme) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off_rounded, size: 64, color: colorScheme.outline),
            const SizedBox(height: 16),
            Text(
              'No matching recipes found.',
              style: textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Try turning on "Assume Pantry Staples" or adjusting filters.',
              style: textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecipeCard(
    BuildContext context,
    ColorScheme colorScheme,
    TextTheme textTheme,
    Map<String, dynamic> rec,
  ) {
    final recipe = rec['recipe'];
    final matchPercentage = (rec['match_percentage'] * 100).toInt();
    final missingIngredients = List<dynamic>.from(rec['missing_ingredients'] ?? []);
    final missingCore = List<dynamic>.from(rec['missing_core_ingredients'] ?? missingIngredients);
    final usedIngredients = List<dynamic>.from(rec['used_ingredients'] ?? []);

    return Card(
      margin: const EdgeInsets.only(bottom: 20),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (recipe['image_url'] != null && recipe['image_url'].toString().isNotEmpty)
            Container(
              height: 180,
              width: double.infinity,
              color: colorScheme.surfaceContainerHighest,
              child: Image.network(
                recipe['image_url'],
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => const SizedBox.shrink(),
              ),
            ),

          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Recipe Title + Match Pill
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        recipe['name'] ?? 'Unknown Recipe',
                        style: textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: matchPercentage >= 80
                            ? Colors.green.withOpacity(0.15)
                            : matchPercentage >= 60
                                ? Colors.amber.withOpacity(0.18)
                                : colorScheme.tertiaryContainer,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '$matchPercentage% Match',
                        style: TextStyle(
                          color: matchPercentage >= 80
                              ? Colors.green.shade800
                              : matchPercentage >= 60
                                  ? Colors.amber.shade900
                                  : colorScheme.onTertiaryContainer,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    )
                  ],
                ),
                const SizedBox(height: 12),

                // Time, Difficulty, Cuisine
                Row(
                  children: [
                    Icon(Icons.timer_outlined, size: 16, color: colorScheme.onSurfaceVariant),
                    const SizedBox(width: 4),
                    Text('${recipe['cook_time'] ?? 30} min', style: textTheme.bodyMedium),
                    const SizedBox(width: 16),
                    Icon(Icons.bar_chart_rounded, size: 16, color: colorScheme.onSurfaceVariant),
                    const SizedBox(width: 4),
                    Text(recipe['difficulty'] ?? 'Easy', style: textTheme.bodyMedium),
                    if (recipe['cuisine'] != null) ...[
                      const SizedBox(width: 16),
                      Icon(Icons.public_rounded, size: 16, color: colorScheme.onSurfaceVariant),
                      const SizedBox(width: 4),
                      Flexible(
                        child: Text(
                          recipe['cuisine'],
                          style: textTheme.bodyMedium,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 14),

                // Basket Utilization Chips
                if (usedIngredients.isNotEmpty) ...[
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(top: 4.0),
                        child: Icon(Icons.check_circle_outline_rounded, size: 15, color: Colors.green.shade700),
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Wrap(
                          spacing: 6,
                          runSpacing: 4,
                          children: [
                            Text(
                              'Uses ${usedIngredients.length} of ${widget.ingredients.length}:',
                              style: textTheme.bodySmall?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: colorScheme.onSurfaceVariant,
                              ),
                            ),
                            ...usedIngredients.map((ing) => Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.green.withOpacity(0.12),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                ing.toString().toUpperCase(),
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.green.shade800,
                                ),
                              ),
                            )),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                ],

                // Missing status badge
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: missingCore.isEmpty
                        ? Colors.green.withOpacity(0.10)
                        : Colors.orange.withOpacity(0.10),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        missingCore.isEmpty ? Icons.check_circle_rounded : Icons.info_outline_rounded,
                        size: 16,
                        color: missingCore.isEmpty ? Colors.green.shade800 : Colors.orange.shade900,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          missingCore.isEmpty
                              ? 'Ready to Cook! (All core ingredients available)'
                              : 'Missing ${missingCore.length} item(s): ${missingCore.take(3).join(', ')}${missingCore.length > 3 ? '...' : ''}',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: missingCore.isEmpty ? Colors.green.shade900 : Colors.orange.shade900,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                FilledButton.tonal(
                  style: FilledButton.styleFrom(
                    minimumSize: const Size.fromHeight(48),
                  ),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => RecipeDetailsScreen(
                          recipe: recipe,
                          matchPercentage: matchPercentage,
                          missingIngredients: missingIngredients,
                          missingCoreIngredients: missingCore,
                          usedIngredients: usedIngredients,
                          assumePantryStaples: _assumePantryStaples,
                        ),
                      ),
                    );
                  },
                  child: const Text('View Recipe Details'),
                )
              ],
            ),
          )
        ],
      ),
    );
  }
}
