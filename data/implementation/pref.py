from typing import get_args

from data.implementation.utilities.abstract import CachedAbstractSQLDatabase
from data.interfaces.pref import PreferencesInterface, UserPreferenceData, supported_autoreply_features, \
    GuildChannelPreferenceData

"""
Table(s) and design:
Pausing: Handled completely through cache.

CHANNEL:
- GuildID: ID of the corresponding channel's guild.
- ChannelID: ID of the corresponding channel. 0 if global/None id
- saying
- text
- letter
- number
PK: (GuildID, ChannelID)

USER:
- UserID: ID of the corresponding user
- saying
- text
- letter
- number
PK: UserID
"""

_all_features: set[supported_autoreply_features] = {i for i in get_args(supported_autoreply_features)}

def _get_feat_attr_name(feat: supported_autoreply_features) -> str:
    if not feat in ['saying', 'text', 'letter', 'number']:
        raise KeyError(f'Feature {feat} not supported.')
    # Conversion TypeAlias to str
    return {i: str(i) for i in get_args(supported_autoreply_features)}[feat]

class PreferencesDatabase(CachedAbstractSQLDatabase, PreferencesInterface):
    def __init__(self, path: str):
        super().__init__(
            db_path=path,
            schema_name='pref',
            schema_version=1
        )

    def pause_all_in_channel(self, guild_id: int, channel_id: int | None, duration: int) -> None:
        try:
            self._cache.register(
                keys=('paused', guild_id, channel_id,),
                val=channel_id if channel_id else 0,
                timeout=duration,
            )
        except ValueError:
            self._cache.refresh(
                keys=('paused', guild_id, channel_id,),
                timeout=duration,
            )

    def is_paused_channel(self, guild_id: int, channel_id: int) -> bool:
        # Registered under str(None) is 'all channels' which overrides this, obviously.
        val = self._cache.get_cached(
            keys=('paused', str(guild_id), str(None),),
            out_type=int,
        )
        if val is not None:
            return True
        val = self._cache.get_cached(
            keys=('paused', str(guild_id), str(channel_id),),
            out_type=int,
        )
        return val is not None

    def set_autoreply_features(self, guild_id: int, channel_id: int | None,
                               features: set[supported_autoreply_features]) -> None:
        self._cache.unregister(
            keys=('guild', guild_id, channel_id,),
        )
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO pref_guild (guild_id,
                                        channel_id,
                                        saying,
                                        text,
                                        letter,
                                        number)
                VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT DO
                UPDATE SET
                    saying = excluded.saying,
                    text = excluded.text,
                    letter = excluded.letter,
                    number = excluded.number
                """,
                (
                    guild_id,
                    channel_id,
                    int("saying" in features),
                    int("text" in features),
                    int("letter" in features),
                    int("number" in features),
                ),
            )

    def guild_channel_autoreplies_enabled(self, guild_id: int, channel_id: int | None) -> GuildChannelPreferenceData:
        val = self._cache.get_cached(
            keys=('guild', guild_id, channel_id,),
            out_type=GuildChannelPreferenceData,
        )
        if val is not None:
            return val

        with self._connection() as conn:
            if channel_id is None:
                row = conn.execute(
                    """
                    SELECT saying, text, letter, number
                    FROM pref_guild
                    WHERE guild_id = ?
                      AND channel_id IS NULL
                    """,
                    (guild_id,),
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT saying, text, letter, number
                    FROM pref_guild
                    WHERE guild_id = ?
                      AND channel_id = ?
                    """,
                    (guild_id, channel_id),
                ).fetchone()

        if row is None:
            val = GuildChannelPreferenceData(
                saying=True,
                text=True,
                letter=True,
                number=True,
            )
        else:
            val = GuildChannelPreferenceData(
                saying=bool(row["saying"]),
                text=bool(row["text"]),
                letter=bool(row["letter"]),
                number=bool(row["number"]),
            )

        self._cache.register(
            keys=('guild', guild_id, channel_id,),
            val=val,
            timeout=120,  # 2min
            auto_refresh=(
                15,
                120
            )
        )

        return val

    def set_user_autoreply_features(self, user_id: int, features: set[supported_autoreply_features]) -> None:
        self._cache.unregister(
            keys=('user', user_id,),
        )

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO pref_user (user_id,
                                       saying,
                                       text,
                                       letter,
                                       number)
                VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO
                UPDATE SET
                    saying = excluded.saying,
                    text = excluded.text,
                    letter = excluded.letter,
                    number = excluded.number
                """,
                (
                    user_id,
                    int("saying" in features),
                    int("text" in features),
                    int("letter" in features),
                    int("number" in features),
                ),
            )

    def user_autoreplies_enabled(self, user_id: int) -> UserPreferenceData:
        val = self._cache.get_cached(
            keys=('user', user_id,),
            out_type=UserPreferenceData,
        )
        if val is not None:
            return val
        
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT saying, text, letter, number
                FROM pref_user
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            val = UserPreferenceData(
                # No entry implies all enabled (none disabled)
                saying=True,
                text=True,
                letter=True,
                number=True,
            )
        else:
            val = UserPreferenceData(
                saying=bool(row["saying"]),
                text=bool(row["text"]),
                letter=bool(row["letter"]),
                number=bool(row["number"]),
            )

        self._cache.register(
            keys=('user', user_id,),
            val=val,
            timeout=120,  # 2min
            auto_refresh=(
                15,
                120
            )
        )

        return val