# Matrix-Telegram Bridge

A simple Python bridge for bidirectional messaging between Telegram and Matrix, designed for personal use cases.

## Key Features
- ↔️ Two-way text messaging
- 🚀 No Matrix server setup required (works with matrix.org)
- 🤖 Uses official Matrix and Telegram APIs
- 🔓 Unencrypted rooms for simplicity (can be upgraded)

## Disclaimer
> This experimental bridge was created with AI assistance and isn't intended for production use. While functional, it may contain imperfections and shouldn't be considered completely secure. It serves as a proof-of-concept that others can build upon.

## How It Works

### Account Setup
1. **Matrix Accounts**:
   - Your personal Matrix account (`@you:matrix.org`)
   - A dedicated "friend account" per Telegram contact (`@friend_user:matrix.org`)

2. **Matrix Room**:
   - Create a private room (unencrypted*) with both accounts
   - Note: Encryption was disabled for simplicity but can be implemented. Requires code modifications to support secure messaging.


### Configuration
```python
# Matrix Settings
MATRIX_HOMESERVER = "https://matrix.org"  # matrix.org or your server
MATRIX_USER_ID = "@friend_user:matrix.org"  # Friend's bridge account
MATRIX_ACCESS_TOKEN = "..."  # Get from Element: Settings > Help > Access Token
MATRIX_ROOM_ID = "!room_id:matrix.org"  # Your private room ID
MATRIX_MY_ID = "@your_account:matrix.org"  # Your Matrix ID

# Telegram Settings
TG_API_ID = 12345  # From https://my.telegram.org/auth
TG_API_HASH = "..."  # From Telegram Dev Center
TG_CHAT_ID = 123456789  # Telegram contact's chat ID

```

### Installation & Running

Install dependencies:
```
pip install pyrogram matrix-nio
```

Run the script:
```
python bridge.py
```

Authenticate when prompted:
```
    Enter phone number or bot token: +1234567890
    Enter verification code: 12345
```
  Subsequent runs won't require re-authentication

Testing

    Send messages from Telegram → Check Matrix room

    Reply in Matrix → Verify Telegram delivery
