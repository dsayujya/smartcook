import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import 'ingredient_confirmation_screen.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  final ImagePicker _picker = ImagePicker();
  final ApiService _apiService = ApiService();
  bool _isLoading = false;
  XFile? _image;

  Future<void> _pickImage(ImageSource source) async {
    try {
      final pickedFile = await _picker.pickImage(
        source: source,
        maxWidth: 800,
        maxHeight: 800,
        imageQuality: 60,
      );
      if (pickedFile != null) {
        setState(() {
          _image = pickedFile;
        });
        await _processImage(pickedFile);
      }
    } catch (e) {
      _showError('Failed to capture image: $e');
    }
  }

  Future<void> _processImage(XFile imageFile) async {
    setState(() {
      _isLoading = true;
    });

    try {
      final ingredients = await _apiService.detectIngredients(imageFile);
      
      if (!mounted) return;
      
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => IngredientConfirmationScreen(
            detectedIngredients: ingredients,
            imagePath: imageFile.path,
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
      });
      _showError('Could not process image. Please try again.\n$e');
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Theme.of(context).colorScheme.error,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan AI Ingredients'),
      ),
      body: Center(
        child: _isLoading 
          ? _buildLoadingState(context) 
          : _buildSelectionState(context),
      ),
    );
  }

  Widget _buildLoadingState(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            SizedBox(
              width: 120,
              height: 120,
              child: CircularProgressIndicator(
                strokeWidth: 6,
                color: colorScheme.primary,
              ),
            ),
            Icon(Icons.auto_awesome_rounded, size: 48, color: colorScheme.primary),
          ],
        ),
        const SizedBox(height: 32),
        Text(
          'SmartCook AI is analyzing\nyour ingredients...',
          textAlign: TextAlign.center,
          style: textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }

  Widget _buildSelectionState(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          _image != null
              ? ClipRRect(
                  borderRadius: BorderRadius.circular(24),
                  child: kIsWeb
                      ? Image.network(
                          _image!.path,
                          height: 250,
                          width: double.infinity,
                          fit: BoxFit.cover,
                        )
                      : Image.file(
                          File(_image!.path),
                          height: 250,
                          width: double.infinity,
                          fit: BoxFit.cover,
                        ),
                )
              : Container(
                  height: 240,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.photo_library_outlined, size: 64, color: colorScheme.onSurfaceVariant),
                      const SizedBox(height: 16),
                      Text(
                        'No ingredient photo selected yet',
                        style: textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
          const SizedBox(height: 44),
          
          FilledButton.icon(
            onPressed: () => _pickImage(ImageSource.camera),
            icon: const Icon(Icons.camera_alt_rounded),
            label: const Text('Take a Photo'),
            style: FilledButton.styleFrom(
              minimumSize: const Size(double.infinity, 54),
            ),
          ),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: () => _pickImage(ImageSource.gallery),
            icon: const Icon(Icons.photo_library_rounded),
            label: const Text('Choose from Gallery'),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size(double.infinity, 54),
            ),
          ),
        ],
      ),
    );
  }
}
