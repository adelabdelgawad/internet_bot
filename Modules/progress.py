import time
from rich.console import Group
from rich.panel import Panel
from rich.progress import Progress
from rich.progress import BarColumn
from rich.progress import TextColumn
from rich.progress import SpinnerColumn
from rich.progress import ProgressColumn
from rich.progress import TimeElapsedColumn
from rich.progress import TaskProgressColumn
from rich.progress import TaskID
from typing import Optional
from typing import Sequence
from typing import Tuple

class ProgressBar(Progress):
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
    @classmethod
    def get_default_columns(cls) -> Tuple[ProgressColumn, ...]:
        return(
    TextColumn("[progress.description]{task.description}"),
    TimeElapsedColumn()
        )

OverAllProgress = ProgressBar()
Procs = Label()
STProgressBar = ProgressBar()
WEProgressBar = ProgressBar()

ProgressGroup = Group(
    Panel(Group(Procs)),
    Panel(Group(STProgressBar)),
    Panel(Group(WEProgressBar)),
    OverAllProgress
)
