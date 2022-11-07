from rich.console import Console
from rich.live import Live
from rich.table import Table
from time import sleep

def print_results(line, quota, st) -> None:
    used = f"{quota['used_percentage']} %"
    line_name = line["line_name"]
    remaining = f"{quota['remaining']} GB"

    table = Table(title=f"{line_name} Speedtest & WE Result")

    table.add_column("Download", justify="center", style="cyan", no_wrap=True)
    table.add_column("Upload", justify="center", style="cyan")
    table.add_column("Used", justify="center", style="green")
    table.add_column("Remaining", justify="center", style="green")
    table.add_column("Next Renew", justify="center", style="green")
    table.add_column("Balance", justify="center", style="green")

    table.add_row(str(st['download']), str(st['upload']),
    str(used), str(remaining),
    str(quota["renew_date"]), str(quota["balance"])
    )

    console = Console()
    console.print("")

    console.print(table)
    console.print("")

console = Console()

def print_st_table(lines) -> None:
    print('\n')
    table = Table(title=f"Speedtest Result")
    table.add_column("Line Name", justify="center", style="cyan", no_wrap=True)
    table.add_column("Download", justify="center", style="cyan", no_wrap=True)
    table.add_column("Upload", justify="center", style="cyan")
    for line in lines:
        table.add_row(str(line['line_name']), str(line['download']), str(line['upload']))
    console.print(table)
    sleep(.2)