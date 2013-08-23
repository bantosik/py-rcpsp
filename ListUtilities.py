import bisect

def insert_value_to_ordered_list(l, value):
    i = bisect.bisect_left(l, value)
    if i >= len(l) or not l[i] == value:
        l.insert(i,value)