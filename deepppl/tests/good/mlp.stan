
networks {
    MLP mlp;
}

data {
    int batch_size;
    int <lower=0, upper=1> imgs[28,28,batch_size];
    int <lower=0, upper=10>  labels[batch_size];
}

parameters {
    real mlp.l1.weight[*];
    real mlp.l1.bias[*];
    real mlp.l2.weight[*];
    real mlp.l2.bias[*];
}

model {
    real logits[batch_size];
    mlp.l1.weight ~  normal(zeros(mlp.l1.weight$shape), ones(mlp.l1.weight$shape));
    mlp.l1.bias ~ normal(zeros(mlp.l1.bias$shape), ones(mlp.l1.bias$shape));
    mlp.l2.weight ~ normal(zeros(mlp.l2.weight$shape), ones(mlp.l2.weight$shape));
    mlp.l2.bias ~  normal(zeros(mlp.l2.bias$shape), ones(mlp.l2.bias$shape));

    logits = mlp(imgs);
    labels ~ categorical_logits(logits);
}

guide parameters {
    real l1wloc[*];
    real l1wscale[*];
    real l1bloc[*];
    real l1bscale[*];
    real l2wloc[*];
    real l2wscale[*];
    real l2bloc[*];
    real l2bscale[*];
}

guide {
    l1wloc = randn();
    l1wscale = randn();
    mlp.l1.weight ~  normal(l1wloc, softplus(l1wscale));
    l1bloc = randn();
    l1bscale = randn();
    mlp.l1.bias ~ normal(l1bloc, softplus(l1bscale));
    l2wloc = randn();
    l2wscale = randn();
    mlp.l2.weight ~ normal(l2wloc, softplus(l2wscale));
    l2bloc = randn();
    l2bscale = randn();
    mlp.l2.bias ~ normal(l2bloc, softplus(l2bscale));
}
