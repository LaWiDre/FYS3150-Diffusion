from frontend import Diffusor_Generator, Diffusor

xc = 0; xb = 1; T = 100; dt = 1E-3; L = (40,10); dx = 1
G = Diffusor_Generator(xc, xb, T, dt, L, dx)
D = G.simulate(algorithm = "ForwardEuler")

D.plot_2D(t = 0, savename = "fwd_0.png")
D.plot_2D(t = T/3, savename = "fwd_1.png")
D.plot_2D(t = 2*T/3, savename = "fwd_2.png")
D.plot_2D(t = T, savename = "fwd_3.png")

D = G.simulate(algorithm = "BackwardEuler")

D.plot_2D(t = 0, savename = "bwd_0.png")
D.plot_2D(t = T/3, savename = "bwd_1.png")
D.plot_2D(t = 2*T/3, savename = "bwd_2.png")
D.plot_2D(t = T, savename = "bwd_3.png")

D = G.simulate(algorithm = "CrankNicolson")

D.plot_2D(t = 0, savename = "cra_0.png")
D.plot_2D(t = T/3, savename = "cra_1.png")
D.plot_2D(t = 2*T/3, savename = "cra_2.png")
D.plot_2D(t = T, savename = "cra_3.png")
