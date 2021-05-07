import numpy as np

import holoviews as hv; hv.extension('bokeh', logo=False)
import panel as pn; pn.extension()

# ============================================================================
def ngon_data( x=0,y=0, specs=[(1,1)], orientation=0., arc=(0,2*np.pi), npoints=3 ):
    ''' compute coordinate locations for n-gons with vertices on an ellipse

    Args:
        x           : x coordinate of n-gon center
        y           : y coordinate of n-gon center
        specs       : array of (a,b) lengths of principal axes of the ellipse(s)
        orientation : inclination of the principal axis of the ellipse in radians
        arc         : (a1,a2) angles in radians of the subtended arc of the n-gon vertices
        npoints     : number of vertices

    Notes:
        | since the resulting paths are closed, the computation yields npoints+1 vertices;
        | thus, arcs that do not correspond to a full circle result in an extra vertex
    '''
    t_vals = np.linspace(*arc,npoints+1)
    s = np.sin(t_vals)
    c = np.cos(t_vals)
    rot  = np.array([[np.cos(orientation), -np.sin(orientation)],
                     [np.sin(orientation),  np.cos(orientation)]])
    gons = []
    for (a,b) in specs:
        data = np.array(list(zip(a*c,b*s)))
        gons.append( np.tensordot(rot, data.T, axes=[1,0]).T+np.array([x,y]))

    return gons
# ----------------------------------------------------------------------------
def ngon_ring(x=0, y=0, specs=[(1,1),(.9,.9)], arc=(0,2*np.pi), orientation=0, npoints=40,
              line_color='k', line_alpha=1, fill_color='k', fill_alpha=0., label=''):
    ''' an ngon outline with finite width
    '''
    l = ngon_data(x,y, specs=specs, arc=arc,orientation=orientation, npoints=npoints)
    d = ( np.hstack([ l[0][:,0],l[1][::-1,0]] ), np.hstack([ l[0][:,1],l[1][::-1,1]] ) )
    
    o_b = {'Polygons' : dict( color=fill_color, alpha=fill_alpha, line_alpha=0), 'Path': dict(line_color=line_color, line_alpha=line_alpha) }
    o_m = {'Polygons' : dict( color=fill_color, alpha=fill_alpha),               'Path': dict(color=line_color,      alpha=line_alpha) }
    return (hv.Polygons([d], label=label)*hv.Path([l[0], l[1]])).opts( o_b, backend='bokeh' ) #.opts( o_m, backend='matplotlib ')
#    return hv.Polygons([d], label=label).opts( color=fill_color, alpha=fill_alpha, line_alpha=0 )*\
#           hv.Path([l[0], l[1]]).opts( line_color=line_color, line_alpha=line_alpha)

# ----------------------------------------------------------------------------
def ngon(x=0,y=0, spec=(1,1), orientation=0., arc=(0,2*np.pi), npoints=40,\
         line_color='k', line_alpha=1., color='k', alpha=0., label=''):
    ''' an ngon ''
    e = ngon_data(x,y,specs=[spec], arc=arc,orientation=orientation,npoints=npoints)

    return hv.Polygons(e, label=label).opts( line_color=line_color,line_alpha=line_alpha, color=color, alpha=alpha)
