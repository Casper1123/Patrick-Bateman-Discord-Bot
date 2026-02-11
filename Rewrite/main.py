# todo: load config
# todo: instantiate db class
from Rewrite.data.data_interface_abstracts import GlobalAdminDataInterface
from Rewrite.discorduser import BotClient
from Rewrite.discorduser.logger.logger import LoggerConfiguration

db: GlobalAdminDataInterface
logconfig: LoggerConfiguration

client = BotClient(db, logconfig)