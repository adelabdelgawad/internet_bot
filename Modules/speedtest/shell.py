import asyncio
from rich import print
from database.database import SQLiteDB


class Shell:
    @classmethod
    async def run(cls, cmd: str) -> None:
        try:
            proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)      
            return await proc.communicate()  # Start the Execution
        except Exception as ex:
            print(ex)