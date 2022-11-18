from rich.panel import Panel

from rich.console import(
    Group,
    Console
) 
from rich.progress import(
    Progress,
    BarColumn,
    TextColumn,
    ProgressColumn,
    TimeElapsedColumn,
    TaskProgressColumn,
)

from typing import Tuple


class ProgressBar(Progress):
    """
    Cloned Rich.Progress Class
    """
    @classmethod
    def get_default_columns(cls) -> Tuple[ProgressColumn, ...]:
        return (
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[progress.percentage]{task.completed}/{task.total}"),
            TimeElapsedColumn(),
        )


class Label(Progress):
    """
    Customized Rich Progress Class
     LabelBar Only
    """
    @classmethod
    def get_default_columns(cls) -> Tuple[ProgressColumn, ...]:
        return(
    TextColumn("[progress.description]{task.description}"),
    TimeElapsedColumn()
        )


Procs = Label()
STProgressBar = ProgressBar()
WEProgressBar = ProgressBar()
ResultConsole = Console()

ProgressGroup = Group(
    Panel(Group(Procs)),
    Panel(Group(STProgressBar)),
    Panel(Group(WEProgressBar))
)
