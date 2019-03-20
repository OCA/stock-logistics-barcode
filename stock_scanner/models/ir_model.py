from odoo import api, models


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    @api.model
    def _update(self, model, module, values, xml_id=False, store=True,
                noupdate=False, mode='init', res_id=False):
        data = [{'values': values,
                 'xml_id': xml_id,
                 'noupdate': noupdate}]
        self.env[model]._load_records(data, mode != 'init')
