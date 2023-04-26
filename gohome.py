import datetime as dt
import logging
import typing

import maubot
import maubot.handlers
import mautrix.util.config


class Config(mautrix.util.config.BaseProxyConfig):
    def do_update(self, helper: mautrix.util.config.ConfigUpdateHelper) -> None:
        helper.copy("command_prefix")
        helper.copy("config")


class GoHomeBot(maubot.Plugin):
    async def start(self) -> None:
        self.config.load_and_update()
        self.store: dict[str, dt.datetime] = {}
        self.logger = logging.getLogger()

    @classmethod
    def get_config_class(cls) -> typing.Type[mautrix.util.config.BaseProxyConfig]:
        return Config

    @maubot.handlers.command.new(name="gohome", require_subcommand=True)
    async def base_command(self, evt: maubot.MessageEvent) -> None:
        # When you require a subcommand, the base command handler doesn't have to do anything.
        pass

    @base_command.subcommand()
    async def now(self, evt: maubot.MessageEvent):
        """Command to let users express they would like to go home to the bot."""
        self.store[evt.sender] = dt.datetime.now()
        await evt.react("👍")
        if self.check_can_gohome():
            await evt.react("🏠")
            user_list = " ".join(
                [
                    f"<a href='https://matrix.to/#/{x['mxid']}'>{x['mxid']}</a>"
                    for x in self.config["config"]["users"]
                ]
            )
            await self.client.send_text(
                self.config["config"]["notice_room"],
                text=None,
                html=f"🏠🏠🏠🏠🏠 ({user_list})",
            )
        else:
            await evt.react("⌛")

    def check_can_gohome(self):
        """Check if all users have said they want to go home today."""
        for user in self.config["config"]["users"]:
            try:
                report = self.store[user["mxid"]]
            except KeyError:
                return False
            if report.date() != dt.date.today():
                return False
        return True
