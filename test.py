import os
import asyncio

sudoPassword = 'D0nttrytoopen'
command = 'pwd'
async def _execute(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)      
    return await proc.communicate()  # Start the Execution

stdout, stderr = asyncio.run(_execute(f"echo {sudoPassword} | sudo -S speedtest --secure --csv"))
if stdout:
    results = stdout.decode().split(',')
    ping = int(float(results[5]))
    download = round(float(results[6]) / 1000 / 1000, 1)
    upload = round(float(results[7]) / 1000 / 1000, 1)
    print(f"{ping}, {download}, {upload}")
if stderr:
    print(f"{stderr.decode()}")