import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';

import '../constants/colors.dart';

class SHelperFunctions {
  SHelperFunctions._();

  static Color withOpacity(Color color, double opacity) {
    return color.withValues(alpha: opacity);
  }

  static Color? getColor(String value) {
    if (value == 'Green') {
      return SColors.success;
    } else if (value == 'Red') {
      return SColors.error;
    } else if (value == 'Blue') {
      return SColors.info;
    } else if (value == 'Pink') {
      return SColors.pink;
    } else if (value == 'Grey') {
      return SColors.grey;
    } else if (value == 'Purple') {
      return SColors.purple;
    } else if (value == 'Black') {
      return SColors.black;
    } else if (value == 'White') {
      return SColors.white;
    }
    return null;
  }

  static void showSnackBar(String message) {
    ScaffoldMessenger.of(Get.context!).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  static void showAlert(String title, String message) {
    showDialog(
      context: Get.context!,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(title),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  static void navigateToScreen(BuildContext context, Widget screen) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => screen),
    );
  }

  static String truncateText(String text, int maxLength) {
    if (text.length <= maxLength) {
      return text;
    } else {
      return '${text.substring(0, maxLength)}...';
    }
  }

  static double screenHeight() {
    return MediaQuery.of(Get.context!).size.height;
  }

  static double screenWidth() {
    return MediaQuery.of(Get.context!).size.width;
  }

  static String getFormattedDate(DateTime date,
      {String format = 'dd MMM yyyy'}) {
    return DateFormat(format).format(date);
  }

  static List<T> removeDuplicates<T>(List<T> list) {
    return list.toSet().toList();
  }

  static List<Widget> wrapWidgets(List<Widget> widgets, int rowSize) {
    final wrappedList = <Widget>[];
    for (var i = 0; i < widgets.length; i += rowSize) {
      final end = (i + rowSize > widgets.length) ? widgets.length : i + rowSize;
      final rowChildren = widgets.sublist(i, end);
      wrappedList.add(Row(children: rowChildren));
    }
    return wrappedList;
  }
}
