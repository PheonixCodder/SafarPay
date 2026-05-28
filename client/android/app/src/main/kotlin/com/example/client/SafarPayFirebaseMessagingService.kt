package com.example.client

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.provider.Settings
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.google.firebase.messaging.RemoteMessage
import io.flutter.plugins.firebase.messaging.FlutterFirebaseMessagingService

class SafarPayFirebaseMessagingService : FlutterFirebaseMessagingService() {
    override fun onMessageReceived(message: RemoteMessage) {
        val data = message.data
        if (data["notification_kind"] != "driver_ride_request") {
            super.onMessageReceived(message)
            return
        }

        val rideId = data["ride_id"].orEmpty()
        val title = data["title"] ?: message.notification?.title ?: "New ride request"
        val body = data["body"]
            ?: data["message"]
            ?: message.notification?.body
            ?: "A passenger request is available near you."
        val deeplink = data["deeplink"].takeUnless { it.isNullOrBlank() }
            ?: if (rideId.isNotBlank()) {
                "safarpay://driver/requests/$rideId"
            } else {
                "safarpay://driver/requests"
            }

        if (Settings.canDrawOverlays(this)) {
            runCatching {
                startService(
                    Intent(this, DriverRideOverlayService::class.java).apply {
                        putExtra("title", title)
                        putExtra("body", body)
                        putExtra("ride_id", rideId)
                        putExtra("deeplink", deeplink)
                    }
                )
            }.onFailure { error ->
                Log.w(TAG, "Unable to show driver ride overlay", error)
                showFallbackNotification(title, body, rideId, deeplink)
            }
            return
        }

        Log.i(TAG, "Overlay permission is missing; showing driver ride fallback notification")
        showFallbackNotification(title, body, rideId, deeplink)
    }

    private fun showFallbackNotification(
        title: String,
        body: String,
        rideId: String,
        deeplink: String,
    ) {
        ensureRideAlertsChannel()
        if (
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            return
        }

        val openIntent = Intent(this, MainActivity::class.java).apply {
            action = "com.example.client.DRIVER_RIDE_REQUEST"
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or
                Intent.FLAG_ACTIVITY_CLEAR_TOP or
                Intent.FLAG_ACTIVITY_SINGLE_TOP
            putExtra("safarpay_deeplink", deeplink)
            putExtra("ride_id", rideId)
        }
        val pendingIntent = PendingIntent.getActivity(
            this,
            rideId.hashCode(),
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val notification = NotificationCompat.Builder(this, RIDE_ALERTS_CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(NotificationCompat.BigTextStyle().bigText(body))
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_TRANSPORT)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build()
        NotificationManagerCompat.from(this).notify(
            rideId.hashCode().takeUnless { it == 0 } ?: title.hashCode(),
            notification,
        )
    }

    private fun ensureRideAlertsChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channel = NotificationChannel(
            RIDE_ALERTS_CHANNEL_ID,
            "Ride alerts",
            NotificationManager.IMPORTANCE_HIGH,
        ).apply {
            description = "Ride requests and active trip updates"
        }
        manager.createNotificationChannel(channel)
    }

    companion object {
        private const val TAG = "SafarPayFCM"
        private const val RIDE_ALERTS_CHANNEL_ID = "ride_alerts"
    }
}
