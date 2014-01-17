import getpass

HAS_ANDROID = False
def Android():
    try:
        import android
        HAS_ANDROID = True
    except:
        return Mocker("android.Android()")
    return android.Android()

def read_settings():
    result = {}
    try:
        for line in open(".xandroid"):
            if ":" in line:
                key, value = line.split(":")[:2]
                result[key] = value
    except:
        pass
    return result

def write_settings(val):
    s = "\n".join([x + ":" + y for x, y in val.items()])
    open(".xandroid", "w").write(s)

def get_input(name):
    if HAS_ANDROID:
        return Android().dialogGetInput(name).result
    else:
        print("Enter " + name + ":")
        return raw_input()

def get_password(name):
    if HAS_ANDROID:
        return Android().dialogGetPassword(name).result
    else:
        return getpass.getpass(name+":")

def get_saved_input(name):
    settings = read_settings()
    if name in settings:
        return settings[name]
    else:
        return get_input(name)

def get_saved_password(name):
    settings = read_settings()
    if name in settings:
        return settings[name]
    else:
        return get_password(name)

def save(name, value):
    settings = read_settings()
    settings[name] = value
    write_settings(settings)

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
