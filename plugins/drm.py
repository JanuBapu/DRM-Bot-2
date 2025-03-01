from fileinput import filename
from pyrogram import filters, Client as ace
from main import LOGGER, prefixes
from pyrogram.types import Message
from main import Config
import os
import subprocess
import tgcrypto
import shutil
import sys
from handlers.uploader import Upload_to_Tg
from handlers.tg import TgClient

@ace.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("drm", prefixes=prefixes)
)
async def drm(bot: ace, m: Message):
    path = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
    tPath = f"{Config.DOWNLOAD_LOCATION}/THUMB/{m.chat.id}"
    os.makedirs(path, exist_ok=True)

    # Request MPD link, name, quality, and caption
    inputData = await bot.ask(m.chat.id, "**Send**\n\nMPD\nNAME\nQUALITY\nCAPTION")
    mpd, raw_name, Q, CP = inputData.text.split("\n")
    name = f"{TgClient.parse_name(raw_name)} ({Q}p)"
    print(mpd, name, Q)

    # ✅ Hardcoded DRM Keys
    keys = "--key ebf95581b80f590b34ef8f9b02689c99:e23bf08b4ffea7c171cd780e51c98ccc " \
           "--key 077c097ec88826f2c268ddb94422f73f:18146a4bdf15e6c6ecf5b1e84e61b5a4 " \
           "--key bd4959ec1b83e901ad2ec67cbf4279f7:813948634df9e34050de5a0f98d267ca"

    print(f"Using DRM Keys: {keys}")

    BOT = TgClient(bot, m, path)
    Thumb = await BOT.thumb()
    prog = await bot.send_message(m.chat.id, f"**Downloading DRM Video!** - [{name}]({mpd})")

    # Step 1: Download Encrypted Video & Audio
    cmd1 = f'yt-dlp -o "{path}/fileName.%(ext)s" -f "bestvideo[height<={int(Q)}]+bestaudio" --allow-unplayable-format --external-downloader aria2c "{mpd}"'
    os.system(cmd1)

    avDir = os.listdir(path)
    print(avDir)
    print("Decrypting...")

    try:
        # Step 2: Decrypt Video & Audio
        for data in avDir:
            if data.endswith("mp4"):
                cmd2 = f'mp4decrypt {keys} --show-progress "{path}/{data}" "{path}/video.mp4"'
                os.system(cmd2)
                os.remove(f'{path}/{data}')
            elif data.endswith("m4a"):
                cmd3 = f'mp4decrypt {keys} --show-progress "{path}/{data}" "{path}/audio.m4a"'
                os.system(cmd3)
                os.remove(f'{path}/{data}')

        # Step 3: Merge Video & Audio
        cmd4 = f'ffmpeg -i "{path}/video.mp4" -i "{path}/audio.m4a" -c copy "{path}/{name}.mp4"'
        os.system(cmd4)
        os.remove(f"{path}/video.mp4")
        os.remove(f"{path}/audio.m4a")

        filename = f"{path}/{name}.mp4"
        cc = f"{name}.mp4\n\n**Description:-**\n{CP}"

        # Step 4: Upload to Telegram
        UL = Upload_to_Tg(bot=bot, m=m, file_path=filename, name=name,
                          Thumb=Thumb, path=path, show_msg=prog, caption=cc)
        await UL.upload_video()

        print("Decryption & Upload Completed!")

    except Exception as e:
        await prog.delete(True)
        await m.reply_text(f"**Error**\n\n`{str(e)}`\n\nOr maybe the video is not available in {Q}p")

    finally:
        # Clean up temporary files
        if os.path.exists(tPath):
            shutil.rmtree(tPath)
        shutil.rmtree(path)
        await m.reply_text("Done")
        
