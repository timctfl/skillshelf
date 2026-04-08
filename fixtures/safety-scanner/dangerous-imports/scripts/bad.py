import subprocess
import socket
from http.client import HTTPConnection

result = subprocess.run(["ls", "-la"], capture_output=True)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = HTTPConnection("example.com")
