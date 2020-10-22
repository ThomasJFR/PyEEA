from ..cashflow import Cashflow, NullCashflow
from ..cashflow import Future, Perpetuity, Dynamic

from ..utilities import parse_ns, parse_d, get_final_period

from copy import deepcopy


class Tax:
    def __init__(self, tag, rate, title=None):
        self._tag = tag
        self._rate = rate
        self._title = title or ("Tax on %s" % self._tag)

    def get_title(self):
        return self._title

    def generate_cashflow(self, cashflows=[], depreciations=[]):
        # Remove any irrelevant cashflows
        taxable_cashflows = [cf for cf in cashflows if self._tag in cf.tags] or [
            NullCashflow()
        ]
        shielding_depreciations = [
            dp for dp in depreciations if self._tag in dp.tags
        ] or [NullCashflow()]

        # Create and return the TaxCashflow object
        return TaxCashflow(
            self._rate,
            taxable_cashflows,
            shielding_depreciations,
            get_final_period(cashflows, finite=True),
            title=self.get_title(),
            tags=self._tag,
        )


class TaxCashflow(Dynamic):
    def __init__(self, rate, cashflows, depreciations, d, title=None, tags=None):
        super().__init__(TaxCashflow.tax_fun, d, title, tags)
        self._rate = rate
        self._cashflows = cashflows
        self._depreciations = depreciations

    def to_shorthand(self):
        return "Tax(%s, %.2f%%)" % (self.tags[0], self._rate * 100)

    def to_pv(self, i):
        # Handles every cashflow in range d
        pv = super().to_pv(i)

        # Check for Perpetuities
        if perpetuities := [cf for cf in self._cashflows if isinstance(cf, Perpetuity)]:
            perpetuities = deepcopy(perpetuities)
            for perpetuity in perpetuities:
                perpetuity.amount = perpetuity[self.d[1] + 1].amount
                perpetuity.d0 = self.d[1]
            pv += sum([perpetuity.to_pv(i) for perpetuity in perpetuities]) * self._rate

        return pv

    # Because of the way Dynamic is set up, we want to reference self. At the same time,
    # we need the function to be static, so that we can manually supply 'self'.
    @staticmethod
    def tax_fun(self, n):
        taxable_sum = sum([cashflow[n] for cashflow in self._cashflows])
        shielding_sum = sum([depreciation[n] for depreciation in self._depreciations])

        taxed_amount = (taxable_sum - shielding_sum) * self._rate
        return taxed_amount

