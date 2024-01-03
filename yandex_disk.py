from config_data import config
import yadisk
import aiofiles
import asyncio
from datetime import datetime

# client = yadisk.AsyncClient(token=config.YADISK_TOKEN.get_secret_value())
client = yadisk.AsyncClient(config.YADISK_SECRET.get_secret_value(), config.YADISK_ID.get_secret_value(), config.YADISK_TOKEN.get_secret_value())


async def upload_backup():
    async with client:
        if await client.check_token():
            await client.upload("currencies_db.sql", f"/Telegram Bots/Курсы криптовалют! backups/currencies_db_{datetime.now().strftime('%d.%m.%Y %H:%M')}.sql")
            # await client.download("/some-file-to-download.txt", "downloaded.txt")

# asyncio.run(upload_backup())


