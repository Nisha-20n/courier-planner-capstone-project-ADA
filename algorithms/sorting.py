"""
sorting.py  --  Merge Sort (Sorting topic)

Hum apna khud ka merge sort likh rahe hain (built-in sorted() nahi) taaki
viva mein bata sako ki sorting kaise kaam karti hai.
We write our own merge sort instead of using sorted(), so it can be explained.

Time complexity : O(n log n)
Space complexity: O(n)
"""


def merge_sort(items, key=lambda x: x, reverse=False):
    """Return a NEW sorted list. Stable sort (equal items keep their order)."""
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = merge_sort(items[:mid], key, reverse)
    right = merge_sort(items[mid:], key, reverse)
    return _merge(left, right, key, reverse)


def _merge(left, right, key, reverse):
    """Merge two already-sorted lists into one sorted list."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        a, b = key(left[i]), key(right[j])
        take_left = (a >= b) if reverse else (a <= b)
        if take_left:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
