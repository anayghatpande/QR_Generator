import 'package:flutter_test/flutter_test.dart';
import 'package:qr_generator_app/main.dart';

void main() {
  testWidgets('App renders correctly', (WidgetTester tester) async {
    await tester.pumpWidget(const QRGeneratorApp());
    expect(find.text('QR Code Generator'), findsOneWidget);
  });
}
