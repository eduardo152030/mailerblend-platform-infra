#!/usr/bin/env python3
"""Prepare ignored runtime files or discover chat IDs without exposing bot tokens."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request

BASE = Path(__file__).resolve().parents[1] / 'services/infra-prom'


def settings():
    path = BASE / '.env'
    if not path.is_file():
        raise ValueError(f'Create {path} from .env.example and fill in the values.')
    if path.stat().st_mode & 0o077:
        raise ValueError('Restrict .env permissions first: chmod 600 services/infra-prom/.env')
    tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', str(path)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if tracked.returncode == 0:
        raise ValueError('.env is tracked by Git; remove it from the index before proceeding.')
    ignored = subprocess.run(['git', 'check-ignore', '-q', str(path)])
    if ignored.returncode != 0:
        raise ValueError('.env must be ignored by Git.')
    values = {}
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        key, sep, value = line.partition('=')
        if not sep or key not in ('TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID'):
            raise ValueError('Use only KEY=value lines from .env.example; no export or quotes.')
        values[key] = value.strip()
    if not re.fullmatch(r'[0-9]+:[A-Za-z0-9_-]+', values.get('TELEGRAM_BOT_TOKEN', '')):
        raise ValueError('TELEGRAM_BOT_TOKEN is missing or has an invalid format.')
    return values


def api(token, method):
    # Never report urllib exceptions: they can contain the token-bearing URL.
    try:
        request = urllib.request.Request('https://api.telegram.org/bot' + token + '/' + method,
                                         data=b'', method='POST')
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.load(response)
        if not result.get('ok'):
            raise ValueError('Telegram rejected the request.')
        return result['result']
    except Exception:
        raise ValueError('Telegram request failed; verify credentials, network and bot configuration.') from None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chat-id', action='store_true', help='Read pending updates; sends no messages.')
    args = parser.parse_args()
    values = settings()
    if args.chat_id:
        me = api(values['TELEGRAM_BOT_TOKEN'], 'getMe')
        if me.get('username', '').lower() != 'codestacks_bot':
            raise ValueError('The configured token does not belong to @Codestacks_Bot.')
        updates = api(values['TELEGRAM_BOT_TOKEN'], 'getUpdates')
        chats = {}
        for update in updates:
            msg = update.get('message', update.get('channel_post', {}))
            chat = msg.get('chat', {})
            if 'id' in chat:
                chats[chat['id']] = chat.get('type', 'unknown')
        for chat, kind in chats.items():
            print(f'chat_id={chat} type={kind}')
        if not chats:
            print('No pending messages. Send /start and a new message to the bot, then retry.')
        return
    chat = values.get('TELEGRAM_CHAT_ID', '')
    if not re.fullmatch(r'-?[1-9][0-9]*', chat):
        raise ValueError('Set TELEGRAM_CHAT_ID to the numeric destination ID (negative for groups).')
    runtime = BASE / '.runtime'
    runtime.mkdir(mode=0o700, exist_ok=True)
    runtime.chmod(0o700)
    config = (BASE / 'config/alertmanager/alertmanager.yml').read_text()
    (runtime / 'alertmanager.yml').write_text(config.replace('__TELEGRAM_CHAT_ID__', chat))
    (runtime / 'alertmanager.yml').chmod(0o644)
    token = runtime / 'telegram_bot_token'
    if token.exists():
        token.chmod(0o600)
    token.write_text(values['TELEGRAM_BOT_TOKEN'])
    # Parent 0700 restricts host access; container's unprivileged user must read the bind mount.
    token.chmod(0o444)
    print('Ignored runtime files prepared. No network request or deployment performed.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
