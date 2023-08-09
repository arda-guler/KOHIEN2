# KOHIEN: KOZMIK HIRDODINAMIK ENERJI SIMULATORU
from tkinter import *
import random
import time
import matplotlib.pyplot as plt

from particle import *
from vector2 import *
from consts import *

cameras = []
particles = []
running = True

########################
#       CAMERA         #
########################

class camera():
    def __init__(self, name, pos, zoom, state):
        self.name = name
        self.pos = pos
        self.zoom = zoom
        self.state = state

    def activate(self):
        self.state = "active"

    def deactivate(self):
        self.state = "standby"

    def set_pos(self, pos):
        self.pos = pos

    def set_zoom(self, zoom):
        self.zoom = zoom

    def move(self, movement):
        self.pos += movement

    def do_zoom(self, zoom):
        self.zoom *= zoom

    def get_state(self):
        return self.state

    def get_pos(self):
        return self.pos

    def get_zoom(self):
        return self.zoom

def get_active_cam():
    current_cam = None

    for cam in cameras:
        if cam.get_state() == "active":
            current_cam = cam
            break

    return cam

def move_current_cam_left(event=None):
    get_active_cam().move(vec2(-30 * get_active_cam().get_zoom(), 0))

def move_current_cam_right(event=None):
    get_active_cam().move(vec2(30 * get_active_cam().get_zoom(), 0))

def move_current_cam_up(event=None):
    get_active_cam().move(vec2(0, 30 * get_active_cam().get_zoom()))

def move_current_cam_down(event=None):
    get_active_cam().move(vec2(0, -30 * get_active_cam().get_zoom()))

def zoom_current_cam_out(event=None):
    get_active_cam().do_zoom(2)

def zoom_current_cam_in(event=None):
    get_active_cam().do_zoom(0.5)

def space2canvas(space_coords):
    current_cam = get_active_cam()

    canvas_x = ((space_coords.x - current_cam.get_pos().x) / current_cam.get_zoom() + 900 / 2)
    canvas_y = ((-space_coords.y + current_cam.get_pos().y) / current_cam.get_zoom() + 500 / 2)
    return vec2(canvas_x, canvas_y)


def canvas2space(canvas_coords):
    current_cam = get_active_cam()

    space_x = (canvas_coords.x - 900 / 2) * current_cam.get_zoom() + current_cam.get_pos().x
    space_y = -((canvas_coords.y - 500 / 2) * current_cam.get_zoom() - current_cam.get_pos().y)

    return vec2(space_x, space_y)

def finish_sim():
    global running
    running = False

def main():
    global particles, cameras, running
    N_PARTICLES = 100

    root = Tk()
    root.title("KOHIEN")
    root.geometry("1150x600")

    tk_canvas = Canvas(root, width=900, height=590, bg="black")
    tk_canvas.grid(row=0, column=1, rowspan=15, columnspan=5)

    star_power_label = Label(root, text="Star Power: unknown", anchor="w")
    star_radius_label = Label(root, text="Star Radius: unknown", anchor="w")
    star_power_label.grid(row=0, column=6)
    star_radius_label.grid(row=1, column=6)

    hydro_label = Label(root, text="Hydrogen: unknown", anchor="w")
    helio_label = Label(root, text="Helium: unknown", anchor="w")
    terro_label = Label(root, text="Heavy Metals: unknown", anchor="w")
    hydro_label.grid(row=3, column=6)
    helio_label.grid(row=4, column=6)
    terro_label.grid(row=5, column=6)

    finish_graph_button = Button(root, text="Finish and See Graphs", command=finish_sim)
    finish_graph_button.grid(row=2, column=6)

    for i in range(N_PARTICLES):
        random_r = random.uniform(0, 10)
        random_theta = random.uniform(0, 2 * PI)
        # random_vel = vec2(-math.sin(random_theta), math.cos(random_theta))

        random_pos = vec2(random_r * math.cos(random_theta), random_r * math.sin(random_theta))
        new_particle = Particle(random_pos, size=500)
        particles.append(new_particle)

    main_cam = camera("main_cam", vec2(0, 0), 0.0125, "active")
    cameras = [main_cam]

    root.bind("<Up>", move_current_cam_up)
    root.bind("<Down>", move_current_cam_down)
    root.bind("<Left>", move_current_cam_left)
    root.bind("<Right>", move_current_cam_right)
    root.bind("<Control_L>", zoom_current_cam_out)
    root.bind("<Shift_L>", zoom_current_cam_in)

    power_list = []
    radius_list = []
    hydro_list = []
    helio_list = []
    terro_list = []
    time_list = []

    dt = 0.25
    sim_time = 0
    running = True
    while running:

        star_power = 0
        star_radius = 0
        hydro = 0
        helio = 0
        terro = 0

        # physics happen below
        for p in particles:
            grav_force = p.calc_gravity(particles)
            hydro_press, mecha_force = p.calc_pressure_and_force(particles)
            p.vel += (grav_force + mecha_force) / mass_const * dt
            p.vel = p.vel - p.vel * drag_multiplier
            # p.vel += p.calc_drag(particles) / mass_const * dt
            p.calc_power(hydro_press)
            p.calc_nuclear_evolution(dt)

            star_power += p.power
            star_radius = p.pos.mag()
            hydro += p.hydro
            helio += p.helio
            terro += p.terro

        star_radius = star_radius / N_PARTICLES

        for p in particles:
            p.pos += p.vel * dt

        # graphics happen below
        for p in particles:
            tk_canvas.create_oval(space2canvas(p.pos).x - 5, space2canvas(p.pos).y - 5,
                                  space2canvas(p.pos).x + 5, space2canvas(p.pos).y + 5,
                                  fill=p.get_color())

        star_power_label.config(text="Star Power: " + str(round(star_power, 25)))
        star_radius_label.config(text="Star Radius: " + str(round(star_radius, 5)))
        hydro_label.config(text="Hydrogen: " + str(round(hydro, 5)))
        helio_label.config(text="Helium: " + str(round(helio, 5)))
        terro_label.config(text="Heavy Metals: " + str(round(terro, 5)))

        root.update()
        tk_canvas.delete("all")

        sim_time += dt

        power_list.append(star_power)
        radius_list.append(star_radius)
        time_list.append(sim_time)
        hydro_list.append(hydro)
        helio_list.append(helio)
        terro_list.append(terro)

    plt.scatter(time_list, power_list)
    plt.xlabel("Time")
    plt.ylabel("Power")
    plt.title("Star Power Evolution")
    plt.grid()
    plt.show()

    plt.plot(time_list, radius_list)
    plt.xlabel("Time")
    plt.ylabel("Radius")
    plt.title("Star Radius Evolution")
    plt.grid()
    plt.show()

    plt.plot(time_list, hydro_list, label="Hydrogen")
    plt.plot(time_list, helio_list, label="Helium")
    plt.plot(time_list, terro_list, label="Heavy Metals")
    plt.xlabel("Time")
    plt.ylabel("Material")
    plt.title("Star Composition")
    plt.legend()
    plt.grid()
    plt.show()

main()
