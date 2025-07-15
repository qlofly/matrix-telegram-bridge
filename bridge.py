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

import asyncio
import logging
from nio import AsyncClient, RoomMessageText, SyncResponse, WhoamiResponse
from pyrogram import Client, filters
from pyrogram.types import Message
import sys

# ====== SETUP LOGGING ======
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("Matrix-Telegram-Bridge")

# ====== GLOBAL STATE ======
tg_client = None
matrix_client = None

# ====== MATRIX HANDLER ======
async def matrix_message_callback(room, event):
    try:
        if room.room_id != MATRIX_ROOM_ID:
            return
            
        if event.sender != MATRIX_MY_ID:
            logger.debug(f"Ignoring message from {event.sender}")
            return

        if isinstance(event, RoomMessageText):
            message_text = event.body
            logger.info(f"Matrix -> Telegram: {message_text}")

            await tg_client.send_message(
                chat_id=TG_CHAT_ID,
                text=message_text
            )
    except Exception as e:
        logger.error(f"Matrix handler error: {e}")

# ====== TELEGRAM HANDLER ======
async def telegram_message_handler(client, message):
    try:
        if message.chat.id != TG_CHAT_ID:
            return
            
        logger.info(f"Telegram -> Matrix: {message.text}")
        
        await matrix_client.room_send(
            room_id=MATRIX_ROOM_ID,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": message.text
            }
        )
    except Exception as e:
        logger.error(f"Telegram handler error: {e}")

# ====== MATRIX INITIALIZATION ======
async def init_matrix_client():
    try:
        logger.info("Initializing Matrix client...")
        client = AsyncClient(MATRIX_HOMESERVER)
        client.access_token = MATRIX_ACCESS_TOKEN
        
        response = await client.whoami()
        
        if not isinstance(response, WhoamiResponse):
            logger.error(f"Matrix auth failed: {response}")
            return None
            
        logger.info(f"Matrix auth as: {response.user_id}")
        
        joined_rooms = await client.joined_rooms()
        if MATRIX_ROOM_ID not in joined_rooms.rooms:
            logger.warning(f"Not in room: {MATRIX_ROOM_ID}")
            join_response = await client.join(MATRIX_ROOM_ID)
            if hasattr(join_response, 'room_id'):
                logger.info(f"Joined room: {MATRIX_ROOM_ID}")
            else:
                logger.error(f"Join failed: {join_response}")
                return None
                
        logger.info(f"Room access: {MATRIX_ROOM_ID}")
        client.add_event_callback(matrix_message_callback, RoomMessageText)
        return client
        
    except Exception as e:
        logger.error(f"Matrix init failed: {str(e)}")
        return None

# ====== TELEGRAM INITIALIZATION ======
async def init_telegram_client():
    try:
        logger.info("Initializing Telegram client...")
        client = Client(
            "tg_account", 
            api_id=TG_API_ID, 
            api_hash=TG_API_HASH,
            device_model="MatrixBridge"
        )
        
        client.on_message(
            filters.chat(TG_CHAT_ID) & 
            filters.private & 
            filters.text
        )(telegram_message_handler)
        
        return client
        
    except Exception as e:
        logger.error(f"Telegram init failed: {str(e)}")
        return None

# ====== MAIN FUNCTION ======
async def main():
    global tg_client, matrix_client
    
    logger.info("Starting bridge...")
    
    matrix_client = await init_matrix_client()
    if not matrix_client:
        logger.error("Matrix init failed")
        return
        
    tg_client = await init_telegram_client()
    if not tg_client:
        logger.error("Telegram init failed")
        return
        
    await tg_client.start()
    
    next_batch = None
    try:
        while True:
            try:
                sync_response = await matrix_client.sync(
                    timeout=30000,
                    since=next_batch
                )
                
                if hasattr(sync_response, 'next_batch'):
                    next_batch = sync_response.next_batch
                else:
                    logger.warning("No next_batch")
                    await asyncio.sleep(5)
                    continue
                    
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Sync error: {e}")
                await asyncio.sleep(5)
                
    finally:
        logger.info("Stopping...")
        await tg_client.stop()
        await matrix_client.close()
        logger.info("Stopped")

if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
