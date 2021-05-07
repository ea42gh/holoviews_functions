import holoviews as hv
from holoviews.operation.datashader import aggregate, shade, datashade, dynspread
import numpy as np
import pandas as pd

# ===========================================================================
import unicodedata as ucd
class DimName(object):
    '''functions to facilitate accessing unicode letters'''
    # https://en.wikipedia.org/wiki/Unicode_subscripts_and_superscripts
    @staticmethod
    def lcg(s, n=None):
        '''lower case greek letters with subscript lcg('alpha',1)'''
        l = ucd.lookup('greek small letter ' + s) 
        if n is None: return l
        else:         return '{0}{1}'.format(l,chr(0x2080 + n))
    @staticmethod
    def ucg(s, n=None):
        '''upper case greek letters with subscript ucg('sigma',1)'''
        l = ucd.lookup('greek capital letter ' + s) 
        if n is None: return l
        else:         return '{0}{1}'.format(l,chr(0x2080 + n))
    @staticmethod
    def subscript(s,n): return '{0}{1}'.format(s,chr(0x2080 + n))

# ===========================================================================
def forest_plot( df = dict( mean    = np.array( [2.0, 4.0, 6.0,   8.0 ]),
                            sd      = np.array( [0.5, 0.5, 0.5,   0.5 ]),
                            low     = np.array( [0.0, 2.0, 4.0,   6.0 ]),
                            hgh     = np.array( [3.0, 5.0, 7.0,   9.0 ]) ),
                 support =.95,
                 index   = [DimName.lcg('alpha'), DimName.lcg('beta', 0),DimName.lcg('beta', 1),DimName.lcg('sigma')],
                 offset  = 0., group = None):
    rng   = (np.floor(df['low'].min()), np.ceil(df['hgh'].max()) )  # improve: this does not work if all data << 1
    d_rng = (rng[1]-rng[0])*.01
    rng   = (rng[0]-d_rng, rng[1]+d_rng)

    e_u = df['hgh' ] - df[ 'mean']
    e_l = df['mean'] - df[ 'low' ]
    
    ticks = [ (i,s) for i,s in enumerate(index) ]
    vals  = np.arange(len(df['mean']))+offset

    specs = {
        'ErrorBars': dict(invert_axes=True, shared_axes=False, show_grid=True,  width=600, height=200,
                          color='slateblue',axiswise=True),
        'Points':    dict(invert_axes=True, tools=['hover'], toolbar='above', shared_axes=False,
                          color='slateblue', marker='+', size=10, line_width=3,
                          axiswise=True),
        'HLine':     dict(color='coral', alpha=0.4, line_width=1.2)
    }
    if group is not None: g={'group':group}
    else:                 g={}

    # Use invisible (i.e., alpha=0) markers to enable hover information
    h = \
        hv.ErrorBars( [i for i in zip(vals,  df['mean' ], e_l, e_u)],
                      kdims=['parameter'], vdims=['value','e_l','e_u'], **g)\
          .opts(line_width=1, yticks=ticks ) \
      * hv.ErrorBars( (vals,  df['mean' ], df['sd' ] ),
                      kdims=['parameter'], vdims=['value','sd' ], **g)\
          .opts(line_width=5, lower_head=None, upper_head=None) \
      * hv.Points( (vals,  df['mean']), ['parameter', 'value'], **g ) \
      * hv.Points( (vals,  df['low' ]), ['parameter', 'value'], **g ).opts(alpha=0) \
      * hv.Points( (vals,  df['hgh' ]), ['parameter', 'value'], **g ).opts(alpha=0) \
      * hv.HLine(0, **g)

    return h.opts(specs).redim.range(parameter=(-.5,len(df['mean'])-.5),value=rng).relabel('%d%% Credible Intervals'%int(100.*support))
# ===========================================================================
def stem(data, curve=True, marker=True):
    '''stem plot:   data=(x,y,e)'''
    x,y,e=data
    vlines = [ np.array( [[x[i], y[i]], [x[i], e[i]]]) for i in range(len(x)) ]

    hs = hv.Path( vlines ).opts( show_legend=True, muted_alpha=0.)

    if marker: hs = hs * hv.Scatter((x,e)).opts(size=4)
    if curve:  hs = hs * hv.Curve((x,y)).opts(line_width=0.8)
    return hs
# ===========================================================================
def jittered_points(data, jitter=0.05, shade=True, shader_opts=dict(cmap="blues")):
    '''given (x_vals[N], y_meas[NumExperiments, N], apply a jitter to the x values
       and possible datashade the resulting scatter plot'''
    
    from holoviews.operation.datashader import datashade
    x_vals, y_meas    = data
    NumExperiments,N  = y_meas.shape

    x_jitter  = np.random.uniform(low=-jitter, high=jitter, size=(N*NumExperiments))
    h_scatter = hv.Scatter( ( np.repeat(x_vals, NumExperiments)+x_jitter, y_meas.T.flatten() ))
    if shade: h_scatter = datashade(h_scatter, **shader_opts)
    return h_scatter
# ---------------------------------------------------------------------------
def regression_lines_spread(data, meas_stats, estim_stats):
    '''given (x_vals[N], y_vals[NumExperiments, N], return hv.Spread overlaid with jittered values'''

    x_vals, y_meas           = data
    y_meas_ave,  y_meas_std  = meas_stats
    y_estim_ave, y_estim_std = estim_stats

    NumExperiments,N  = y_meas.shape

    h_spread_pts  = hv.Spread((x_vals, y_estim_ave, y_estim_std))*\
                    hv.Spread((x_vals, y_meas_ave,  y_meas_std))*\
                    hv.Curve( (x_vals, y_estim_ave))
    return h_spread_pts

