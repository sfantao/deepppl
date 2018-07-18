/*
 * Copyright 2018 IBM Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


data {
    int n_characters;
    int input[n_characters];
    int target[n_characters];
}

network {
    RNN rnn with parameters:
         encoder.weight;
        // gru.weight_ih_l0;
        // gru.weight_hh_l0;
        // gru.bias_ih_l0;
        // gru.bias_hh_l0;
        // decoder.weight;
        // decoder.bias;
}

prior
{
     rnn.encoder.weight ~  Normal(zeros(rnn.encoder.weight$shape), ones(rnn.encoder.weight$shape));
    // rnn.gru.weight_ih_l0 ~ Normal(zeros(rnn.gru.weight_ih_l0$shape), 0.01*ones(rnn.gru.weight_ih_l0$shape));
    // rnn.gru.weight_hh_l0 ~ Normal(zeros(rnn.gru.weight_hh_l0$shape), 0.01*ones(rnn.gru.weight_hh_l0$shape));
    // rnn.gru.bias_ih_l0 ~  Normal(zeros(rnn.gru.bias_ih_l0$shape), 0.01*ones(rnn.gru.bias_ih_l0$shape));
    // rnn.gru.bias_hh_l0 ~  Normal(zeros(rnn.gru.bias_hh_l0$shape), 0.01*ones(rnn.gru.bias_hh_l0$shape));
    // rnn.decoder.weight ~  Normal(zeros(rnn.decoder.weight$shape), 0.01*ones(rnn.decoder.weight$shape));
    // rnn.decoder.bias ~  Normal(zeros(rnn.decoder.bias$shape), 0.01*ones(rnn.decoder.bias$shape));
}

guide_parameters
{
     real ewl[rnn.encoder.weight$shape];
     real ews[rnn.encoder.weight$shape];
    // real gw1l[rnn.gru.weight_ih_l0$shape];
    // real gw1s[rnn.gru.weight_ih_l0$shape];
    // real gw2l[rnn.gru.weight_hh_l0$shape];
    // real gw2s[rnn.gru.weight_hh_l0$shape];
    // real gb1l[rnn.gru.bias_ih_l0$shape];
    // real gb1s[rnn.gru.bias_ih_l0$shape];
    // real gb2l[rnn.gru.bias_hh_l0$shape];
    // real gb2s[rnn.gru.bias_hh_l0$shape];
    // real dwl[rnn.decoder.weight$shape];
    // real dws[rnn.decoder.weight$shape];
    // real dbl[rnn.decoder.bias$shape];
    // real dbs[rnn.decoder.bias$shape];

}

guide {
     ewl = randn(ewl$shape);
     ews = randn(ews$shape) -10.0;
     rnn.encoder.weight ~  Normal(ewl, exp(ews));
    // gw1l = .001*randn(gw1l$shape);
    // gw1s = randn(gw1s$shape) -10.0;
    // rnn.gru.weight_ih_l0 ~ Normal(gw1l, exp(gw1s));
    // gw2l = .001*randn(gw2l$shape);
    // gw2s = randn(gw2s$shape) -10.0;
    // rnn.gru.weight_hh_l0 ~ Normal(gw2l, exp(gw2s));
    // gb1l = .001*randn(gb1l$shape);
    // gb1s = randn(gb1s$shape) -10.0;
    // rnn.gru.bias_ih_l0 ~  Normal(gb1l, exp(gb1s));
    // gb2l = .001*randn(gb2l$shape);
    // gb2s = randn(gb2s$shape) -10.0;
    // rnn.gru.bias_hh_l0 ~  Normal(gb2l, exp(gb2s));
    // dwl = .001*randn(dwl$shape);
    // dws = randn(dws$shape) -10.0;
    // rnn.decoder.weight ~  Normal(dwl, exp(dws));
    // dbl = .001*randn(dbl$shape);
    // dbs = randn(dbs$shape) -10.0;
    // rnn.decoder.bias ~  Normal(dbl, exp(dbs));
}

model {
    int logits[n_characters];
    logits = rnn(input);
    target ~ CategoricalLogits(logits);
}

