import asyncio
from pyrogram import Client, Filters, Message
import res
from res import Configurations

configurations_map = {
	"commands": "commands",
	"logger": "logger"
}

loop = asyncio.get_event_loop()

config = Configurations("config/config.json", configurations_map)
loop.run_until_complete(config.parse())
config.set("app_hash", os.environ.pop("app_hash", None))
config.set("app_id", int(os.environ.pop("app_id", None)))
config.set("bot_token", os.environ.pop("bot_token", None))
config.set("bot_username", os.environ.pop("bot_username", None))
config.set("creator", int(os.environ.pop("creator", None)))

logger.basicConfig(
	filename=config.get("logger")["path"],
	datefmt="%d/%m/%Y %H:%M:%S",
	format=config.get("logger")["format"],
	level=config.get("logger").pop("level", logger.INFO))

logger.info("Initializing the Client ...")
app = Client(session_name=config.get("bot_username"), api_id=config.get("app_id"), api_hash=config.get("app_hash"), bot_token=config.get("bot_token"), lang_code="it", workdir=".", parse_mode="html")


@app.on_message(Filters.command("print", prefixes="/"))
async def print_chat(client: Client, message: Message):
	# /print
	# Checking if the data are of a chat or of a user
	if message.reply_to_message is not None:
		# Retrieving the data of the new admin
		chat = message.reply_to_message.from_user
	else:
		# Retrieving the data of the chat
		chat = message.chat

	# Deleting the message
	await message.delete(revoke=True)

	chat = chat.__dict__

	# Removing inutil informations
	chat.pop("_client", None)
	chat.pop("_", None)
	chat.pop("photo", None)
	chat.pop("description", None)
	chat.pop("pinned_message", None)
	chat.pop("sticker_set_name", None)
	chat.pop("can_set_sticker_set", None)
	chat.pop("members_count", None)
	chat.pop("restrictions", None)
	chat.pop("permissions", None)
	chat.pop("distance", None)
	chat.pop("status", None)
	chat.pop("last_online_date", None)
	chat.pop("next_offline_date", None)
	chat.pop("dc_id", None)
	chat.pop("is_self", None)
	chat.pop("is_contact", None)
	chat.pop("is_mutual_contact", None)
	chat.pop("is_deleted", None)
	chat.pop("is_bot", None)
	chat.pop("is_verified", None)
	chat.pop("is_restricted", None)
	chat.pop("is_scam", None)
	chat.pop("is_support", None)
	
	chat = str(chat)
	chat = chat.replace("\":", "\": ")
	chat = chat.replace(",\"", ",\n\"")

	# Printing the chat's data
	print(chat)
	await split_send_text(chat, "me")

	logger.info("I\'ve answered to /print because of {}.".format("@{}".format(message.from_user.username) if message.from_user.username is not None else message.from_user.id))


@app.on_message(Filters.command("report", prefixes="/") & Filters.user(config.get("creator")) & Filters.private)
async def report(_, message: Message):
	# /report
	global config

	await res.split_reply_text(config, message, "\n".join(list(map(lambda n: "{} - {}".format(n["name"], n["description"]), config.get("commands")))), quote=False)

	logger.info("I\'ve answered to /report because of {}.".format("@{}".format(message.from_user.username) if message.from_user.username is not None else message.from_user.id))


@app.on_message(Filters.command("start", prefixes="/") & Filters.private)
async def start(client: Client, message: Message):
	# /start
	global config

	# Setting the maximum message length
	max_length = await client.send(functions.help.GetConfig())
	config.set("message_max_length", max_length.message_length_max)

	# Retrieving the bot id
	bot = await client.get_users(config.get("bot_username"))
	config.set("bot_id", bot.id)

	logger.info("I\'ve answered to /start because of {}.".format("@{}".format(message.from_user.username) if message.from_user.username is not None else message.from_user.id))


@app.on_message(res.unknown_filter(config) & Filters.user(config.get("creator")) & Filters.private)
async def unknown(_, message: Message):
	global config

	await res.split_reply_text(config, message, "This command isn\'t supported.", quote=False)
	logger.info("I managed an unsupported command.")


logger.info("Client initializated\nStarted serving ...")
app.run()
