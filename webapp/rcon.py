import aiorcon
import asyncio
# from webapp.models import Servers


class GameServer:
    def __init__(self):
        # self.server = Servers.query.filter_by(busy=False).first()[0]
        # self.hostname = self.server.hostname
        # self.ip = self.server.ip
        # self.password = self.server.password
        self.hostname = 'aman'
        self.ip = 'bigbang.cargo.win'
        self.password = 'zeroinf'

    def load_match(self):
        async def main(loop, command):
            rcon = await aiorcon.RCON.create(self.ip, 27015, self.password, loop)
            output = await(rcon(command))
            print(output)
            rcon.close()
            return output

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop, 'get5_loadmatch_url "freddyhome.ddns.net/api/' + self.hostname + '"'))

    def server_status(self):
        async def main(loop, command):
            rcon = await aiorcon.RCON.create(self.ip, 27015, self.password, loop)
            output = await(rcon(command))
            print(output)
            rcon.close()
            return output

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop, 'get5_status'))
