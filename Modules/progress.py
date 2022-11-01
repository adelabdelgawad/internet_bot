from rich.table import Table
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

class TaskProgressBar(Progress):
    @classmethod
    def get_default_columns(cls) -> Tuple[ProgressColumn, ...]:
        return (
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[progress.percentage]{task.completed}/{task.total}"),
            TimeElapsedColumn(),
        )

class TaskLabel(Progress):
    @classmethod
    def get_default_columns(cls) -> Tuple[ProgressColumn, ...]:
        return(
    TextColumn("[progress.description]{task.description}"),
    TimeElapsedColumn()
        )

Task = Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TextColumn("[progress.percentage]{task.completed}/{task.total}"),
    TimeElapsedColumn(),
)

class TaskProgressLabel(Progress):
    @classmethod
    def get_default_columns(cls) -> Tuple[ProgressColumn, ...]:
        return(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TextColumn("[progress.percentage]{task.completed}/{task.total}"),
    TimeElapsedColumn(),
        )

class RichOverall:
    @classmethod
    def construct_rows(cls) -> None:
        """Create Rows of Progress by the same sequence of the List Indexes
            By default it will just reserve the location onlly,
            and will be shown once add task executed for each progress

        Sequence:
            [1] table -> Reserved Row For Rich liveview table.
             [2] process_label_class -> Reserved Row For Main Process Label.
            [3] subproc_label_class -> Reserved Row For Current Running Task Name Label.
             [4] subproc_pb_class -> Reserved Row ForCurrent Running Task ProgressBar in Percentage approach.
            [5] ProgressBar -> Reserved Row For Main Process ProgressBar in Percentage approach.
             [6] OverAllProgress -> Reserved Row For Whole Program ProgressBar in Percentage approach.
        """
        return [ rich_console.add_row(row) for row in progress_rows ]

    @classmethod
    def create_pb(cls, description: str, total: int) -> None:
        return OverAllProgress.add_task(description=description, total=total)

    @classmethod
    def advance(cls, task_id: TaskID, advance: Optional[int]=1):
        OverAllProgress.update(task_id, advance=advance)

class TaskPB():
    @classmethod
    def create(cls, description: str, total: int) -> TaskID:
        return Task.add_task(description=f"{description}", total = total)

    @classmethod
    def advance(cls, task_id: TaskID, advance: Optional[int] = 1):
        Task.update(task_id=task_id, advance=advance)
    
    @classmethod
    def finish(cls, task_id: TaskID):
        Task.update(task_id=task_id, completed=True, visible=False)



class Rich():
    def __init__(
        self, pb: TaskID, label: TaskID, sub: Optional[bool] = False
        ):
        self.pb = pb
        self.label = label
        self.sub = sub

    def create_label(self, description: str) -> TaskID:
        if self.sub:
            return self.label.add_task(description=f"   {description}")
        return self.label.add_task(description=description)

    def create_pb(self, total: int, description: str="") -> TaskID:
        return self.pb.add_task(description=description, total=total)

    def advance_pb(self, subproc_id: TaskID, advance: Optional[int]=1) -> None:
        self.pb.update(task_id=subproc_id, advance=advance)
    
    def finish(self, progress_id: TaskID, label_id: TaskID):
        self.label.stop_task(label_id)
        self.pb.update(progress_id, completed=True,finished_time=True, visible=False)
        if self.sub:
            [self.label.update(task_id=task_id, completed=True, visible=False) for task_id in self.label.task_ids]
            return
        self.label.update(label_id, description = f"[green]{self.label.tasks[label_id].description}", completed=True, finished_time=True)

    def finish_label(self, label_id: TaskID):
        self.label.stop_task(label_id)
        self.label.update(label_id, description = f"[green]{self.label.tasks[label_id].description}", completed=True, finished_time=True)

    def hide_labels(self):
        self.label.stop()
        [self.label.update(task_id=task_id, completed=True, visible=False) for task_id in self.label.task_ids]


OverAllProgress = TaskProgressBar()

ProcPB = TaskProgressBar()  # Process ProgressBar Instance
SubProcPB = TaskProgressBar()  # SubProcess ProgressBar Instance
ProcLabel = TaskLabel()  # Process Label Instance
SubProcLabel = TaskLabel()  # SubProcess Label Instance
ProgressLabel = TaskProgressLabel()  # SubProcess Label Instance

Proc = Rich(ProcPB, ProcLabel)
SubProc = Rich(SubProcPB, SubProcLabel, True)

IPAddressTable = Table() # Logs Table
SpeedtestTable = Table() # Logs Table

ProgressGroup = Group(
    IPAddressTable,
    SpeedtestTable,
    Panel(Group(ProcLabel, SubProcLabel, SubProcPB, ProcPB, Task)),
    OverAllProgress,
)

#  = Table(show_header=False, show_edge=False)
# 

# progress_rows: list= [
#     ProcLabel, SubProcLabel, SubProcPB, ProcPB, Task, OverAllProgress
# ]
