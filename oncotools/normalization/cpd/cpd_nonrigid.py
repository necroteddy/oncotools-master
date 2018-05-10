import numpy as np
from numpy.matlib import repmat
import scipy.sparse
from .cpd_helpers import cpd_p

def plateau(vals, thresh, length):
    '''
    Identify if there is a plateau of length, length, at the end of a list, vals
    '''
    if len(vals) < length:
        return False
    else:
        sublist = vals[-length:]
        g = np.gradient(sublist)
        check = [abs(gi) < thresh for gi in g]
        return all(check)

def register_nonrigid(x, y, w,
                      lamb=3.0, beta=2.0, max_it=150, plateau_thresh=1.0e-5, plateau_length=20):
    '''
    Registers Y to X using the Coherent Point Drift algorithm.
    For the transformed points, t = y + g*wc.

    Positional arguments:
        :x:     (ndarray) The static shape that Y will be registered to.
                Expected array shape is [n_points_x, n_dims]
        :y:     (ndarray) The moving shape. Expected array shape is [n_points_y, n_dims].
                Note that n_dims should be equal for X and Y, but n_points does not need to match.
        :w:     (float) Weight for the outlier suppression.
                Value is expected to be in range [0.0, 1.0].

    Keyword arguments:
        :lamb:      (float) lamb represents the trade-off between
                    the goodness of maximum likelihood fit and regularization.(default = 3.0)
        :beta:      (float) beta defines the model of the smoothness regularizer
                    or the width of smoothing Gaussian filter (default = 2.0)
        :max_it:    (int) Maximum number of iterations. (default = 150)
        :tol:       (float) tolerance

    Returns:
        :t:         (ndarray) The transformed version of y. Output shape is [n_points_y, n_dims].
        :g:         (ndarray) G matrix
        :wc:        (ndarray) weights
        :errors:    (list) error per iteration
    '''
    # Construct G
    g = y[:, np.newaxis, :] - y
    g = g*g
    g = np.sum(g, 2)
    g = np.exp(-1.0/(2*beta*beta)*g)
    [n, d] = x.shape
    [m, d] = y.shape
    t = y
    # initialize sigma^2
    sigma2 = (m*np.trace(np.dot(np.transpose(x), x)) + n*np.trace(np.dot(np.transpose(y), y)) -
              2*np.dot(sum(x), np.transpose(sum(y)))) / (m*n*d)
    n_iter = 0
    errors = []
    # Keep iterating until we reach max_iterations, are under threshold, or plateau
    while (n_iter < max_it) and (sigma2 > 1.0e-5) and (
            not plateau(errors, plateau_thresh, plateau_length)):
        [p1, pt1, px] = cpd_p(x, t, sigma2, w, m, n, d)
        # Precompute diag(p)
        dp = scipy.sparse.spdiags(p1.T, 0, m, m)
        # wc is a matrix of coefficients
        wc = np.dot(np.linalg.inv(dp*g + lamb*sigma2*np.eye(m)), (px - dp*y))
        t = y + np.dot(g, wc)
        Np = np.sum(p1)
        # Compute error
        sigma2 = np.abs(
            (np.sum(x*x*repmat(pt1, 1, d)) + np.sum(t*t*repmat(p1, 1, d)) -
             2 * np.trace(np.dot(px.T, t))) / (Np*d))
        # Update iteration count and store errors
        n_iter += 1
        errors.append(sigma2)
    return t, g, wc, errors
