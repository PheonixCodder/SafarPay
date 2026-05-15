import 'package:flutter/material.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../../../utils/device/utility.dart';
import '../../../../utils/helpers/helpers.dart';
import '../../../../utils/http/client.dart';
import '../../models/auth_models.dart';
import '../../repositories/auth_repository.dart';
import '../../utils/auth_navigation.dart';
import '../otp/otp.dart';
import 'widgets/google_phone_link_form.dart';
import 'widgets/google_phone_link_header.dart';

class GoogleOtpProfileScreen extends StatefulWidget {
  const GoogleOtpProfileScreen({
    super.key,
    this.displayName,
    this.email,
  });

  final String? displayName;
  final String? email;

  @override
  State<GoogleOtpProfileScreen> createState() => _GoogleOtpProfileScreenState();
}

class _GoogleOtpProfileScreenState extends State<GoogleOtpProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController();
  bool _isSendingOtp = false;

  String get _displayName {
    final name = widget.displayName?.trim();
    if (name != null && name.isNotEmpty) return name;

    final email = widget.email?.trim();
    if (email != null && email.isNotEmpty) return email;

    return STexts.googleAccountVerified;
  }

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    SDeviceUtils.hideKeyboard(context);

    if (_isSendingOtp || !(_formKey.currentState?.validate() ?? false)) {
      return;
    }

    setState(() => _isSendingOtp = true);
    try {
      final phoneNumber = _phoneController.text.trim();
      await SAuthRepository.instance.sendOtp(phoneNumber);
      SHelperFunctions.showSnackBar(STexts.otpSent);
      SAuthNavigation.to(
        OtpScreen(
          phoneNumber: phoneNumber,
          flow: SAuthOtpFlow.googlePhoneLink,
          displayName: widget.displayName,
        ),
      );
    } on SHttpException catch (error) {
      SHelperFunctions.showSnackBar(error.message);
    } catch (_) {
      SHelperFunctions.showSnackBar(STexts.unexpectedError);
    } finally {
      if (mounted) setState(() => _isSendingOtp = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      body: Stack(
        children: [
          Positioned(
            top: SSizes.googlePhoneLinkBackgroundTop,
            left: SSizes.googlePhoneLinkBackgroundHorizontal,
            right: SSizes.googlePhoneLinkBackgroundHorizontal,
            child: Container(
              height: SSizes.googlePhoneLinkBackgroundHeight,
              decoration: const BoxDecoration(
                borderRadius: BorderRadius.only(
                  bottomLeft: Radius.circular(
                    SSizes.googlePhoneLinkBackgroundRadius,
                  ),
                  bottomRight: Radius.circular(
                    SSizes.googlePhoneLinkBackgroundRadius,
                  ),
                ),
              ),
            ),
          ),
          SafeArea(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(SSizes.defaultSpace),
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(
                      maxWidth: SSizes.googlePhoneLinkMaxWidth,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const SizedBox(height: SSizes.md),
                        SGooglePhoneLinkHeader(
                          displayName: _displayName,
                          email: widget.email,
                        ),
                        const SizedBox(height: SSizes.spaceBtwSections),
                        SGooglePhoneLinkForm(
                          formKey: _formKey,
                          phoneController: _phoneController,
                          isSendingOtp: _isSendingOtp,
                          onSubmit: _sendOtp,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
