def drive_from_vector(x, y):
    leftReturn = clamp(y+x, -1, 1)
    rightReturn = clamp(y-x, -1, 1)
    return (leftReturn,rightReturn)

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))
