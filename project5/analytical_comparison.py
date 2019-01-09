from frontend import Diffusor_Generator, Diffusor
import matplotlib.pyplot as plt
import numpy as np

algs = ["ForwardEuler", "BackwardEuler", "CrankNicolson"]
names = ["fwd", "bwd", "cra"]
xc = 0; xb = 1; T = 0.001; L = (0.1,); dx = 1E-3
# dt = 0.5*dx**2

for a,b in zip(algs, names):
    datafile = "analytical_comparison"; algorithm = a
    #
    # G = Diffusor_Generator(xc, xb, T, dt, L, dx, datafile)
    # D = G.simulate(algorithm)
    #
    # x = np.arange(0, L[0], dx)
    # t = np.arange(0, T, dt)
    # print("Calculating Analytical Solution", end = "")
    # A = D.analytical_1D(x, t)
    # print(" [DONE]\nCalculating Differences", end = "")
    # print(" [DONE]\n")
    #
    # times = np.linspace(0, T, D.M.shape[0])
    # diff_means = np.zeros(D.M.shape[0])
    # for n in range(D.M.shape[0]-1):
    #     diff_means[n] = np.mean(A[2][n]-D.M[n])
    #
    # plt.xlabel("Time [s]")
    # plt.ylabel("Difference")
    # plt.xlim([0, T])
    # plt.plot(times, np.abs(diff_means))
    # plt.savefig("fig1.pdf")
    # TeX Caption: The mean difference in the 1-D numerical and analytical solution
    # of the diffusion equation over time, with $n_\text{max} = 10000$.

    ########## dt dx comparison ###########
    # dt < 0.5*dx**2 supposed boundary

    dt_vals = np.linspace(0.1*dx**2, 0.75*dx**2, 50)
    dtdx2 = dt_vals/(dx**2)
    x = np.arange(0, L[0], dx)
    vals = np.zeros_like(dtdx2)
    length = len(dtdx2)
    p = 0
    first_val = None
    done = False
    for n,dt in enumerate(dt_vals):
        t = np.arange(0, T, dt)
        G = Diffusor_Generator(xc, xb, T, dt, L, dx, datafile)
        D = G.simulate(algorithm)
        A = D.analytical_1D(x, t)
        new_val = np.abs(np.mean(A[2][-1]-D.M[-1]))
        if first_val is None:
            first_val = new_val
        if np.isfinite(new_val) and done is False and new_val <= first_val:
            vals[n] = new_val
        else:
            done = True
            vals[n] = np.nan

        if int(100*n/length) > p:
            p = int(100*n/length)
            print("Loading {:d}%".format(p))

    plt.figure()
    plt.xlabel(r"Ratio $\frac{dt}{dx^2}$")
    plt.ylabel("Difference")
    plt.xlim([np.min(dtdx2), np.max(dtdx2)])
    plt.plot(dtdx2, vals)
    plt.savefig("fig2_{}.pdf".format(b))
