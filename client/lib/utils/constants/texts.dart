// This class contains all the App Text in String formats.

class STexts {
  STexts._();

  // -- GLOBAL Texts

  // -- OnBoarding Texts
  static const String onBoardingTitle1 = "Get There Faster";
  static const String onBoardingTitle2 = "Feel Safe, Ride Smart";
  static const String onBoardingTitle3 = "Ride at Honest Prices";

  static const String onBoardingSubTitle1 =
      "Find a nearby driver and ride within minutes, anytime, anywhere.";
  static const String onBoardingSubTitle2 =
      "With verified drivers and ride tracking, your safety is built into every trip.";
  static const String onBoardingSubTitle3 =
      "No hidden charges. What you see is what you pay, always.";
  static const String onBoardingNext = "Next";
  static const String onBoardingSkip = "Skip";
  static const String onBoardingGetStarted = "Get Started";

  // -- Permissions Pages
  static const String locationTitle = "What is Your Location?";
  static const String notificationsTitle = "Enable Notification Access";

  static const String locationSubTitle =
      "We need to know your location in order to suggest nearby services";
  static const String notificationsSubTitle =
      "Enable Notification to receive real-time updates";
  static const String allowLocationAccess = "Allow Location Access";
  static const String allowNotificationAccess = "Allow Notification Access";
  static const String permissionDenied = "Permission is required to continue.";
  static const String permissionsCompleted = "Permissions completed.";

  // -- Home
  static const String homeAppbarTitle = "Skip the wait. Command the road.";
  static const String homeAppbarSubTitle = "DriveOn";
  static const String homeTitle = "Welcome to SafarPay";
  static const String homeSubTitle =
      "Your basic home screen is ready after permissions are completed.";
  static const String navHome = "Home";
  static const String searchBarText = "Where to?";
  static const String rideSearchTitle = "Plan your ride";
  static const String rideSearchSubTitle = "Choose a pickup and dropoff.";
  static const String rideSearchPickup = "Pickup";
  static const String rideSearchDropoffHint = "Search dropoff";
  static const String rideSearchUseSearchPickup = "Set pickup by search";
  static const String rideSearchNoResults = "Search for a destination.";
  static const String ridePreviewTitle = "Ride Preview";
  static const String ridePreviewConfirm = "Confirm ride";
  static const String ridePreviewRequesting = "Requesting...";
  static const String ridePreviewUnavailable = "Route preview unavailable";
  static const String rideTrackingTitle = "Live Ride";
  static const String rideTrackingConnecting = "Connecting to ride tracking...";
  static const String navTrips = "Trips";
  static const String navRent = "Rent";
  static const String navProfile = "Profile";
  static const String driverNavHome = "Drive";
  static const String driverNavRequests = "Requests";
  static const String driverNavEarnings = "Earnings";
  static const String driverNavHomeTitle = "Driver Home";
  static const String driverNavHomeSubTitle =
      "Driver availability, nearby demand, and active trip controls will appear here.";
  static const String driverNavRequestsTitle = "Ride Requests";
  static const String driverNavRequestsSubTitle =
      "Incoming ride offers and accepted trip requests will appear here.";
  static const String driverNavEarningsTitle = "Earnings";
  static const String driverNavEarningsSubTitle =
      "Daily totals, payouts, and earning history will appear here.";
  static const String tripsTabTitle = "Trips";
  static const String tripsTabSubTitle =
      "Your upcoming and completed rides will appear here once ride booking is connected.";
  static const String rentTabTitle = "Rent";
  static const String rentTabSubTitle =
      "Rental options and saved vehicle choices will appear here in a future ride feature.";
  static const String profileTabTitle = "Profile";
  static const String profileTabSubTitle =
      "Account details, saved preferences, and safety settings will appear here as the profile area grows.";

  // -- Trips
  static const String tripsTitle = "Trips";
  static const String tripsOngoing = "Ongoing";
  static const String tripsScheduled = "Scheduled";
  static const String tripsCanceled = "Canceled";
  static const String tripsCompleted = "Completed";
  static const String tripsPickup = "Pickup";
  static const String tripsDropoff = "Dropoff";
  static const String tripsViewDetails = "View details";
  static const String tripsPayment = "Payment";
  static const String tripsPrice = "Price";
  static const String tripsScheduledFor = "Scheduled for";
  static const String tripsCancellationReason = "Cancellation reason";
  static const String tripsCreated = "Created";
  static const String tripsCompletedAt = "Completed";
  static const String tripsCanceledAt = "Canceled";
  static const String tripsStops = "Stops";
  static const String tripsRideDetails = "Ride Details";
  static const String tripsRoute = "Route";
  static const String tripsRideSummary = "Ride summary";
  static const String tripsService = "Service";
  static const String tripsCategory = "Category";
  static const String tripsPricing = "Pricing";
  static const String tripsPaymentMethod = "Payment method";
  static const String tripsProofs = "Proof images";
  static const String tripsVerificationCodes = "Verification codes";
  static const String tripsOperational = "Operational";
  static const String tripsDriverAssigned = "Driver assigned";
  static const String tripsDriverPending = "Finding driver";
  static const String tripsNoOngoing = "No ongoing rides";
  static const String tripsNoScheduled = "No scheduled rides";
  static const String tripsNoCanceled = "No canceled rides";
  static const String tripsNoCompleted = "No completed rides";
  static const String tripsEmptySubTitle =
      "Rides in this state will appear here once they are available.";

  // -- Categories
  static const String groceries = "Groceries";
  static const String groceriesEta = "in 30 min";
  static const String categoryNew = "NEW";
  static const String cityRides = "City Rides";
  static const String freight = "Freight";
  static const String courier = "Couriers";
  static const String cityToCity = "City to City";
  static const String categories = "Categories";
  static const String categoriesExplore = "Explore";

  // -- Login
  static const String phoneNo = "Phone Number";
  static const String phoneHelperText = "We'll send you a verification code.";
  static const String sendOtp = "Send OTP";
  static const String otpSent = "OTP sent to your phone number.";
  static const String loginTitle = "Login";
  static const String loginSubTitle =
      "Enter your phone number to continue securely.";
  static const String orContinueWith = "or continue with";
  static const String continueWithGoogle = "Continue with Google";
  static const String googlePhoneRequired =
      "Google login verified. Add your phone number to continue.";
  static const String googleTokenMissing =
      "Google did not return a valid token. Please try again.";
  static const String googleLoginFailed =
      "Google login failed. Please try again.";
  static const String googlePhoneLinkTitle = "Confirm your phone";
  static const String googlePhoneLinkSubTitle =
      "Your Google account is verified. Add a phone number so SafarPay can secure your rides and send trip updates.";
  static const String googleAccountVerified = "Google account verified";
  static const String googlePhoneLinkCta = "Send verification code";
  static const String googleExistingPhoneMasked = "your saved phone";
  static const String googleExistingPhoneResendHint =
      "Please sign in with Google again to resend this code.";
  static const String unexpectedError =
      "Something went wrong. Please try again.";

  // -- OTP
  static const String otpTitle = "Verify your number";
  static const String googleOtpTitlePrefix = "Hi";
  static const String otpSubTitle =
      "Enter the 6-digit code sent to WhatsApp at";
  static const String changeNumber = "Change number";
  static const String verifyOtp = "Verify OTP";
  static const String resendOnWhatsapp = "Resend on WhatsApp";
  static const String resendOtpIn = "Resend code in";
  static const String otpSentWhatsapp = "OTP sent on WhatsApp.";
  static const String otpVerified = "OTP verified.";
  static const String invalidOtp = "Enter the 6-digit code.";

  // -- Complete Profile
  static const String completeProfileTitle = "Complete your Profile";
  static const String completeProfileSubTitle =
      "Tell us a little about yourself to finish setting up your account.";
  static const String firstName = "First Name";
  static const String lastName = "Last Name";
  static const String emailAddress = "Email Address";
  static const String continueText = "Continue";
  static const String profileGenderMale = "Male";
  static const String profileGenderFemale = "Female";
  static const String profileGenderOther = "Other";
  static const String profileGenderRequired = "Gender is required.";
  static const String profileDateOfBirthRequired = "Date of birth is required.";
  static const String profileDateOfBirthMinimumAge =
      "You must be at least 13 years old.";
  static const String acceptTermsRequired =
      "Please accept the privacy policy and terms of use.";
  static const String profileCompleted = "Profile completed.";
  static const String iAgreeTo = "I agree to";
  static const String privacyPolicy = "Privacy Policy";
  static const String termsOfUse = "Terms of use";
  static const String verificationCode = "verificationCode";
  static const String resendEmail = "Resend Code";
  static const String resendEmailIn = "Resend Code in";

  // -- Settings
  static const String settingsAccount = "Account";
  static const String currentUserFallbackName = "User";
  static const String currentUserNoEmail = "No email added";
  static const String currentUserNoPhone = "No phone added";
  static const String profileNotSet = "Not set";
  static const String accountSettings = "Account Settings";
  static const String appSettings = "App Settings";
  static const String logout = "Logout";
  static const String switchToDriverMode = "Switch to Driver Mode";
  static const String switchToPassengerMode = "Switch to Passenger Mode";
  static const String userInfo = "User Info";
  static const String userInfoSubTitle = "Update your basic info and image";
  static const String settingsPayments = "Payments";
  static const String settingsPaymentsSubTitle =
      "Add, remove and manage payment methods";
  static const String settingsSupport = "Help & Support";
  static const String settingsSupportSubTitle =
      "Find answers, explore guides, and contact our team for assistance.";
  static const String driver = "Register as a Driver";
  static const String driverSubTitle =
      "Turn your vehicle into profit and start earning on your own terms.";
  static const String driverRegistrationTitle =
      "How do you want to work with us";
  static const String driverVehicleSelectionTitle = "Choose your vehicle";
  static const String driverVehicleReuseDialogTitle = "Use existing vehicle?";
  static const String driverVehicleReuseDialogMessage =
      "Your {vehicle} is already registered. Do you want to use it for {service} too?";
  static const String driverVehicleReuseCancel = "Cancel";
  static const String driverVehicleReuseConfirm = "Use this vehicle";
  static const String driverVerificationTitle = "Driver Registration";
  static const String driverVerificationHeaderSubtitle =
      "Complete your checklist and submit it for SafarPay review.";
  static const String driverVerificationUnavailable =
      "Driver registration unavailable";
  static const String driverVerificationNotStartedTitle =
      "Start your driver registration";
  static const String driverVerificationNotStartedMessage =
      "Complete each section to prepare your profile for verification review.";
  static const String driverVerificationPendingTitle =
      "Registration in progress";
  static const String driverVerificationPendingMessage =
      "Finish the remaining sections, then submit your profile for review.";
  static const String driverVerificationUnderReviewTitle = "Under review";
  static const String driverVerificationUnderReviewMessage =
      "Your submitted details are locked while SafarPay reviews your driver profile.";
  static const String driverVerificationRejectedTitle = "Action required";
  static const String driverVerificationRejectedMessage =
      "One or more sections need correction before your driver profile can be approved.";
  static const String driverVerificationVerifiedTitle = "Already registered";
  static const String driverVerificationVerifiedMessage =
      "You are already approved for this vehicle. No further action is needed.";
  static const String driverVerificationSubmitReview = "Submit for Review";
  static const String driverVerificationSubmittingReview = "Submitting...";
  static const String driverRegistrationStepSave = "Submit Step";
  static const String driverRegistrationStepSaving = "Submitting...";
  static const String driverRegistrationCamera = "Camera";
  static const String driverRegistrationGallery = "Gallery";
  static const String driverRegistrationRemoveImage = "Remove image";
  static const String driverRegistrationExpiryDate = "Expiry Date";
  static const String driverRegistrationSelectDate = "Select date";
  static const String driverRegistrationCnicTitle = "CNIC Info";
  static const String driverRegistrationCnicNumber = "CNIC Number";
  static const String driverRegistrationCnicFront = "CNIC Front";
  static const String driverRegistrationCnicBack = "CNIC Back";
  static const String driverRegistrationLicenseTitle = "Driver's License";
  static const String driverRegistrationLicenseNumber = "License Number";
  static const String driverRegistrationLicenseFront = "License Front";
  static const String driverRegistrationLicenseBack = "License Back";
  static const String driverRegistrationSelfieTitle = "Selfie with License";
  static const String driverRegistrationSelfieCapture =
      "Capture a live selfie while holding your driving license.";
  static const String driverRegistrationSelfieCaptureAction = "Capture";
  static const String driverRegistrationSelfieRetry = "Retry";
  static const String driverRegistrationSelfieUse = "Use this photo";
  static const String driverRegistrationVehicleInfoTitle = "Vehicle Info";
  static const String driverRegistrationBrand = "Brand";
  static const String driverRegistrationModel = "Model";
  static const String driverRegistrationColor = "Color";
  static const String driverRegistrationVehicleType = "Vehicle Type";
  static const String driverRegistrationMaxPassengers = "Max Passengers";
  static const String driverRegistrationPlateNumber = "Plate Number";
  static const String driverRegistrationProductionYear = "Production Year";
  static const String driverRegistrationRegistrationFront =
      "Registration Front";
  static const String driverRegistrationRegistrationBack = "Registration Back";
  static const String driverRegistrationVehiclePhotoFront =
      "Vehicle Photo Front";
  static const String driverRegistrationVehiclePhotoBack =
      "Vehicle Photo Back";
  static const String driverRegistrationFrontSideHelp =
      "Clear image of the front side.";
  static const String driverRegistrationBackSideHelp =
      "Clear image of the back side.";
  static const String driverRegistrationRegistrationFrontHelp =
      "Front side of the vehicle registration document.";
  static const String driverRegistrationRegistrationBackHelp =
      "Back side of the vehicle registration document.";
  static const String driverRegistrationVehicleFrontHelp =
      "Front view of the vehicle.";
  static const String driverRegistrationVehicleBackHelp =
      "Back view of the vehicle.";
  static const String settingsBankAccount = "Bank Account";
  static const String settingsBankAccountSubTitle =
      "Withdraw balance to registered bank account";
  static const String settingsLocation = "Location";
  static const String settingsLocationSubTitle = "Set your location";
  static const String settingsLocationTrailing = "Address";
  static const String settingsPrivacySecurity = "Privacy & Security";
  static const String settingsPrivacySecuritySubTitle = "Manage your privacy";
  static const String settingsNotifications = "Notifications";
  static const String settingsNotificationsSubTitle = "Manage notifications";
  static const String settingsDarkMode = "Dark Mode";
  static const String settingsDarkModeSubTitle = "Toggle dark mode";

  // -- Privacy Policy
  static const String privacyPolicyTitle = "Privacy Policy";
  static const String privacyPolicyEffectiveDate = "Effective May 16, 2026";
  static const String privacyPolicySummary =
      "SafarPay uses your data to keep rides reliable, payments clear, and safety support available when you need it.";
  static const String privacyPolicyUpdated = "Updated";
  static const String privacyPolicyDataControl = "Data controls";
  static const String privacyPolicyDataControlSubTitle =
      "Manage account, location, and communication choices from settings.";
  static const String privacyPolicySecureHandling = "Secure handling";
  static const String privacyPolicySecureHandlingSubTitle =
      "Sensitive account and trip information is handled with restricted access.";
  static const String privacyPolicyContactTitle = "Questions about privacy?";
  static const String privacyPolicyContactSubTitle =
      "Contact SafarPay support before using the app if any policy detail is unclear.";
  static const String privacyPolicyContactAction = "Contact support";

  // -- Notifications
  static const String notificationsPageTitle = "Notifications";
  static const String notificationsNewUpdates = "new updates";
  static const String notificationsAllCaughtUp = "All caught up";
  static const String notificationsInboxSummary =
      "updates across trips, payments, offers, safety, and account activity";
  static const String notificationsFilterAll = "All";
  static const String notificationsFilterTrips = "Trips";
  static const String notificationsFilterPayments = "Payments";
  static const String notificationsFilterOffers = "Offers";
  static const String notificationsFilterSafety = "Safety";
  static const String notificationsFilterSystem = "System";
  static const String notificationsEmptyTitle = "No notifications here";
  static const String notificationsEmptySubTitle =
      "New updates for this category will appear as your rides, payments, and account activity grow.";

  // -- Help & Support
  static const String helpSupportTitle = "Help & Support";
  static const String helpSupportQuestion = "What can we help you with?";
  static const String helpSupportLiveChat = "Live Chat";
  static const String helpSupportContactUs = "Contact Us";
  static const String helpSupportFaqs = "FAQ's";
  static const String helpSupportTermsConditions = "Terms & Condition";
  static const String helpSupportSomethingElse = "Something else";
  static const String helpSupportPlaceholderSubTitle =
      "This support section will be connected in a future unit.";
  static const String contactTitle = "Let's get in touch!";
  static const String contactSupportPhone = "+92 317 805 9528";
  static const String contactSupportEmail = "support@safarpay.com";

  // -- Edit Drawer
  static const String editDrawerSave = "Save changes";
  static const String editDrawerConfirm = "Confirm";
  static const String editDrawerCancel = "Cancel";
  static const String editDrawerRequired = "This field is required.";
  static const String editDrawerTitlePrefix = "Edit";
  static const String editDrawerDefaultDescription =
      "Update this value and save when you're done.";

  // -- Profile
  static const String profileTitle = "Profile";
  static const String changeProfilePicture = "Change Profile Picture";
  static const String profileInformation = "Profile Information";
  static const String personalInformation = "Personal Information";
  static const String profileName = "Name";
  static const String profileEmail = "E-mail";
  static const String profilePhoneNumber = "Phone Number";
  static const String profileGender = "Gender";
  static const String profileDateOfBirth = "Date of Birth";
  static const String profileUpdated = "Profile updated.";
  static const String profileEditDescription =
      "Update this profile value and save it to your account.";
}
