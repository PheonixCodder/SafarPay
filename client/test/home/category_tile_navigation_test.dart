import 'package:client/features/home/screens/home/widgets/category_tile.dart';
import 'package:client/utils/constants/images.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('category tile invokes tap callback', (tester) async {
    var tapped = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SCategoryTile(
            title: 'Freight',
            image: SImages.freight,
            onTap: () => tapped = true,
          ),
        ),
      ),
    );

    await tester.tap(find.text('Freight'));
    await tester.pump();

    expect(tapped, isTrue);
  });
}
