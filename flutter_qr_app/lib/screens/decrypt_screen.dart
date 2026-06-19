import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:image_picker/image_picker.dart';
import 'package:url_launcher/url_launcher.dart';
import '../theme/app_theme.dart';
import '../services/encryption_service.dart';

class DecryptScreen extends StatefulWidget {
  const DecryptScreen({super.key});

  @override
  State<DecryptScreen> createState() => _DecryptScreenState();
}

class _DecryptScreenState extends State<DecryptScreen> {
  final _passwordController = TextEditingController();
  final _textController = TextEditingController();
  final _encryptionService = EncryptionService();
  final _scannerController = MobileScannerController(autoStart: false);

  bool _scanning = false;
  String? _scannedData;
  String? _decryptedUrl;
  bool _decrypting = false;
  String? _error;

  @override
  void dispose() {
    _passwordController.dispose();
    _textController.dispose();
    _scannerController.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_scannedData != null) return;
    final barcode = capture.barcodes.firstOrNull;
    if (barcode?.rawValue != null) {
      setState(() {
        _scannedData = barcode!.rawValue;
        _textController.text = _scannedData!;
      });
      _stopScanning();
    }
  }

  void _startScanning() {
    setState(() => _scanning = true);
    unawaited(_scannerController.start());
  }

  void _stopScanning() {
    setState(() => _scanning = false);
    unawaited(_scannerController.stop());
  }

  void _toggleScanning() {
    if (_scanning) {
      _stopScanning();
    } else {
      _startScanning();
    }
  }

  Future<void> _pickFromGallery() async {
    final picker = ImagePicker();
    final image = await picker.pickImage(source: ImageSource.gallery);
    if (image == null) return;

    final result = await _scannerController.analyzeImage(image.path);
    if (!mounted) return;
    final barcode = result?.barcodes.firstOrNull;
    if (barcode?.rawValue != null) {
      setState(() {
        _scannedData = barcode!.rawValue;
        _textController.text = _scannedData!;
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No QR code found in the image')),
      );
    }
  }

  void _decrypt() {
    final text = _textController.text.trim();
    final password = _passwordController.text;

    if (text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Scan a QR code or paste the encrypted text')),
      );
      return;
    }
    if (password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter the password')),
      );
      return;
    }

    setState(() {
      _decrypting = true;
      _decryptedUrl = null;
      _error = null;
    });

    debugPrint('Decrypting: text="${text.length}chars" password="${password.length}chars"');
    try {
      final url = _encryptionService.decrypt(text, password);
      setState(() => _decryptedUrl = url);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _decrypting = false);
    }
  }

  void _openUrl(String url) async {
    final uri = Uri.tryParse(url);
    if (uri != null && await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  Widget _errorBuilder(
      BuildContext context, MobileScannerException error, Widget? child) {
    return Container(
      color: Colors.black,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, color: Colors.white, size: 48),
            const SizedBox(height: 16),
            Text(
              error.errorCode.message,
              style: const TextStyle(color: Colors.white, fontSize: 16),
              textAlign: TextAlign.center,
            ),
            if (error.errorDetails?.message case final String msg) ...[
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Text(
                  msg,
                  style: const TextStyle(color: Colors.white70, fontSize: 13),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => unawaited(_scannerController.start()),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Scan QR Code',
                      style: Theme.of(context)
                          .textTheme
                          .titleSmall
                          ?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  SizedBox(
                    height: 220,
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Stack(
                        children: [
                          MobileScanner(
                            controller: _scannerController,
                            onDetect: _onDetect,
                            errorBuilder: _errorBuilder,
                          ),
                          if (!_scanning)
                            Container(
                              decoration: BoxDecoration(
                                color: AppTheme.bg,
                                border: Border.all(color: AppTheme.border),
                              ),
                              child: Center(
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.qr_code_scanner,
                                        size: 48,
                                        color: AppTheme.textSecondary),
                                    const SizedBox(height: 8),
                                    Text('Tap below to start scanning',
                                        style: Theme.of(context)
                                            .textTheme
                                            .bodySmall
                                            ?.copyWith(
                                                color:
                                                    AppTheme.textSecondary)),
                                  ],
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _toggleScanning,
                          icon: Icon(_scanning
                              ? Icons.stop
                              : Icons.qr_code_scanner),
                          label: Text(_scanning ? 'Stop' : 'Scan QR'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: _pickFromGallery,
                          icon: const Icon(Icons.photo_library_outlined),
                          label: const Text('Gallery'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Or paste encrypted text manually',
                      style: Theme.of(context)
                          .textTheme
                          .bodySmall
                          ?.copyWith(color: AppTheme.textSecondary)),
                  const SizedBox(height: 8),
                  TextFormField(
                    controller: _textController,
                    maxLines: 3,
                    decoration: const InputDecoration(
                      hintText: 'ENC:...',
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text('Password',
                      style: Theme.of(context)
                          .textTheme
                          .titleSmall
                          ?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  TextFormField(
                    controller: _passwordController,
                    obscureText: true,
                    decoration: const InputDecoration(
                      hintText: 'Enter password',
                      prefixIcon: Icon(Icons.lock_outline),
                    ),
                    onFieldSubmitted: (_) => _decrypt(),
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _decrypting ? null : _decrypt,
                      icon: _decrypting
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                  strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.lock_open),
                      label: const Text('Decrypt'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.protectedTag,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (_error != null) ...[
            const SizedBox(height: 16),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.red.shade200),
              ),
              child: Row(
                children: [
                  Icon(Icons.error_outline, color: Colors.red.shade700),
                  const SizedBox(width: 10),
                  Text(_error!,
                      style: TextStyle(color: Colors.red.shade700)),
                ],
              ),
            ),
          ],
          if (_decryptedUrl != null) ...[
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.check_circle,
                            color: AppTheme.success, size: 20),
                        const SizedBox(width: 8),
                        Text('Decrypted URL',
                            style: Theme.of(context)
                                .textTheme
                                .titleSmall
                                ?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: AppTheme.success)),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: AppTheme.warningBg,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        _decryptedUrl!,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () => _openUrl(_decryptedUrl!),
                            icon: const Icon(Icons.open_in_browser),
                            label: const Text('Open'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () {
                              Clipboard.setData(
                                  ClipboardData(text: _decryptedUrl!));
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                    content: Text('URL copied to clipboard')),
                              );
                            },
                            icon: const Icon(Icons.copy),
                            label: const Text('Copy'),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
