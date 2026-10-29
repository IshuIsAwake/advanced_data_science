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
