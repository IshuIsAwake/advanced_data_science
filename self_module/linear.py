import torch

from .base import Model


class LinearRegression(Model):
    """z = X W          r = y - z          residual
    J = ||r||^2 / 2n    squared euclidean norm , the 1/2 only to keep dJ/dW clean"""

    def forward(self , X):
        return X @ self.W

    def loss(self , y , z):
        r = y - z
        return (r * r).sum() / (2 * y.shape[0])

    # J = (y - XW).T (y - XW) / 2n
    # dJ/dW = -2 X.T (y - XW) / 2n = -X.T r / n
    def grad(self , X , y , z):
        return -(X.T @ (y - z)) / X.shape[0]

    # H = d2J/dW2 = X.T X / n , constant -> J is a convex quadratic
    # W <- W - a (H W - X.T y / n)  so the error obeys  e <- (I - a H) e
    # in the eigenbasis of H that is  e_i <- (1 - a lam_i) e_i  , decaying only while
    # |1 - a lam_i| < 1 for every lam_i  ->  0 < a < 2 / lam_max
    def max_lr(self , X):
        lam = torch.linalg.eigvalsh(X.T @ X / X.shape[0]).max()
        return (2 / lam).item()

    # R^2 = 1 - ||y - z||^2 / ||y - ybar||^2
    def score(self , X , y):
        r = y - self.forward(X)
        return (1 - (r * r).sum() / ((y - y.mean()) ** 2).sum()).item()
