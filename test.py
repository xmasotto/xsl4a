import xandroid

droid = xandroid.Android()
message = droid.dialogGetInput("TTS", "What would you like to say?").result
droid.ttsSpeak(message)
