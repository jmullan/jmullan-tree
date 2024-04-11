#!/usr/bin/env python3.11
import logging
import sys

from jmullan_cmd import cmd
from jmullan_logging import easy_logging

from jmullan.tree import tree

logger = logging.getLogger(__name__)


class TreeMain(cmd.Main):
    def __init__(self):
        super().__init__()
        easy_logging.easy_initialize_logging(log_level="INFO", stream=sys.stderr)
        self.parser.add_argument(dest="files", nargs="*")
        self.parser.add_argument("--indent", type=int, required=False, default=None)
        self.parser.add_argument("--color", action="store_true", default=False)
        self.parser.add_argument("--max-depth", type=int, required=False, default=None)

    def main(self):
        super().main()
        files = self.args.files or []
        if not files:
            files = ["."]

        for file in files:
            seed = tree.DirectorySeed(file)
            arborist = tree.Arborist(seed, self.args.indent, self.args.color, self.args.max_depth)
            arborist.make_tree(seed.get_root())
            print("")


def main():
    TreeMain().main()


if __name__ == "__main__":
    main()
