import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../../../utils/device/utility.dart';
import '../../../../utils/helpers/helpers.dart';
import '../../../../utils/http/client.dart';
import '../../../../utils/validators/validator.dart';
import '../../models/auth_models.dart';
import '../../repositories/auth_repository.dart';
import '../../utils/auth_navigation.dart';
import '../otp/otp.dart';

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
            top: -96,
            left: -56,
            right: -56,
            child: Container(
              height: 230,
              decoration: const BoxDecoration(
                borderRadius: BorderRadius.only(
                  bottomLeft: Radius.circular(120),
                  bottomRight: Radius.circular(120),
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
                    constraints: const BoxConstraints(maxWidth: 420),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const SizedBox(height: SSizes.md),
                        _GooglePhoneLinkHeader(
                          displayName: _displayName,
                          email: widget.email,
                        ),
                        const SizedBox(height: SSizes.spaceBtwSections),
                        _GooglePhoneLinkForm(
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

class _GooglePhoneLinkHeader extends StatelessWidget {
  const _GooglePhoneLinkHeader({
    required this.displayName,
    this.email,
  });

  final String displayName;
  final String? email;

  @override
  Widget build(BuildContext context) {
    final emailText = email?.trim();

    return Column(
      children: [
        Container(
          width: 72,
          height: 72,
          decoration: BoxDecoration(
            color: SColors.primary.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
          ),
          child: const Icon(
            Iconsax.user_edit,
            color: SColors.primary,
            size: SSizes.iconLg,
          ),
        ),
        const SizedBox(height: SSizes.defaultSpace),
        Text(
          STexts.googlePhoneLinkTitle,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                color: SColors.textPrimary,
              ),
        ),
        const SizedBox(height: SSizes.sm),
        FractionallySizedBox(
          widthFactor: 0.9,
          child: Text(
            STexts.googlePhoneLinkSubTitle,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: SColors.textSecondary,
                ),
          ),
        ),
        const SizedBox(height: SSizes.defaultSpace),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(SSizes.md),
          decoration: BoxDecoration(
            color: SColors.white,
            border: Border.all(color: SColors.borderSecondary),
            borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
          ),
          child: Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: SColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusSm),
                ),
                child: const Icon(
                  Iconsax.user,
                  color: SColors.primary,
                  size: SSizes.iconMd,
                ),
              ),
              const SizedBox(width: SSizes.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      displayName,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: SColors.textPrimary,
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    if (emailText != null && emailText.isNotEmpty) ...[
                      const SizedBox(height: SSizes.xs),
                      Text(
                        emailText,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: SColors.textSecondary,
                            ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _GooglePhoneLinkForm extends StatelessWidget {
  const _GooglePhoneLinkForm({
    required this.formKey,
    required this.phoneController,
    required this.isSendingOtp,
    required this.onSubmit,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController phoneController;
  final bool isSendingOtp;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    return Form(
      key: formKey,
      child: Column(
        children: [
          TextFormField(
            controller: phoneController,
            keyboardType: TextInputType.phone,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => onSubmit(),
            validator: SValidator.validatePhoneNumber,
            decoration: const InputDecoration(
              labelText: STexts.phoneNo,
              helperText: STexts.phoneHelperText,
              prefixIcon: Icon(Iconsax.call),
            ),
          ),
          const SizedBox(height: SSizes.spaceBtwSections),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: isSendingOtp ? null : onSubmit,
              child: isSendingOtp
                  ? const SizedBox(
                      width: SSizes.iconMd,
                      height: SSizes.iconMd,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text(STexts.googlePhoneLinkCta),
            ),
          ),
        ],
      ),
    );
  }
}
