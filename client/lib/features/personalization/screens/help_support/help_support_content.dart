import 'package:iconsax/iconsax.dart';

import '../../../../utils/constants/texts.dart';
import 'help_support_option.dart';
import 'screens/contact/contact.dart';
import 'screens/faqs/faqs.dart';
import 'screens/live_chat/live_chat.dart';
import 'screens/something_else/something_else.dart';
import 'screens/terms_conditions/terms_conditions.dart';

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
