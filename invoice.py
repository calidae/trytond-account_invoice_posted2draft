# This file is part account_invoice_posted2draft module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import Workflow, ModelView
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta

__all__ = ['Invoice']
__metaclass__ = PoolMeta


class Invoice:
    __name__ = 'account.invoice'

    @classmethod
    def __setup__(cls):
        super(Invoice, cls).__setup__()
        cls._check_modify_exclude.append('move')
        cls._transitions |= set((('posted', 'draft'),))
        cls._buttons.update({
                'draft': {
                    'invisible': (Eval('state').in_(['draft', 'paid'])
                    | ((Eval('state') == 'cancel') & Eval('cancel_move'))),
                    },
                })

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(self, invoices):
        Move = Pool().get('account.move')

        moves = []
        for invoice in invoices:
            if invoice.move:
                moves.append(invoice.move)
        if moves:
            Move.draft(moves)
        super(Invoice, self).draft(invoices)
