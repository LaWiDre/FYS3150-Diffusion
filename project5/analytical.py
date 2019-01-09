from frontend import Diffusor_Generator, Diffusor
import matplotlib.pyplot as plt
import numpy as np

xc = 0; xb = 1; T = 1; dt = 1E-3; L = (1,); dx = 1E-2
datafile = "analytical_comparison"; algorithm = "ForwardEuler"

G = Diffusor_Generator(xc, xb, T, dt, L, dx, datafile)
D = G.simulate(algorithm)

x = np.arange(0, L[0], dx)
t = np.arange(0, T, dt)
X,T,u = D.analytical_1D(x, t)

fig, ax = plt.subplots()
plt.xlabel("Time")
plt.ylabel("Position")

# Plotting
cax = plt.pcolormesh(T, X, u, cmap = 'magma', vmin=0, vmax=u.max())
cbar = fig.colorbar(cax)
cbar.set_label("Intensity [scaled]")
plt.savefig("analytical_solution.png")
