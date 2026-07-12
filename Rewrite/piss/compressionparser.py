from __future__ import annotations

from abc import ABC


class ParseTreeNode(ABC):
    def __init__(self, left: ParseTreeNode, right: ParseTreeNode):
        self.left = left
        self.right = right

    def pivot(self, new_right_child: ParseTreeNode):
        """
        Mutates self and new right child such that the previous right child of this node is the new child's left child.
        :param new_right_child: New right child node.
        """
        new_right_child.left = self.right
        self.right = new_right_child

class ParseTreeValue(ParseTreeNode):
    ...

class ParseTreeOperation(ParseTreeNode):
    ...