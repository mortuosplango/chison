
# spatialisation
import math
from numpy import linalg
    
halfpi = (0.5 * math.pi)

def angle2d(x1, y1,x2, y2):
        return halfpi - math.atan2(y1 - y2, x1 - x2)

def elevation(eye, point):
        return angle2d(eye[1], eye[2],
                       point[1],point[2])

def azimuth(eye, point):
        return angle2d(eye[0], eye[2],
                       point[0],point[2])

def calculate_position(eye, point,distance_offset=0):
        # distance shouldn't become 0 for ambisonics
        distance = max(0.01, linalg.norm(point-eye) + distance_offset)
        az = azimuth(eye, point)
        ele = elevation(eye, point)
        return distance, az, ele
