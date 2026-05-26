import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../controllers/earnings_controller.dart';
import 'widgets/earnings_body.dart';
import 'widgets/earnings_period_menu.dart';

class SEarningsScreen extends StatelessWidget {
  const SEarningsScreen({super.key, this.controller});

  final SEarningsController? controller;

  @override
  Widget build(BuildContext context) {
    final earningsController = Get.put(controller ?? SEarningsController());

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        title: Text(
          STexts.earningsTitle,
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        actions: [
          Obx(
            () => SEarningsPeriodMenu(
              selected: earningsController.selectedPeriod.value,
              onSelected: earningsController.selectPeriod,
            ),
          ),
          const SizedBox(width: SSizes.md),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: earningsController.loadEarnings,
        color: SColors.primary,
        child: Obx(
          () => SEarningsBody(
            earnings: earningsController.earnings.value,
            isLoading: earningsController.isLoading.value,
            errorMessage: earningsController.errorMessage.value,
          ),
        ),
      ),
    );
  }
}
