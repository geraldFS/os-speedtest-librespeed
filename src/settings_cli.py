#!/usr/local/bin/python3
"""Configd-only root settings helper: show or save base64url encoded validated JSON."""
import base64
import json
import sys
from librespeed_settings import read_settings, save_settings

def main():
    if len(sys.argv) == 1:
        return {'settings':read_settings(), 'error':None}
    if len(sys.argv) != 2:
        raise ValueError('expected zero or one argument')
    encoded = sys.argv[1]
    if len(encoded) > 4096 or not encoded.isascii() or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_' for c in encoded):
        raise ValueError('invalid settings payload')
    data = json.loads(base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4)))
    return {'settings':save_settings(data), 'error':None}

if __name__ == '__main__':
    try:
        print(json.dumps(main(), separators=(',', ':')))
    except Exception as e:
        print(json.dumps({'error':str(e)[:200]}))
        sys.exit(1)
