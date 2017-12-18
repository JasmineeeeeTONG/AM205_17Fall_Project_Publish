import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy import sparse


def my_laplacian(M):
    """
    Return Laplacian of a 2D matrix M with periodic boundary condition
    """
    return -4 * M + np.roll(M, 1, axis=1) + np.roll(M, -1, axis=1) + np.roll(M, 1, axis=0) + np.roll(M, -1, axis=0)


def Laplace_matrix(Ny, Nx):
    """
    Return Laplace matrix that operates on flattened 2d array of size Ny X Nx
    (Jasmine's method)
    """
    N = Ny * Nx
    I = np.eye(N)
    T = -4 * I + np.roll(I, -1, axis=1) + np.roll(I, -Nx, axis=1) + np.roll(I, 1, axis=1) + np.roll(I, Nx, axis=1)
    # Correct vertical boundary values
    for i in range(N):
        if i % Nx == 0:  # left vertical boundary
            if i - 1 < 0:
                T[i, i + N - 1] = 0
            else:
                T[i, i - 1] = 0
            T[i, i - 1 + Nx] = 1
        elif i % Nx == (Nx - 1):  # right vertical boundary
            if i + 1 >= N:
                T[i, i - N + 1] = 0
            else:
                T[i, i + 1] = 0
            T[i, i + 1 - Nx] = 1
    return sparse.csr_matrix(T)


def Laplace_matrix_sparse(Ny, Nx):
    """
    Return Laplace matrix that operates on flattened 2d array of size Ny X Nx
    (Rui's method)
    """
    N = Nx * Ny

    center = np.ones(N) * (-4)
    west = np.ones(N);
    west[np.arange(N) % Nx == 0] = 0
    east = np.ones(N);
    east[np.arange(N) % Nx == Nx - 1] = 0

    vals = [center, east, west[1:], 1, 1, 1, 1]
    offsets = np.array([0, 1, -1, Nx, -Nx, -N + Nx, N - Nx])

    D2 = sparse.diags(vals, offsets)

    D2.setdiag(1 - west, Nx - 1)
    D2.setdiag((1 - east)[Nx - 1:], 1 - Nx)

    return D2

def plot_norm_evolution(time_range, U_norm_arr, V_norm_arr, r, time_steps, end_t):
	"""
    Plot the U and V matrices' Frobenius norms' evolution over time
    :param time_range:	time range of the entire time duration for pattern formation [ndarray of shape (Nt,)]
    :param U_norm_arr:  1D array of the Frobenius norms of u over time [ndarray of shape (Nt,)]
    :param V_norm_arr:  1D array of the Frobenius norms of v over time [ndarray of shape (Nt,)]
    :param r:      		the denominator of the time steps for the cutoff point upto which to plot the norm's evolution [int]
    :param time_steps:	number of time steps = int(end_t/dt) [int]
    :param end_t:		the end point time of the evolution [int]
    :return:        	None
    """
	fig, axes = plt.subplots(1, 2, figsize = (14, 6))
	cutoff = int(time_steps/r)
	axes[0].plot(time_range[:cutoff], U_norm_arr[:cutoff], 'b-')
	axes[0].set_title('Frobenius_norm(U - np.mean(U)) \n over time (t <= {})'.format(int(end_t/r)), fontsize=16)
	axes[0].set_xlabel('Time (sec)', fontsize=16)
	axes[1].plot(time_range[:cutoff], V_norm_arr[:cutoff], 'r-')
	axes[1].set_title('Frobenius_norm(V - np.mean(V)) \n over time (t <= {})'.format(int(end_t/r)), fontsize=16)
	axes[1].set_xlabel('Time (sec)', fontsize=16)
	plt.show()

def plot_pattern_evolution(M, h, dt, time_steps, name, r, Nout):
    """
    Plot a series of the Nout states of the pattern (M) over time before some cutoff point = int(time_steps/r)
    :param M:           solution of u or v in the Ny by Nx grid for Nt time steps [ndarray of shape Nt X Ny X Nx]
    :param h:           space step size [float]
    :param dt:          time step size [float]
    :param time_steps:  number of time steps = int(end_t/dt) [int]
    :param name:        name of the pattern (U or V)
    :param r:           the denominator of the time steps for the cutoff point upto which to plot the norm's evolution [int]
    :param Nout:        number of pattern figures to output [int]
    :return:            None
    """
    Nx, Ny = M.shape[2], M.shape[1]
    t_size = int(time_steps/r/Nout) # the length of time between 2 output plots
    t_points = [i * t_size for i in np.arange(Nout)] # time points when to output a plot
    fig, axes = plt.subplots(1, Nout, figsize = (24, int(24/Nout)))
    for i, ax in enumerate(axes):
        t = t_points[i]
        
        # 2D meshgrid setup
        x = np.linspace(0, (Nx - 1) * h, Nx)
        y = np.linspace(0, (Ny - 1) * h, Ny)
        X, Y = np.meshgrid(x, y)

        if np.amin(M[t]) != np.amax(M[t]):
            levelsM = np.linspace(np.amin(M[t]), np.amax(M[t]), 20)
            ax.contourf(X, Y, M[t], levels=levelsM, cmap=plt.cm.coolwarm)
        else:
            ax.contourf(X, Y, M[t], cmap=plt.cm.coolwarm)
        ax.set_title('{} (t = {})'.format(name, (dt * t)))
        ax.set_aspect('equal')
    
    plt.show()

def plot_pattern(U, V, tu, tv, h, dt, filled=True):
    """
    Show contour plots of u at time step tu and v at time step tv
    :param U:       solution of u in the Ny by Nx grid for Nt time steps [ndarray of shape Nt X Ny X Nx]
    :param V:       solution of v in the Ny by Nx grid for Nt time steps [ndarray of shape Nt X Ny X Nx]
    :param tu:      for which time step to plot u [int]
    :param tv:      for which time step to plot v [int]
    :param h:       space step size [float]
    :param dt:      time step size [float]
    :param filled:  whether or not to plot filled contours [boolean]
    :return:        None
    """
    Nx, Ny = U.shape[2], U.shape[1]

    # 2D meshgrid setup
    x = np.linspace(0, (Nx - 1) * h, Nx)
    y = np.linspace(0, (Ny - 1) * h, Ny)
    X, Y = np.meshgrid(x, y)

    # Contour plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    extent = [x[0], x[-1], y[0], y[-1]]
    levelsU = np.linspace(np.amin(U[tu]), np.amax(U[tu]), 20)
    levelsV = np.linspace(np.amin(V[tv]), np.amax(V[tv]), 20)

    if not filled and tu != 0 and tv != 0:
        csU = axes[0].contour(X, Y, U[tu], levels=levelsU, extent=extent, cmap=plt.cm.coolwarm)
        csV = axes[1].contour(X, Y, V[tv], levels=levelsV, extent=extent, cmap=plt.cm.coolwarm)
    else:
        csU = axes[0].contourf(X, Y, U[tu], levels=levelsU, extent=extent, cmap=plt.cm.coolwarm)
        csV = axes[1].contourf(X, Y, V[tv], levels=levelsV, extent=extent, cmap=plt.cm.coolwarm)

    fig.colorbar(csU, ax=axes[0], shrink=0.8)
    fig.colorbar(csV, ax=axes[1], shrink=0.8)

    axes[0].set_title('U at n = %s, time = %.2f sec' % (tu, tu * dt), fontsize=16)
    axes[1].set_title('V at n = %s, time = %.2f sec' % (tv, tv * dt), fontsize=16)

    axes[0].set_aspect('equal')
    axes[1].set_aspect('equal')

    fig.tight_layout()

    plt.show()


def plot_pattern_end_states(end_states, titles, h):
    """
    Plot the initial condition and different ending state with different parameter setup
    :param end_states:  ending state patterns [ndarray of shape n X Ny X Nx], 
                        where n is the number of different parameter setups
    :param titles:      a list titles for each parameter setup [list of size n]
    :param h:           space step size [float]
    :return:            None
    """
    n_axes = end_states.shape[0]
    Nx, Ny = end_states.shape[2], end_states.shape[1]
    fig, axes = plt.subplots(1, n_axes, figsize = (30, int(30/n_axes)))
    
    for i, ax in enumerate(axes):
        # 2D meshgrid setup
        x = np.linspace(0, (Nx - 1) * h, Nx)
        y = np.linspace(0, (Ny - 1) * h, Ny)
        X, Y = np.meshgrid(x, y)
        
        if np.amin(end_states[i]) != np.amax(end_states[i]):
            levels = np.linspace(np.amin(end_states[i]), np.amax(end_states[i]), 20)
            ax.contourf(X, Y, end_states[i], levels=levels, cmap=plt.cm.coolwarm)
        else:
            ax.contourf(X, Y, end_states[i], cmap=plt.cm.coolwarm)
        ax.set_title(titles[i])
        ax.set_aspect('equal')
    plt.show()


def plot_init(U0, V0, h, filled=True):
    """
    Show contour plots of u and v at the starting time
    :param U0:      initial state of u in the Ny by Nx grid for Nt time steps [ndarray of shape Nt X Ny X Nx]
    :param V0:      initial state of v in the Ny by Nx grid for Nt time steps [ndarray of shape Nt X Ny X Nx]
    :param h:       space step size [float]
    :param filled:  whether or not to plot filled contours [boolean]
    :return:        None
    """
    Nx, Ny = U0.shape[1], U0.shape[0]

    # 2D meshgrid setup
    x = np.linspace(0, (Nx - 1) * h, Nx)
    y = np.linspace(0, (Ny - 1) * h, Ny)
    X, Y = np.meshgrid(x, y)

    # Contour plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    extent = [x[0], x[-1], y[0], y[-1]]

    if not filled:
        csU = axes[0].contour(X, Y, U0, extent=extent, cmap=plt.cm.coolwarm)
        csV = axes[1].contour(X, Y, V0, extent=extent, cmap=plt.cm.coolwarm)
    else:
        csU = axes[0].contourf(X, Y, U0, extent=extent, cmap=plt.cm.coolwarm)
        csV = axes[1].contourf(X, Y, V0, extent=extent, cmap=plt.cm.coolwarm)

    fig.colorbar(csU, ax=axes[0], shrink=0.8)
    fig.colorbar(csV, ax=axes[1], shrink=0.8)

    axes[0].set_title('Initial U', fontsize=16)
    axes[1].set_title('Initial V', fontsize=16)

    axes[0].set_aspect('equal')
    axes[1].set_aspect('equal')

    fig.tight_layout()

    plt.show()


def animate_pattern(U, V, h, dt, Nsteps, Nout):
    """
    Animate the contour plots of u, v for Nsteps time steps
    :param U:       solution of u in the Ny by Nx grid for Nt time steps [ndarray of shape Nt X Ny X Nx]
    :param V:       solution of v in the Ny by Nx grid for Nt time steps [ndarray of shape Nt X Ny X Nx]
    :param h:       space step size [float]
    :param dt:      time step size [float]
    :param Nsteps:  total number of time steps to animate [int]
    :param Nout:    output figure per Nout time steps [int]
    :return:        [animation object]
    """

    Nx, Ny = U.shape[2], U.shape[1]

    # 2D meshgrid setup
    x = np.linspace(0, (Nx - 1) * h, Nx)
    y = np.linspace(0, (Ny - 1) * h, Ny)
    X, Y = np.meshgrid(x, y)

    # Contour plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    extent = [x[0], x[-1], y[0], y[-1]]
    levelsU = np.linspace(np.amin(U), np.amax(U), 20)
    levelsV = np.linspace(np.amin(V), np.amax(V), 20)

    csU = axes[0].contourf(X, Y, U[0], levels=levelsU, extent=extent, cmap=plt.cm.coolwarm)
    csV = axes[1].contourf(X, Y, V[0], levels=levelsV, extent=extent, cmap=plt.cm.coolwarm)

    fig.colorbar(csU, ax=axes[0], shrink=0.8)
    fig.colorbar(csV, ax=axes[1], shrink=0.8)

    axes[0].set_aspect('equal')
    axes[1].set_aspect('equal')

    fig.tight_layout()

    def updatefig(i):
        axes[0].clear()
        axes[1].clear()

        axes[0].contourf(X, Y, U[i * Nout], levels=levelsU, extent=extent, cmap=plt.cm.coolwarm)
        axes[1].contourf(X, Y, V[i * Nout], levels=levelsV, extent=extent, cmap=plt.cm.coolwarm)

        axes[0].set_title('U at n = %s, time = %.2f sec' % (i * Nout, i * Nout * dt), fontsize=16)
        axes[1].set_title('V at n = %s, time = %.2f sec' % (i * Nout, i * Nout * dt), fontsize=16)

    ani = animation.FuncAnimation(fig, updatefig, frames=int(Nsteps / Nout), interval=200, blit=False)

    # plt.show()

    return ani


def animate_pattern_2(U, V, h, dt, Nsteps, Nout):
    """
    Animate the imshow plots of u, v for Nsteps time steps
    :param U:       solution of u in the Ny by Nx grid for Nt time steps [ndarray of shape Nt X Ny X Nx]
    :param V:       solution of v in the Ny by Nx grid for Nt time steps [ndarray of shape Nt X Ny X Nx]
    :param h:       space step size [float]
    :param dt:      time step size [float]
    :param Nsteps:  total number of time steps to animate [int]
    :param Nout:    output figure per Nout time steps [int]
    :return:        [animation object]
    """

    Nx, Ny = U.shape[2], U.shape[1]

    # 2D meshgrid setup
    x = np.linspace(0, (Nx - 1) * h, Nx)
    y = np.linspace(0, (Ny - 1) * h, Ny)
    X, Y = np.meshgrid(x, y)

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    extent = [x[0], x[-1], y[0], y[-1]]

    imU = axes[0].imshow(U[0], origin='lower', extent=extent, animated=True)
    imV = axes[1].imshow(V[0], origin='lower', extent=extent, animated=True)
    cbarU = fig.colorbar(imU, ax=axes[0], shrink=0.8)
    cbarV = fig.colorbar(imV, ax=axes[1], shrink=0.8)
    axes[0].set_title('U at n = %s, time = %.2f sec' % (0, 0 * dt), fontsize=16)
    axes[1].set_title('V at n = %s, time = %.2f sec' % (0, 0 * dt), fontsize=16)

    def updatefig(i):
        global cbarU, cbarV
        cbarU.remove()
        cbarV.remove()

        axes[0].cla()
        axes[1].cla()

        imU = axes[0].imshow(U[i * Nout], origin='lower', extent=extent, animated=True)
        imV = axes[1].imshow(V[i * Nout], origin='lower', extent=extent, animated=True)
        cbarU = fig.colorbar(imU, ax=axes[0], shrink=0.8)
        cbarV = fig.colorbar(imV, ax=axes[1], shrink=0.8)
        axes[0].set_title('U at n = %s, time = %.2f sec' % (i * Nout, i * Nout * dt), fontsize=16)
        axes[1].set_title('V at n = %s, time = %.2f sec' % (i * Nout, i * Nout * dt), fontsize=16)
        return imU, imV

    ani = animation.FuncAnimation(fig, updatefig, frames=int(Nsteps / Nout), interval=200, blit=True)

    # plt.show()

    return ani


