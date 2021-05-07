import numpy as np

import holoviews as hv; hv.extension('bokeh', logo=False)
import panel as pn; pn.extension()

# ----------------------------------------------------------------------
def set_toolbar_autohide(plot, element):
    '''autohide the bokeh toolbar. Use with hv.opts(  hooks=[set_toolbar_autohide]'''
    bokeh_plot = plot.state
    bokeh_plot.toolbar.autohide = True

# ======================================================================
def spikes(data, y_base=0, dims=["Time", "x"], label="Signal", curve=True):
    '''plot stems and a curve'''
    if isinstance(data, tuple):
        t,s=data
    else:
        t=np.arange(0,len(data), 1)
        s=data

    vlines = [ np.array( [[t[i], y_base], [t[i], s[i]]]) for i in range(len(s)) ]

    hs = hv.Path( vlines, kdims=dims, label=label ).opts( show_legend=True, muted_alpha=0., color='black')

    if curve: hs = hs * hv.Curve((t,s), dims[0], dims[1], label=label).opts(line_width=0.8)
    return hs

def cx_spikes(data, dims=["Time", "x"], y_base=0, curve=False):
    '''plot stems and a curve for complex data'''
    if isinstance(data, tuple):
        t,s=data
    else:
        t=np.arange(0,len(data), 1)
        s=data
    h = hv.Overlay([
            *spikes((t, np.real(s)), y_base=y_base, label='real', curve=True).opts( "Path", color='blue'),
            *spikes((t, np.imag(s)), y_base=y_base, label='imag', curve=True).opts( "Path", color='red')])
    return h

# ========================================================================
def interpolated_scalogram( x,y, d, method='nearest'):
    ''' interpolate the values of a scalogram'''
    from scipy.interpolate import griddata

    x_lin = np.linspace( x[np.argmin(x)], x[np.argmax(x)], len(x), endpoint=True)

    ndx_ymin = np.argmin(y)
    ndx_ymax = np.argmax(y)
    if ndx_ymax == 0:
        y_lin = np.linspace( y[ndx_ymin], y[ndx_ymax] + 0.25*(y[0]-y[1]), len(y), endpoint=True)
    else:
        y_lin = np.linspace( y[ndx_ymin], y[ndx_ymax] + 0.25*(y[ndx_ymax]-y[ndx_ymax-1]), len(y), endpoint=True)

    xx,yy = np.meshgrid(x, y)
    xi,yi = np.meshgrid(x_lin,y_lin)

    di = griddata( (xx.ravel(), yy.ravel()), d.ravel(), (xi.ravel(), yi.ravel()), method=method )
    return xi,yi, di.reshape(d.shape)

def estimate_levels( d, l = np.sin(0.5*np.pi*np.linspace( 0.1, 1, 5, endpoint=False)), decimals=2 ):
    '''obtain a set of labels for a contour plot'''
    dmin,dmax = np.min(d), np.max(d)
    return np.round( [dmin + t*(dmax-dmin) for t in l], decimals)

def plot_qmesh_contours(t, freqs, tfr, l = None, filled=True, overlaid=True, img_args={}, contour_args={} ):
    '''plot an interpolated QuadMesh as an Image overlaid with contours'''
    from holoviews.operation import contours
    ti,freqsi,tfri = interpolated_scalogram( t, freqs, tfr, 'cubic')
    img = hv.Image( (ti[0,:], freqsi[:,0], tfri), ["Time", "Frequency"] )\
            .opts(cmap="Viridis", width=400,show_grid=False)\
            .opts( **img_args )
    if l is None: l = estimate_levels(tfr)
    return contours(img, levels=l, filled=filled, overlaid=overlaid).opts("Contours", **contour_args)
