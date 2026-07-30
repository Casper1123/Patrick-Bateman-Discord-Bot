from Rewrite.data.interfaces.fact import GlobalAdminFactInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.discorduser.user import BotClient
from Rewrite.discorduser.logger.__init__ import GlobalLoggerConfig

db: GlobalAdminFactInterface = None
pref: PreferencesInterface = None
logconfig: GlobalLoggerConfig = None

client = BotClient(db, pref, logconfig)