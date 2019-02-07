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


networks {
    RNN rnn;
}

data {
    int n_characters;
    int input[n_characters];
    int category[n_characters];
}

parameters {
    real[] rnn.encoder.weight;
}

model {
    int logits[n_characters];
    rnn.encoder.weight ~  normal(zeros(rnn.encoder.weight$shape), ones(rnn.encoder.weight$shape));
    logits = rnn(input);
    category ~ categorical_logits(logits);
}

guide parameters {
     real ewl[rnn.encoder.weight$shape];
     real ews[rnn.encoder.weight$shape];
}

guide {
     ewl = randn(ewl$shape);
     ews = randn(ews$shape) -10.0;
     rnn.encoder.weight ~  normal(ewl, exp(ews));
}
