import numpy as np


from benchopt import BaseSolver


class Solver(BaseSolver):
    '''
    Alternating Proximal gradient
    '''
    name = "apg"

    # any parameter defined here is accessible as a class attribute
    parameters = {
        'n_inner_iter': [1, 5]
    }

    stopping_strategy = "callback"

    def set_objective(self, X, rank, fac_init):
        # The arguments of this function are the results of the
        # `to_dict` method of the objective.
        # They are customizable.
        self.X = X
        self.rank = rank
        self.fac_init = fac_init  # None if not initialized beforehand

    def run(self, callback):
        m, n = self.X.shape
        rank = self.rank
        n_inner_iter = self.n_inner_iter

        if not self.fac_init:
            # Random init if init is not provided
            W, H = [np.random.rand(m, rank), np.random.rand(rank, n)]
        else:
            W, H = [np.copy(self.fac_init[i]) for i in range(2)]

        while callback((W, H)):
            HHt = np.dot(H, H.T)
            XHt = np.dot(self.X, H.T)
            Lw = np.linalg.norm(HHt)  # upper bound of Lw
            # W update
            for inner in range(n_inner_iter):
                W = np.maximum(
                    W - (np.dot(W, HHt) - XHt) / Lw, 0)

            # H update
            WtW = np.dot(W.T, W)
            WtX = np.dot(W.T, self.X)
            Lh = np.linalg.norm(WtW)  # upper bound for Lh
            # H update
            for inner in range(n_inner_iter):
                H = np.maximum(
                    H - (np.dot(WtW, H) - WtX) / Lh, 0)

        self.fac = (W, H)

    def get_result(self):
        # The outputs of this function are the arguments of the
        # `compute` method of the objective.
        # They are customizable.
        return self.fac
