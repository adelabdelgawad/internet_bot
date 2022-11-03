from rich.console import Console
from rich.table import Table

def print_result(lines_result: list):
    """
    Print Results Table Using Rich Tables Module
    Results Contains Speedtest And Quota Check
    Args:
     lines_result: list -> he Database Results row 
    """

    table = Table(title="Today Results")

    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Ping", style="cyan")
    table.add_column("Upload", style="cyan")
    table.add_column("Download", style="cyan")
    table.add_column("Used", style="cyan")
    table.add_column("Remainig", style="cyan")
    table.add_column("Renewing Date", style="cyan")
    table.add_column("Balace", style="cyan")

    for line in lines_result:
        table.add_row(
            f"{line['line_name']}",
            f"{line['ping']} ms",
            f"{line['upload']} mb/s",
            f"{line['download']} mb/s",
            f"{line['used']} GB - {line['used_percentage']}%",
            f"{line['remaining']} GB",
            f"{line['renew_date']}",
            f"{line['balance']} LE",
        )
    console = Console()
    console.print(table)