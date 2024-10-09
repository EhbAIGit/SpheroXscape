def minY(coordinate, y_delta, times=1):
    return addY(coordinate, -y_delta, times)

def addY(coordinate, y_delta, times=1):
    x, y, z = coordinate
    return (x, y + (y_delta * times),z)

def minX(coordinate, x_delta, times=1):
    return addX(coordinate, -x_delta)

def addX(coordinate, x_delta, times=1):
    x, y, z = coordinate
    return (x + x_delta, y, z)

def dim2(coordinate):
    x,y,_ = coordinate
    return (x,y)