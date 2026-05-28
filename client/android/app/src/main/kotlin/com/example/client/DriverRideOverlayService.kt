package com.example.client

import android.app.Service
import android.content.Intent
import android.graphics.Color
import android.graphics.PixelFormat
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.IBinder
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class DriverRideOverlayService : Service() {
    private var windowManager: WindowManager? = null
    private var overlayView: View? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (!Settings.canDrawOverlays(this)) {
            stopSelf()
            return START_NOT_STICKY
        }

        hideOverlay()
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager

        val title = intent?.getStringExtra("title") ?: "New ride request"
        val body = intent?.getStringExtra("body") ?: "A passenger request is available near you."
        val rideId = intent?.getStringExtra("ride_id") ?: ""
        val deeplink = intent?.getStringExtra("deeplink")
            ?: if (rideId.isNotBlank()) "safarpay://driver/requests/$rideId" else "safarpay://driver/requests"

        overlayView = buildOverlay(title, body, rideId, deeplink)
        val layoutType = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON or
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
            y = 56
        }

        windowManager?.addView(overlayView, params)
        return START_NOT_STICKY
    }

    override fun onDestroy() {
        hideOverlay()
        super.onDestroy()
    }

    private fun buildOverlay(title: String, body: String, rideId: String, deeplink: String): View {
        val density = resources.displayMetrics.density
        fun dp(value: Int): Int = (value * density).toInt()

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(16), dp(18), dp(16))
            background = GradientDrawable().apply {
                setColor(Color.WHITE)
                cornerRadius = dp(18).toFloat()
                setStroke(dp(1), Color.rgb(224, 229, 232))
            }
            elevation = dp(12).toFloat()
        }

        val titleView = TextView(this).apply {
            text = title
            textSize = 18f
            setTextColor(Color.rgb(17, 24, 39))
            setTypeface(typeface, Typeface.BOLD)
        }
        val bodyView = TextView(this).apply {
            text = body
            textSize = 14f
            setTextColor(Color.rgb(75, 85, 99))
            setPadding(0, dp(6), 0, dp(14))
        }
        val actions = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.END
        }
        val dismiss = Button(this).apply {
            text = "Dismiss"
            setOnClickListener { stopSelf() }
        }
        val open = Button(this).apply {
            text = "Open"
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply {
                setColor(Color.rgb(0, 121, 131))
                cornerRadius = dp(10).toFloat()
            }
            setOnClickListener {
                val launchIntent = Intent(this@DriverRideOverlayService, MainActivity::class.java).apply {
                    action = "com.example.client.DRIVER_RIDE_REQUEST"
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or
                        Intent.FLAG_ACTIVITY_CLEAR_TOP or
                        Intent.FLAG_ACTIVITY_SINGLE_TOP
                    putExtra("safarpay_deeplink", deeplink)
                    putExtra("ride_id", rideId)
                }
                startActivity(launchIntent)
                stopSelf()
            }
        }

        actions.addView(dismiss)
        actions.addView(open)
        root.addView(titleView)
        root.addView(bodyView)
        root.addView(actions)

        return LinearLayout(this).apply {
            setPadding(dp(14), 0, dp(14), 0)
            addView(root)
        }
    }

    private fun hideOverlay() {
        overlayView?.let { view ->
            runCatching { windowManager?.removeView(view) }
        }
        overlayView = null
    }
}
