from .harness import MCMCTest
from pprint import pprint

def test_neal_funnel():   
    test_neal_funnel = MCMCTest(
        name='neal_funnel',
        model_file='deepppl/tests/good/neal_funnel.stan'
    )
    
    return test_neal_funnel.run()
    
if __name__ == "__main__":
    pprint(test_neal_funnel())