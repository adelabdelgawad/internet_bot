import asyncio
import re
import os
import sys
from .banners import print_st_table
from .progress import Progress
from time import sleep

async def _find_result(sl, ind):
    """
    :parmts: sl = shell_line, means the result of the line
    :parmts: ind = Indicator (Upload or Download)
    """
    pattern = f"{ind}:(.*?) Mbit/s"
    substring = re.search(pattern, sl).group(1)
    ind = substring.replace(' ', '')
    return ind

async def _start_speedtest_onshell(DB, line, shell):
        """
        Create the subprocess; redirect the standard output
        into a pipe
        """
        try:
            proc = await asyncio.create_subprocess_shell(
                shell,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await proc.communicate()
            if stdout:  # Valid out
                stdout = stdout.decode()
                try:
                    download = await _find_result(stdout, 'Download')
                    download = float(download)
                except:
                    download = 0

                try:
                    upload = await _find_result(stdout, 'Upload')
                    upload = float(upload)
                except:
                    upload = 0
            if stderr:  # error out
                sys.stderr.write(f"")

        except Exception as ex:
            print(ex)
        finally:
            result = f"download='{download}', upload='{upload}'"  
            print(f"{line['line_name']} {result}")
            await DB.add_result_to_today_line_row(line, result)
            return download, upload

async def _speedtest_method(line, shell, DB, progress, pb):
    download: int = 0
    upload: int = 0

    download_list: list = []
    upload_list: list = []

    """Start the Speed SubPrcess x times"""
    for _ in range(3):
        download, upload = await _start_speedtest_onshell(DB, line, shell)
        download_list.append(download)
        upload_list.append(upload)
        progress.update(pb, advance=1)
    # Update the Results on the DataBase result to db
    try:
        result = f"upload='{max(upload_list)}', download='{max(download_list)}'"  
        await DB.add_result_to_today_line_row(line, result) 
    except Exception as ex:
        result = f"upload=' ', download=' '"  
        await DB.add_result_to_today_line_row(line, result)
    

def st_start(lines, DB, cc)-> None:
    """
    Pram:
    Popped IPs will used on the changing ips
    Cloned IPs will used on the running async model
    """
    chuck_lines = [lines[i:i +cc] for i in range (0, len(lines), cc)]
    for chuck_line in chuck_lines:
        with Progress(transient=True) as progress:
            cloned_lines = chuck_line.copy()
            # Changing IP Address:
            primary_ip = chuck_line.pop()
            os.system(rf"""netsh interface ipv4 set address name=Ethernet static {primary_ip['ip_address']} {primary_ip['subnet_mask']} {primary_ip['gateway']}""")
            sleep(.5)

            # Add Secondery IPs
            for line in chuck_line:
                os.system(rf"""netsh interface ipv4 add address name=Ethernet {line['ip_address']} {line['subnet_mask']}""")
                sleep(.5)
            sleep(5)

            async def main():
                tasks: list = []
                for line in cloned_lines:
                    pb = progress.add_task(f"[red]{line['line_name']} Speedtest Progress...", total=3)
                    shell = f"python speedtest.py --secure --source {line['ip_address']}"
                    tasks.append(_speedtest_method(line, shell, DB, progress, pb))
                await asyncio.gather(*tasks)
            asyncio.run(main())
            sleep(1)

    lines_result = DB.get_last_result_dict(lines)
    print_st_table(lines_result)
    return lines_result


