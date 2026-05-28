package com.example.client

import android.content.Intent
import android.net.Uri
import android.provider.Settings
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val overlayChannelName = "safarpay/driver_overlay"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, overlayChannelName)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "canDrawOverlays" -> result.success(Settings.canDrawOverlays(this))
                    "openOverlaySettings" -> {
                        val intent = Intent(
                            Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                            Uri.parse("package:$packageName")
                        )
                        startActivity(intent)
                        result.success(null)
                    }
                    "showDriverRideOverlay" -> {
                        if (!Settings.canDrawOverlays(this)) {
                            result.success(false)
                            return@setMethodCallHandler
                        }
                        val intent = Intent(this, DriverRideOverlayService::class.java).apply {
                            putExtra("title", call.argument<String>("title") ?: "New ride request")
                            putExtra(
                                "body",
                                call.argument<String>("body") ?: "A passenger request is available near you."
                            )
                            putExtra("ride_id", call.argument<String>("rideId") ?: "")
                            putExtra("deeplink", call.argument<String>("deeplink") ?: "")
                        }
                        startService(intent)
                        result.success(true)
                    }
                    "hideDriverRideOverlay" -> {
                        stopService(Intent(this, DriverRideOverlayService::class.java))
                        result.success(null)
                    }
                    "consumeOverlayIntent" -> result.success(consumeOverlayIntent())
                    else -> result.notImplemented()
                }
            }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
    }

    private fun consumeOverlayIntent(): Map<String, String>? {
        val currentIntent = intent ?: return null
        val deeplink = currentIntent.getStringExtra("safarpay_deeplink") ?: return null
        val rideId = currentIntent.getStringExtra("ride_id") ?: ""
        currentIntent.removeExtra("safarpay_deeplink")
        currentIntent.removeExtra("ride_id")
        return mapOf(
            "notification_kind" to "driver_ride_request",
            "deeplink" to deeplink,
            "ride_id" to rideId,
        )
    }
}
