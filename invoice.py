# This file is part account_invoice_posted2draft module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import Workflow, ModelView
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.tools import grouped_slice
from trytond.transaction import Transaction

__all__ = ['Invoice', 'Move']


class Invoice:
    __metaclass__ = PoolMeta
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
        cls._error_messages.update({
                'draft_closed_period': ('You can not set to draft invoice '
                    '"%(invoice)s" because period "%(period)s" is closed.'),
                'cancel_invoice_with_number': ('You cannot cancel an invoice '
                    'with number.'),
                })

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, invoices):
        pool = Pool()
        Move = pool.get('account.move')
        try:
            Payment = pool.get('account.payment')
        except KeyError:
            Payment = None
        try:
            Commission = pool.get('commission')
        except KeyError:
            Commission = None
        moves = []
        lines = []
        for invoice in invoices:
            if invoice.move:
                if invoice.move.period.state == 'close':
                    cls.raise_user_error('draft_closed_period', {
                            'invoice': invoice.rec_name,
                            'period': invoice.move.period.rec_name,
                            })
                moves.append(invoice.move)
                lines.extend([l.id for l in invoice.move.lines])
        if moves:
            with Transaction().set_context(draft_invoices=True):
                Move.write(moves, {'state': 'draft'})
        if Payment:
            payments = Payment.search([
                    ('line', 'in', lines),
                    ('state', '=', 'failed'),
                    ])
            if payments:
                Payment.write(payments, {'line': None})
        if Commission:
            for sub_invoices in grouped_slice(invoices):
                ids = [i.id for i in sub_invoices]
                commissions = Commission.search([
                        ('origin.invoice', 'in', ids, 'account.invoice.line'),
                        ])
                Commission.delete(commissions)
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
                cls.raise_user_error('cancel_invoice_with_number')

        return super(Invoice, cls).cancel(invoices)


class Move:
    __metaclass__ = PoolMeta
    __name__ = 'account.move'

    @classmethod
    def check_modify(cls, *args, **kwargs):
        if Transaction().context.get('draft_invoices', False):
            return
        return super(Move, cls).check_modify(*args, **kwargs)
