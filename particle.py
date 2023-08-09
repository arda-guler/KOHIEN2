from vector2 import *
from consts import *

class Particle:
    def __init__(self, pos=vec2(), vel=vec2(), size=1, hydro=1, helio=0, terro=0, power=0):
        self.pos = pos
        self.vel = vel
        self.size = size
        self.hydro = hydro
        self.helio = helio
        self.terro = terro
        self.power = power

    def calc_pressure_and_force(self, particles):
        """Calculates pressure due to surrounding particles and the resulting force."""
        press = 0
        force = vec2()
        for p in particles:
            if not p == self:
                if p.hydro < 5 and p.power > 0:
                    helio_multiplier = 100
                else:
                    helio_multiplier = 1

                press += (Young_modulus + p.power * press_multiplier) / (p.pos - self.pos).mag() ** 2
                if (p.pos - self.pos).mag() > self.size * 0.001:
                    force -= (p.pos - self.pos).normalized() * ((p.power * force_multiplier) / (p.pos - self.pos).mag() ** 2) * helio_multiplier
                else:
                    force -= (p.pos - self.pos).normalized() * Young_modulus / (p.pos - self.pos).mag()
                    force -= (p.pos - self.pos).normalized() * ((p.power * force_multiplier) / (self.size * 10)**2 ) * helio_multiplier

        self.press = press

        return press, force

    def calc_drag(self, particles):
        drag = vec2()
        for p in particles:
            if not p == self and (p.pos - self.pos).mag() < self.size * 2:
                drag = drag + (p.vel - self.vel) * drag_multiplier

        return drag

    def calc_gravity(self, particles):
        """Calculates gravitational accel. Self-explanatory."""
        gravity = vec2()
        for p in particles:
            if not p == self:
                if (p.pos - self.pos).mag() > self.size * 10:
                    gravity += (p.pos - self.pos).normalized() * grav_const / ((p.pos - self.pos).mag()**2)
                else:
                    gravity += (p.pos - self.pos).normalized() * grav_const / ((self.size * 10)**2)

        return gravity

    def calc_nuclear_evolution(self, dt):
        if self.power > 0:
            if self.hydro > 0.5:
                self.hydro -= self.power * fuel_consumption_multiplier * dt
                self.helio += self.power * fuel_consumption_multiplier * dt

            elif self.hydro <= 0.5 and self.helio < 0.7:
                self.hydro -= self.power * 0.6 * fuel_consumption_multiplier * dt
                self.helio += self.power * 0.6 * fuel_consumption_multiplier * dt

                self.helio -= self.power * 0.4 * fuel_consumption_multiplier * dt
                self.terro += self.power * 0.4 * fuel_consumption_multiplier * dt

            else:
                pass

        self.hydro = max(min(self.hydro, 1), 0)
        self.helio = max(min(self.helio, 1), 0)
        self.terro = max(min(self.terro, 1), 0)

    def calc_power(self, press):
        if press > 1:
            if self.hydro > 0.5:
                self.power = press * 1

            elif self.hydro <= 0.5 and self.helio > 0.2:
                self.power = press * 3

            else:
                self.power = 0

        else:
            self.power = 0

        self.power = self.power * power_multiplier
        self.power = min(self.power, 1e-5)

    def get_color(self):
        if self.power == 0:
            if self.hydro > 0.1:
                return "gray"
            else:
                return "blue"

        else:
            if self.hydro > 0.5:
                return "yellow"
            else:
                return "red"
