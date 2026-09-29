import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';

class RecipeDetailsScreen extends StatefulWidget {
  final Map<String, dynamic> recipe;
  final int matchPercentage;
  final List<dynamic> missingIngredients;

  const RecipeDetailsScreen({
    super.key,
    required this.recipe,
    required this.matchPercentage,
    required this.missingIngredients,
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
                  
                  // Ingredients Section
                  Text('Ingredients Needed', style: textTheme.titleLarge),
                  const SizedBox(height: 12),
                  ...List.generate(
                    (widget.recipe['ingredients'] as List).length,
                    (index) {
                      final item = widget.recipe['ingredients'][index];
                      final ingredientName = item['ingredient']['name'];
                      final isMissing = widget.missingIngredients.contains(ingredientName.toString().toLowerCase());
                      
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6.0),
                        child: Row(
                          children: [
                            Icon(
                              isMissing ? Icons.cancel_outlined : Icons.check_circle_rounded,
                              color: isMissing ? colorScheme.error : colorScheme.primary,
                              size: 20,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                '${item['quantity'] ?? ''} ${item['unit'] ?? ''} ${ingredientName.toString().toUpperCase()}',
                                style: textTheme.bodyLarge?.copyWith(
                                  color: isMissing ? colorScheme.error : colorScheme.onSurface,
                                  fontWeight: isMissing ? FontWeight.w600 : FontWeight.normal,
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                  
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
}
