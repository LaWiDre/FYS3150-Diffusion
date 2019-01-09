using NPZ

function printMatrix(M)
    #=
    Ineffective function for printing smaller matrices
    aestethically
    =#
    for i=1:length(M[1,:])
        println(M[:,i])
    end
end

function ForwardStep(j, n, Ns, alph, Ufinal)
    #Time loop and boundary condition
    Ufinal[j,:,end] .= 1
    @inbounds for k=1:n
        #Dimension loop
        Nk = Int64(Ns[k])
        @inbounds for i=2:(Nk-1)
            #Spatial loop
            Ufinal[j,k,i] = alph*(Ufinal[j-1,k,i+1] + Ufinal[j-1,k,i-1]) + (1-2alph)*Ufinal[j-1,k,i]
        end #for
    end #for
    return Ufinal[j,:,:]
end

function BackwardStep(j, n, Ns, alpha, Ufinal)
    #Time loop and boundary condition
    Ufinal[j,:,:] .= copy(Ufinal[j-1,:,:])
    @inbounds for k=1:n
        Nx = Int64(Ns[k])
        y = ones(Nx)*(1 - 2alpha)

        @inbounds for i=2:(Nx-1)
            q = alpha/y[i-1]
            y[i] -= q*alpha         #Reevaluating diagonal
            Ufinal[j,k,i] -= q*Ufinal[j-1,k,i-1]
        end

        #Backward Substitution
        @inbounds for i=Nx:-1:3
            Ufinal[j, k, i-1] -= Ufinal[j-1, k, i]*alpha  #Reevaluating augmented column element i
        end

        #Normalizing the solutions
        @inbounds for i=1:(Nx-1)
            Ufinal[j,k,i] /= y[i]                #Dividing augmented element by diagonal
        end
    end
    return Ufinal[j,:,:]
end

function ForwardEuler(U0, T, dt, dx)
    #=
    Attempt two at getting the explisit ForwardEuler algorithm to work
    this time without messy linear algebra. Takes the arguments:

    U0 - (Nx,n)-array - Initial state of the system. n is the number of Dimensions
                         and Nx is the number of points in said dimension
    T  - Float/Int     - Period of simulation
    dt - Float         - Time resolution
    dx - (n)-array     - Distance between points in the nth dimension
    =#

    #Array and variable initialisation
    alph = dt/dx^2
    time = collect(0:dt:T)
    Nt = length(time)
    n = length(U0[1,:])

    #Setting up in case of different length in dimensions
    Ns = zeros(n)
    for i=1:n
        Ns[i] = length(U0[:,i])
    end
    Nx = Int64(maximum(Ns))

    #Prepping the final matrix with initial condition
    Ufinal = zeros((Nt,n, Nx))
    Ufinal[1,:,:] = transpose(U0)

    @inbounds for j=2:Nt
        Ufinal[j,:,:] = ForwardStep(j, n, Ns, alph, Ufinal)
    end #for
    return Ufinal
end

function rrefTridiag(y, z, x, b, dx)
        #=
            Given a matrix with three centered diagonals:
                y: Diagonal array
                z: Top Diagonal Array
                x: Bottom Diagonal Array
                b: Augmented Matrix Column

            Performs Gaussian elimination on a matrix of the given form, and returns
            a vector representative of the solution
            Function returns a variable
            B-tilde which is an augmented version of b to account for it being twice integrated
            This is done by multiplying each element with dx^2
        =#
        b = copy(b)
        N = size(x)[1]              #Array lengths
        #Forward Substitution
        for i=3:N
            b[i] += b[i-1]/y[i-1]         #Reevaluating augmented column element i
            y[i] += z[i-1]/y[i-1]         #Reevaluating diagonal
        end
        #Backward Substitution
        b[N] = 0                        #Applying upper Dirichlet boundary condition
        for i=N-1:-1:2
            b[i-1] += b[i]/y[i]  #Reevaluating augmented column element i
        end
        b[1] = 0                        #Applying lower Dirichlet boundary condition
        #Normalizing the solutions
        for i=1:N
            b[i] /= y[i]                #Dividing augmented element by diagonal
        end
        btild = copy(b)
        return btild
end

function BackwardEuler(U0, T, dt, dx)
    #=
        Given a matrix with three centered diagonals:
            y: Diagonal array
            z: Top and Bottom Diagonal Array
            b: Augmented Matrix Column
        Performs Gaussian elimination on a matrix of the given form, and returns
        a vector representative of the solution
        Function returns a matrix U which is the
    =#
    time = collect(0:dt:T)
    Nt = length(time)
    n = length(U0[1,:])

    #Setting up in case of different length in dimensions
    Ns = zeros(n)
    for i=1:n
        Ns[i] = length(U0[:,i])
    end
    Nx = Int64(maximum(Ns))

    #Prepping the final matrix with initial condition
    Ufinal = zeros((Nt,n, Nx))
    Ufinal[1,:,:] = U0

    alpha = -dt/dx^2


    @inbounds for j=2:Nt
        #Time loop and boundary condition
        Ufinal[j,:,:] .= copy(Ufinal[j-1,:,:])
        @inbounds for k=1:n
            Nx = Int64(Ns[k])
            y = ones(Nx)*(1 - 2alpha)


            @inbounds for i=2:(Nx-1)
                q = alpha/y[i-1]
                y[i] -= q*alpha         #Reevaluating diagonal
                Ufinal[j,k,i] -= q*Ufinal[j-1,k,i-1]
            end


            #Backward Substitution
            @inbounds for i=Nx:-1:3
                Ufinal[j, k, i-1] -= Ufinal[j-1, k, i]*alpha  #Reevaluating augmented column element i
            end

            #Normalizing the solutions
            @inbounds for i=1:(Nx-1)
                Ufinal[j,k,i] /= y[i]                #Dividing augmented element by diagonal
            end

        end

    end
    return Ufinal
end

function CrankNicolson(U0, T, dt, dx)
    #=
    Function implementing the implicit Crank-Nicolson scheme to solve
    the diffusion equation. Takes the arguments:

    U0  -  Initial state of the system
    T   -  Simulation runtime
    dt  -  Timestep
    dx  -  steplength
    =#

    time = collect(0:dt:T)
    Nt = length(time)
    n = length(U0[1,:])

    #Setting up in case of different length in dimensions
    Ns = zeros(n)
    for i=1:n
        Ns[i] = length(U0[:,i])
    end

    Nx = Int64(maximum(Ns))
    #Prepping the final matrix with initial condition
    Ufinal = zeros((Nt, n, Nx))
    Ufinal[1,:,:] = transpose(U0)
    alpha = 0.5*dt/dx^2

    @inbounds for j=2:Nt
        #Time loop and boundary condition
        R = copy(Ufinal[j-1,:,:])
        Ufinal[j,:,:] .= copy(Ufinal[j-1,:,:])
        @inbounds for k=1:n
            Nx = Int64(Ns[k])
            
            @inbounds for i=2:(Nx-1)
                R[k, i] = alpha*(Ufinal[j-1,k, i+1] + Ufinal[j-1,k,i-1]) + (1 - 2alpha)*Ufinal[j-1, k, i]
            end
            
            y = ones(Nx)*(1 + 2alpha)

            @inbounds for i=2:(Nx-1)
                q = -alpha/y[i-1]
                y[i] += q*alpha         #Reevaluating diagonal
                Ufinal[j,k,i] -= q*R[k,i]
            end

            #Backward Substitution
            @inbounds for i=Nx:-1:3
                Ufinal[j, k, i-1] += R[k, i]*alpha  #Reevaluating augmented column element i
            end

                #Normalizing the solutions
            @inbounds for i=1:(Nx-1)
                Ufinal[j,k,i] /= 1.01*y[i]                #Dividing augmented element by diagonal
            end
        end

        if n > 1
            @inbounds for i=1:Nx
                Nx = Int64(Ns[k])
                
                @inbounds for k=2:(n-1)
                    R[k,i] = alpha*(Ufinal[j-1,k, i+1] + Ufinal[j-1,k,i-1]) + (1 - 2alpha)*Ufinal[j-1, k, i]
                end
                
                y = ones(Nx)*(1 + 2alpha)
    
                @inbounds for i=2:(Nx-1)
                    q = -alpha/y[i-1]
                    y[i] += q*alpha         #Reevaluating diagonal
                    Ufinal[j,k,i] -= q*R[k,i]
                end
    
                #Backward Substitution
                @inbounds for i=Nx:-1:3
                    Ufinal[j, k, i-1] += R[k, i]*alpha  #Reevaluating augmented column element i
                end
    
                    #Normalizing the solutions
                @inbounds for i=1:(Nx-1)
                    Ufinal[j,k,i] /= 1.01*y[i]                #Dividing augmented element by diagonal
                end
            end
        end
    end

    return Ufinal
end

function read_file_data(filename)
    #=
        Given a data-file generated in the python class Diffuser, will extract
        and return the different initial conditions and simulation settings for
        the upcoming integrations as a list of Float64s and Int64s.
    =#
    quantities = ["xc", "xb", "T", "dt", "N", "dx"]         # All Quantities
    values = []                                             # The values of each respective quantity
    open(filename) do infile                                # Opening the datafile
        for (line, q) in zip(eachline(infile), quantities)  # Iterating through the datafile's lines
            if q != "N"                                     # Checking if current value should be of type Tuple
                val = parse(Float64, split(line)[1])        # Converting Strings to Float64
            else
                dims = split(line)                           # Extracting the Array Shape
                dims = split(dims[1], ":")                   # Gathering Individual Dimensions
                val = []
                for d in dims
                    push!(val, parse(Int64, d))
                end
            end
            push!(values, val)                              # Appending current value to values list
        end
    end
    return values
end

function initial_conditions(values)
    #=
        Given an array of values generated from "read_file_data()", will
        return a Matrix of values "xc", with values at an index given by
        [:,:, ... ,:,end] (ie the boundaries) set to "xb".

        Here is an example with L = (5, 5), xc = 0, xb = 1:

                               [ 0 0 0 0 1;
                                 0 0 0 0 1;
                            M =  0 0 0 0 1;
                                 0 0 0 0 1;
                                 0 0 0 0 1 ]
    =#

    xc, xb, T, dt, N, dx = values                   # Values read from frontend
    L = Tuple(N)                                    # Converting L into a Tuple
    M = ones(L).*xc                                 # Generating the final matrix

    # If 1-D, a special case must take over the general case:
    if length(L) == 1
        M[end] = xb                                 # Replacing the boundary of M with matrix B
    else
        # Here, we create the slice [:,:, ... ,:,end] in three steps:
        M_slice = [L[1]]
        for l in L[2:end]
            M_slice = vcat(M_slice, [1:l])
        end
        M_slice = CartesianIndices(Tuple(M_slice))
        B_dims = L[2:end]
        B = ones(B_dims).*xb                        # Generating D-1 dimensional boundary

        M[M_slice] = B                              # Replacing the boundary of M with matrix B
    end

    return M
end


function save_array(arr, filename = "outfile.dat")
    npzwrite(filename, arr)
end

function main(test = nothing)
    M_final = nothing #To solve some scope issues
    if test == "1DFE"
        datafile = ARGS[1]
        values = read_file_data(datafile)
        M = initial_conditions(values)
        xc, xb, T, dt, N, dx = values
        alph = dt/dx^2
        test = ForwardEuler(M, T, dt, dx)
    elseif test == nothing
        datafile = ARGS[1]
        values = read_file_data(datafile)
        M_initial = initial_conditions(values)
        xc, xb, T, dt, N, dx = values
        if ARGS[2] == "ForwardEuler"
            M_final = ForwardEuler(M_initial, T, dt, dx)
        elseif ARGS[2] == "BackwardEuler"
            M_final = BackwardEuler(M_initial, T, dt, dx)
        elseif ARGS[2] == "ForwardEulerLitho"
            M_final = ForwardEulerLitho(M_initial, T, dt, dx)
        elseif ARGS[2] == "CrankNicolson"
            M_final = CrankNicolson(M_initial, T, dt, dx)
        end
        print("Saving Array")
        save_array(M_final)
        println(" [DONE]")

    elseif test == "debug"
        #This is a debugging option and isn't made for
        #high quality simulations in mind
        T = 1
        dt = 5e-3
        dx = 1e-1
        M = zeros((10,10))
        M[:,end] .= 1
        M_final = CrankNicolson(M,T,dt,dx)
    else
        error("Value \"$test\" for argument \"test\" is invalid.")
    end
end

main()
