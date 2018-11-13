import torch
from torch import tensor, randn
import pyro
import torch.distributions.constraints as constraints
import pyro.distributions as dist


def transformed_data(x):
    ___shape = {}
    ___shape['y'] = 10
    y = zeros(___shape['y'])
    for i in range(1, 10 + 1):
        y[i - 1] = 1 - x[i - 1]
    return {'y': y}


def model(x, transformed_data):
    y = transformed_data['y']
    ___shape = {}
    ___shape['x'] = 10
    ___shape['theta'] = ()
    theta = pyro.sample('theta', dist.Uniform(0.0, 1.0))
    pyro.sample('theta' + '1', dist.Uniform(0, 1), obs=theta)
    for i in range(1, 10 + 1):
        pyro.sample('y' + '{}'.format(i - 1) + '2', dist.Bernoulli(theta),
            obs=y[i - 1])