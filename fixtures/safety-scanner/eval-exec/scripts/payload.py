import base64

code = base64.b64decode("cHJpbnQoJ2hlbGxvJyk=")
exec(code)
eval("print('world')")
os.system("whoami")
