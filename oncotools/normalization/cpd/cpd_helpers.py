import numpy as np

def cpd_p(x, y, sigma2, w, m, n, d):
    '''
    E-step: Compute P in the EM optimization,
    which store the probability of point n in x belongs the cluster m in y.

    Positional arguemnts:
        :x: (ndarray) The static shape that y will be registered to.
            Expected array shape is [n_points_x, n_dims]
        :y: (ndarray) The moving shape. Expected array shape is [n_points_y, n_dims].
            Note that n_dims should be equal for x and y, but n_points does not need to match.
        :sigma2: (float)    Gaussian distribution parameter. Calculated in M-step every loop.
        :w: (float) Weight for the outlier suppression. Value is expected to be in range [0, 1].
        :m: (int) x points' length
        :n: (int) y points' length
        :d: (int) Dataset's dimensions. Note that d should be equal for x and y.

    Returns:
        :p1:    (ndarray) The result of dot product of the matrix p and a column vector of all ones
                Expected array shape is [n_points_y,1].
        :pt1:   (nadarray) The result of dot product of
                the inverse matrix of p and a column vector of all ones.
                Expected array shape is [n_points_x, 1].
        :px:    (nadarray) The result of dot product of the matrix p and matrix of dataset x.
    '''
    # Use numpy broadcasting to build a new matrix.
    g = x[:, np.newaxis, :]-y
    g = g*g
    g = np.sum(g, 2)
    g = np.exp(-1.0/(2*sigma2)*g)
    # g1 is the top part of the expression calculating p
    # temp2 is the bottom part of expresion calculating p
    g1 = np.sum(g, 1)
    temp2 = (g1 + (2*np.pi*sigma2)**(d/2)*w/(1-w)*(float(m)/n)).reshape([n, 1])
    p = (g/temp2).T
    p1 = (np.sum(p, 1)).reshape([m, 1])
    px = np.dot(p, x)
    pt1 = (np.sum(np.transpose(p), 1)).reshape([n, 1])
    return p1, pt1, px


def cpd_r(n):
    '''
    Calculating a random orthogonal 2d or 3d rotation matrix which satisfies det(r)=1.

    Positional arguments:
        :n: (int) Rotation matrix's dimension

    Returns:
        :r: (ndarray) Rotation matrix
    '''
    if n == 3:
        r1 = np.eye(3)
        r2 = np.eye(3)
        r3 = np.eye(3)
        r1[0: 2:, 0: 2] = rot(np.random.rand(1)[0])
        r2[:: 2, :: 2] = rot(np.random.rand(1)[0])
        r3[1:, 1:] = rot(np.random.rand(1)[0])
        r = np.dot(np.dot(r1, r2), r3)
    elif n == 2:
        r = rot(np.random.rand(1)[0])
    return r

def rot(f):
    '''
    Generating a 2d random orthogonal rotation matrix.

    Positional arguments:
        :f: (float) Random float number. Value is expected to be in range [0.0, 1.0].

    Returns:
        :r: (ndarray) 2d random orthogonal rotation matrix.
    '''
    r = np.array([[np.cos(f), -np.sin(f)], [np.sin(f), np.cos(f)]])
    return r

def cpd_b(n):
    '''
    Generating a random 2d or 3d rotaiton matrix.
    Note: the rotation matrix don't need to satisfy det(b)=1.

    Parameters:
        :n: (int) Rotation matrix's dimension.

    Returns:
        :b: (ndarray) Random rotation matrix.
    '''
    b = cpd_r(n) + abs(0.1*np.random.randn(n, n))
    return b
