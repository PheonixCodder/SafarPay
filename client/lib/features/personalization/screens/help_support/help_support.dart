import 'package:flutter/material.dart';

import '../../../../utils/constants/colors.dart';
import 'widgets/help_support_header.dart';
import 'widgets/help_support_sheet.dart';

class HelpSupportScreen extends StatelessWidget {
  const HelpSupportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: SColors.primaryBackground,
      body: SingleChildScrollView(
        child: Column(
          children: [
            SHelpSupportHeader(),
            SHelpSupportSheet(),
          ],
        ),
      ),
    );
  }
}
