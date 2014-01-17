import xandroid

droid = xandroid.Android()
message = droid.dialogGetInput("TTS", "What would you like to say?").result
droid.ttsSpeak(message)

print(xandroid.getSavedInput("test_username"))
print(xandroid.getSavedPassword("test_password"))
