from abc import ABC, abstractmethod
from enum import Enum
from collections.abc import Iterable
from ..utilities import parse_ns
from numbers import Number

class Cashflow(ABC):
    """ Representation of a cash transfer
    
    Abstract representation of a transfer of cash into or out of some entity.
    Cashflows are intended to be easy to convert to different forms.
    
    Attributes:
        amount: The characteristic value of the cash flow
        title: Optional; A descriptive, human-readable title of the cashflow
        tags: Optional: A string or collection of strings which identify the 
            cashflow as belonging to a certain collection of cashflows.
            The title is automatically included as a tag, if supplied.
    """

    CURRENCY_FMT_STR = "${:,.2f}"
    cashflow_id = 1  # Unique ID for each cashflow

    def __init__(self, amount, title=None, tags=None):
        """ Creates a new Cashflow instance

        Initializes an instance of Cashflow. This constructor should generally 
        be called first in children. Each Cashflow is assigned a unique ID.
        """
        self._id = Cashflow.cashflow_id
        self._amount = float(amount)
        self._title = str(title or f"{self.get_classname()} {self._id}") 
        self._tags = list((self.title,))
        if tags:
            if isinstance(tags, str):
                self._tags.append(tags)
            else:
                self._tags.extend(tags)
        Cashflow.cashflow_id += 1

    @abstractmethod
    def cashflow_at(self, ns):
        """ Gets the cashflow at one or multiple periods

        Given some periods, returns the single cash transfer associated with
        that period for a Cashflow instance. For example, consider an
        Annuity of amount -250 for four years:
        
            0 --- 1 --- 2 --- 3 --- 4 --- 5 --- 6 --- 
                  |     |     |     |
                  v     v     v     v -250

        In this case, the cashflows at periods 1, 2, 3 and 4 are Future payments
        of -250 at each respective period. However, the cashflow at period 5 is
        zero - equivalent to a NullCashflow, which would be returned.

        In general, this method serves an implementation for the __get_item__ 
        method, which is used as a proxy for its neatness and cleanliness.

        Args:
            ns: A integer or sequence of integers representing periods
        
        Returns:
            A single cashflow or tuple of of cashflows, type matching ns.
            Cashflows may be of type NullCashflow (if amount = 0) or 
            Present (if n = 0) or Future (if n > 0)
        
        See Also:
            Cashflow.__get_item__
            NullCashflow
            Present
            Future
        """
        pass

    @abstractmethod
    def to_pv(self, i):
        """ Converts this Cashflow to an equivalent Present cashflow

        Given a compound interest rate, computes and returns an equivalent 
        single cashflow occuring now.

        Args:
            i: The decimal interest rate to be applied in the conversion

        Returns:
            Present
        """
        pass

    @abstractmethod
    def to_fv(self, i, n):
        """ Converts this Cashflow to an equivalent Future cashflow

        Given a compound interest rate, computes and returns an equivalent
        single cashflow occurring at a specified period. 

        Args:
            i: The decimal interest rate to be applied in the conversion
            n: The period for the future payment

        Returns:
            Future
        """
        pass

    @abstractmethod
    def to_av(self, i, d, scheme):
        """ Converts this Cashflow to an equivalent Annuity

        Given a compound interest rate, computes and returns an equivalent
        recurrent cashflow occurring at the specified periods. 

        Args:
            i: The decimal interest rate to be applied in the conversion
            d: The duration over which the cashflow takes place.

        Returns:
            Future

        See Also:
            parse_d: Explains the format for argument d
        """""
        pass

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, val):
        self._amount = float(val)

    @property
    def title(self):
        return self._title
    
    def set_title(self, title):
        self._title = str(title)
        self._tags[0] = self.title  # Position zero contains the title

    def get_title(self):
        print("")
        return self.title

    @property
    def tags(self):
        return self._tags

    def add_tag(self, tag):
        self.tags.append(tag)

    def add_tags(self, tags):
        for tag in tags:
            self.add_tag(tag)

    def show(self, **kwargs):
        from ..output import generate_cashflow_diagram
        from matplotlib.pyplot import show
        generate_cashflow_diagram(self, **kwargs)
        show()
    
    def __repr__(self, info):
        """ Returns an unambiguous string representation of the Cashflow
       
        Returns a string that can be used to completely characterize a cashflow; 
        in other words, one should be able to fully reproduce the exact defintion
        of a cashflow given only this string representation. As such, the string
        necessarily includes:
            The characteristc cashflow amount; 
            A letter or few letters indicating the type of cashflow; and 
            Any other information needed to fully characterize the Cashflow. 

        The representation optionally begins with a currency, followed by 
        the amount and parentheses containing information, as shown below:
            
                CUR amount(type, info...)

        For example, a Future cashflow of -300 New Zealand Dollars occurring at 
        period 2 would be shown as

                NZD -300(F, 2)

        More complex cashflows will generally have additional parentheticals.
        For example, a Geometric annuity of -500 Turkish Lira growing at 5% per 
        year over 10 years would be represented as:

                TRY -500(G, 0.05, [0, 10])

        Children of Cashflows should always include all information included by the
        parent class. For example, a Gradient cashflow should always include the 
        duration of the cashflow as its parent, Annuity, does.

        Args:
            info: A sequence of informational content to be displayed within 
                the parantheses.
        """
        valstr = str(self)
        infostr = ", ".join((str(i) for i in info)) 
        infostr = infostr.replace('\'', '')  # Remove unnecessary quotation marks
        return f"{valstr}({infostr})"

    def __str__(self):
        valstr = Cashflow.CURRENCY_FMT_STR.format(self.amount)
        valstr = valstr.replace("$-", "-$")
        return valstr

    def __getitem__(self, ns):
        """ Proxy for cashflow_at() method """
        ns = parse_ns(ns)
        return self.cashflow_at(ns)

    def __radd__(self, other):
        if other == 0:  # Accounts for first iteration of sum()
            return self
        else:
            return self.__add__(other)

    def __rsub__(self, other):
        return self.__sub__(other)
   
    @classmethod
    def get_classname(cls):
        """ Used for default Cashflow title generation """
        return cls.__name__


class NullCashflow(Cashflow):
    """ A cash transfer of value zero
    
    Defines a cashflow with no value - that is, its amount is necessarily zero. 
    This can be represented by a blank cashflow diagram, as shown:

        0 --- 1 --- 2 --- 3 --- 4 --- 5 --- 6 --- 
        
    
    All arithmetic operations with a NullCashflow instance return the other operand. 
    A NullCashflow is generally used to explicitly indicate that the result of some
    operation (e.g. retrieving all cashflows at a period) yielded no cashflows.
    All conversions return the type specified by the conversion with an amount
    equal to zero.
    """

    def __init__(self, title=None, tags=None):
        """ See base class """
        return super().__init__(0, title, tags)

    def to_pv(self, i):
        """ See base class """
        from .SinglePaymentFactory import Present
        return Present(0)

    def to_fv(self, i, n):
        """ See base class """
        from .SinglePaymentFactory import Future
        return Future(0, n)

    def to_av(self, i, d):
        """ See base class """
        from .UniformSeriesFactory import Annuity
        return Annuity(0, d)

    def cashflow_at(self, n):
        """ See base class """
        return self
    
    def __repr__(self):
        info = ('N',)  # Explicitly indicates that Cashflow is null
        return super().__repr__(info)

    def __neg__(self):
        return self
    
    def __add__(self, other):
        return other

    def __sub__(self, other):
        return other

    def __mul__(self, other):
        return self

    def __lt__(self, them):
        # Because interest cannot cause a cash amount to invert signs when
        # converting across time, we can compare single cashflows to
        # NullCashflows. In essence, this operation is equivalent to checking
        # if the sign of a cashflow is negative.

        them = them.amount if isinstance(them, Future) else float(them)
        return self.amount < them


    def __le__(self, them):
        # Because interest cannot cause a cash amount to invert signs when
        # converting across time, we can compare single cashflows to
        # NullCashflows. In essence, this operation is equivalent to checking 
        # if the sign of a cashflow is not positive.

        them = them.amount if isinstance(them, Future) else float(them)
        return self.amount <= them

    def __gt__(self, them):
        return not self.__le__(them)

    def __ge__(self, them):
        return not self.__lt__(them)

