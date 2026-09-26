#!/bin/bash
# Run OUTSIDE (needs docker). But we can't docker-in-docker. Instead: the file was corrupted by
# PowerShell redirection. Re-copy using docker cp semantics via a container that writes to /work.
# This script runs INSIDE ctf-env which has the libc? No. We must extract from debian image on host.
echo "placeholder"
