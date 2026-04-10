import asyncio, aiohttp, aiosqlite, datetime, os
from disnake import Webhook
from bs4 import BeautifulSoup

#####################
# Main Bot Settings #
#####################

# The Name Is Not Actually Used
# I found it easier to keep track

CHANNELS_TO_CHECK = {
    "LucaTheGuide" : "UC0zrazFd2Qx6iSODhr3tkqw",
    "LucaTheShopkeeper" : "UCdTTM2b7ofMIpauCby6CImw"
}

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

BOT_NAME = "LucaTheBot"
BOT_IMAGE = "https://cdn.discordapp.com/icons/656070244321984532/fcfd0a039781de6bd1db261d3cb8b225.webp?size=80&quality=lossless"

# Please use '{}' where you want the values to go
# You can use a number in the brackets to change the order
# For example '{1}' would be the title
# They are in the order below:
# 0: Youtuber Name
# 1: Title
# 2: Link
# 3: Date

BOT_MESSAGE = "@everyone\nNew Upload From {0}!\t{3}\n{1}\n{2}"

#####################

LAST_YEAR = datetime.datetime.now().year - 1

def main():
    if __name__ == "__main__":
        m_loop = asyncio.get_event_loop()
        m_loop.run_until_complete(check_channel())
        m_loop.run_forever()

async def connect_to_db():
    return await aiosqlite.connect("LucaTheDatabase.db")

async def start_webhook(title, link, name, date):
    async with aiohttp.ClientSession() as session:

        webhook = Webhook.from_url(WEBHOOK_URL, session = session)

        await webhook.send(content = BOT_MESSAGE.format(name, title, link, date), username = BOT_NAME, avatar_url = BOT_IMAGE)

        await asyncio.sleep(3)

        db = await connect_to_db()

        pointer = await db.execute("INSERT INTO Videos VALUES (?, ?, ?, ?)", (title, link, name, date))

        print(f"LOG || Added new video to Database > {title, link}")

        await db.commit()

        await pointer.close()

        await db.close()


async def check_channel():
    while True:
        for channel_id in CHANNELS_TO_CHECK:
            async with aiohttp.ClientSession() as session:
                await asyncio.sleep(18)
                async with session.get(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNELS_TO_CHECK[channel_id]}") as response:
                    response_soup = BeautifulSoup(await response.text(), "lxml")

                    for video in response_soup.find_all("entry"):
                        for title in video.find_all("title"):
                            title = title.text
                        
                        for link in video.find_all("link"):
                            link = link['href']

                        for name in video.find_all("name"):
                            name = name.text

                        for date in video.find_all("published"):
                            date = date.text[:10]

                        db = await connect_to_db()

                        pointer = await db.execute("CREATE TABLE IF NOT EXISTS Videos(title, link, name, date)")
                        await db.commit()
                        await pointer.close()

                        video_check = await db.execute(f"SELECT * FROM Videos WHERE title = ?", (title,))
                        videos_fetched = await video_check.fetchall()

                        if len(videos_fetched) < 1:
                            vid_date = datetime.datetime.strptime(date, "%Y-%m-%d")
                            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1))

                            # We want to post videos from yesterday or newer
                            if vid_date >= yesterday:
                                await start_webhook(title, link, name, date)
                            else:
                                old_vid = await db.execute("INSERT INTO Videos VALUES (?, ?, ?, ?)", (title, link, name, date))
                                await db.commit()
                                await old_vid.close()
                            await video_check.close()
                            await db.close()

main()