# This file is part account_invoice_posted2draft module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import Workflow
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['Invoice', 'Move']


class Invoice(metaclass=PoolMeta):
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
    def draft(cls, invoices):
        Move = Pool().get('account.move')

        moves = []
        for invoice in invoices:
            if invoice.move:
                if invoice.move.period.state == 'close':
                    raise UserError(gettext(
                        'account_invoice_posted2draft.draft_closed_period',
                            invoice=invoice.rec_name,
                            period=invoice.move.period.rec_name,
                            ))
                moves.append(invoice.move)
        if moves:
            with Transaction().set_context(draft_invoices=True):
                Move.write(moves, {'state': 'draft'})
        cls.write(invoices, {
            'invoice_report_format': None,
            'invoice_report_cache': None,
            })
        return super(Invoice, cls).draft(invoices)

    @classmethod
    @Workflow.transition('cancel')
    def cancel(cls, invoices):
        for invoice in invoices:
            if invoice.type == 'out' and invoice.number:
                raise UserError(gettext(
                    'account_invoice_posted2draft.cancel_invoice_with_number'))

        return super(Invoice, cls).cancel(invoices)


class Move(metaclass=PoolMeta):
    __name__ = 'account.move'

    @classmethod
    def check_modify(cls, *args, **kwargs):
        if Transaction().context.get('draft_invoices', False):
            return
        return super(Move, cls).check_modify(*args, **kwargs)
