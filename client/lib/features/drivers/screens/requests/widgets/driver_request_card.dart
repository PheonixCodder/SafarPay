import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../../../domain/driver_request_models.dart';

class SDriverRequestCard extends StatefulWidget {
  const SDriverRequestCard({
    super.key,
    required this.request,
    required this.onTap,
  });

  final SDriverRideRequest request;
  final VoidCallback onTap;

  @override
  State<SDriverRequestCard> createState() => _SDriverRequestCardState();
}

class _SDriverRequestCardState extends State<SDriverRequestCard> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final eta = widget.request.driverToPickup?.durationMinutes.round();
    final distance = widget.request.driverToPickup?.distanceKm;

    return GestureDetector(
      onTapDown: (_) => setState(() => _isPressed = true),
      onTapUp: (_) => setState(() => _isPressed = false),
      onTapCancel: () => setState(() => _isPressed = false),
      onTap: widget.onTap,
      child: AnimatedScale(
        scale: _isPressed ? 0.97 : 1.0,
        duration: const Duration(milliseconds: 100),
        curve: Curves.easeOutCubic,
        child: Container(
          decoration: BoxDecoration(
            color: SColors.white,
            borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
            border: Border.all(color: SColors.borderSecondary, width: 1.2),
            boxShadow: [
              BoxShadow(
                color: SHelperFunctions.withOpacity(SColors.pureBlack, 0.04),
                blurRadius: 16.0,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(SSizes.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header: Passenger Profile, Details & Fare
                Row(
                  children: [
                    CircleAvatar(
                      radius: 20.0,
                      backgroundColor: SHelperFunctions.withOpacity(SColors.primary, 0.1),
                      child: Text(
                        widget.request.passengerId.isEmpty
                            ? 'R'
                            : widget.request.passengerId[0].toUpperCase(),
                        style: textTheme.titleMedium?.copyWith(
                          color: SColors.primary,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                    const SizedBox(width: SSizes.md),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'RIDE REQUEST',
                            style: textTheme.labelMedium?.copyWith(
                              color: SColors.textSecondary,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.8,
                            ),
                          ),
                          const SizedBox(height: 2.0),
                          Text(
                            _formatLabel(widget.request.category),
                            style: textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w800,
                              color: SColors.textPrimary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.baseline,
                          textBaseline: TextBaseline.alphabetic,
                          children: [
                            Text(
                              'PKR ',
                              style: textTheme.titleSmall?.copyWith(
                                fontWeight: FontWeight.w800,
                                color: SColors.primary,
                              ),
                            ),
                            Text(
                              '${widget.request.displayFare.round()}',
                              style: textTheme.headlineMedium?.copyWith(
                                fontWeight: FontWeight.w900,
                                color: SColors.textPrimary,
                                height: 1.0,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: SSizes.spaceBtnItems),
                
                // Divider
                Container(
                  height: 1.0,
                  color: SColors.borderSecondary,
                ),
                const SizedBox(height: SSizes.spaceBtnItems),

                // Route section with a beautiful custom vertical timeline
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Styled Timeline Indicators
                    Column(
                      children: [
                        const SizedBox(height: 4.0),
                        // Pickup Pin Dot (Uber-style)
                        Container(
                          width: 14.0,
                          height: 14.0,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: SColors.white,
                            border: Border.all(color: SColors.primary, width: 2.0),
                          ),
                          child: Center(
                            child: Container(
                              width: 5.0,
                              height: 5.0,
                              decoration: const BoxDecoration(
                                shape: BoxShape.circle,
                                color: SColors.primary,
                              ),
                            ),
                          ),
                        ),
                        // Connector Line
                        Container(
                          width: 1.5,
                          height: 28.0,
                          color: SColors.borderPrimary,
                        ),
                        // Dropoff Pin Dot
                        Container(
                          width: 14.0,
                          height: 14.0,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: SColors.white,
                            border: Border.all(color: SColors.pureBlack, width: 2.0),
                          ),
                          child: Center(
                            child: Container(
                              width: 5.0,
                              height: 5.0,
                              decoration: const BoxDecoration(
                                shape: BoxShape.circle,
                                color: SColors.pureBlack,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(width: 12.0),
                    // Addresses
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Pickup
                          Text(
                            widget.request.pickup?.displayName ?? 'Pickup unavailable',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: textTheme.bodyLarge?.copyWith(
                              fontWeight: FontWeight.w700,
                              color: SColors.textPrimary,
                            ),
                          ),
                          const SizedBox(height: 16.0),
                          // Dropoff
                          Text(
                            widget.request.dropoff?.displayName ?? 'Dropoff unavailable',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: textTheme.bodyMedium?.copyWith(
                              color: SColors.textSecondary,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: SSizes.spaceBtnItems),

                // Divider
                Container(
                  height: 1.0,
                  color: SColors.borderSecondary,
                ),
                const SizedBox(height: SSizes.spaceBtnItems),

                // Info badging footer
                Wrap(
                  spacing: SSizes.sm,
                  runSpacing: SSizes.xs,
                  children: [
                    // Payment Badging
                    _buildInfoPill(
                      icon: Iconsax.wallet_2,
                      label: widget.request.paymentMethod.replaceAll('_', ' '),
                      backgroundColor: SHelperFunctions.withOpacity(SColors.success, 0.08),
                      textColor: SColors.success,
                    ),
                    // Pricing Mode Badging
                    _buildInfoPill(
                      icon: Iconsax.tag,
                      label: _formatLabel(widget.request.pricingMode),
                      backgroundColor: SHelperFunctions.withOpacity(SColors.purple, 0.08),
                      textColor: SColors.purple,
                    ),
                    // ETA Badging
                    if (eta != null)
                      _buildInfoPill(
                        icon: Iconsax.clock,
                        label: '$eta min away',
                        backgroundColor: SHelperFunctions.withOpacity(SColors.warning, 0.08),
                        textColor: SColors.warning,
                      ),
                    // Distance Badging
                    if (distance != null)
                      _buildInfoPill(
                        icon: Iconsax.route_square,
                        label: '${distance.toStringAsFixed(1)} km',
                        backgroundColor: SHelperFunctions.withOpacity(SColors.info, 0.08),
                        textColor: SColors.info,
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildInfoPill({
    required IconData icon,
    required String label,
    required Color backgroundColor,
    required Color textColor,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 6.0),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(SSizes.borderRadiusLg),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14.0, color: textColor),
          const SizedBox(width: 4.0),
          Text(
            label,
            style: TextStyle(
              fontSize: 12.0,
              fontWeight: FontWeight.w700,
              color: textColor,
            ),
          ),
        ],
      ),
    );
  }

  String _capitalize(String text) {
    if (text.isEmpty) return text;
    return text.split(' ').map((word) {
      if (word.isEmpty) return word;
      return '${word[0].toUpperCase()}${word.substring(1).toLowerCase()}';
    }).join(' ');
  }

  String _formatLabel(String value) {
    return _capitalize(value.replaceAll('_', ' '));
  }
}
