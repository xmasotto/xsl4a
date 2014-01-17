def Android():
    try:
        import android
        return android.Android()
    else:
        return Mocker("android.Android()")

class Mocker():
    def __init__(self, name):
        self.name = name

    def __getattr__(self, name):
        newname = self.name + "." + name
        return Mocker(newname)

    def __call__(self, *args):
        newname = self.name + "()"
        print("Called %s" % newname)
        return Mocker(newname)
