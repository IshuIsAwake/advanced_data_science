import torch


def diff_in_means(y , z , level=0.95):
    """y : outcome , z : 1 = assigned , 0 = not assigned (both 1-d)
    d = ybar_1 - ybar_0                 when z is randomised this is the ITT , the effect of the offer"""
    y , z = torch.as_tensor(y , dtype=torch.float64) , torch.as_tensor(z , dtype=torch.float64)
    y1 , y0 = y[z == 1] , y[z == 0]
    d = y1.mean() - y0.mean()

    # var(ybar) = s^2 / n  for a mean of n independent draws
    # the two groups are independent , so the variances add :  var(d) = s1^2 / n1 + s0^2 / n0
    # each group keeps its own s^2 (welch) , nothing assumes the offer leaves the spread unchanged
    se = torch.sqrt(y1.var() / len(y1) + y0.var() / len(y0))

    # CLT : d is roughly normal around the true effect , so  P(|d - effect| < q se) = level
    # q = Phi^-1(1 - (1 - level) / 2) , 1.96 for 95%
    q = torch.special.ndtri(torch.tensor((1 + level) / 2 , dtype=torch.float64))

    # p value : chance of a |d| this big when the true effect is 0
    # p = 2 (1 - Phi(|d| / se)) = 2 Phi(-|d| / se)       Phi(x) = (1 + erf(x / sqrt 2)) / 2
    # the second form by symmetry , 1 - Phi rounds to 0 once p is below ~1e-16
    t = d / se
    p = 2 * torch.special.ndtr(-t.abs())

    return {'treated mean' : y1.mean().item() , 'control mean' : y0.mean().item() , 'diff' : d.item() ,
            'se' : se.item() , 'ci low' : (d - q * se).item() , 'ci high' : (d + q * se).item() , 'p' : p.item()}


def cramers_v(a , b):
    """a , b : two category columns as integer codes 0 , 1 , 2 ... (both 1-d)
    how strongly they go together , 0 = unrelated , 1 = one fixes the other , the labels don't matter"""
    a , b = torch.as_tensor(a , dtype=torch.int64) , torch.as_tensor(b , dtype=torch.int64)
    n , r , c = len(a) , a.max().item() + 1 , b.max().item() + 1

    # n_ij : rows with a = i and b = j , only the pairs that occur
    pairs , n_ij = torch.unique(a * c + b , return_counts=True)
    n_i , n_j = torch.bincount(a).double() , torch.bincount(b).double()

    # unrelated columns would give  e_ij = n_i n_j / n
    # chi2 = sum (n_ij - e_ij)^2 / e_ij = sum n_ij^2 / e_ij - 2 sum n_ij + sum e_ij = n ( sum n_ij^2 / (n_i n_j) - 1 )
    # so a pair that never occurs drops out , no need for the full r x c table
    chi2 = n * ((n_ij.double() ** 2 / (n_i[pairs // c] * n_j[pairs % c])).sum() - 1)

    # chi2 grows with n and with the size of the table , its largest value is n (min(r , c) - 1)
    return torch.sqrt(chi2 / (n * (min(r , c) - 1))).item()
