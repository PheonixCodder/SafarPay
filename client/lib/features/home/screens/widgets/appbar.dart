import 'package:flutter/material.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../common/widgets/notification.dart';
import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/texts.dart';

class SHomeAppBar extends StatelessWidget {
  const SHomeAppBar({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return SAppBar(
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            STexts.homeAppbarTitle,
            style: Theme.of(context).textTheme.labelMedium,
          ),
          Text(
            STexts.homeAppbarSubTitle,
            style: Theme.of(context).textTheme.headlineMedium,
          ),
        ],
      ),
      actions: [
        SNotificationCounterIcon(
          onPressed: () {},
          iconColor: SColors.primary,
        ),
      ],
    );
  }
}
