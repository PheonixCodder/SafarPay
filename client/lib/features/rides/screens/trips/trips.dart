import 'package:flutter/material.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import 'screens/canceled/canceled.dart';
import 'screens/completed/completed.dart';
import 'screens/ongoing/ongoing.dart';
import 'screens/scheduled/scheduled.dart';
import 'widgets/trips_tab_bar.dart';

class TripsScreen extends StatefulWidget {
  const TripsScreen({super.key});

  @override
  State<TripsScreen> createState() => _TripsScreenState();
}

class _TripsScreenState extends State<TripsScreen> {
  int _selectedIndex = 0;

  static const List<String> _tabs = [
    STexts.tripsOngoing,
    STexts.tripsScheduled,
    STexts.tripsCanceled,
    STexts.tripsCompleted,
  ];

  static const List<Widget> _screens = [
    OngoingTripsScreen(),
    ScheduledTripsScreen(),
    CanceledTripsScreen(),
    CompletedTripsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        title: Text(
          STexts.tripsTitle,
          style: Theme.of(context).textTheme.headlineMedium,
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SSizes.defaultSpace),
        child: Column(
          children: [
            STripsTabBar(
              tabs: _tabs,
              selectedIndex: _selectedIndex,
              onTabSelected: (index) => setState(() => _selectedIndex = index),
            ),
            const SizedBox(height: SSizes.spaceBtnItems),
            IndexedStack(index: _selectedIndex, children: _screens),
          ],
        ),
      ),
    );
  }
}
