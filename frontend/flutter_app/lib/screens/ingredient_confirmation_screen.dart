import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import '../services/api_service.dart';
import 'recommendation_screen.dart';

class IngredientConfirmationScreen extends StatefulWidget {
  final List<Map<String, dynamic>> detectedIngredients;
  final String? imagePath;

  const IngredientConfirmationScreen({
    super.key,
    required this.detectedIngredients,
    this.imagePath,
  });

  @override
  State<IngredientConfirmationScreen> createState() => _IngredientConfirmationScreenState();
}

class _IngredientConfirmationScreenState extends State<IngredientConfirmationScreen> {
  late List<String> _ingredients;
  final TextEditingController _addController = TextEditingController();
  final ApiService _apiService = ApiService();
  bool _isLoading = false;
  bool _showFilters = false;

  // Filter state
  String? _selectedCuisine;
  String? _selectedMealType;
  int? _selectedMaxTime;

  static const List<String> _cuisineOptions = [
    'Indian', 'Continental', 'Italian', 'South Indian',
    'North Indian', 'Bengali', 'Mexican', 'Maharashtrian',
    'Kerala', 'Karnataka', 'Fusion', 'Rajasthani', 'Andhra',
  ];

  static const List<Map<String, dynamic>> _mealTypeOptions = [
    {'label': '🍲 Savoury', 'value': 'savoury'},
    {'label': '🍰 Sweet', 'value': 'sweet'},
  ];

  static const List<Map<String, dynamic>> _timeOptions = [
    {'label': '⚡ Quick (≤15 min)', 'value': 15},
    {'label': '🕐 Fast (≤30 min)', 'value': 30},
    {'label': '🕑 Medium (≤60 min)', 'value': 60},
    {'label': '🍳 Slow Cook (60+ min)', 'value': 120},
  ];

  @override
  void initState() {
    super.initState();
    _ingredients = widget.detectedIngredients.map((e) => e['name'].toString()).toList();
  }

  @override
  void dispose() {
    _addController.dispose();
    super.dispose();
  }

  void _removeIngredient(int index) {
    setState(() {
      _ingredients.removeAt(index);
    });
  }

  void _addIngredient() {
    final text = _addController.text.trim();
    if (text.isNotEmpty && !_ingredients.contains(text.toLowerCase())) {
      setState(() {
        _ingredients.add(text.toLowerCase());
        _addController.clear();
      });
    }
  }

  int get _activeFilterCount {
    int count = 0;
    if (_selectedCuisine != null) count++;
    if (_selectedMealType != null) count++;
    if (_selectedMaxTime != null) count++;
    return count;
  }

  Future<void> _findRecipes() async {
    if (_ingredients.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please add at least one ingredient.')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final normalized = await _apiService.normalizeIngredients(_ingredients);
      
      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => RecommendationScreen(
            ingredients: normalized,
            cuisine: _selectedCuisine,
            mealType: _selectedMealType,
            maxCookTime: _selectedMaxTime,
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $e'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Confirm Ingredients'),
      ),
      body: _isLoading 
        ? Center(child: CircularProgressIndicator(color: colorScheme.primary)) 
        : Column(
            children: [
              // Image Header
              if (widget.imagePath != null && widget.imagePath!.isNotEmpty)
                Container(
                  height: 180,
                  width: double.infinity,
                  margin: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(24),
                    image: DecorationImage(
                      image: kIsWeb
                          ? NetworkImage(widget.imagePath!) as ImageProvider
                          : FileImage(File(widget.imagePath!)),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
              
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Detected Ingredients',
                      style: textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    Chip(
                      label: Text('${_ingredients.length} items'),
                      backgroundColor: colorScheme.secondaryContainer,
                    ),
                  ],
                ),
              ),

              // Ingredient List
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: _ingredients.length,
                  itemBuilder: (context, index) {
                    return Card(
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: colorScheme.primaryContainer,
                          child: Icon(Icons.eco_rounded, color: colorScheme.onPrimaryContainer, size: 20),
                        ),
                        title: Text(
                          _ingredients[index].toUpperCase(),
                          style: textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
                        ),
                        trailing: IconButton(
                          icon: Icon(Icons.remove_circle_outline_rounded, color: colorScheme.error),
                          onPressed: () => _removeIngredient(index),
                        ),
                      ),
                    );
                  },
                ),
              ),

              // Bottom Panel
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: colorScheme.surfaceContainerLow,
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.04),
                      blurRadius: 16,
                      offset: const Offset(0, -4),
                    )
                  ],
                ),
                child: SafeArea(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Filter Toggle Button
                      GestureDetector(
                        onTap: () => setState(() => _showFilters = !_showFilters),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            color: _activeFilterCount > 0
                                ? colorScheme.primaryContainer
                                : colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                Icons.tune_rounded,
                                size: 20,
                                color: _activeFilterCount > 0 ? colorScheme.onPrimaryContainer : colorScheme.onSurfaceVariant,
                              ),
                              const SizedBox(width: 10),
                              Text(
                                'Recipe Filters',
                                style: textTheme.titleMedium?.copyWith(
                                  fontSize: 14,
                                  color: _activeFilterCount > 0 ? colorScheme.onPrimaryContainer : colorScheme.onSurfaceVariant,
                                ),
                              ),
                              if (_activeFilterCount > 0) ...[
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: colorScheme.primary,
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  child: Text(
                                    '$_activeFilterCount',
                                    style: TextStyle(color: colorScheme.onPrimary, fontSize: 12, fontWeight: FontWeight.bold),
                                  ),
                                ),
                              ],
                              const Spacer(),
                              Icon(
                                _showFilters ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded,
                                color: colorScheme.onSurfaceVariant,
                              ),
                            ],
                          ),
                        ),
                      ),

                      // Filter Chips
                      if (_showFilters) ...[
                        const SizedBox(height: 16),
                        _buildFilterSection(
                          'Cuisine',
                          Icons.public_rounded,
                          _cuisineOptions.map((c) => _buildChip(
                            c,
                            isSelected: _selectedCuisine == c,
                            onTap: () => setState(() {
                              _selectedCuisine = _selectedCuisine == c ? null : c;
                            }),
                            colorScheme: colorScheme,
                          )).toList(),
                          colorScheme: colorScheme,
                        ),
                        const SizedBox(height: 12),
                        _buildFilterSection(
                          'Meal Type',
                          Icons.set_meal_rounded,
                          _mealTypeOptions.map((m) => _buildChip(
                            m['label'],
                            isSelected: _selectedMealType == m['value'],
                            onTap: () => setState(() {
                              _selectedMealType = _selectedMealType == m['value'] ? null : m['value'];
                            }),
                            colorScheme: colorScheme,
                          )).toList(),
                          colorScheme: colorScheme,
                        ),
                        const SizedBox(height: 12),
                        _buildFilterSection(
                          'Max Cooking Time',
                          Icons.timer_outlined,
                          _timeOptions.map((t) => _buildChip(
                            t['label'],
                            isSelected: _selectedMaxTime == t['value'],
                            onTap: () => setState(() {
                              _selectedMaxTime = _selectedMaxTime == t['value'] ? null : t['value'];
                            }),
                            colorScheme: colorScheme,
                          )).toList(),
                          colorScheme: colorScheme,
                        ),
                      ],

                      const SizedBox(height: 16),

                      // Add Manually Row
                      Row(
                        children: [
                          Expanded(
                            child: TextField(
                              controller: _addController,
                              decoration: const InputDecoration(
                                hintText: 'Add extra ingredient...',
                                prefixIcon: Icon(Icons.add_circle_outline_rounded),
                              ),
                              onSubmitted: (_) => _addIngredient(),
                            ),
                          ),
                          const SizedBox(width: 12),
                          FilledButton.tonal(
                            onPressed: _addIngredient,
                            style: FilledButton.styleFrom(
                              padding: const EdgeInsets.all(16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16),
                              ),
                            ),
                            child: const Icon(Icons.add_rounded),
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),

                      FilledButton(
                        onPressed: _findRecipes,
                        style: FilledButton.styleFrom(
                          minimumSize: const Size.fromHeight(52),
                        ),
                        child: Text(
                          _activeFilterCount > 0
                            ? 'Find Recipes ($_activeFilterCount filters)'
                            : 'Find Recipes Now',
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
    );
  }

  Widget _buildFilterSection(String label, IconData icon, List<Widget> chips, {required ColorScheme colorScheme}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 16, color: colorScheme.onSurfaceVariant),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 38,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: chips,
          ),
        ),
      ],
    );
  }

  Widget _buildChip(String label, {required bool isSelected, required VoidCallback onTap, required ColorScheme colorScheme}) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        margin: const EdgeInsets.only(right: 8),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? colorScheme.primary : colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected ? colorScheme.onPrimary : colorScheme.onSurface,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
            fontSize: 13,
          ),
        ),
      ),
    );
  }
}
