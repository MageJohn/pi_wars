def drive_from_vector(x, y):
    leftReturn = clamp(x+y, -1, 1)
    rightReturn = clamp(x-y, -1, 1)
    return (leftReturn,rightReturn)

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))
