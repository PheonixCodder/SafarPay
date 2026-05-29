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
            WindowManager.LayoutParams.MATCH_PARENT,
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON or
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.FILL
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
            setPadding(dp(24), dp(80), dp(24), dp(36))
            setBackgroundColor(Color.WHITE)
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT
            )
        }

        val titleView = TextView(this).apply {
            text = title
            textSize = 24f
            setTextColor(Color.rgb(17, 24, 39))
            setTypeface(typeface, Typeface.BOLD)
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                bottomMargin = dp(16)
            }
        }
        val bodyView = TextView(this).apply {
            text = body
            textSize = 16f
            setTextColor(Color.rgb(75, 85, 99))
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        val spacer = View(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                0,
                1.0f
            )
        }
        val actions = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        val dismiss = Button(this).apply {
            text = "Dismiss"
            textSize = 16f
            setTextColor(Color.rgb(75, 85, 99))
            background = GradientDrawable().apply {
                setColor(Color.rgb(243, 244, 246))
                cornerRadius = dp(12).toFloat()
            }
            layoutParams = LinearLayout.LayoutParams(
                0,
                dp(50),
                1.0f
            ).apply {
                rightMargin = dp(8)
            }
            setOnClickListener { stopSelf() }
        }
        val open = Button(this).apply {
            text = "Open"
            textSize = 16f
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply {
                setColor(Color.rgb(0, 121, 131))
                cornerRadius = dp(12).toFloat()
            }
            layoutParams = LinearLayout.LayoutParams(
                0,
                dp(50),
                1.0f
            ).apply {
                leftMargin = dp(8)
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
        root.addView(spacer)
        root.addView(actions)

        return root
    }

    private fun hideOverlay() {
        overlayView?.let { view ->
            runCatching { windowManager?.removeView(view) }
        }
        overlayView = null
    }
}
