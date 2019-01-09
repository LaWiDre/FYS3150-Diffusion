from frontend import Diffusor_Generator, Diffusor

# Simulation Parameters
xc = 0
xb = 0
T = 1E9
L = (1.2E5, 1.2E5)
dx = 1E3               # Position-Step
dt = 5E6               # Time-Step

G = Diffusor_Generator(xc, xb, T, dt, L, dx)
D = G.simulate(algorithm = "ForwardEulerLitho")
D.plot_2D(T/100, savename = "fwd_litho_0.png", litho = True)
D.plot_2D(T/50, savename = "fwd_litho_1.png", litho = True)
D.plot_2D(T/10, savename = "fwd_litho_2.png", litho = True)
D.plot_2D(T/5, savename = "fwd_litho_3.png", litho = True)
D.plot_2D(T/2, savename = "fwd_litho_4.png", litho = True)
D.plot_2D(T, savename = "fwd_litho_5.png", litho = True)
D.animate_2D(frames = 400, litho = True)
