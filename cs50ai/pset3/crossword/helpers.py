import copy

def deQueue(queue):
    """
    Removes an arc form the queue and returns it's x and y value
    """
    if queue == None:
        return None
    for item in queue:
        copy = item
        del queue[item]
        return copy


def removeNone(queue):
    """
    Removes all arcs that has no overlaps
    """
    for key in copy.deepcopy(queue):
        if queue[key] == None:
            del queue[key]
    return queue