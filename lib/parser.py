import re
import lib.entities as en

class Pattern:
    """The pattern class defines the keywords and patterns accepted in the
    grammar of supply chain description format
    """

    KEYWORDS={'PROD_DEF': 'product', 'COMP_DEF': 'component', 'PR_HIGH': 'high', 'PR_LOW': 'low', 'SUPP': 'supplier'}
    ID="[a-zA-Z_][a-zA-Z0-9_]*"
    PRODUCT_DEF=f"\\s{KEYWORDS['PROD_DEF']}\\s"

class StatementType:
    """The type of statements are defined in this class

    """
    PROD_DEF=0
    COMP_DEF=1
    TRAN_DEF=2

class Statement:
    """The Statement class constructs a valid statement of supply chain
       description format

    """

    def __init__(self, stmt_type):
        self._stmt_type=stmt_type

    @classmethod
    def factory(cls, stmt_str):
        # parse the first token
        result=re.match(f"\s*(?P<first_token>{Pattern.ID})\s*(?P<the_rest>(?s:.*))",stmt_str)
        if result:
            if result['first_token'] == Pattern.KEYWORDS['PROD_DEF']:
                return ProductDef(result['the_rest'])
            elif result['first_token'] == Pattern.KEYWORDS['COMP_DEF']:
                return ComponentDef(result['the_rest'])
            else:
                return TransitionDef(stmt_str)
        else:
            raise ValueError(f'Invalid statement: "{stmt_str}"')

    def get_type(self):
        """returns the statement type"""
        return self._stmt_type

    def _tokenize_def_body(self, def_body):
        def_list=def_body.split(',')
        if len(def_list) == 1 and def_list[0] == '':
            raise ValueError('Definition body is empty')
        return def_list

    def _parse(self,stmt_body):
        pass

class ProductDef(Statement):
    def __init__(self, stmt_body):
        super(ProductDef, self).__init__(StatementType.PROD_DEF)
        self._parse(stmt_body)

    def _parse(self, stmt_body):
        """parses a product definition statement"""
        prod_list=self._tokenize_def_body(stmt_body)
        pattern=f"^(\s*(?P<pname>{Pattern.ID})\s*=\s*(?P<ord_sz>[0-9]+)(\s+(?P<priority>({Pattern.KEYWORDS['PR_HIGH']})|({Pattern.KEYWORDS['PR_LOW']})))?)$"
        matcher=re.compile(pattern)

        self._products=[]
        for p in prod_list:
            res=matcher.match(p)

            if res is None:
                raise ValueError('[Err] Invalid product definition.')

            priority=en.ProductPriority.HIGH if res['priority'] == Pattern.KEYWORDS['PR_HIGH'] else en.ProductPriority.LOW
            self._products.append(en.Product(res['pname'], int(res['ord_sz']), priority))

class ComponentDef(Statement):

    def __init__(self, stmt_body):
        super(ComponentDef, self).__init__(StatementType.COMP_DEF)
        self._parse(stmt_body)

    def _parse(self, stmt_body):
        """parses a component definition statement"""
        comp_list=self._tokenize_def_body(stmt_body)
        pattern=f"^(\s*(?P<cname>{Pattern.ID})\s*(=\s*(?P<stock>[0-9]+)\s*)?)$"
        matcher=re.compile(pattern)

        self._components=[]
        for p in comp_list:
            res=matcher.match(p)

            if res is None:
                raise ValueError('[Err] Invalid component definition.')

            stock=int(res['stock']) if res['stock'] else 0
            self._components.append(en.Component(res['cname'], stock))

class TransitionDef(Statement):
    """The transition definiton class
       It holds information about a transition. The correct format is as follows:
       {target} <- {source1} + {source2} + ...
       or
       {targe}: <- {source1} | {source2} | ...
       or
       {target} <- supplier
       where {target} and {source1} ... are valid identifiers.
    """
    def __init__(self, stmt_body):
        super(TransitionDef, self).__init__(StatementType.TRAN_DEF)
        self.parse(stmt_body)

    def parse(self, stmt_body):
        """parses a tarnsition definition"""
        res=re.match(f"\s*(?P<target>{Pattern.ID})\s*<-(?P<sources>(?s:.*))", stmt_body)

        if res is None:
            raise ValueError('[ERR] Invalid transition.')

        matcher=re.compile(f"^(\s*(?P<source>{Pattern.ID})\s*)$")
        if res['sources'].find('|') > 0:
            tr_type=en.TransitionType.OR
            source_list=res['sources'].split('|')
        elif res['sources'].find('+') > 0:
            tr_type=en.TransitionType.AND
            source_list=res['sources'].split('+')
        else:
            source_list=[res['sources']]
            tr_type=None
        sources=[]
        for src in source_list:
            res_src=matcher.match(src)
            if res_src is None:
                raise ValueError(f'[ERR] Invalid identifier is given for transition "{src}".')

            sources.append(res_src['source'])

        if tr_type is None:
            if sources[0] == Pattern.KEYWORDS['SUPP']:
                tr_type=en.TransitionType.DIR
            else:
                tr_type=en.TransitionType.AND
        self._transition=en.Transition(sources,res['target'],tr_type)

class Parser:
    """
       The Parser class parses and an input file describing a supply chain into
       a set of syntactically correct statements, each describing the definition
       of either a set of products, a set of componnents or a transition.
    """

    def __init__(self, modelfile):
        self._modelfile=modelfile

    def parse(self):
        """parses an input file describing a supply chain into a list of statements.
           It returns the list of statements.
        """
        empty_stmt=re.compile('^(\s*)$') # matches an empty statement
        with open(self._modelfile,"r") as reader:
            stmt_list=reader.read().split(';') # statements are delimited by ';'
            statements=[]
            for s in stmt_list:
                if empty_stmt.match(s) is None: # parses only if it is not an empty statement
                    try:
                        stmt=Statement.factory(s)
                        statements.append(stmt)
                    except Exception as e:
                        print(f'Error when parsing statement {s}')
                        print(f'More details:\n{e}')
                        return None
        return statements
