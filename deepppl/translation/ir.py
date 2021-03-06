import warnings
from itertools import chain

class IRMeta(type):
    def __init__(cls, *args, **kwargs):
        selector = 'return visitor.visit{}(self)'.format(cls.__name__)
        accept_code = "def accept(self, visitor):\n\t{}".format(selector)
        l = {}
        exec(accept_code, globals(), l)
        setattr(cls, "accept", l["accept"])

class IR(metaclass=IRMeta):
    def is_variable_decl(self):
        return False

    def is_property(self):
        return False


    def is_variable(self):
        return False

    def is_net_var(self):
        return False

    def is_tuple(self):
        return False

    @property
    def children(self):
        return []

    @children.setter
    def children(self, children):
        assert not children, "Setting children to object without children"

    def ensureReal(self):
        warnings.warn("don't know how to ensure Real", Warning)
        return True

    def ensureInt(self):
        warnings.warn("don't know how to ensure Int", Warning)
        return True

class Program(IR):
    def __init__(self, body = []):
        super(Program, self).__init__()
        self.body = body
        self.initBlocksNone()
        self.addBlocks(body)

    def initBlocksNone(self):
        for name in self.blockNames():
            setattr(self, name, None)

    @property
    def children(self):
        return self.blocks()

    @children.setter
    def children(self, blocks):
        self.addBlocks(blocks)

    def addBlocks(self, blocks):
        for block in blocks:
            name = block.blockName()
            if getattr(self, name) is not None:
                assert False, "trying to set :{} twice.".format(name)
            setattr(self, name, block)

    def blocks(self):
        ## impose an evaluation order
        for name in self.blockNames():
            block = getattr(self, name, None)
            if block is not None:
                yield block

    def blockNames(self):
        return [
            'networksblock', 'data', 'transformeddata', 'parameters', 'transformedparameters', \
                    'guideparameters', \
                    'guide', 'prior', 'model', 'generatedquantities' ]



class ProgramBlocks(IR):
    def __init__(self, body = []):
        super(ProgramBlocks, self).__init__()
        self.body = body
        self._nets = []
        self._blackBoxNets = set()


    def __eq__(self, other):
        """Basic equality"""
        return self.children == other.children

    @property
    def children(self):
        return self.body

    @children.setter
    def children(self, body):
        self.body = body

    @classmethod
    def blockName(cls):
        return cls.__name__.lower()

    def is_data(self):
        return False

    def is_transformed_data(self):
        return False

    def is_transformed_parameters(self):
        return False

    def is_model(self):
        return False

    def is_guide(self):
        return False

    def is_networks(self):
        return True

    def is_guide_parameters(self):
        return False

    def is_prior(self):
        return False

    def is_parameters(self):
        return False

    def is_generated_quantities(self):
        return False


class SamplingBlock(ProgramBlocks):
    """A program block where sampling is a valid statement """
    def __init__(self, body = []):
        super(SamplingBlock, self).__init__(body = body)
        self._sampled = set()

    def addSampled(self, variable):
        self._sampled.add(variable)



class Model(SamplingBlock):
    def is_model(self):
        return True

class Guide(SamplingBlock):
    def is_guide(self):
        return True

class Prior(SamplingBlock):
    def is_prior(self):
        return True

class GuideParameters(ProgramBlocks):
    def is_guide_parameters(self):
        return True

class NetworksBlock(ProgramBlocks):
    def __init__(self, decls = None):
        super(NetworksBlock, self).__init__(body = decls)

    @property
    def decls(self):
        return self.body

    @decls.setter
    def decls(self, decls):
        self.body = decls

    def is_networks(self):
        return True


class Parameters(ProgramBlocks):
    def is_parameters(self):
        return True


class Data(ProgramBlocks):
    def is_data(self):
        return True

class TransformedData(ProgramBlocks):
    def is_transformed_data(self):
        return True

class TransformedParameters(ProgramBlocks):
    def is_transformed_parameters(self):
        return True

class GeneratedQuantities(ProgramBlocks):
    def is_generated_quantities(self):
        return True

class Statements(IR):
    pass

class AssignStmt(Statements):
    def __init__(self, target = None, value = None, constraints = None):
        super(AssignStmt, self).__init__()
        self.target = target
        self.value = value
        self.constraints = constraints

    @property
    def children(self):
        return [self.target, self.value]

    @children.setter
    def children(self, children):
        [self.target, self.value] = children

class SamplingStmt(Statements):
    def __init__(self, target = None, id = None, args = None, shape = None):
        super(SamplingStmt, self).__init__()
        self.target = target
        self.id = id
        self.args = args
        self.shape = shape

    @property
    def children(self):
        assert False, "SamplingStmt.children should not be called"
        # return [self.target,] + self.args + ([self.shape] if self.shape else [])

    # @children.setter
    # def children(self, children):
    #     self.target = children[0]
    #     self.args = children[1:]

class SamplingDeclaration(SamplingStmt):
    pass

class SamplingObserved(SamplingStmt):
    pass

class SamplingParameters(SamplingStmt):
    pass

class SamplingFactor(SamplingStmt):
    """
    Like observe but without distribution,
    just the log-density.
    This behavior is achieved using the following identity:
    ```
        target += exp   ==   -exp ~ exponential(1)
    ```
    """
    def __init__(self, target = None):
        super(SamplingFactor, self).__init__(target = target,
                                            id = None,
                                            args = [],
                                            shape = None)

class ForStmt(Statements):
    def __init__(self, id = None, from_ = None, to_ = None, body = None):
        super(ForStmt, self).__init__()
        self.id = id
        self.from_ = from_
        self.to_ = to_
        self.body = body


    @property
    def children(self):
        return [self.from_, self.to_, self.body]

    @children.setter
    def children(self, children):
        [self.from_, self.to_, self.body] = children

class ConditionalStmt(Statements):
    def __init__(self, test = None, true = None, false = None):
        super(ConditionalStmt, self).__init__()
        self.test = test
        self.true = true
        self.false = false

    @property
    def children(self):
        return [self.test, self.true, self.false]

    @children.setter
    def children(self, children):
        [self.test, self.true, self.false] = children

class WhileStmt(Statements):
    def __init__(self, test = None, body = None):
        super(WhileStmt, self).__init__()
        self.test = test
        self.body = body

    @property
    def children(self):
        return [self.test, self.body]

    @children.setter
    def children(self, children):
        [self.test, self.body] = children

class BlockStmt(Statements):
    def __init__(self, body = None):
        super(BlockStmt, self).__init__()
        self.body = body

    @property
    def children(self):
        return self.body

    @children.setter
    def children(self, children):
        self.body = children

class CallStmt(Statements):
    def __init__(self, id = None, args = None):
        super(CallStmt, self).__init__()
        self.id = id
        self.args = args

    @property
    def children(self):
        return [self.args]

    @children.setter
    def children(self, children):
        [self.args,] = children

    def __str__(self):
        s = str(self.id) + "("
        first = True
        for a in self.args.children:
            if first:
                first = False
            else:
                s = s + ","
            s = s + str(a)
        s = s + ")"
        return s

class BreakStmt(Statements):
    pass

class ContinueStmt(Statements):
    pass

class Expression(Statements):
    def is_data_var(self):
        return all(x.is_data_var() for x in self.children)

    def is_transformed_data_var(self):
        return all(x.is_transformed_data_var() for x in self.children)


    def is_transformed_parameters_var(self):
        return all(x.is_transformed_parameters_var() for x in self.children)

    def is_params_var(self):
        return (x.is_params_var() for x in self.children)

    def is_guide_var(self):
        return (x.is_guide_var() for x in self.children)

    def is_guide_parameters(self):
        return (x.is_guide_parameters_var() for x in self.children)

    def is_prior_var(self):
        return (x.is_prior_var() for x in self.children)

    def is_generated_quantities_var(self):
        return all(x.is_generated_quantities_var() for x in self.children)

class Constant(Expression):
    def __init__(self, value = None):
        super(Constant, self).__init__()
        self.value = value

    def ensureInt(self):
        self.value = int(self.value)

    def ensureReal(self):
        self.value = float(self.value)


class Tuple(Expression):
    def __init__(self, exprs = None):
        super(Tuple, self).__init__()
        self.exprs = exprs

    def is_tuple(self):
        return True

    @property
    def children(self):
        return self.exprs

    @children.setter
    def children(self, children):
        self.exprs = children

class Str(Expression):
    def __init__(self, value = None):
        super(Str, self).__init__()
        self.value = value

class List(Expression):
    def __init__(self, elements = []):
        super(List, self).__init__()
        self.elements = elements

    @property
    def children(self):
        return self.elements

    @children.setter
    def children(self, children):
        self.elements = children

class BinaryOperator(Expression):
    def __init__(self, left = None, op = None, right = None):
        super(BinaryOperator, self).__init__()
        self.left = left
        self.right = right
        self.op = op

    @property
    def children(self):
        return [self.left, self.right, self.op]

    @children.setter
    def children(self, children):
        [self.left, self.right, self.op] = children


class UnaryOperator(Expression):
    def __init__(self, value = None, op = None):
        super(UnaryOperator, self).__init__()
        self.value = value
        self.op = op

    @property
    def children(self):
        return [self.value, self.op]

    @children.setter
    def children(self, children):
        [self.value, self.op] = children

class Subscript(Expression):
    def __init__(self, id = None, index = None):
        super(Subscript, self).__init__()
        self.id = id
        self.index = index

    @property
    def children(self):
        return [self.id, self.index]

    @children.setter
    def children(self, children):
        [self.id, self.index] = children

    def is_data_var(self):
        return self.id.is_data_var()

    def is_transformed_data_var(self):
        return self.id.is_transformed_data_var()

    def is_transformed_parameters_var(self):
        return self.id.is_transformed_parameters_var()

    def is_params_var(self):
        return self.id.is_params_var()

    def is_guide_var(self):
        return self.id.is_guide_var()

    def is_guide_parameters_var(self):
        return self.id.is_guide_parameters_var()

    def is_prior_var(self):
        return self.id.is_prior_var()

    def is_generated_quantities_var(self):
        return self.id.is_generated_quantities_var()

class VariableDecl(IR):
    def __init__(self, id = None, dim = None, init = None,
                    type_ = None):
        super(VariableDecl, self).__init__()
        self.id = id
        self.dim = dim
        self.init = init
        self.data = False
        self.parameters = False
        self.transformed_parameters = False
        self.transformed_data = False
        self.generated_quantities = False
        self.type_ = type_

    def is_variable_decl(self):
        return True

    def set_data(self):
        self.data = True

    def set_parameters(self):
        self.parameters = True

    def set_transformed_parameters(self):
        self.transformed_parameters = True

    def set_transformed_data(self):
        self.transformed_data = True

    def set_generated_quatities(self):
        self.generated_quantities = True

    @property
    def children(self):
        return [self.dim, self.init, self.type_]

    @children.setter
    def children(self, children):
        [self.dim, self.init, self.type_] = children

class Type_(IR):
    def __init__(self, type_ = None, constraints = None, is_array = False, dim = None):
        super(Type_, self).__init__()
        self.type_ = type_
        self.constraints = constraints or []
        self.is_array = is_array
        self.dim = dim
        if self.constraints:
            if self.type_ == 'int':
                f = lambda x: x.ensureInt()
            elif self.type_ == 'real':
                f = lambda x: x.ensureReal()
            elif self.type_ == 'vector':
                f = lambda x: x.ensureReal()
            elif self.type_ == 'matrix':
                f = lambda x: x.ensureReal()
            else:
                assert False, f"Unknown type: {self.type_}"
            [f(constraint) for constraint in self.constraints]

    @property
    def children(self):
        return self.constraints

    @children.setter
    def children(self, constraints):
        self.constraints = constraints

class Constraint(IR):
    def __init__(self, sort = None, value = None):
        super(Constraint, self).__init__()
        self.sort = sort
        self.value = value

    def ensureReal(self):
        self.value.ensureReal()

    def ensureInt(self):
        self.value.ensureInt()


    @property
    def children(self):
        return [self.value, ]

    @children.setter
    def children(self, values):
        self.value, = values


class Variable(Expression):
    def __init__(self, id = None):
        super(Variable, self).__init__()
        self.id = id
        self.block_name = None

    def __str__(self):
        return str(self.id)

    def __eq__(self, other):
        return isinstance(other, Variable) and \
                self.id == other.id

    def is_variable(self):
        return True

    def is_data_var(self):
        return self.block_name == Data.blockName()

    def is_transformed_data_var(self):
        return self.block_name == TransformedData.blockName()

    def is_params_var(self):
        return self.block_name == Parameters.blockName()

    def is_transformed_parameters_var(self):
        return self.block_name == TransformedParameters.blockName()

    def is_guide_var(self):
        return self.block_name == Guide.blockName()

    def is_guide_parameters_var(self):
        return self.block_name == GuideParameters.blockName()

    def is_prior_var(self):
        return self.block_name == Prior.blockName()

    def is_generated_quantities_var(self):
        return self.block_name == GeneratedQuantities.blockName()

class VariableProperty(Expression):
    def __init__(self, var = None, prop = None):
        super(VariableProperty, self).__init__()
        self.var = var
        self.prop = prop

    def is_property(self):
        return True

class AnonymousShapeProperty(VariableProperty):

    @classmethod
    def newvar(cls):
        if hasattr(cls, 'counter'):
            cls.counter = cls.counter+1
        else:
            cls.counter = 0
        return Variable(id="anon"+str(cls.counter))

    def __init__(self):
        super(AnonymousShapeProperty, self).__init__(var = AnonymousShapeProperty.newvar(), prop="shape")


class NetVariableProperty(VariableProperty):
    pass

class NetDeclaration(IR):
    def __init__(self, name = None, cls = None, params = []):
        super(NetDeclaration, self).__init__()
        self.name = name
        self.net_cls = cls
        self.params = params

class NetVariable(Expression):
    def __init__(self, name = None, ids =  []):
        super(NetVariable, self).__init__()
        self.name = name
        self.ids = ids
        self.block_name = None

    @property
    def id(self):
        return  '.'.join(chain([self.name], self.ids))

    def is_net_var(self):
        return True


class Operator(Expression):
    pass

class Plus(Operator):
    pass

class Minus(Operator):
    pass

class Pow(Operator):
    pass

class Mult(Operator):
    pass

class DotMult(Operator):
    pass

class Div(Operator):
    pass

class DotDiv(Operator):
    pass

class And(Operator):
    pass

class Or(Operator):
    pass

class LE(Operator):
    pass

class GE(Operator):
    pass

class LT(Operator):
    pass

class GT(Operator):
    pass

class EQ(Operator):
    pass


class UOperator(Operator):
    """Unary operators."""

class UPlus(UOperator):
    pass

class UMinus(UOperator):
    pass

class UNot(UOperator):
    pass
