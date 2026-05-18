import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/common/widgets/notification.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';

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
