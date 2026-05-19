import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../../common/navigation/right_slide_page_route.dart';
import '../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../features/personalization/screens/help_support/screens/something_else/controllers/something_else_controller.dart';
import '../../../../../../features/personalization/screens/help_support/screens/something_else/screens/ticket_created_screen.dart';
import '../../../../../../features/personalization/screens/help_support/screens/something_else/widgets/support_attachments_section.dart';
import '../../../../../../features/personalization/screens/help_support/screens/something_else/widgets/support_issue_field.dart';
import '../../../../../../features/personalization/screens/help_support/screens/something_else/widgets/support_related_ride_card.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';

class SomethingElseScreen extends StatefulWidget {
  const SomethingElseScreen({super.key});

  @override
  State<SomethingElseScreen> createState() => _SomethingElseScreenState();
}

class _SomethingElseScreenState extends State<SomethingElseScreen> {
  late final String _controllerTag;
  late final SSomethingElseController _controller;

  @override
  void initState() {
    super.initState();
    _controllerTag = 'something-else-${identityHashCode(this)}';
    _controller = Get.put(
      SSomethingElseController(),
      tag: _controllerTag,
    );
  }

  @override
  void dispose() {
    if (Get.isRegistered<SSomethingElseController>(tag: _controllerTag)) {
      Get.delete<SSomethingElseController>(tag: _controllerTag, force: true);
    }
    super.dispose();
  }

  Future<void> _submit() async {
    final response = await _controller.submit();
    if (!mounted || response == null) return;

    Navigator.of(context).push(
      SRightSlidePageRoute(
        page: TicketCreatedScreen(response: response),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Obx(
                () {
                  final description = _controller.description.value;
                  final attachments = _controller.attachments.toList();
                  final errorMessage = _controller.errorMessage.value;
                  final isSubmitting = _controller.isSubmitting.value;

                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'Tell us more',
                        textAlign: TextAlign.center,
                        style: textTheme.titleLarge?.copyWith(
                          color: SColors.textPrimary,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: SSizes.xs),
                      Text(
                        'Please provide more details about\nyour issue.',
                        textAlign: TextAlign.center,
                        style: textTheme.bodySmall?.copyWith(
                          color: SColors.textSecondary,
                          height: 1.3,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: SSizes.lg),
                      SSupportIssueField(
                        controller: _controller.descriptionController,
                        onChanged: _controller.onDescriptionChanged,
                        currentLength: description.length,
                      ),
                      if (errorMessage.isNotEmpty) ...[
                        const SizedBox(height: SSizes.xs),
                        Text(
                          errorMessage,
                          style: textTheme.bodySmall?.copyWith(
                            color: SColors.error,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                      const SizedBox(height: SSizes.md),
                      const SSupportRelatedRideCard(),
                      const SizedBox(height: SSizes.md),
                      SSupportAttachmentsSection(
                        attachments: attachments,
                        onAddAttachment: (type) {
                          _controller.addDemoAttachment(type);
                        },
                      ),
                      const SizedBox(height: SSizes.lg),
                      ElevatedButton(
                        onPressed: isSubmitting ? null : _submit,
                        child: Text(
                          isSubmitting ? 'Submitting...' : 'Submit Ticket',
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );
  }
}
