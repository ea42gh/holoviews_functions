import numpy as np
import holoviews as hv

def vector_field_with_background(x,y, slopes, length=1, subsample=3):
    """
    Given vectors x, y and an array of slopes(x,y)
    return a grayscale image of the slopes y' together with
           a vector field representation of the slopes
    """

    # compute the data
    theta = np.arctan2( slopes, 1)       # angle of the slope y' at x,y

    # Obtain the vector field (subsample the grid)
    decim_x       = x[::subsample]
    decim_y       = y[::subsample]
    decim_theta   = theta[::subsample,::subsample]
    
    if isinstance( length, (int,float)):
        decim_len  = np.full_like( decim_theta, length)
    else:
        decim_len  = length[::subsample, ::subsample]
    vf_opts       = dict(size_index=3, alpha=0.3, muted_alpha=0.05)
    vec_field     = hv.VectorField((decim_x,decim_y,decim_theta,decim_len) ).opts(**vf_opts)

    # Normalize the given array so that it can be used with the RGB element's alpha channel   
    def norm(arr):
        arr = (arr-arr.min())
        return arr/arr.max()

    normXY    = norm(np.copy(slopes))
    img_field = hv.RGB( (x, y, normXY, normXY, normXY, np.full_like(theta, 0.1)),
                        vdims=['R','G','B','A'] )\
                .opts(shared_axes=False)

    return img_field*vec_field

