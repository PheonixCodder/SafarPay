import 'dart:async';
import 'dart:io';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart' as rtc;
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';
import 'package:record/record.dart';

import '../../../common/runtime/app_lifecycle_controller.dart';
import '../../../common/runtime/runtime_diagnostics_controller.dart';
import '../../../utils/helpers/helpers.dart';
import '../../../utils/http/client.dart';
import '../../rides/orchestration/ride_realtime_orchestrator.dart';
import '../data/communication_repository.dart';
import '../data/communication_socket_event.dart';
import '../data/communication_socket_repository.dart';
import '../domain/communication_models.dart';

class SRideCommunicationController extends GetxController {
  SRideCommunicationController({
    required this.rideId,
    this.notificationCallId,
    this.openCallOnLoad = false,
    SCommunicationRepository repository = const SCommunicationRepository(),
    SCommunicationSocketRepository? socketRepository,
    SAppLifecycleController? appLifecycleController,
    SRideRealtimeOrchestrator? realtimeOrchestrator,
  })  : _repository = repository,
        _socketRepository =
            socketRepository ?? SCommunicationSocketRepository(),
        _appLifecycleController =
            appLifecycleController ?? SAppLifecycleController.instance,
        _realtimeOrchestrator =
            realtimeOrchestrator ?? SRideRealtimeOrchestrator.instance;

  final String rideId;
  final String? notificationCallId;
  final bool openCallOnLoad;
  final SCommunicationRepository _repository;
  final SCommunicationSocketRepository _socketRepository;
  final SAppLifecycleController _appLifecycleController;
  final SRideRealtimeOrchestrator _realtimeOrchestrator;
  final ImagePicker _imagePicker = ImagePicker();
  final AudioRecorder _recorder = AudioRecorder();
  final AudioPlayer _audioPlayer = AudioPlayer();

  final RxBool isLoading = false.obs;
  final RxBool isSending = false.obs;
  final RxBool isRecording = false.obs;
  final RxBool isInCall = false.obs;
  final RxBool isMuted = false.obs;
  final RxString errorMessage = ''.obs;
  final RxString draft = ''.obs;
  final RxString callStatusText = 'Ready'.obs;
  final RxBool shouldPresentCallScreen = false.obs;
  final Rxn<SConversation> conversation = Rxn<SConversation>();
  final Rxn<SCommunicationCall> activeCall = Rxn<SCommunicationCall>();
  final RxList<SCommunicationMessage> messages = <SCommunicationMessage>[].obs;
  final RxSet<String> ownParticipantIds = <String>{}.obs;

  StreamSubscription<SCommunicationSocketEvent>? _socketSub;
  rtc.RTCPeerConnection? _peerConnection;
  rtc.MediaStream? _localStream;
  Timer? _typingTimer;
  Worker? _appLifecycleWorker;

  @override
  void onInit() {
    super.onInit();
    _appLifecycleWorker = ever<AppLifecycleState>(
      _appLifecycleController.state,
      (state) {
        if (state == AppLifecycleState.resumed) {
          unawaited(recoverRealtimeState());
        }
      },
    );
    unawaited(connect());
  }

  @override
  void onClose() {
    _typingTimer?.cancel();
    _socketSub?.cancel();
    _appLifecycleWorker?.dispose();
    _socketRepository.close();
    SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
      SRuntimeRealtimeChannel.communication,
      isConnected: false,
    );
    _recorder.dispose();
    _audioPlayer.dispose();
    _disposeCall();
    super.onClose();
  }

  Future<void> connect() async {
    isLoading.value = true;
    errorMessage.value = '';
    try {
      final resolved = await _resolveConversationWithRetry();
      conversation.value = resolved;
      await refreshMessages();
      if (notificationCallId != null && notificationCallId!.isNotEmpty) {
        await hydrateNotificationCall(
          notificationCallId!,
          presentCallScreen: openCallOnLoad,
        );
      }
      if (_realtimeOrchestrator.shouldConnectCommunicationSocketForRide(
        rideId,
      )) {
        _connectSocket(resolved.id);
      }
    } catch (_) {
      errorMessage.value = 'Ride chat is not ready yet.';
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> refreshMessages() async {
    final current = conversation.value;
    if (current == null) return;
    messages.assignAll(await _repository.messages(current.id));
    unawaited(_hydrateMediaUrls());
  }

  void updateDraft(String value) {
    draft.value = value;
    final current = conversation.value;
    if (current == null) return;
    _socketRepository.typingStarted(current.id);
    _typingTimer?.cancel();
    _typingTimer = Timer(const Duration(seconds: 2), () {
      _socketRepository.typingStopped(current.id);
    });
  }

  Future<void> sendText() async {
    final current = conversation.value;
    final body = draft.value.trim();
    if (current == null || body.isEmpty || isSending.value) return;
    isSending.value = true;
    try {
      final message = await _repository.sendText(
        conversationId: current.id,
        body: body,
      );
      ownParticipantIds.add(message.senderParticipantId);
      _appendMessage(message);
      draft.value = '';
    } catch (_) {
      SHelperFunctions.showSnackBar('Unable to send message.');
    } finally {
      isSending.value = false;
    }
  }

  Future<void> sendImage() async {
    final file = await _imagePicker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 82,
    );
    if (file == null) return;
    final bytes = await file.readAsBytes();
    await _sendMedia(
      bytes: bytes,
      mediaType: SCommunicationMediaType.image,
      mimeType: _imageMimeType(file.name),
      fileName: file.name,
    );
  }

  Future<void> toggleRecording() async {
    if (isRecording.value) {
      await _stopAndSendVoiceNote();
      return;
    }
    if (!await _recorder.hasPermission()) {
      SHelperFunctions.showSnackBar('Microphone permission is required.');
      return;
    }
    final path =
        '${Directory.systemTemp.path}/safarpay-voice-${DateTime.now().millisecondsSinceEpoch}.m4a';
    await _recorder.start(
      const RecordConfig(encoder: AudioEncoder.aacLc),
      path: path,
    );
    isRecording.value = true;
  }

  Future<void> playVoiceNote(SCommunicationMessage message) async {
    var url = message.mediaUrl;
    if (url == null || url.isEmpty) {
      url = await _repository.mediaUrl(message.id);
      _replaceMessage(message.copyWith(mediaUrl: url));
    }
    await _audioPlayer.play(UrlSource(url));
  }

  Future<void> startVoiceCall() async {
    final current = conversation.value;
    if (current == null || isInCall.value) return;
    callStatusText.value = 'Calling...';
    isInCall.value = true;
    try {
      await _preparePeerConnection();
      final offer = await _peerConnection!.createOffer();
      await _peerConnection!.setLocalDescription(offer);
      final call = await _repository.startCall(
        conversationId: current.id,
        initialOffer: _descriptionPayload(offer),
      );
      activeCall.value = call;
      _socketRepository.sendOffer(
        conversationId: current.id,
        callId: call.id,
        payload: _descriptionPayload(offer),
      );
      callStatusText.value = 'Ringing...';
    } catch (_) {
      callStatusText.value = 'Call failed';
      isInCall.value = false;
      await _disposeCall();
      SHelperFunctions.showSnackBar('Unable to start call.');
    }
  }

  Future<void> acceptIncomingCall() async {
    final current = conversation.value;
    final call = activeCall.value;
    final offer = call?.initialOffer;
    if (current == null || call == null || offer == null) return;
    callStatusText.value = 'Connecting...';
    isInCall.value = true;
    try {
      await _preparePeerConnection();
      await _peerConnection!.setRemoteDescription(_descriptionFrom(offer));
      final answer = await _peerConnection!.createAnswer();
      await _peerConnection!.setLocalDescription(answer);
      _socketRepository.sendAnswer(
        conversationId: current.id,
        callId: call.id,
        payload: _descriptionPayload(answer),
      );
      callStatusText.value = 'Connected';
    } catch (_) {
      await endCall(status: SCommunicationCallStatus.failed);
    }
  }

  Future<void> rejectIncomingCall() {
    return endCall(status: SCommunicationCallStatus.rejected);
  }

  Future<void> endCall({
    SCommunicationCallStatus status = SCommunicationCallStatus.ended,
  }) async {
    final call = activeCall.value;
    try {
      if (call != null) {
        await _repository.endCall(callId: call.id, status: status);
      }
    } catch (_) {
      // Local cleanup still matters if the call is already terminal server-side.
    }
    callStatusText.value = 'Ended';
    isInCall.value = false;
    activeCall.value = null;
    shouldPresentCallScreen.value = false;
    await _disposeCall();
  }

  Future<void> recoverRealtimeState() async {
    if (isClosed) return;
    final current = conversation.value;
    if (current == null) {
      await connect();
      return;
    }
    await refreshMessages();
    if (_realtimeOrchestrator.shouldConnectCommunicationSocketForRide(rideId)) {
      _connectSocket(current.id);
    } else {
      await _socketSub?.cancel();
      _socketSub = null;
      await _socketRepository.close();
      SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
        SRuntimeRealtimeChannel.communication,
        isConnected: false,
      );
    }
  }

  void markCallScreenPresented() {
    shouldPresentCallScreen.value = false;
  }

  Future<void> hydrateNotificationCall(
    String callId, {
    bool presentCallScreen = true,
  }) async {
    await _restoreCallFromNotification(callId);
    if (presentCallScreen && activeCall.value != null) {
      shouldPresentCallScreen.value = true;
    }
  }

  void toggleMute() {
    isMuted.value = !isMuted.value;
    final enabled = !isMuted.value;
    for (final track
        in _localStream?.getAudioTracks() ?? <rtc.MediaStreamTrack>[]) {
      track.enabled = enabled;
    }
  }

  Future<SConversation> _resolveConversationWithRetry() async {
    SHttpException? lastError;
    for (var attempt = 0; attempt < 6; attempt++) {
      try {
        return await _repository.conversationByRide(rideId);
      } on SHttpException catch (error) {
        lastError = error;
        if (error.statusCode != 404) rethrow;
        await Future<void>.delayed(const Duration(milliseconds: 700));
      }
    }
    throw lastError ??
        const SHttpException(message: 'Not found', statusCode: 404);
  }

  void _connectSocket(String conversationId) {
    _socketSub?.cancel();
    SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
      SRuntimeRealtimeChannel.communication,
      isConnected: true,
    );
    _socketSub = _socketRepository.connect(conversationId).listen(
          _handleSocketEvent,
          onError: (_) {
            SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
              SRuntimeRealtimeChannel.communication,
              isConnected: false,
            );
            errorMessage.value = 'Chat is reconnecting...';
          },
          onDone: () {
            SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
              SRuntimeRealtimeChannel.communication,
              isConnected: false,
            );
          },
        );
  }

  Future<void> _handleSocketEvent(SCommunicationSocketEvent event) async {
    if (event.message != null) {
      _appendMessage(event.message!);
      if (event.message!.isImage || event.message!.isVoiceNote) {
        unawaited(_hydrateMediaUrl(event.message!));
      }
      return;
    }
    if (event.type == SCommunicationSocketEventType.callRinging &&
        event.call != null) {
      activeCall.value = event.call;
      callStatusText.value = 'Incoming call';
      if (openCallOnLoad) {
        shouldPresentCallScreen.value = true;
      }
      return;
    }
    if (event.type == SCommunicationSocketEventType.callAccepted) {
      callStatusText.value = 'Connected';
      isInCall.value = true;
      return;
    }
    if (event.type == SCommunicationSocketEventType.callEnded) {
      await endCall();
      return;
    }
    if (event.type == SCommunicationSocketEventType.webRtcOffer &&
        event.callId != null &&
        event.payload != null) {
      activeCall.value = SCommunicationCall(
        id: event.callId!,
        conversationId: conversation.value?.id ?? '',
        callerParticipantId: event.senderParticipantId ?? '',
        calleeParticipantId: '',
        status: SCommunicationCallStatus.ringing,
        initialOffer: event.payload,
      );
      callStatusText.value = 'Incoming call';
      return;
    }
    if (event.type == SCommunicationSocketEventType.webRtcAnswer &&
        event.payload != null) {
      await _peerConnection?.setRemoteDescription(
        _descriptionFrom(event.payload!),
      );
      callStatusText.value = 'Connected';
      return;
    }
    if (event.type == SCommunicationSocketEventType.webRtcIceCandidate &&
        event.payload != null) {
      await _peerConnection?.addCandidate(_candidateFrom(event.payload!));
    }
  }

  Future<void> _restoreCallFromNotification(String callId) async {
    try {
      final call = await _repository.callById(callId);
      activeCall.value = call;
      callStatusText.value =
          call.status == SCommunicationCallStatus.accepted
              ? 'Connected'
              : 'Incoming call';
    } catch (_) {
      // Ignore stale call notifications and keep chat usable.
    }
  }

  Future<void> _sendMedia({
    required Uint8List bytes,
    required SCommunicationMediaType mediaType,
    required String mimeType,
    String? fileName,
    double? durationSeconds,
  }) async {
    final current = conversation.value;
    if (current == null || isSending.value) return;
    isSending.value = true;
    try {
      final ticket = await _repository.createMediaUpload(
        conversationId: current.id,
        mediaType: mediaType,
        mimeType: mimeType,
        sizeBytes: bytes.length,
        fileName: fileName,
        durationSeconds: durationSeconds,
      );
      await _repository.uploadMediaBytes(ticket: ticket, bytes: bytes);
      final message = await _repository.registerMediaMessage(
        conversationId: current.id,
        mediaId: ticket.mediaId,
      );
      ownParticipantIds.add(message.senderParticipantId);
      _appendMessage(message);
      unawaited(_hydrateMediaUrl(message));
    } catch (_) {
      SHelperFunctions.showSnackBar('Unable to send attachment.');
    } finally {
      isSending.value = false;
    }
  }

  Future<void> _stopAndSendVoiceNote() async {
    final path = await _recorder.stop();
    isRecording.value = false;
    if (path == null || path.isEmpty) return;
    final file = File(path);
    if (!await file.exists()) return;
    await _sendMedia(
      bytes: await file.readAsBytes(),
      mediaType: SCommunicationMediaType.voiceNote,
      mimeType: 'audio/mp4',
      fileName: 'voice-note.m4a',
    );
  }

  Future<void> _hydrateMediaUrls() async {
    for (final message
        in messages.where((item) => item.isImage || item.isVoiceNote)) {
      await _hydrateMediaUrl(message);
    }
  }

  Future<void> _hydrateMediaUrl(SCommunicationMessage message) async {
    try {
      final url = await _repository.mediaUrl(message.id);
      if (url.isNotEmpty) _replaceMessage(message.copyWith(mediaUrl: url));
    } catch (_) {}
  }

  Future<void> _preparePeerConnection() async {
    final iceServers = await _repository.iceServers();
    _localStream ??= await rtc.navigator.mediaDevices.getUserMedia({
      'audio': true,
      'video': false,
    });
    final peerConnection = await rtc.createPeerConnection({
      'iceServers': iceServers.isEmpty
          ? [
              {
                'urls': ['stun:stun.l.google.com:19302']
              },
            ]
          : iceServers,
    });
    for (final track in _localStream!.getTracks()) {
      await peerConnection.addTrack(track, _localStream!);
    }
    peerConnection.onIceCandidate = (candidate) {
      final current = conversation.value;
      final call = activeCall.value;
      if (current == null || call == null || candidate.candidate == null) {
        return;
      }
      _socketRepository.sendIceCandidate(
        conversationId: current.id,
        callId: call.id,
        payload: _candidatePayload(candidate),
      );
    };
    _peerConnection = peerConnection;
  }

  Future<void> _disposeCall() async {
    await _peerConnection?.close();
    _peerConnection = null;
    _localStream?.getTracks().forEach((track) => track.stop());
    await _localStream?.dispose();
    _localStream = null;
  }

  void _appendMessage(SCommunicationMessage message) {
    if (messages.any((item) => item.id == message.id)) return;
    messages.add(message);
  }

  void _replaceMessage(SCommunicationMessage message) {
    final index = messages.indexWhere((item) => item.id == message.id);
    if (index == -1) return;
    messages[index] = message;
  }
}

String _imageMimeType(String fileName) {
  final lower = fileName.toLowerCase();
  if (lower.endsWith('.png')) return 'image/png';
  if (lower.endsWith('.webp')) return 'image/webp';
  if (lower.endsWith('.heic')) return 'image/heic';
  return 'image/jpeg';
}

Map<String, dynamic> _descriptionPayload(
    rtc.RTCSessionDescription description) {
  return {
    'sdp': description.sdp,
    'type': description.type,
  };
}

rtc.RTCSessionDescription _descriptionFrom(Map<String, dynamic> payload) {
  return rtc.RTCSessionDescription(
    payload['sdp']?.toString(),
    payload['type']?.toString(),
  );
}

Map<String, dynamic> _candidatePayload(rtc.RTCIceCandidate candidate) {
  return {
    'candidate': candidate.candidate,
    'sdpMid': candidate.sdpMid,
    'sdpMLineIndex': candidate.sdpMLineIndex,
  };
}

rtc.RTCIceCandidate _candidateFrom(Map<String, dynamic> payload) {
  return rtc.RTCIceCandidate(
    payload['candidate']?.toString(),
    payload['sdpMid']?.toString(),
    payload['sdpMLineIndex'] is int ? payload['sdpMLineIndex'] as int : null,
  );
}
