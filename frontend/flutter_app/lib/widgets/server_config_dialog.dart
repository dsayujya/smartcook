import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class ServerConfigDialog extends StatefulWidget {
  const ServerConfigDialog({super.key});

  static Future<void> show(BuildContext context) async {
    return showDialog(
      context: context,
      builder: (_) => const ServerConfigDialog(),
    );
  }

  @override
  State<ServerConfigDialog> createState() => _ServerConfigDialogState();
}

class _ServerConfigDialogState extends State<ServerConfigDialog> {
  late TextEditingController _urlController;
  bool _isTesting = false;
  String? _testResult;
  bool _testSuccess = false;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: ApiService.customBaseUrl);
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  void _applyPreset(String url) {
    setState(() {
      _urlController.text = url;
      _testResult = null;
    });
  }

  void _testConnection() async {
    final apiService = Provider.of<ApiService>(context, listen: false);
    setState(() {
      _isTesting = true;
      _testResult = null;
    });

    final targetUrl = _urlController.text.trim();
    final ok = await apiService.testConnection(testUrl: targetUrl);

    if (mounted) {
      setState(() {
        _isTesting = false;
        _testSuccess = ok;
        _testResult = ok
            ? 'Connection Successful! Server is reachable.'
            : 'Could not connect. Ensure uvicorn is running on 0.0.0.0:8000.';
      });
    }
  }

  void _save() async {
    final apiService = Provider.of<ApiService>(context, listen: false);
    await apiService.setCustomBaseUrl(_urlController.text.trim());
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Server URL updated to ${ApiService.baseUrl}'),
          backgroundColor: Theme.of(context).colorScheme.primary,
        ),
      );
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.dns_rounded, color: colorScheme.primary),
          const SizedBox(width: 8),
          const Text('Backend Server Settings'),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Enter your PC local IP or backend URL so your mobile device can connect:',
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: 'Base API URL',
                hintText: 'http://192.168.1.14:8000/api',
                prefixIcon: Icon(Icons.link_rounded),
              ),
            ),
            const SizedBox(height: 16),
            const Text('Presets:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
            const SizedBox(height: 6),
            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: [
                ActionChip(
                  avatar: const Icon(Icons.cloud_done_rounded, size: 16),
                  label: const Text('Cloud Render (Live)'),
                  onPressed: () => _applyPreset('https://smartcook-api-y1sk.onrender.com/api'),
                ),
                ActionChip(
                  label: const Text('Wi-Fi (192.168.1.14)'),
                  onPressed: () => _applyPreset('http://192.168.1.14:8000/api'),
                ),
                ActionChip(
                  label: const Text('Android Emulator (10.0.2.2)'),
                  onPressed: () => _applyPreset('http://10.0.2.2:8000/api'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: _isTesting ? null : _testConnection,
              icon: _isTesting
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.network_check_rounded),
              label: const Text('Test Connection'),
            ),
            if (_testResult != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: _testSuccess
                      ? Colors.green.withValues(alpha: 0.15)
                      : colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _testResult!,
                  style: TextStyle(
                    fontSize: 12,
                    color: _testSuccess ? Colors.green[800] : colorScheme.onErrorContainer,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _save,
          child: const Text('Save & Connect'),
        ),
      ],
    );
  }
}
