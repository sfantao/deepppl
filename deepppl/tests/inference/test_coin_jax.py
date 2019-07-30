import torch
from torch import nn
from torch.nn import functional as F
from torch import tensor
import pyro
import numpy as np
from numpyro.hmc_util import initialize_model
from numpyro.mcmc import mcmc
from numpyro import distributions as dist
import jax.numpy as jnp
import jax.random as random
import logging
import time
import pystan
import deepppl
import os
import pandas as pd


stan_model_file = 'deepppl/tests/good/coin.stan'
global_num_iterations=10000
global_num_chains=1
global_warmup_steps = 1000

x = [0, 0, 0, 0, 0, 0, 1, 0, 0, 1]

def test_coin():
    model = deepppl.NumPyroDPPLModel(model_file=stan_model_file)
    #model._model = model2

    posterior = model.posterior(global_num_iterations, global_warmup_steps)

    t1 = time.time()
    states = posterior(x)
    samples_fstan = states['theta'][global_warmup_steps:]

    t2 = time.time()
    
    pystan_output, pystan_time, pystan_compilation_time = compare_with_stan_output()

    pystan_output = pystan_output.squeeze()
    assert samples_fstan.shape == pystan_output.shape
    from scipy.stats import entropy, ks_2samp
    hist1 = np.histogram(samples_fstan, bins = 10)
    hist2 = np.histogram(pystan_output, bins = hist1[1])
    kl = entropy(hist1[0]+1, hist2[0]+1)
    skl = kl + entropy(hist2[0]+1, hist1[0]+1)
    ks = ks_2samp(samples_fstan, pystan_output)
    print('skl for theta is:{:.6}'.format(skl))
    print(f'ks for theta is: {ks}')

    print("Time taken: deepstan:{:.2f}, pystan_compilation:{:.2f}, pystan:{:.2f}".format(t2-t1, pystan_compilation_time, pystan_time))

def compare_with_stan_output():
    stan_code = open(stan_model_file).read()
    data = {
        'x': x
    }

    # Compile and fit
    t1 = time.time()

    sm1 = pystan.StanModel(model_code=str(stan_code))
    print("Compilation done")
    t2 = time.time()
    pystan_compilation_time = t2-t1

    t1 = time.time()
    fit_stan = sm1.sampling(data = data, iter=global_num_iterations, chains=global_num_chains, 
                            warmup = global_warmup_steps)

    t2 = time.time()
    theta = fit_stan.extract(permuted=True)['theta']

    theta = np.reshape(theta, (theta.shape[0], 1))

    t2 = time.time()
    return theta, t2-t1, pystan_compilation_time


if __name__ == "__main__":
    test_coin()
