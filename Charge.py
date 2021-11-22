# Author: Muhammad Nur Farizky
# Year: 2019
# Description: This is a class file to support ekigame.py

import numpy as np

class charge:
    def __init__(self, posx, posy, radius, q):
        self.x = posx
        self.y = posy
        self.radius = radius
        self.q = q

    def getPotential(self, x, y):
        r = pow(pow(x-self.x, 2) + pow(y-self.y, 2), 0.5)
        k = 1
        if r == 0:
            return 0
        else:
            return k*self.q/r

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getR(self):
        return self.radius

    def drawBallx(self):
        t = np.arange(0, 2*np.pi, 0.01)
        x = self.radius*np.cos(t) + self.x
        return x
    
    def drawBally(self):
        t = np.arange(0, 2*np.pi, 0.01)
        y = self.radius*np.sin(t) + self.y
        return y