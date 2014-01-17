def android():
    return Mocker("android")

class Mocker():
    def __init__(self, name):
        self.name = name
        try:
            import android
            self.has_android = True
        except:
            self.has_android = False

    def __getattr__(self, name):
        if self.has_android:
            return android.__getattr__(name)
        else:
            newname = self.name + "." + name
            return Mocker(newname)

    def __call__(self, *args):
        newname = self.name + "()"
        print("Called %s" % newname)
        return Mocker(newname)
