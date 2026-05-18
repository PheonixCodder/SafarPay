import 'package:iconsax/iconsax.dart';

import 'package:client/features/personalization/screens/help_support/screens/contact/contact.dart';
import 'package:client/features/personalization/screens/help_support/screens/faqs/faqs.dart';
import 'package:client/features/personalization/screens/help_support/screens/live_chat/live_chat.dart';
import 'package:client/features/personalization/screens/help_support/screens/something_else/something_else.dart';
import 'package:client/features/personalization/screens/help_support/screens/terms_conditions/terms_conditions.dart';
import 'package:client/utils/constants/texts.dart';

import '../models/help_support_option.dart';

class SHelpSupportContent {
  SHelpSupportContent._();

  static const List<SHelpSupportOption> options = [
    SHelpSupportOption(
      icon: Iconsax.message_text,
      title: STexts.helpSupportLiveChat,
      destination: LiveChatScreen(),
    ),
    SHelpSupportOption(
      icon: Iconsax.call,
      title: STexts.helpSupportContactUs,
      destination: ContactScreen(),
    ),
    SHelpSupportOption(
      icon: Iconsax.clipboard_text,
      title: STexts.helpSupportFaqs,
      destination: FaqsScreen(),
    ),
    SHelpSupportOption(
      icon: Iconsax.document_text,
      title: STexts.helpSupportTermsConditions,
      destination: TermsConditionsScreen(),
    ),
    SHelpSupportOption(
      icon: Iconsax.message_question,
      title: STexts.helpSupportSomethingElse,
      destination: SomethingElseScreen(),
    ),
  ];
}
