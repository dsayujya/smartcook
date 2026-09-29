import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'recipe_details_screen.dart';

class RecommendationScreen extends StatefulWidget {
  final List<String> ingredients;
  final String? cuisine;
  final String? mealType;
  final int? maxCookTime;

  const RecommendationScreen({
    super.key,
    required this.ingredients,
    this.cuisine,
    this.mealType,
    this.maxCookTime,
  });

  @override
  State<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends State<RecommendationScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  List<dynamic> _recipes = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchRecommendations();
  }

  Future<void> _fetchRecommendations() async {
    try {
      final results = await _apiService.recommendRecipes(
        widget.ingredients,
        cuisine: widget.cuisine,
        mealType: widget.mealType,
        maxCookTime: widget.maxCookTime,
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
      body: _isLoading 
        ? Center(child: CircularProgressIndicator(color: colorScheme.primary))
        : _error != null 
          ? Center(child: Text('Error: $_error', style: TextStyle(color: colorScheme.error)))
          : _recipes.isEmpty 
            ? _buildEmptyState(colorScheme, textTheme)
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _recipes.length,
                itemBuilder: (context, index) {
                  final rec = _recipes[index];
                  final recipe = rec['recipe'];
                  final matchPercentage = (rec['match_percentage'] * 100).toInt();
                  final missingIngredients = rec['missing_ingredients'] ?? [];
                  
                  return _buildRecipeCard(context, colorScheme, textTheme, recipe, matchPercentage, missingIngredients);
                },
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
              'No recipes found.',
              style: textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              _subtitle.isNotEmpty 
                ? 'Try adjusting your filters or adding more ingredients.'
                : 'Try adding common kitchen ingredients.',
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
    Map<String, dynamic> recipe,
    int matchPercentage,
    List<dynamic> missingIngredients,
  ) {
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        recipe['name'] ?? 'Unknown Recipe',
                        style: textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: matchPercentage >= 80 
                            ? Colors.green.withOpacity(0.15) 
                            : colorScheme.tertiaryContainer,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '$matchPercentage% Match',
                        style: TextStyle(
                          color: matchPercentage >= 80 ? Colors.green.shade800 : colorScheme.onTertiaryContainer,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    )
                  ],
                ),
                const SizedBox(height: 12),
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
                const SizedBox(height: 20),
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
