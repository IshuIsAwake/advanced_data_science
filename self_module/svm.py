import torch

from .base import Model , accuracy


class SVM(Model):
    """labels arrive as {0 , 1} like every other model , train maps them to s in {-1 , +1}
    z = X W                             signed distance to the hyperplane , up to ||w||
    m = s z                             functional margin , right side and confident when m >= 1"""

    def __init__(self , lr=0.01 , epochs=1000 , C=0.01):
        super().__init__(lr , epochs)
        self.C = C

    # {0 , 1} -> {-1 , +1} once , before the loop : the margin has to go negative
    # on the wrong side , which a 0 label cannot do
    def train(self , X , y , X_val=None , y_val=None , log_every=None):
        s_val = None if y_val is None else 2 * y_val - 1
        return super().train(X , 2 * y - 1 , X_val , s_val , log_every)

    def forward(self , X):
        return X @ self.W

    # J = mean( max(0 , 1 - m) ) + C/2 ||w||^2      w = W without the bias row
    def loss(self , s , z):
        hinge = torch.clamp(1 - s * z , min=0)
        return hinge.mean() + self.C / 2 * (self.W[:-1] ** 2).sum()

    # d/dm max(0 , 1 - m) = -1 if m < 1 else 0      subgradient , at m = 1 we take 0
    # dm/dW = s X   ->   dJ/dW = -X.T (s [m < 1]) / n + C w
    # only the points with m < 1 pull on W , the rest are already outside the margin
    def grad(self , X , s , z):
        active = ((s * z) < 1).float()
        reg = self.C * self.W
        reg[-1] = 0                     # the bias only shifts the hyperplane , never penalised
        return -(X.T @ (s * active)) / X.shape[0] + reg

    # hinge is piecewise linear so H = 0 almost everywhere , no 2 / lam_max bound to give

    def predict(self , X):
        # sign(z) in {-1 , +1} mapped back to {0 , 1}
        return (self.forward(X) >= 0).float()

    def score(self , X , y):
        return accuracy(y , self.predict(X))


class WeightedSVM(SVM):
    """same SVM , but every point's hinge is scaled by a weight for its class
    c_i = n / (2 n_class)    ->    each class carries half the loss (sklearn's class_weight='balanced')
    with 12% yes the plain hinge is happiest parking everyone at z = -1 :
    every no sits on the margin for free and each yes costs 2 , the weights make a yes count ~7x more"""

    # weights come from the training labels , then the usual {0 , 1} -> {-1 , +1} in SVM.train
    def train(self , X , y , X_val=None , y_val=None , log_every=None):
        n , n_pos = len(y) , y.sum()
        self.c_pos = (n / (2 * n_pos)).item()
        self.c_neg = (n / (2 * (n - n_pos))).item()
        return super().train(X , y , X_val , y_val , log_every)

    def c(self , s):
        return torch.where(s > 0 , self.c_pos , self.c_neg)

    # J = mean( c max(0 , 1 - m) ) + C/2 ||w||^2
    def loss(self , s , z):
        hinge = torch.clamp(1 - s * z , min=0)
        return (self.c(s) * hinge).mean() + self.C / 2 * (self.W[:-1] ** 2).sum()

    # same subgradient as SVM , each active point now pulls with strength c
    # dJ/dW = -X.T (c s [m < 1]) / n + C w
    def grad(self , X , s , z):
        active = ((s * z) < 1).float()
        reg = self.C * self.W
        reg[-1] = 0
        return -(X.T @ (self.c(s) * s * active)) / X.shape[0] + reg
