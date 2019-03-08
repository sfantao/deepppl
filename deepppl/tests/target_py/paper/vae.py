import torch
from torch import tensor, rand
import pyro
import torch.distributions.constraints as constraints
import pyro.distributions as dist


def guide_(nz=None, x=None):
    pyro.module('encoder', encoder)
    encoded = encoder(x)
    mu_z = encoded[1 - 1]
    sigma_z = encoded[2 - 1]
    z = pyro.sample('z', dist.Normal(mu_z, sigma_z))


def model(nz=None, x=None):
    pyro.module('decoder', decoder)
    z = pyro.sample('z', ImproperUniform(shape=nz))
    mu = zeros((28, 28))
    pyro.sample('z' + '__1', dist.Normal(zeros(nz), 1), obs=z)
    mu = decoder(z)
    pyro.sample('x' + '__2', dist.Bernoulli(mu), obs=x)
