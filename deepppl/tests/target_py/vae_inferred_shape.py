import torch
from torch import tensor, rand
import pyro
import torch.distributions.constraints as constraints
import pyro.distributions as dist


def guide_(x=None):
    pyro.module('encoder', encoder)
    encoded = encoder(x)
    mu_z = encoded[1 - 1]
    sigma_z = encoded[2 - 1]
    z = sample('z', dist.Normal(mu_z, sigma_z))


def model(x=None):
    pyro.module('decoder', decoder)
    z = sample('z', ImproperUniform(shape=encoder(x)[1].size()))
    mu = zeros((28, 28))
    sample('z' + '__1', dist.Normal(zeros(encoder(x)[1].size()), 1), obs=z
        )
    mu = decoder(z)
    sample('x' + '__2', dist.Bernoulli(mu), obs=x)
