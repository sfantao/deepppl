# /*
#  * Copyright 2018 IBM Corporation
#  *
#  * Licensed under the Apache License, Version 2.0 (the "License");
#  * you may not use this file except in compliance with the License.
#  * You may obtain a copy of the License at
#  *
#  * http://www.apache.org/licenses/LICENSE-2.0
#  *
#  * Unless required by applicable law or agreed to in writing, software
#  * distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.
# */

from deepppl import dpplc
from deepppl.translation.exceptions import *
from contextlib import contextmanager

import ast
import pytest


def code_to_normalized(code):
    return ast.dump(ast.parse(code), annotate_fields=False)


from contextlib import contextmanager


@contextmanager
def not_raises(exception):
    try:
        yield
    except exception:
        raise pytest.fail("DID RAISE {0}".format(exception))

# Note about setting verbose=False

# if we use verbose mode, then the code generates annotated types.
# it sets simple=1 in the AnnAssign constructor
# to avoid parenthesis for simple identifiers
# This is good, as it makes the generated python code nicer.
# unfortunately, when parsing back in the code, python sometimes
# sets simple=0.  When we then compare, it fails.
# The simplest solution, taken here, is just not to generate type annotations
# for this and similar examples

def normalize_and_compare(src_file, target_file, verbose=True):
    with open(target_file) as f:
        target_code = f.read()
    target = code_to_normalized(target_code)
    config = dpplc.Config()
    
    compiled = dpplc.stan2astpyFile(src_file, config, verbose)
    assert code_to_normalized(compiled) == target


def test_coin():
    filename = r'deepppl/tests/good/coin.stan'
    target_file = r'deepppl/tests/target_py/coin.py'
    normalize_and_compare(filename, target_file)


def test_gaussian():
    filename = r'deepppl/tests/good/gaussian.stan'
    target_file = r'deepppl/tests/target_py/gaussian.py'
    normalize_and_compare(filename, target_file)


def test_gaussian_log_density():
    filename = r'deepppl/tests/good/gaussian_log_density.stan'
    target_file = r'deepppl/tests/target_py/gaussian_log_density.py'
    normalize_and_compare(filename, target_file)


def test_double_gaussian():
    filename = r'deepppl/tests/good/double_gaussian.stan'
    target_file = r'deepppl/tests/target_py/double_gaussian.py'
    normalize_and_compare(filename, target_file)


def test_log_normal():
    filename = r'deepppl/tests/good/log_normal.stan'
    target_file = r'deepppl/tests/target_py/log_normal.py'
    normalize_and_compare(filename, target_file)


def test_operators():
    filename = r'deepppl/tests/good/operators.stan'
    target_file = r'deepppl/tests/target_py/operators.py'
    normalize_and_compare(filename, target_file)


def test_operators_expr():
    filename = r'deepppl/tests/good/operators-expr.stan'
    target_file = r'deepppl/tests/target_py/operators-expr.py'
    normalize_and_compare(filename, target_file)


def test_coin_vectorized():
    filename = r'deepppl/tests/good/coin_vectorized.stan'
    target_file = r'deepppl/tests/target_py/coin_vectorized.py'
    normalize_and_compare(filename, target_file)


@pytest.mark.xfail(strict=False, reason="Type inference does not currently support promoting an integer to a float")
def test_coin_transformed_data():
    filename = r'deepppl/tests/good/coin_transformed_data.stan'
    target_file = r'deepppl/tests/target_py/coin_transformed_data.py'
    normalize_and_compare(filename, target_file)


@pytest.mark.xfail(strict=True)
def test_coin_reverted_lines():
    """Inside a `block`, stan semantics do not requires lines to be
    ordered.
    """
    filename = r'deepppl/tests/good/coin_reverted.stan'
    target_file = r'deepppl/tests/target_py/coin_vectorized.py'
    normalize_and_compare(filename, target_file)


def test_coin_guide():
    filename = r'deepppl/tests/good/coin_guide.stan'
    target_file = r'deepppl/tests/target_py/coin_guide.py'
    normalize_and_compare(filename, target_file)


def test_coin_guide_init():
    filename = r'deepppl/tests/good/coin_guide_init.stan'
    target_file = r'deepppl/tests/target_py/coin_guide_init.py'
    normalize_and_compare(filename, target_file)


def test_simple_init():
    filename = r'deepppl/tests/good/simple_init.stan'
    target_file = r'deepppl/tests/target_py/simple_init.py'
    normalize_and_compare(filename, target_file)


@pytest.mark.xfail(strict=False, reason="This currently fails with type inference.  Reasons not yet investigated.")
def test_lstm():
    filename = r'deepppl/tests/good/lstm.stan'
    target_file = r'deepppl/tests/target_py/lstm.py'
    normalize_and_compare(filename, target_file)

def compile(filename):
    config = dpplc.Config()
    dpplc.stan2astpyFile(filename, config, verbose=True)

def test_coin_guide_missing_var():
    with pytest.raises(MissingGuideException):
        filename = r'deepppl/tests/good/coin_guide_missing_var.stan'
        compile(filename)


def test_coin_guide_sample_obs():
    with pytest.raises(ObserveOnGuideException):
        filename = r'deepppl/tests/good/coin_guide_sample_obs.stan'
        compile(filename)


def test_coin_guide_missing_model():
    "Implicit prior allows to write missing model."
    with not_raises(MissingModelException):
        filename = r'deepppl/tests/good/coin_guide_missing_model.stan'
        compile(filename)


def test_mlp_undeclared_parameters():
    with pytest.raises(UndeclaredParametersException):
        filename = r'deepppl/tests/good/mlp_undeclared_parameters.stan'
        compile(filename)


def test_mlp_undeclared_network1():
    with pytest.raises(UndeclaredNetworkException):
        filename = r'deepppl/tests/good/mlp_undeclared_net1.stan'
        compile(filename)


def test_mlp_undeclared_network2():
    with pytest.raises(UndeclaredNetworkException):
        filename = r'deepppl/tests/good/mlp_undeclared_net2.stan'
        compile(filename)


def test_mlp_missing_guide():
    with pytest.raises(MissingGuideNetException):
        filename = r'deepppl/tests/good/mlp_missing_guide.stan'
        compile(filename)


@pytest.mark.xfail(strict=False, reason="This currently fails with type inference.  Reasons not yet investigated.")
def test_mlp_missing_model():
    with not_raises(MissingPriorNetException):
        filename = r'deepppl/tests/good/mlp_missing_model.stan'
        compile(filename)


@pytest.mark.xfail(strict=False, reason="Type inference results in a different error.")
def test_mlp_incorrect_shape1():
    with pytest.raises(IncompatibleShapes):
        filename = r'deepppl/tests/good/mlp_incorrect_shape1.stan'
        compile(filename)


@pytest.mark.xfail(strict=False, reason="Type inference results in this test passing.")
def test_mlp_incorrect_shape2():
    with pytest.raises(IncompatibleShapes):
        filename = r'deepppl/tests/good/mlp_incorrect_shape2.stan'
        compile(filename)


@pytest.mark.xfail(strict=False, reason="Type inference results in this test passing.")
def test_mlp_incorrect_shape3():
    with pytest.raises(IncompatibleShapes):
        filename = r'deepppl/tests/good/mlp_incorrect_shape3.stan'
        compile(filename)


@pytest.mark.xfail(strict=False, reason="Type inference results in this test passing.")
def test_mlp_incorrect_shape4():
    with pytest.raises(IncompatibleShapes):
        filename = r'deepppl/tests/good/mlp_incorrect_shape4.stan'
        compile(filename)


def test_coin_invalid_sampling():
    with not_raises(InvalidSamplingException):
        filename = r'deepppl/tests/good/coin_invalid_sampling.stan'
        compile(filename)


def test_coin_invalid_sampling2():
    with not_raises(NonRandomSamplingException):
        filename = r'deepppl/tests/good/coin_invalid_sampling2.stan'
        compile(filename)


def test_coin_unknown_identifier():
    with pytest.raises(UndeclaredVariableException):
        filename = r'deepppl/tests/good/coin_unknown_identifier.stan'
        compile(filename)


def test_coin_unknown_distribution():
    with pytest.raises(UnknownDistributionException):
        filename = r'deepppl/tests/good/coin_unknown_distribution.stan'
        compile(filename)


def test_coin_already_declared():
    with pytest.raises(AlreadyDeclaredException):
        filename = r'deepppl/tests/good/coin_already_declared_var.stan'
        compile(filename)


def test_mlp_unsupported_property():
    with pytest.raises(UnsupportedProperty):
        filename = r'deepppl/tests/good/mlp_unsupported_prop.stan'
        target_file = r'deepppl/tests/target_py/mlp.py'
        normalize_and_compare(filename, target_file)


def test_mlp_unsupported_property1():
    with pytest.raises(UnsupportedProperty):
        filename = r'deepppl/tests/good/mlp_unsupported_prop1.stan'
        target_file = r'deepppl/tests/target_py/mlp.py'
        normalize_and_compare(filename, target_file)


def test_mlp():
    filename = r'deepppl/tests/good/mlp.stan'
    target_file = r'deepppl/tests/target_py/mlp.py'
    normalize_and_compare(filename, target_file, verbose=False)


def test_mlp_default_init():
    filename = r'deepppl/tests/good/mlp_default_init.stan'
    target_file = r'deepppl/tests/target_py/mlp_init.py'
    normalize_and_compare(filename, target_file, verbose=False)


def test_vae():
    filename = r'deepppl/tests/good/vae.stan'
    target_file = r'deepppl/tests/target_py/vae.py'
    normalize_and_compare(filename, target_file)


@pytest.mark.xfail(strict=False, reason="This test does not currently work with type inference")
def test_linear_regression():
    filename = r'deepppl/tests/good/linear_regression.stan'
    target_file = r'deepppl/tests/target_py/linear_regression.py'
    normalize_and_compare(filename, target_file)


def test_kmeans():
    filename = r'deepppl/tests/good/kmeans.stan'
    target_file = r'deepppl/tests/target_py/kmeans.py'
    normalize_and_compare(filename, target_file, verbose=False)


def test_schools():
    filename = r'deepppl/tests/good/schools.stan'
    target_file = r'deepppl/tests/target_py/schools.py'
    normalize_and_compare(filename, target_file, verbose=False)


@pytest.mark.xfail(strict=False, reason="This currently fails with type inference.  Reasons not yet investigated.")
def test_gaussian_process():
    filename = r'deepppl/tests/good/gaussian_process.stan'
    target_file = r'deepppl/tests/target_py/gaussian_process.py'
    normalize_and_compare(filename, target_file)


def test_missing_data():
    filename = r'deepppl/tests/good/missing_data.stan'
    target_file = r'deepppl/tests/target_py/missing_data.py'
    normalize_and_compare(filename, target_file)


@pytest.mark.xfail(strict=False, reason="This currently fails with type inference.  Reasons not yet investigated.")
def test_regression_matrix():
    filename = r'deepppl/tests/good/regression_matrix.stan'
    target_file = r'deepppl/tests/target_py/regression_matrix.py'
    normalize_and_compare(filename, target_file)


@pytest.mark.xfail(strict=False, reason="This currently fails with type inference.  Reasons not yet investigated.")
def test_logistic():
    filename = r'deepppl/tests/good/logistic.stan'
    target_file = r'deepppl/tests/target_py/logistic.py'
    normalize_and_compare(filename, target_file)

# def test_row_vector_expr_terms():
#     filename = r'deepppl/tests/good/row_vector_expr_terms.stan'
#     target_file = r'deepppl/tests/target_py/row_vector_expr_terms.py'
#     normalize_and_compare(filename, target_file)


@pytest.mark.xfail(strict=False, reason="This currently fails with type inference.  Reasons not yet investigated.")
def test_gradient_warn():
    filename = r'deepppl/tests/good/gradient_warn.stan'
    target_file = r'deepppl/tests/target_py/gradient_warn.py'
    normalize_and_compare(filename, target_file)


@pytest.mark.xfail(strict=False, reason="This currently fails with type inference.  Reasons not yet investigated.")
def test_squared_error():
    filename = r'deepppl/tests/good/squared_error.stan'
    target_file = r'deepppl/tests/target_py/squared_error.py'
    normalize_and_compare(filename, target_file)

# def test_validate_arr_expr_primitives():
#     filename = r'deepppl/tests/good/validate_arr_expr_primitives.stan'
#     target_file = r'deepppl/tests/target_py/validate_arr_expr_primitives.py'
#     normalize_and_compare(filename, target_file)


@pytest.mark.xfail(strict=False, reason="This currently fails with type inference.  Reasons not yet investigated.")
def test_vectorized_probability():
    filename = r'deepppl/tests/good/vectorized_probability.stan'
    target_file = r'deepppl/tests/target_py/vectorized_probability.py'
    normalize_and_compare(filename, target_file)


def test_lda():
    filename = r'deepppl/tests/good/lda.stan'
    target_file = r'deepppl/tests/target_py/lda.py'
    normalize_and_compare(filename, target_file, verbose=False)


def test_neal_funnel():
    filename = r'deepppl/tests/good/neal_funnel.stan'
    target_file = r'deepppl/tests/target_py/neal_funnel.py'
    normalize_and_compare(filename, target_file)


def test_cockroaches():
    filename = r'deepppl/tests/good/cockroaches.stan'
    target_file = r'deepppl/tests/target_py/cockroaches.py'
    normalize_and_compare(filename, target_file)


def test_seeds():
    filename = r'deepppl/tests/good/seeds.stan'
    target_file = r'deepppl/tests/target_py/seeds.py'
    normalize_and_compare(filename, target_file)
