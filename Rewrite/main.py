from Rewrite.data.interfaces.data import GlobalAdminDataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.discorduser.user import BotClient
from Rewrite.discorduser.logger.__init__ import LoggerConfiguration

db: GlobalAdminDataInterface = None
pref: PreferencesInterface = None
logconfig: LoggerConfiguration = None

client = BotClient(db, pref, logconfig)