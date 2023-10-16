import unittest
from .knowledge_base import KnowledgeBase

class KnowledgeBaseTest(unittest.TestCase):
    def test_load_nothing(self):
        kb: KnowledgeBase = KnowledgeBase()

        kb.load(recipe=False, loot=False, drop=False, resume=False)

        del(kb)

    def test_load_recipe_only(self):
        kb: KnowledgeBase = KnowledgeBase()

        kb.load(recipe=True, loot=False, drop=False, resume=False)

        del(kb)
