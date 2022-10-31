import asyncio
from rich import print
from .progress import SubProc
from .connection import SQLiteDB


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

    @classmethod
    async def change_nic_ip(cls, line: dict) -> None: 
        stdout, stderr = await Shell.run(
            rf"netsh interface ipv4 set address name=Ethernet static {line['ip_address']} {line['subnet_mask']} {line['gateway']}"
        )
        await asyncio.sleep(3)
        if stdout:
            if 'The requested operation requires elevation (Run as administrator)' in stdout.decode():
                print(f"[red] {line['ip_address']} {line['subnet_mask']} : The requested operation requires elevation (Run as administrator)")
            else:
                print(f"[green] Network Interface IP Address Changed to :{line['ip_address']} {line['subnet_mask']}")
        if stderr:
            print(stderr)

    @classmethod
    async def add_second_ip(cls, line: dict):
        stdout, stderr = await Shell.run(
            rf"netsh interface ipv4 add address name=Ethernet {line['ip_address']} {line['subnet_mask']}"
        )
        await asyncio.sleep(1)
        if stdout:
            if 'The requested operation requires elevation (Run as administrator)' in stdout.decode():
                print(f"[red] {line['ip_address']} {line['subnet_mask']} : The requested operation requires elevation (Run as administrator)")
            else:
                print(f"[green] IP Address :{line['ip_address']} {line['subnet_mask']} Added Succefully")
        if stderr:
            print(stderr)

    @classmethod
    def change_to_bestline(lines):
        st_results = SQLiteDB.get_today_results(lines)
        lines_sorted: list = sorted(st_results, key=lambda d: float(d['ping']))  # Sort lines by Ping
        # Loop in the lines list to get the line information and change the IPAddress
        for line in lines:
            if line['line_id'] == lines_sorted[0]['line_id']:
                asyncio.run(Shell.change_nic_ip(line))
