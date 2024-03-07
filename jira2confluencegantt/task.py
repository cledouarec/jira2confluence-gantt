"""Manage tasks."""

import logging
from datetime import date

from anytree import NodeMixin, PreOrderIter, RenderTree, find

#: Create logger for this file.
logger = logging.getLogger()


class Task(NodeMixin):
    """Manage task."""

    def __init__(
        self,
        key: str,
        summary: str,
        start_date: date,
        end_date: date,
        progress_in_percent: float = 0.0,
        blocking_tasks: list[str] | None = None,
        parent=None,
        children=None,
    ) -> None:
        """Create the task with all attributes.

        :param key: Task unique identifier.
        :param summary: Task summary.
        :param start_date: Start date of the task.
        :param end_date: End date of the task.
        :param progress_in_percent: Progress in percent of the task.
        :param blocking_tasks: Tasks key list which block this task.
        :param parent: Parent task.
        :param children: Sub tasks.
        """
        super().__init__()
        #: Task unique identifier
        self.key: str = key
        #: Task summary
        self.summary: str = summary
        #: Start date of the task
        self.start_date: date = start_date
        #: End date of the task
        self.end_date: date = end_date
        #: Progress in percent of the task
        self.progress_in_percent: float = progress_in_percent
        #: Tasks key list which block this task
        self.blocking_tasks: list[str] = []
        if blocking_tasks:
            self.blocking_tasks = blocking_tasks
        #: Parent task
        self.parent = parent

        if children:
            #: Sub tasks
            self.children = children


class TaskList(NodeMixin):
    """Manage task list.

    It is used as root node of the tree so modify the parent attribute will
    raise an error.
    """

    def __init__(self) -> None:
        """Create the task list."""
        super().__init__()

        #: Parent task
        self.parent = None

    def _pre_attach(self, _):
        """Attach a parent task is forbidden."""
        raise RuntimeError

    def _pre_detach(self, _):
        """Detach a parent task is forbidden."""
        raise RuntimeError

    def to_pre_order_list(self) -> list[Task]:
        """Create a list with the tasks pre-ordered (Depth-First Search).

        :return: Tasks list sorted.
        """
        return list(PreOrderIter(self, filter_=lambda task: not task.is_root))


def find_task_by_key(tasks: TaskList, key: str) -> Task | None:
    """Find a task by a `key` identifier in `tasks` list.

    :param tasks: Tasks list.
    :param key: Key identifier.
    :return: Task found or None.
    """
    return find(tasks, lambda task: not task.is_root and task.key == key)


def print_tasks(tasks: TaskList) -> None:
    """Print the tasks tree.

    :param tasks: Tasks list.
    """
    for pre, _, node in RenderTree(tasks):
        if isinstance(node, TaskList):
            logger.debug("%s%s", pre, "Root")
        else:
            logger.debug("%s%s", pre, node.key)
