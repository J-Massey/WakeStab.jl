import numpy as np
from lotusvis.spod import spod
import h5py
import os

import matplotlib.pyplot as plt
import seaborn as sns
import scienceplots
import matplotlib.animation as animation
plt.style.use(["science"])
plt.rcParams["font.size"] = "10.5"

def load_and_process_data(filepath):
    data = np.load(filepath)
    data = np.einsum("ijk -> kji", data)
    return data[::2, ::2, :]

# Define the slicing pattern as a variable for clarity
slice_pattern = (slice(None, None, 2), slice(None, None, 2), slice(None, None, 4))

u = load_and_process_data("data/stationary/10k/u.npy")
v = load_and_process_data("data/stationary/10k/v.npy")
p = load_and_process_data("data/stationary/10k/p.npy")

xlims, ylims = (-0.35, 2), (-0.35, 0.35)
nx, ny, nt = v.shape

T = 7  # number of cycles
dt = T / nt

pxs = np.linspace(*xlims, nx)
dx = np.diff(pxs).mean()

pys = np.linspace(*ylims, ny)
dy = np.diff(pys).mean()

# Reynolds decomposition
u_flucs = np.empty_like(u)
v_flucs = np.empty_like(v)
p_flucs = np.empty_like(p)
u_mean = u.mean(axis=2)
v_mean = v.mean(axis=2)
p_mean = p.mean(axis=2)
for t in range(nt):
    u_flucs[:, :, t] = u[:, :, t] - u_mean
    v_flucs[:, :, t] = v[:, :, t] - v_mean
    p_flucs[:, :, t] = p[:, :, t] - p_mean

print("Flucs done")

# means = np.array([u_mean, v_mean, p_mean])
flucs_field = np.array([u_flucs, v_flucs, p_flucs])
# flat_mean_field = means.reshape(3, nx * ny)
flatflucs = flucs_field.reshape(3, nx * ny, nt)

print("FFT done")

# Define inputs for DMD on the vertical velocity
flatflucs.resize(3*nx*ny, nt)
flatflucs = flatflucs.T

# Test plot
fig, ax = plt.subplots(figsize=(5, 3))
lim = [-0.5, 0.5]
levels = np.linspace(lim[0], lim[1], 44)
_cmap = sns.color_palette("seismic", as_cmap=True)
cs = ax.contourf(
    pxs,
    pys,
    flatflucs.mean(axis=0).reshape(ny, nx),
    levels=levels,
    vmin=lim[0],
    vmax=lim[1],
    # norm=norm,
    cmap=_cmap,
    extend="both",
)
ax.set_aspect(1)
# ax.set_title(f"$\omega={frequencies_bsort[oms]:.2f},St={frequencies_bsort[oms]/(2*np.pi):.2f}$")
plt.savefig(f"./stationary/figures/testv10k.pdf", dpi=600)
plt.close()

print("Plotted")


spod(flatflucs,dt,"stationary/10k",weight='default',nOvlp='default',window='default',method='fast', nDFT=nt/4)

SPOD_LPf  = h5py.File(os.path.join('stationary/10k','SPOD_LPf.h5'),'r') # load data from h5 format

L = SPOD_LPf['L'][:,:]    # modal energy E(f, M)
# P = SPOD_LPf['P'][:,:,:]  # mode shape
f = 2*np.pi*SPOD_LPf['f'][:]      # frequency
SPOD_LPf.close()


hl_idx = 3
fig, ax = plt.subplots(figsize=(4, 3))
        
# loop over each mode
for imode in range(L.shape[1]):
    if imode < hl_idx:  # highlight modes with colors
        ax.loglog(f[0:-1],L[0:-1,imode],label='Mode '+str(imode+1)) # truncate last frequency
    elif imode == L.shape[1]-1:
        ax.loglog(f[0:-1],L[0:-1,imode],color='lightgrey',label='Others')
    else:
        ax.loglog(f[0:-1],L[0:-1,imode],color='lightgrey',label='')

# figure format
ax.set_xlabel(r'$\omega$')
ax.set_ylabel(r'$\lambda_i$')
ax.legend(loc='upper right')

plt.savefig(f"./stationary/figures/SPODspectrum.png", dpi=600)
plt.close()