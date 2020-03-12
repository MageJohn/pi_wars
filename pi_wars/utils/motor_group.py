from yrk_oo.motors import MotorDriver, Motors


class MotorGroup:
    def __init__(self, bus):
        m1 = MotorDriver(Motors.MOTOR1, bus, 0.1)
        m11 = MotorDriver(Motors.MOTOR2, bus, 0.1)
        m2 = MotorDriver(Motors.MOTOR3, bus, 0.1)
        m22 = MotorDriver(Motors.MOTOR4, bus, 0.1)

        self.left = m1, m11
        self.right = m2, m22

    def set(self, left, right):
        for m in self.left:
            m.set(left)
        for m in self.right:
            m.set(right)

    def brake(self):
        for ml, mr in zip(self.left, self.right):
            ml.brake()
            mr.brake()
