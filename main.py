import asyncio, logging, datetime, xmltodict, os, aiosqlite
from aiohttp import web, ClientSession
from dotenv import load_dotenv
from pyngrok import ngrok
from disnake import Webhook


logger = logging.getLogger(__name__)

CHANNELS = {
    "LucaTheShopkeeper" : "UCdTTM2b7ofMIpauCby6CImw",
    "LucaTheGuide" : "UC0zrazFd2Qx6iSODhr3tkqw",
    "FoxGaming" : "UCim-6_qUEk5Ft91Vf5oceCA"
}

BOT_NAME = "LucaTheBot"
BOT_IMAGE = "https://cdn.discordapp.com/icons/656070244321984532/fcfd0a039781de6bd1db261d3cb8b225.webp?size=80&quality=lossless"
USE_LOCAL_DB = True


def log(message, level):
    match level:
        case logging.DEBUG:
            print(datetime.datetime.now(), "|| DEBUG || ", message)
            logger.debug(message)

        case logging.INFO:
            print(datetime.datetime.now(), "|| INFO || ", message)
            logger.info(message)

        case logging.WARNING:
            print(datetime.datetime.now(), "|| WARNING || ", message)
            logger.warning(message)

        case logging.ERROR:
            print(datetime.datetime.now(), "|| ERROR || ", message)
            logger.error(message)

        case logging.CRITICAL:
            print(datetime.datetime.now(), "|| CRITICAL || ", message)
            logger.critical(message)

async def check_webhook():
    async with ClientSession() as session:
        webhook = Webhook.from_url(os.getenv("WEBHOOK_URL"), session = session)
        await webhook.send(content = "@everyone\nNew Upload From {0}!\t{3}\n{1}\n{2}".format("channel_name", "title", "video_url", "date_published"), username = BOT_NAME, avatar_url = BOT_IMAGE)

def main():
    if __name__ == "__main__":
        with open("LucaTheLog.log", "w"):
            pass
        logging.basicConfig(filename="LucaTheLog.log", level=logging.DEBUG, format="%(asctime)s || %(levelname)s || %(message)s")

        log("Logging Started", logging.INFO)

        log("Loading DotEnv", logging.INFO)

        load_dotenv()

        log("Loaded DotEnv", logging.INFO)

        log("Connecting To ngrok", logging.INFO)

        try:
            tunnel = ngrok.connect(addr="localhost:8080")
            log("Connected To ngrok", logging.INFO)
        except Exception as E:
            log(E, logging.DEBUG)
            log("Failed To Connect To ngrok!", logging.CRITICAL)
            raise(E)
        
        handler = NewVideoHandler(tunnel)
        m_loop = asyncio.get_event_loop()
        m_loop.run_until_complete(handler.server())
        m_loop.run_forever()

    else:
        exit()

class NewVideoHandler():
    
    def __init__(self, tunnel):
        if USE_LOCAL_DB:
            # self.db = None
            # self.connect_to_db()
            log("Connected To Local DB", logging.INFO)
        else:
            self.memory = set()
            log("Using RAM", logging.INFO)
        self.tunnel_url = tunnel.public_url
        self.first_run = 1

    async def subscribe(self, channel_id):
        async with ClientSession() as session:
            payload = {
                "hub.callback" : self.tunnel_url,
                "hub.mode" : "subscribe",
                "hub.topic" : f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}",
                "hub.lease_numbers" : "",
                "hub.secret" : "",
                "hub.verify" : "async",
                "hub.verify_token" : "",
            }
            async with session.post("https://pubsubhubbub.appspot.com/subscribe", data=payload) as resp:
                if resp.status == 202:
                    log("Subscribe Request Sent", logging.INFO)
                else:
                    log("Failed To Subscribe", logging.CRITICAL)

    def __unload(self):
        # FOR THE LOVE OF LUCA
        # DO *NOT* REMOVE THIS
        # IT WILL JUST KEEP RUNNING
        asyncio.ensure_future(self.site.stop())

    async def connect_to_db(self):
        db = await aiosqlite.connect("LucaTheDatabase.db")
        self.db = db
        pointer = await self.db.execute("CREATE TABLE IF NOT EXISTS Videos(id, title, link, name, date)")
        await self.db.commit()
        await pointer.close()

    async def server(self):

        if self.first_run:
            if False:
                await check_webhook()
            self.first_run = 0

        route = web.RouteTableDef()

        @route.get("/")
        async def auth(req):
            if "hub.challenge" in req.query:
                log("Authenticated", logging.INFO)
                response = req.query.get("hub.challenge")
                return web.Response(text=response, status=200)
            else:
                log("Authentication Failed", logging.WARNING)
                return web.Response(status=404)
        
        @route.post("/")
        async def receive(req):
            if req.content_type != "application/atom+xml":
                log("Incoming Data Incorrect Type!", logging.WARNING)
                return web.Response(status=400)
            else:
                log("Data Recieved", logging.INFO)
                content = await req.content.read(n=-1)
                log(content, logging.DEBUG)
                log("Parsing Data", logging.INFO)
                data = xmltodict.parse(content, "UTF-8")
                log(data, logging.DEBUG)

                if USE_LOCAL_DB:
                    await self.connect_to_db()
                    check_vid = await self.db.execute(f"SELECT * FROM Videos WHERE id = ?", (data["feed"]["entry"]["yt:videoId"],))
                    vid_result = await check_vid.fetchall()
                    if "entry" in data["feed"] and len(vid_result) < 1:
                        entry = data["feed"]["entry"]

                        video_data = {
                            "id": entry["yt:videoId"],
                            "title": entry["title"],
                            "video_url": entry["link"]["@href"],
                            "channel_name": entry["author"]["name"],
                            "channel_url": entry["author"]["uri"],
                            "date_published": entry["published"]
                        }

                        # self.memory.add(entry["yt:videoId"])
                        await self.db.execute("INSERT INTO Videos VALUES (?, ?, ?, ?, ?)", (video_data["id"], video_data["title"], video_data["video_url"], video_data["channel_name"], video_data["date_published"]))
                        await self.db.commit()

                        log("Data Added To Database", logging.INFO)

                        async with ClientSession() as session:
                            webhook = Webhook.from_url(os.getenv("WEBHOOK_URL"), session = session)
                            await webhook.send(content = "@everyone\nNew Upload From {0}!\t{3}\n{1}\n{2}".format(video_data["channel_name"], video_data["title"], video_data["video_url"], video_data["date_published"]), username = BOT_NAME, avatar_url = BOT_IMAGE)
                    else:
                        log("Data Already In Database!", logging.INFO)
                else:
                    if "entry" in data["feed"] and data["feed"]["entry"]["yt:videoId"] not in self.memory:
                        entry = data["feed"]["entry"]

                        self.memory.add(entry["yt:videoId"])

                        log("Data Added To Memory", logging.INFO)

                        video_data = {
                            "title": entry["title"],
                            "video_url": entry["link"]["@href"],
                            "channel_name": entry["author"]["name"],
                            "channel_url": entry["author"]["uri"],
                            "date_published": entry["published"],
                            "video_id": entry["yt:videoId"]
                        }

                        async with ClientSession() as session:
                            webhook = Webhook.from_url(os.getenv("WEBHOOK_URL"), session = session)
                            await webhook.send(content = "@everyone\nNew Upload From {0}!\t{3}\n{1}\n{2}".format(video_data["channel_name"], video_data["title"], video_data["video_url"], video_data["date_published"]), username = BOT_NAME, avatar_url = BOT_IMAGE)
                    else:
                        log("Data Already In Memory!", logging.INFO)
                return web.Response(status=200)
        
        app = web.Application(logger=logger)
        log("Created Web Application", logging.INFO)

        app.add_routes(route)
        log("Added Routes To Web Application", logging.INFO)
        runner = web.AppRunner(app)
        await runner.setup()
        log("Runner Setup", logging.INFO)
        self.site = web.TCPSite(runner, "localhost", 8080)
        await self.site.start()
        log("Site Started", logging.INFO)
        for channel in CHANNELS:
            await self.subscribe(CHANNELS[channel])
            log(f"Run Subscribe To {channel}", logging.INFO)


main()