import abc
import dataclasses
import logging
import os
import typing
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


TEE = "├"
ELL = "└"
BAR = "──"
SSS = "  "
PIPE = "│"
SPACE = " "

BRANCH_COLOR = "\x1b[36;5;34m"
RESET = "\x1b[0m"


class Seed(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def get_root(self) -> T: ...

    @abc.abstractmethod
    def get_children(self, item: T) -> list[T]: ...

    @abc.abstractmethod
    def get_base(self, item: T) -> str: ...

    @abc.abstractmethod
    def get_label(self, item: T) -> str: ...

    @abc.abstractmethod
    def is_leaf(self, item: T) -> bool: ...


class Arborist:
    def __init__(
        self,
        seed: Seed,
        indent: int | None = None,
        color: bool | None = None,
        max_depth: int | None = None,
    ):
        if indent is None:
            self.indent = 0
        else:
            self.indent = indent
        self.color = color or False
        self.max_depth = max_depth or None
        self.seed = seed

    def make_tree(
        self, item: Any, prefix: str | None = None, second_prefix: str | None = None, depth: int = 0
    ):
        logger.debug(f"Making tree from {item}")
        if depth is None:
            depth = 0
        depth = depth + 1
        if self.max_depth is not None and depth > self.max_depth:
            logger.debug(f"Reached max depth {depth} of {self.max_depth}")
            return
        if prefix is None:
            prefix = ""
        if second_prefix is None:
            second_prefix = prefix

        base = self.seed.get_base(item)
        if not self.color or self.seed.is_leaf(item):
            print(f"{prefix}{base}")
        else:
            if self.color:
                print(f"{prefix}{BRANCH_COLOR}{base}{RESET}")
            else:
                print(f"{prefix}{base}")

        if self.indent < 0:
            base_length = len(base) + self.indent
            width = max(base_length, 0)
        else:
            width = self.indent
        space = width * " "

        children = self.seed.get_children(item)

        item_count = len(children)
        item = 0
        for child in children:
            item = item + 1
            if item < item_count:
                item_prefix = f"{second_prefix}{space}{TEE}{BAR}{SPACE}"
                second_item_prefix = f"{second_prefix}{space}{PIPE}{SSS}{SPACE}"
            else:
                item_prefix = f"{second_prefix}{space}{ELL}{BAR}{SPACE}"
                second_item_prefix = f"{second_prefix}{space}{SPACE}{SSS}{SPACE}"
            self.make_tree(child, item_prefix, second_item_prefix, depth)


def valid_name(name: str | None) -> bool:
    if name is None:
        return False
    return (
        name is not None
        and len(name) > 0
        and not name.startswith(".")
        and not (name.startswith("__") and (name.endswith("__") or name.endswith("__.py")))
    )


class Entry(typing.Protocol):
    path: str
    name: str

    @abc.abstractmethod
    def is_dir(self): ...


@dataclasses.dataclass
class FakeDirEntry:
    path: str
    name: str

    def is_dir(self):
        return os.path.isdir(self.path)


class DirectorySeed(Seed[Entry]):
    def __init__(self, root: str, should_sort: bool | None = None):
        self.root = FakeDirEntry(root, os.path.basename(root))
        self.should_sort = should_sort or False

    def get_root(self) -> Entry:
        return self.root

    def get_children(self, item: Entry) -> list[Entry]:
        dirs = []
        files = []
        if os.path.isdir(item.path):
            with os.scandir(item.path) as directory:
                for entry in directory:
                    if valid_name(entry.name):
                        if entry.is_dir():
                            dirs.append(entry)
                        else:
                            files.append(entry)
        if self.should_sort:
            dirs = list(sorted(dirs, key=lambda d: d.name))
            files = list(sorted(files, key=lambda d: d.name))
        return [FakeDirEntry(x.path, x.name) for x in dirs + files]

    def get_base(self, item: Entry) -> str:
        return os.path.basename(item.path).lstrip("/")

    def get_label(self, item: Entry) -> str:
        return item.name

    def is_leaf(self, item: Entry) -> bool:
        return not item.is_dir()
