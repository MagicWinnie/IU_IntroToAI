import unittest
from main import Word, Point, Direction


class TestFitness(unittest.TestCase):
    def test_not_intersect_1(self):
        """
        . . a b c d . . .
        . . e f g . . . .
        """
        w1 = Word("abcd", Point(0, 2), Direction.HORIZONTAL, 0)
        w2 = Word("efg", Point(1, 2), Direction.HORIZONTAL, 1)
        self.assertIsNone(w1.intersects(w2))
        self.assertIsNone(w2.intersects(w1))

    def test_not_intersect_2(self):
        """
        . . a b c d . . .
        . . . . . e . . .
        . . . . . f . . .
        """
        w1 = Word("abcd", Point(0, 2), Direction.HORIZONTAL, 0)
        w2 = Word("ef", Point(1, 5), Direction.VERTICAL, 1)
        self.assertIsNone(w1.intersects(w2))
        self.assertIsNone(w2.intersects(w1))

    def test_not_intersect_3(self):
        """
        . e a b c d . . .
        . f . . . . . . .
        . . . . . . . . .
        """
        w1 = Word("abcd", Point(0, 2), Direction.HORIZONTAL, 0)
        w2 = Word("ef", Point(0, 1), Direction.VERTICAL, 1)
        self.assertIsNone(w1.intersects(w2))
        self.assertIsNone(w2.intersects(w1))

    def test_not_intersect_4(self):
        """
        . . a b c d e f .
        . . . . . . . . .
        . . . . . . . . .
        """
        w1 = Word("abcd", Point(0, 2), Direction.HORIZONTAL, 0)
        w2 = Word("ef", Point(0, 6), Direction.VERTICAL, 1)
        self.assertIsNone(w1.intersects(w2))
        self.assertIsNone(w2.intersects(w1))

    def test_not_intersect_5(self):
        """
        . . a/e b/f c d . . .
        . . .   .   . . . . .
        . . .   .   . . . . .
        """
        w1 = Word("abcd", Point(0, 2), Direction.HORIZONTAL, 0)
        w2 = Word("ef", Point(0, 2), Direction.HORIZONTAL, 1)
        self.assertIsNone(w1.intersects(w2))
        self.assertIsNone(w2.intersects(w1))

    def test_intersect_1(self):
        """
        . . a/e b c d . . .
        . . f   . . . . . .
        . . .   . . . . . .
        """
        w1 = Word("abcd", Point(0, 2), Direction.HORIZONTAL, 0)
        w2 = Word("ef", Point(0, 2), Direction.VERTICAL, 1)
        intersection = w1.intersects(w2)
        self.assertIsNotNone(intersection)
        self.assertEqual(intersection, (0, 0))

        intersection = w2.intersects(w1)
        self.assertIsNotNone(intersection)
        self.assertEqual(intersection, (0, 0))

    def test_parallel_1(self):
        """
        . . a b c d . . .
        . d e f . . . . .
        . . . . . . . . .
        """
        w1 = Word("abcd", Point(0, 2), Direction.HORIZONTAL, 0)
        w2 = Word("def", Point(1, 1), Direction.HORIZONTAL, 1)
        self.assertEqual(w1.parallel_close(w2), 1)
        self.assertEqual(w2.parallel_close(w1), 1)

    def test_parallel_2(self):
        """
        . . . . a . . . .
        . . . . b d . . .
        . . . . c g . . .
        """
        w1 = Word("abc", Point(0, 4), Direction.VERTICAL, 0)
        w2 = Word("ef", Point(1, 5), Direction.VERTICAL, 1)
        self.assertEqual(w1.parallel_close(w2), 1)
        self.assertEqual(w2.parallel_close(w1), 1)

    def test_parallel_3(self):
        """
        . . . . . . . . .
        . a b c d e f . .
        . . . . . . . . .
        """
        w1 = Word("abcd", Point(1, 1), Direction.HORIZONTAL, 0)
        w2 = Word("ef", Point(1, 5), Direction.HORIZONTAL, 1)
        self.assertEqual(w1.parallel_close(w2), 1)
        self.assertEqual(w2.parallel_close(w1), 1)

    def test_parallel_4(self):
        """
        . . . . a . . . .
        . . . . b . . . .
        . . . . c . . . .
        """
        w1 = Word("ab", Point(0, 4), Direction.VERTICAL, 0)
        w2 = Word("c", Point(2, 4), Direction.VERTICAL, 1)
        self.assertEqual(w1.parallel_close(w2), 1)
        self.assertEqual(w2.parallel_close(w1), 1)

    def test_parallel_5(self):
        """
        . . . . . . . . .
        . a b c d e f . .
        . . . . . . . . .
        """
        w1 = Word("abcd", Point(1, 1), Direction.HORIZONTAL, 0)
        w2 = Word("def", Point(1, 4), Direction.HORIZONTAL, 1)
        self.assertEqual(w1.parallel_close(w2), 0)
        self.assertEqual(w2.parallel_close(w1), 0)

    def test_parallel_6(self):
        """
        . . . . a . . . .
        . . . . b . . . .
        . . . . c . . . .
        """
        w1 = Word("ab", Point(0, 4), Direction.VERTICAL, 0)
        w2 = Word("bc", Point(1, 4), Direction.VERTICAL, 1)
        self.assertEqual(w1.parallel_close(w2), 0)
        self.assertEqual(w2.parallel_close(w1), 0)

    def test_parallel_7(self):
        """
        . . . . a b c . .
        . . d e . . . . .
        . . . . . . . . .
        """
        w1 = Word("abc", Point(0, 4), Direction.HORIZONTAL, 0)
        w2 = Word("de", Point(1, 2), Direction.HORIZONTAL, 1)
        self.assertEqual(w1.parallel_close(w2), 0)
        self.assertEqual(w2.parallel_close(w1), 0)

    def test_parallel_8(self):
        """
        . . a b c d e f .
        . . . . . . . . .
        . . . . . . . . .
        """
        w1 = Word("abcdef", Point(0, 2), Direction.HORIZONTAL, 0)
        w2 = Word("bcde", Point(0, 3), Direction.HORIZONTAL, 1)
        self.assertEqual(w1.parallel_close(w2), 3)
        self.assertEqual(w2.parallel_close(w1), 3)

    def test_parallel_9(self):
        """
        . . a b c . . . .
        . . . . d e f . .
        . . . . . . . . .
        """
        w1 = Word("abc", Point(0, 2), Direction.HORIZONTAL, 0)
        w2 = Word("def", Point(1, 4), Direction.HORIZONTAL, 1)
        self.assertEqual(w1.parallel_close(w2), 0)
        self.assertEqual(w2.parallel_close(w1), 0)


if __name__ == "__main__":
    unittest.main()
