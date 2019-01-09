from matplotlib.animation import FuncAnimation
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from subprocess import call
import numpy as np

class Diffusor_Generator:

    """
        Representative of a wavelike diffusion from regions with high
        concentrations to regions with low concentrations of an arbitrary
        quantity.

        All calculations are run on a julia backend, sent via the _write_data()
        method.  The data is then re-read into python for data-analysis
        purposes.
    """

    # For users

    def __init__(self, xc, xb, T, dt, L, dx, datafile = "wave_data.dat"):

        """
            Initializes and saves initial conditions and simulation settings as
            attributes, then runs _check_vars() to make sure all attributes are
            of correct type and within their restricted ranges (if they are
            limited).
        """
        print("Initializing New Diffusor_Generator", end = '')

        self.xc = xc                    # Inner Initial Conditions
        self.xb = xb                    # Outer Initial Conditions
        self.T = T                      # Simulation Time
        self.dt = dt                    # Time-Step
        self.L = L                      # Physical Array Size
        self.dx = dx                    # Position-Step
        self.datafile = datafile        # Filename for Data Transfer

        self.N = []
        for l in self.L:
            self.N.append(int(l/dx))
        self.N = tuple(self.N)
        self._check_vars()              # Checking that types and ranges match

        print(" [DONE]")

    def simulate(self, algorithm = "ForwardEuler"):
        """
            Uses the simulation settings generated in the constructor to load
            the julia backend, run the simulation, and subsequently re-read the
            data into python, and finally returns a "Diffusor" object, which can
            be used to access the simulation data repeatedly without re-running
            the simulation.
        """
        print("Initializing Julia Backend", end = '')
        self._write_data()
        self._call_backend(algorithm = algorithm)
        print(" [DONE]\nInterpreting Results", end = '')
        M = self._read_backend()
        print(" [DONE]\nGenerating Diffusor", end = '')
        S = self._gen_Diffusor_obj(M)
        print(" [DONE]")
        return S

    def __str__(self):
        """
            Prints out useful information on the simulation settings
        """
        size_str = ""
        shape_str = ""
        for i,j in zip(self.L, self.N):
            size_str += "{:d}x".format(i)
            shape_str += "{:d}x".format(j)

        size_str = size_str[:-1]
        shape_str = shape_str[:-1]

        msg = "\n"
        msg += "{:>25s}: {:>5.3E}\n".format("Inner Initial Conditions", self.xc)
        msg += "{:>25s}: {:>5.3E}\n".format("Outer Initial Conditions", self.xb)
        msg += "{:>25s}: {:>5.3E}\n".format("Simulation Time", self.T)
        msg += "{:>25s}: {:>5.3E}\n".format("Time-Step", self.dt)
        msg += "{:>25s}: {:<s}\n".format("Array Size (Physical)", size_str)
        msg += "{:>25s}: {:<s}\n".format("Array Shape (Numerical)", shape_str)
        msg += "{:>25s}: {:>5.3E}\n".format("Position-Step", self.dx)
        return msg

    # Not for users

    def _check_vars(self):
        """
            Checks that all the attributes initalized in the constructor are of
            compatible type; for numbers, also checks if they fit the required
            conditions.
        """

        # The names of the constructor parameters and class attributes
        vars = ["xc", "xb", "T", "dt", "N", "dx", "datafile"]

        # The desired types for each attribute, respective to "vars"
        num = (float, int)
        types = [num, num, num, num, tuple, num, str]

        # The smallest allowed values for each attribute
        minima = [None, None, 0, 0, 1, 0, None]

        # Running the tests, potentially raising TypeErrors or ValueErrors
        for v,t,m in zip(vars, types, minima):
            var = self.__dict__[v]
            if not isinstance(var, t):
                msg = "Argument \"{}\" is of {}, should be of {}"\
                .format(v, type(var), t)
                raise TypeError(msg)
            elif m is not None:
                if m == 0 and var <= 0:
                    msg = "Argument \"{}\" must be greater than zero".format(v)
                    raise ValueError(msg)
                elif m == 1:
                    msg = "Elements of tuple \"L\" must each be greater than zero when divided by argument \"dx\"".format(v)
                    for i in var:
                        if i <= 0:
                            raise ValueError(msg)

    def _write_data(self):
        """
            Writes the initial conditions and simulation settings to a file
            given by the "datafile" attribute, which will be read by the julia
            backend when initializing the simulation.  The file is saved in the
            "backend" directory.

            File will be of the following format:

                    0.000000E+00	Inner Initial Conditions
                    1.000000E+00	Outer Initial Conditions
                    1.000000E+01	Simulation Time
                    1.000000E-03	Time-Step
                    5:5	Array Shape
                    1.000000E-02	Position-Step
        """

        shape_str = ""
        for i in self.N:
            shape_str += "{:d}:".format(i)
        shape_str = shape_str[:-1]

        write_str  = "{:E}\tInner Initial Conditions\n".format(self.xc)
        write_str += "{:E}\tOuter Initial Conditions\n".format(self.xb)
        write_str += "{:E}\tSimulation Time\n".format(self.T)
        write_str += "{:E}\tTime-Step\n".format(self.dt)
        write_str += "{}\tArray Shape\n".format(shape_str)
        write_str += "{:E}\tPosition-Step\n".format(self.dx)
        save_path = "./backend/{}".format(self.datafile)
        with open(save_path, "w+") as outfile:
            outfile.write(write_str)

    def _call_backend(self, script = "prototype", algorithm = "ForwardEuler"):
        """
            Opens the desired julia script located in the "backend" directory.
            It will also pass the name of the simulation datafile to be read by
            the julia backend as a command line argument.
        """
        call(["julia", "{}.jl".format(script), self.datafile, algorithm],
        cwd="backend")

    def _read_backend(self, outfile = "outfile.dat"):
        """
            Once the backend has run its calculations, it will store an N+1
            dimensional array in an output file.  This method will allow us to
            access that data in the python frontend, and returns the julia array
            as a numpy array.
        """
        return np.load("./backend/{}".format(outfile))

    def _gen_Diffusor_obj(self, M):
        """
            Creates a Diffusor object using the array M and the simulation
            settings initialized in the constructor.
        """
        return Diffusor(M, self.T, self.dt, self.L, self.dx, "prototype")

class Diffusor:
    """
        Given that a dataset generated by a Diffusor_Generator object may
        require some time to calculate, it is best to store the data as an
        object that can be called upon for data visualization; this is the
        purpose of Diffusor objects.  They can be called upon to save an
        animation, or to display an image at a given time without needing to
        recalculate everything.
    """

    def __init__(self, M, T, dt, L, dx, sim_type = "prototype"):
        """
            Stores the data needed to successfully create a detailed plot
        """
        self.M = M                      # The Simulated Array
        self.T = T                      # Simulation Time
        self.dt = dt                    # Time-Step
        self.L = L                      # Physical Array Size
        self.dx = dx                    # Position-Step
        self.sim_type = sim_type        # Information on the Simulation

        self.t = np.arange(0, T, dt)    # Time Array

    def analytical_1D(self, x, t):
        """
            The one-dimensional analytical solution to the diffusion equation
            x and t should be arrays for best results, returns two meshgrids
            X and T, and their corresponding intensities.
        """
        X,T = np.meshgrid(x,t)
        u = -(2/np.pi)*np.sin(np.pi*X/(2*self.L[0]))*np.exp(-(np.pi/(2*self.L[0]))**2*T)
        return X, T, u

    def animate_2D(self, filename = "animation_2D.mp4", frames = None,
    litho = False):
        """
            Given a 2+1 dimensional array, will save a graphical visualization
            of the dataset into an mp4 file.
        """
        if frames is None:
            frames = len(self.M)-1
            step = 1
        elif isinstance(frames, int) and frames > 0 and frames < len(self.M):
            step = int(len(self.M)/frames)
        else:
            raise TypeError("Frames must be a positive integer smaller than the number of time steps")
        print("Initializing Animation", end = "")
        # Checking that the array is 2-D
        if len(self.L) != 2:
            raise Exception("Method \"animate_2D()\" only works for 2-D arrays")

        # Setting up the Plotting Area
        fig, ax = plt.subplots(figsize = (10, 6))

        # Preparing Axis Data

        xlim = self.M.shape[2]*self.dx
        ylim = self.M.shape[1]*self.dx

        x = np.arange(0, xlim, self.dx)
        y = np.arange(0, ylim, self.dx)

        if litho is True:
            x *= 1E-3
            y *= 1E-3
            self.M /= self.dx**3
            plt.xlabel("x [km]")
            plt.ylabel("y [km]")
            plt.title("Heat in the Lithosphere over Time, T= {:>5.3E}Gy".format(0))
        else:
            plt.xlabel("x [scaled]")
            plt.ylabel("y [scaled]")
            plt.title("Diffusion at T= {:>5.3E}s".format(0))

        # Creating the Color Meshes and Colorbar
        cax = ax.pcolormesh(x, y, self.M[0,:-1,:-1], cmap = 'magma',
        vmin = 0, vmax = np.max(self.M[:,:,1:-1]))
        cbar = fig.colorbar(cax)
        cbar.set_label("Intensity [scaled]")

        # Animation Loop
        def animate(i):
            cax.set_array(self.M[i,:-1,:-1].flatten())
            if litho is True:
                ax.set_title("Heat in the Lithosphere over Time, T= {:>5.3E}Gy".format(i*self.dt*1E-9))
            else:
                ax.set_title("Diffusion over Time, T= {:>5.3E}s".format(i*self.dt))
        print(" [DONE]\nSaving Animation", end = "")
        # Saving the Animation
        anim = FuncAnimation(fig, animate, interval = 100, frames = range(0,len(self.M),step))
        anim.save(filename)
        plt.close()
        print(" [DONE]")

    def plot_2D(self, t, litho = False, savename = False):
        """
            Given a 2+1 dimensional array, will display a graphical
            visualization of the dataset at the desired time "t".
        """

        # Checking that the array is 2-D
        if len(self.L) != 2:
            raise Exception("Method \"plot_2D(t)\" only works for 2-D arrays")

        # Making sure the time is within range of the simulation
        if t < 0:
            msg = "Negative times are not allowed".format(T)
            msg += ", attempted to plot for t= {:>5.3E}s failed".format(t)
            raise ValueError(msg)
        elif t > self.T:
            msg = "Simulation runs for {:>5.3E}s".format(T)
            msg += ", attempt to plot for t= {:>5.3E}s failed".format(t)
            raise ValueError(msg)

        # Searching for the closest available time:
        idx_vals = self.t - t
        idx_vals[idx_vals > 0] = np.inf
        idx = np.argmin(abs(idx_vals))

        # Preparing Axis Data
        xlim = self.M.shape[2]*self.dx
        ylim = self.M.shape[1]*self.dx

        x = np.arange(0, xlim, self.dx)
        y = np.arange(0, ylim, self.dx)

        # Initializing Plot and Labels
        fig, ax = plt.subplots()


        if litho is True:
            plt.xlabel("x [km]")
            plt.ylabel("y [km]")
            plt.title("Diffusion at T= {:>5.3E}Gy".format(t*1E-9))
        else:
            plt.xlabel("x [scaled]")
            plt.ylabel("y [scaled]")
            plt.title("Diffusion at T= {:>5.3E}s".format(t))

        # Plotting
        cax = plt.pcolormesh(x, y, self.M[idx,:-1,:-1], cmap = 'magma',
        vmin=0, vmax=self.M.max())
        cbar = fig.colorbar(cax)
        cbar.set_label("Intensity [scaled]")
        if savename is False:
            plt.show()
        else:
            plt.savefig(savename)

def test_Diffusor_visual():
    """
        Not rigorous – for visual testing.  Should produce an animation of a
        changing color gradient, as well as displaying five images.
    """

    # Initial Conditions
    T = 12                      # Simulation Runtime
    dt = 1E-1                   # Time-Step
    L = 1                       # "Physical" Array Dimensions
    x_steps = 50                # Number of Steps
    dx = L/x_steps              # Position-Step
    L = (L, L)

    # Generating test matrix
    t_steps = int(T/dt)
    M = np.ones((t_steps, x_steps, x_steps))
    for i in range(t_steps):
        M[i] = M[i]*i
    M = M/t_steps

    S = Diffusor(M, T, dt, L, dx)
    S.animate_2D(filename = "test_animation_2D.mp4")
    S.plot_2D(1)
    S.plot_2D(3)
    S.plot_2D(6)
    S.plot_2D(9)
    S.plot_2D(12)

if __name__ == "__main__":

    xc = 0                      # Initial Interior Conditions
    xb = 1                      # Initial Boundary Conditions
    T = 1E-2                    # Simulation Runtime
    dt = 1E-6                   # Time-Step
    L = (1, 1)                  # "Physical" Array Dimensions
    dx = 1E-2                   # Position-Step

    G = Diffusor_Generator(xc, xb, T, dt, L, dx)
    D = G.simulate(algorithm = "CrankNicolson")

    D.plot_2D(T/100)
    D.plot_2D(T/50)
    D.plot_2D(T/10)
    D.plot_2D(T/5)
    D.plot_2D(T/2)
    D.plot_2D(T)
    D.animate_2D(frames = 400, litho = False)
