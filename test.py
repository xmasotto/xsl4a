import xandroid
android = xandroid.android()

droid = android.Android()
message = droid.dialogGetInput("TTS", "What would you like to say?").result
droid.ttsSpeak(message)
