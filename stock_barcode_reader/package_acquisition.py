# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from osv import osv,fields
from tools.translate import _
from report import report_sxw
from report_aeroo import report_aeroo
import datetime
from tools import misc

class stock_fill_inventory(osv.osv_memory):
    _inherit = "stock.fill.inventory"    
    def fill_inventory(self, cr, uid, ids, context=None):
        res = super(stock_fill_inventory, self).fill_inventory(cr, uid, ids, context=context)        
        stock_inventory_obj = self.pool.get('stock.inventory')
        fill_inventory = self.browse(cr, uid, ids[0], context=context)
        if stock_inventory_obj.browse(cr, uid, context.get('active_id', False), context).location_id:
            stock_inventory_obj.write(cr, uid, context.get('active_id', False), {'location_id': fill_inventory.location_id.id})
        return res    
stock_fill_inventory()

class acquisition_acquisition(osv.osv):
    
    _name = "acquisition.acquisition"    
    _order = 'id desc'
        
    _columns = {
        'state': fields.selection([('open', 'Open'),('done', 'Done'),], 'State', readonly=True),
        'name': fields.char('Name', size=128, required=True, readonly=True, states={'open':[('readonly',False)]}),
        'acquisition_ids': fields.one2many('acquisition.list','acquisition_id','Acquisition', readonly=True, states={'open':[('readonly',False)]}),
        'origin_id': fields.many2one('stock.location', 'Origin Location' , required=True, readonly=True, states={'open':[('readonly',False)]}),
        'type': fields.selection([
            ('order','Order Preparation'),
            ('pack','Pack Preparation'),
            ('inventory','Inventory Preparation'),
            ('move_stock','Move Stock'),
        ],'Type', size=128, readonly=True, states={'open':[('readonly',False)]}),
        'destination_id': fields.many2one('stock.location', 'Destination Location' , readonly=True, states={'open':[('readonly',False)]}),
        'address_id': fields.many2one('res.partner.address','Partner Address', readonly=True, states={'open':[('readonly',False)]}),
        'logistic_unit': fields.many2one('product.ul', 'Unit Size', readonly=True, states={'open':[('readonly',False)]}),
        'inventory_id': fields.many2one('stock.inventory', 'Inventory', readonly=True, states={'open':[('readonly',False)]}),
        'pack_id': fields.many2one('stock.tracking', 'Pack', readonly=True),
        'pack_name': fields.related('pack_id', 'name', type='char', string="Pack Name", size=64, readonly=True),
        'picking_id': fields.many2one('stock.picking', 'Picking', readonly=True),
        'picking_name': fields.related('picking_id', 'name', type='char', string="Picking Name", size=64, readonly=True),
        'move_stock_destination': fields.many2one('stock.location', 'Destination Location' , readonly=True, states={'open':[('readonly',False)]}),
        'move_stock_date': fields.datetime('Move Date', readonly=True, states={'open':[('readonly',False)]}),
    }
    _defaults = {
        'state': 'open',
        'type': 'pack',
        'name': lambda self,cr,uid,ctx={}: self.pool.get('ir.sequence').get(cr, uid, 'acquisition.acquisition'),
        'move_stock_date': lambda * a: datetime.datetime.now().strftime(misc.DEFAULT_SERVER_DATETIME_FORMAT),
    }
    
    def onchange_destination(self, cr, uid, ids, destination_id=False, context=None):
        res = {'value':{'address_id': False}}
        if destination_id:
            destination = self.pool.get('stock.location').browse(cr, uid, destination_id)
            if destination.address_id:
                res['value']['address_id'] = destination.address_id.id
        return res
    
    def onchange_inventory(self, cr, uid, ids, inventory_id=False, context=None):
        res = {'value':{'location_id': False}}
        if inventory_id:
            inventory = self.pool.get('stock.inventory').browse(cr, uid, inventory_id)
            if inventory.location_id:
                res['value']['origin_id'] = inventory.location_id.id
        return res
    
#    def print_pack_report(self, cr, uid, ids, context=None):
#        '''init'''
#        if context is None:
#            context = {}
#
#        '''process'''
#        data = self.pool.get('stock.tracking').read(cr, uid, ids)[0]
#        datas = {
#             'ids': ids,
#             'model': 'stock.tracking',
#             'form': data
#        }
#        '''print report'''
#        return {'type': 'ir.actions.report.xml',
#                'report_name': 'voltalis.tracking.barcode.report.aeroo',
#                'datas': datas
#                }

    def check_production_lot_location(self, cr, uid, origin_id, logistic_unit_id, context=None):
        result = {}
        stock_move_obj = self.pool.get('stock.move')
        stock_production_lot_data = self.pool.get('stock.production.lot').browse(cr, uid, logistic_unit_id)
        logistic_unit_number = stock_production_lot_data.id            
        product = stock_production_lot_data.product_id                    
        name_list = self.pool.get('product.product').name_get(cr, uid, [product.id], context)
        stock_production_lot_name = name_list[0][1]
        '''If the production lot is not in the current stock'''        
        '''We add a move form it position to the current stock'''
        if stock_production_lot_data.location_id:
            if stock_production_lot_data.location_id.id != origin_id:
                result = stock_move_obj.create(cr, uid, {'name': stock_production_lot_name,
                                                              'state': 'draft',
                                                              'product_id': product.id,
                                                              'product_uom': product.uom_id.id,
                                                              'prodlot_id': logistic_unit_number,
                                                              'location_id': stock_production_lot_data.location_id.id,
                                                              'location_dest_id': origin_id,
                                                })       
        return result
    
    def update_delivery_order_line(self, cr, uid, res_id=None, order_id=None, origin_id=None, destination_id=None, tracking_id=None, context=None):
        result = {}
        move_obj = self.pool.get('stock.move')
        production_lot_obj = self.pool.get('stock.production.lot')
        split_obj = self.pool.get('stock.move.split')
        split_line_obj = self.pool.get('stock.move.split.lines')
        production_lot = production_lot_obj.browse(cr, uid, res_id)
        product_id = production_lot.product_id and production_lot.product_id.id or False
        if product_id:
            move_ids = move_obj.search(cr, uid, [
                ('state', 'not in', ['cancel']),
                ('picking_id', '=', order_id),
                ('product_id', '=', product_id),
                ('prodlot_id', '=', False),
            ])
            if move_ids:
                """ The move can be split """
                vals = {}
                split_context = context
                split_context.update({'active_id': move_ids[0], 'active_ids': [move_ids[0]], 'active_model': 'stock.move', 'tracking_id': tracking_id})
                split_id = split_obj.create(cr, uid, vals, split_context)
                split_line_obj.create(cr, uid, {'prodlot_id': res_id, 'wizard_exist_id': split_id, 'quantity':1})
                split_obj.split_lot(cr, uid, [split_id], split_context)
            else:
                """ There are no move """
                product = production_lot.product_id       
                name_list = self.pool.get('product.product').name_get(cr, uid, [product_id], context)                    
                stock_production_lot_name = name_list[0][1]
                move_id = move_obj.create(cr, uid, {
                                              'name': stock_production_lot_name,
                                              'product_id': product_id,
                                              'product_uom': product.uom_id.id,
                                              'prodlot_id': res_id,
                                              'location_id': origin_id,
                                              'location_dest_id': destination_id,
                                              'picking_id': order_id,
                                              'tracking_id': tracking_id,
                                            })
        return result
    
    def process(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        res = {}
        acquisition_data = self.browse(cr, uid, ids, context)
        for acquisition in acquisition_data:
            if acquisition.type == 'order':
                if acquisition.picking_id:
                    self.order_preparation(cr, uid, acquisition, context)
                else:
                    self.order_creation(cr, uid, acquisition, context)
            elif acquisition.type == 'pack':
                self.pack_preparation(cr, uid, acquisition, context)
            elif acquisition.type == 'inventory':
                self.inventory_preparation(cr, uid, acquisition, context)
            elif acquisition.type == 'move_stock':
                self.move_stock_preparation(cr, uid, acquisition, context)
            self.write(cr, uid, acquisition.id, {'state': 'done'}, context=context)
        return res
    
    """
    ### DELIVERY ORDER PREPARATION ###
    """
    def order_preparation(self, cr, uid, acquisition, context=None):
        res = {}
        if context==None:
            context = {}
        first_code = True
        parent_id = None
        for line in acquisition.acquisition_ids:
            if first_code == True:
                first_code = False
                self.update_order(cr, uid, acquisition, context)
            parent_id = self.update_stock_move(cr, uid, line, parent_id, context)
        return res
    
    '''Updating the order'''
    def update_order(self, cr, uid, acquisition, context=None):
        if context == None:
            context = {} 
        stock_picking_obj = self.pool.get('stock.picking')
        address_id = acquisition.address_id.id
        picking_id = acquisition.picking_id.id
        stock_picking_obj.write(cr, uid, picking_id, {'address_id': address_id, 'type': 'out'})
        return picking_id
    
    '''Split moves of the order into different production lot / tracking packs'''
    def update_stock_move(self, cr, uid, line, parent_id=None, context=None):
        stock_tracking_obj = self.pool.get('stock.tracking')
        history_obj = self.pool.get('stock.tracking.history') 
        setting_obj = self.pool.get('acquisition.setting')       
        if context == None:
            context = {}
        barcode = line.barcode_id
        res_model = barcode.res_model
        res_id = barcode.res_id
        order_id = line.acquisition_id and line.acquisition_id.picking_id and line.acquisition_id.picking_id.id or False
        
        acquisition_data = self.browse(cr, uid, line.acquisition_id.id)
        origin_id = acquisition_data.origin_id.id    
        destination_id = acquisition_data.destination_id.id
        
        """ If a barcode creation pack is detected """
        acquisition_setting_ids = setting_obj.search(cr, uid, [('barcode_id','=',barcode.id)], limit=1)
        if acquisition_setting_ids:
            acquisition_setting_id = acquisition_setting_ids[0]
            acquisition_setting_data = setting_obj.browse(cr, uid, acquisition_setting_id, context)
            if acquisition_setting_data.action_type == 'create_pack':     
                logistic_unit = self.pool.get('product.ul').search(cr, uid, [('type','=','pack')], limit=1)[0]
                parent_id = setting_obj.create_pack(cr, uid, [line.acquisition_id.id], logistic_unit, context)
                return parent_id           
            elif parent_id and acquisition_setting_data.action_type == 'close_pack':
                setting_obj.close_pack(cr, uid, [parent_id], context)
                parent_id = None
        if parent_id:
            setting_obj.add_child(cr, uid, barcode.id, parent_id, context) 
        
        if res_model == 'stock.production.lot':
            """ Check of production lot creation """
            new_move_id = self.check_production_lot_location(cr, uid, origin_id, res_id, context) 
            """ Split in production lot """
            self.update_delivery_order_line(cr, uid, res_id, order_id, origin_id, destination_id, parent_id, context)  
                      
        elif res_model == 'stock.tracking':
            stock_tracking_data = stock_tracking_obj.browse(cr, uid, res_id)   
            pack_list = {}
            pack_number = 1            
            """ Check if current pack is available """
            if stock_tracking_data.parent_id:
                raise osv.except_osv(_('Warning!'),_('You cannot move this pack because it\'s inside of an other pack: %s.') % (stock_tracking_data.parent_id.name))
            for child in stock_tracking_data.child_ids:
                if child.state != 'close':
                    raise osv.except_osv(_('Warning!'),_('You cannot move this pack because there is a none closed pack inside of it: %s.') % (child.name))   
            child_packs = stock_tracking_obj.hierarchy_ids(stock_tracking_data)
            for child_pack in child_packs:
                '''historic creation'''
                hist_id = history_obj.create(cr, uid, {
                                                       'tracking_id': child_pack.id,
                                                       'type': 'move',
                                                       'location_id': child_pack.location_id.id,
                                                       'location_dest_id': destination_id,
                                                       })
                for move_data in child_pack.move_ids:
                    """ Split in production lot """
                    self.update_delivery_order_line(cr, uid, move_data.prodlot_id.id, order_id, origin_id, destination_id, res_id, context)
                            
        return parent_id
    
    """
    ### DELIVERY ORDER CREATION ###
    """
    def order_creation(self, cr, uid, acquisition, context=None):
        res = {}
        if context==None:
            context = {}
        first_code = True
        acquisition_obj = self.pool.get('acquisition.acquisition')
        setting_obj = self.pool.get('acquisition.setting')
        for line in acquisition.acquisition_ids:
            if first_code == True:
                first_code = False
                order_id = self.create_order(cr, uid, [acquisition.id], context)
                acquisition_obj.write(cr, uid, acquisition.id, {'picking_id': order_id})
            if line.type == 'object':
                self.add_stock_move(cr, uid, [acquisition.id], line.barcode_id, order_id, context)
            else:
                tracking_id = setting_obj.do_action(cr, uid, [acquisition.id], line.type, context)
                context['tracking_id'] = tracking_id
        return res
    
    ''' Picking Creation '''
    def create_order(self, cr, uid, ids, context=None):
        '''init'''
        if context == None:
            context = {}
        acquisition_obj = self.pool.get('acquisition.acquisition')
        acquisition_data = acquisition_obj.browse(cr, uid, ids[0])  
        stock_picking_obj = self.pool.get('stock.picking')
        '''variables'''
        address_id = acquisition_data.address_id.id
        ''''order creation'''
        order_id = stock_picking_obj.create(cr, uid, {'address_id': address_id, 'type': 'out'})
        '''End'''   
        return order_id
    
    ''' Adding move in a picking '''
    def add_stock_move(self, cr, uid, ids, barcode_data, order_id, context=None):
        '''init'''
        res = {}
        if context == None:
            context = {}
        barcode_obj = self.pool.get('tr.barcode')
        stock_move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        stock_tracking_obj = self.pool.get('stock.tracking')
        history_obj = self.pool.get('stock.tracking.history')
        acquisition_obj = self.pool.get('acquisition.acquisition')
        stock_production_lot_obj = self.pool.get('stock.production.lot')        
        
        acquisition_data = acquisition_obj.browse(cr, uid, ids[0])  
        
        '''process'''        
        origin_id = acquisition_data.origin_id.id    
        destination_id = acquisition_data.destination_id.id
        logistic_unit_id = barcode_data.res_id
        tracking_id = context.get('tracking_id', False)
        if barcode_data.res_model == 'stock.production.lot':            
            stock_production_lot_data = stock_production_lot_obj.browse(cr, uid, logistic_unit_id)
            logistic_unit_number = stock_production_lot_data.id            
            product = stock_production_lot_data.product_id                    
            name_list = self.pool.get('product.product').name_get(cr, uid, [product.id], context)
            stock_production_lot_name = name_list[0][1]
            '''If the production lot is not in the current stock'''
            new_move_id = self.check_production_lot_location(cr, uid, origin_id, logistic_unit_id, context)            
            ''''stock move creation'''
            move_id = stock_move_obj.create(cr, uid, {
                                                  'name': stock_production_lot_name,
                                                  'product_id': product.id,
                                                  'product_uom': product.uom_id.id,
                                                  'prodlot_id': logistic_unit_number,
                                                  'location_id': origin_id,
                                                  'location_dest_id': destination_id,
                                                  'picking_id': order_id,
                                                  'move_ori_id': new_move_id,
                                                  'tracking_id' : tracking_id,
                                                })
        elif barcode_data.res_model == 'product.product':
            product_data = product_obj.browse(cr, uid, logistic_unit_id)
            move_id = stock_move_obj.create(cr, uid, {
                                                  'name': product_data.name,
                                                  'product_id': product_data.id,
                                                  'product_uom': product_data.uom_id.id,
                                                  'location_id': origin_id,
                                                  'location_dest_id': destination_id,
                                                  'picking_id': order_id,
                                                  'tracking_id' : tracking_id,
                                                })
        elif barcode_data.res_model == 'stock.tracking':
            stock_tracking_data = stock_tracking_obj.browse(cr, uid, logistic_unit_id)                                          
            if stock_tracking_data.parent_id:
                raise osv.except_osv(_('Warning!'),_('You cannot move this pack because it\'s inside of an other pack: %s.') % (stock_tracking_data.parent_id.name))
            for child in stock_tracking_data.child_ids:
                if child.state != 'close':
                    raise osv.except_osv(_('Warning!'),_('You cannot move this pack because there is a none closed pack inside of it: %s.') % (child.name))
                
            for move_data in stock_tracking_data.move_ids:
                if move_data.location_dest_id.id != origin_id:
                    new_move_id = stock_move_obj.create(cr, uid, {
                                                              'name': move_data.name,
                                                              'state': 'draft',
                                                              'product_id': move_data.product_id.id,
                                                              'product_uom': move_data.product_uom.id,
                                                              'prodlot_id': move_data.prodlot_id.id,
                                                              'location_id': move_data.location_dest_id.id,
                                                              'location_dest_id': origin_id,
                                                        })    
                
            child_packs = stock_tracking_obj.hierarchy_ids(stock_tracking_data)
            for child_pack in child_packs:
                '''historic creation'''
                hist_id = history_obj.create(cr, uid, {
                                               'tracking_id': child_pack.id,
                                               'type': 'move',
                                               'location_id': child_pack.location_id.id,
                                               'location_dest_id': destination_id,
                                           })
                for move_data in child_pack.move_ids:
                    if move_data.location_dest_id.id != origin_id:
                        new_move_id = stock_move_obj.create(cr, uid, {'name': move_data.name,
                                                                'state': 'draft',
                                                                'product_id': move_data.product_id.id,
                                                                'product_uom': move_data.product_uom.id,
                                                                'prodlot_id': move_data.prodlot_id.id,
                                                                'location_id': move_data.location_dest_id.id,
                                                                'location_dest_id': origin_id,
                                                                })                
                '''new move creation'''
                for move in child_pack.current_move_ids:
                    defaults = {
                        'location_id': origin_id,
                        'location_dest_id': destination_id,
                        'picking_id': order_id
                    }
                    new_id = stock_move_obj.copy(cr, uid, move.id, default=defaults, context=context)
                    stock_move_obj.write(cr, uid, [move.id], {'pack_history_id': hist_id, 'move_dest_id': new_id})
                    
                stock_tracking_obj.write(cr, uid, [child_pack.id], {'location_id': destination_id})
        '''End'''
        return res
    
    """
    ### PACK PREPARATION ###
    """
    def pack_preparation(self, cr, uid, acquisition, context=None):
        res = {}
        if context==None:
            context = {}
        first_code = True
        parent_id = False
        setting_obj = self.pool.get('acquisition.setting')
        for line in acquisition.acquisition_ids:
            if first_code == True:
                first_code = False
                logistic_unit = acquisition.logistic_unit.id
                parent_id = setting_obj.create_pack(cr, uid, [acquisition.id], logistic_unit, context)
                self.write(cr, uid, acquisition.id, {'pack_id': parent_id})
            setting_obj.add_child(cr, uid, line.barcode_id.id, parent_id, context)
        if parent_id:
            setting_obj.close_pack(cr, uid, [parent_id], context)
        return res
    
    """
    ### INVENTORY ###
    """
    def inventory_preparation(self, cr, uid, acquisition, context=None):
        res = {}
        if context==None:
            context = {}
        inventory_id = acquisition.inventory_id or False
        if not inventory_id:
            raise osv.except_osv(_('Warning!'),_('There is no inventory, please create one!'))
        if inventory_id.state != 'draft':
            raise osv.except_osv(_('Warning!'),_('This inventory is not in draft state, you can\'t continue !'))
        location_id = acquisition.origin_id or False
        if not location_id:
            raise osv.except_osv(_('Warning!'),_('There is no location defined, please select one!'))
        for line in acquisition.acquisition_ids:
            self.check_inventory_line(cr, uid, line, context)
        return res
    
    def check_inventory_line(self, cr, uid, line, context=None):
        if context == None:
            context = {}
        acquisition = line.acquisition_id
        barcode = line.barcode_id
        production_lot_obj = self.pool.get('stock.production.lot')
        inventory_line_obj = self.pool.get('stock.inventory.line')
        product_obj = self.pool.get('product.product')
        inventory_id = acquisition.inventory_id and acquisition.inventory_id.id or False
        location_id = acquisition.origin_id and acquisition.origin_id.id or False
        logistic_unit_id = barcode.res_id
        
        if barcode.res_model == 'stock.production.lot':
            """ Production Lot Case """
            """ TODO What if the production lot is in a tracking ? """
            production_lot = production_lot_obj.browse(cr, uid, logistic_unit_id)
            product = production_lot.product_id
            lot_id = production_lot.id
            vals = {
                'inventory_id': inventory_id,     
                'location_id': location_id,
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'product_qty': 1,
                'prod_lot_id': lot_id,
            }
            line_ids = inventory_line_obj.search(cr, uid, [('inventory_id', '=', inventory_id), ('product_id', '=', product.id), ('prod_lot_id', '=', lot_id)])
            if line_ids:
                inventory_line_obj.write(cr, uid, [line_ids[0]], vals)
            else:
                inventory_line_obj.create(cr, uid, vals)
                    
        elif barcode.res_model == 'product.product':
            """ Product Case """
            product = product_obj.browse(cr, uid, logistic_unit_id)
            vals = {
                'inventory_id': inventory_id,               
                'location_id': location_id,
                'product_id': product.id,
                'product_uom': product.uom_id.id,
            }
            line_ids = inventory_line_obj.search(cr, uid, [('inventory_id', '=', inventory_id), ('product_id', '=', product.id), ('location_id', '=', location_id)])
            if line_ids:
                qty = inventory_line_obj.read(cr, uid, line_ids[0], ['product_qty'])['product_qty']
                vals_update = vals
                vals_update.update({'product_qty': qty >= 0 and qty + line.quantity or line.quantity})
                inventory_line_obj.write(cr, uid, [line_ids[0]], vals_update)
            else:
                vals_create = vals
                vals_create.update({'product_qty': line.quantity})
                inventory_line_obj.create(cr, uid, vals_create)
    
    """
    ### MOVE STOCK CREATION ###
    """
    def move_stock_preparation(self, cr, uid, acquisition, context=None):
        res = {}
        if context==None:
            context = {}
        first_code = True
        move_stock_id = False
        for line in acquisition.acquisition_ids:
            if first_code == True:
                first_code = False
                move_stock_id = self.create_move_stock(cr, uid, [acquisition.id], context) 
            self.add_stock_move_line(cr, uid, [acquisition.id], line.barcode_id.id, move_stock_id, context) 
        return res
    
    def create_move_stock(self, cr, uid, ids, context=None):
        '''init'''
        if context == None:
            context = {}
        acquisition_data = self.browse(cr, uid, ids[0])
        stock_inventory_obj = self.pool.get('stock.inventory')      
        
        '''variables'''       
        origin_id = acquisition_data.origin_id.id    
        destination_id = acquisition_data.move_stock_destination.id      
        date = acquisition_data.move_stock_date
        ''''inventory creation'''
        context.update({'type':'move'})
        move_stock_id = stock_inventory_obj.create(cr, uid, {
                    'type': 'move',
                    'date_done': date,
                    'location_id': origin_id,
                    'location_dest_id': destination_id,
                }, context=context)
        '''End'''
        return move_stock_id
    
    def add_stock_move_line(self, cr, uid, ids, barcode_id, inventory_id, inventory_line_id, context=None):
        res = {} 
        '''init'''        
        if context == None:
            context = {}
        barcode_obj = self.pool.get('tr.barcode')  
        stock_production_lot_obj = self.pool.get('stock.production.lot')  
        inventory_line_obj = self.pool.get('stock.inventory.line')     
        stock_tracking_obj = self.pool.get('stock.tracking')   
        product_obj = self.pool.get('product.product') 
        barcode_data = barcode_obj.browse(cr, uid, barcode_id, context=context)
        acquisition_data = self.browse(cr, uid, ids[0], context=context) 
         
        location_id = acquisition_data.origin_id.id
        logistic_unit_id = barcode_data.res_id
        if barcode_data.res_model == 'stock.production.lot':       
            stock_production_lot_data = stock_production_lot_obj.browse(cr, uid, logistic_unit_id, context=context)
            product = stock_production_lot_data.product_id
            logistic_unit_number = stock_production_lot_data.id 
            vals = {
                    'inventory_id': inventory_id,                    
                    'location_id': location_id,
                    'product_id': product.id,
                    'product_uom': product.uom_id.id,
                    'product_qty': 1,
                    'prod_lot_id':logistic_unit_number}     
            inventory_line_obj.create(cr, uid, vals)
        elif barcode_data.res_model == 'product.product':
            product_data = product_obj.browse(cr, uid, logistic_unit_id)
            vals = {
                    'inventory_id': inventory_id,               
                    'location_id': location_id,
                    'product_id': product_data.id,
                    'product_uom': product_data.uom_id.id,
                    'product_qty': 1}        
            inventory_line_obj.create(cr, uid, vals)            
        elif barcode_data.res_model == 'stock.tracking':
            stock_tracking_data = stock_tracking_obj.browse(cr, uid, logistic_unit_id)
            if stock_tracking_data.parent_id:
                raise osv.except_osv(_('Warning!'),_('You cannot move this pack because it\'s inside of an other pack: %s.') % (stock_tracking_data.parent_id.name))
            for child in stock_tracking_data.child_ids:
                if child.state != 'close':
                    raise osv.except_osv(_('Warning!'),_('You cannot move this pack because there is a none closed pack inside of it: %s.') % (child.name))            
            
            raise osv.except_osv(_('Warning!'),_('Not developed yet'))
                                 
        return res
    
acquisition_acquisition()

class acquisition_list(osv.osv):    
    
    _name = "acquisition.list"
    _columns = {
        'name': fields.char('List Name', size=128),
        'barcode_id': fields.many2one('tr.barcode', 'Barcode', readonly=True),
        'acquisition_id': fields.many2one('acquisition.acquisition','Acquisition'),
        'type': fields.selection([
            ('object','Logistic Unit'),
            ('create_add', 'Create a pack and add a logistic unit'),
            ('create_pack','Create a pack'), 
            ('add_child','Add a logistic unit'), 
            ('close_pack','Close a pack'),
        ], 'Action Type', size=32),
        'quantity': fields.float('Quantity'),
     }
    
    _defaults = {
        'quantity': 1,
    }
    
    def on_change_quantity(self, cr, uid, ids, quantity=1, barcode_id=False, context=None):
        res = {'value': {'quantity': 1}}
        if context == None:
            context = {}
        if barcode_id:
            if self.pool.get('tr.barcode').browse(cr, uid, barcode_id).res_model == 'product.product':
                res = {'value': {'quantity' : quantity}}
        return res
    
    def _check_quantity(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.quantity != 1 and record.barcode_id.res_model!='product.product':
                return False
        return True
    
    _constraints = [
        (_check_quantity,
        'You assigned a wrong quantity for this line',
        ['name']),
    ]
    
acquisition_list()

class acquisition_setting(osv.osv):
    
    _name = "acquisition.setting"
    _columns = {
        'barcode_id': fields.many2one('tr.barcode', 'Barcode', required=True, readonly=False),
        'action_type': fields.selection([
            ('create_add', 'Create a pack and add a logistic unit'),
            ('create_pack','Create a pack'),
            ('add_child','Add a logistic unit'),
            ('close_pack','Close a pack'),
        ], 'Action Type', size=32, required=True, help="Selection of an action"),           
    }
    
#    def create_add(self, cr, uid, ids, ul_id, context=None):
#        if context == None:
#            context = {}
#        tracking_id = self.create_pack(cr, uid, ids, ul_id, context)
#        return tracking_id

    def do_action(self, cr, uid, ids, action_type, context=None):
        if context == None:
            context = {}
        tracking_id = False
        if action_type == 'create_add':
            tracking_id = self.create_pack(cr, uid, ids, context=context)
        elif action_type == 'close_pack':
            tracking_to_close_id = context.get('tracking_id', False)
            if tracking_to_close_id:
                self.close_pack(cr, uid, [tracking_to_close_id], context=context)
        return tracking_id
    
    '''Function for pack creation'''    
    def create_pack(self, cr, uid, ids, ul_id=None, context=None):        
        '''Init'''
        res = {}
        stock_tracking_obj = self.pool.get('stock.tracking')
        if context == None:
            context = {}
        '''Location determination'''
        acquisition_data = self.pool.get('acquisition.acquisition').browse(cr, uid, ids[0])
        location_id = acquisition_data.origin_id.id
        if ul_id == None:
            ul_id = self.pool.get('product.ul').search(cr, uid, [], limit=1)[0]
        logistic_unit = ul_id
        '''Pack Creation'''
        tracking_id = stock_tracking_obj.create(cr, uid, {'ul_id': logistic_unit, 'location_id': location_id})        
        '''Pack name is returned'''
        return tracking_id
    
    def add_child(self, cr, uid, barcode_id, parent_id, context=None):
        '''Init'''
        res = {}
        barcode_obj = self.pool.get('tr.barcode')
        tracking_obj = self.pool.get('stock.tracking')               
        if context == None:
            context = {}                        
        '''Get barcode number'''        
        barcode_data = barcode_obj.browse(cr, uid, barcode_id)
        barcode_code = barcode_data.code  
        ''' Call of adding function '''
        tracking_obj.add_validation(cr, uid, [parent_id], [barcode_id], context=None) 
        return res
    
    def close_pack(self, cr, uid, ids, context=None):
        '''init'''
        if context == None:
            context = {}
        tracking_obj = self.pool.get('stock.tracking')     
        '''Call of the function in stock_tracking_reopen'''
        tracking_obj.set_close(cr, uid, ids, context)
        '''Call of the function in stock_tracking_reopen'''
        if self.pool.get('acquisition.acquisition').browse(cr, uid, context.get('current_id'), context).picking_id:
            origin_id = self.pool.get('acquisition.acquisition').browse(cr, uid, context.get('current_id'), context).origin_id.id
            destination_id = self.pool.get('acquisition.acquisition').browse(cr, uid, context.get('current_id'), context).destination_id.id
            stock_move_ids = self.pool.get('stock.move').search(cr, uid, [('tracking_id','=',ids[0])])
            for stock_move_id in stock_move_ids:
                stock_move_data = self.pool.get('stock.move').browse(cr, uid, stock_move_id, context)
                self.pool.get('stock.move').write(cr, uid, stock_move_id, {'state':'done', 'picking_id': False, 'location_dest_id': origin_id}, context)
                self.pool.get('stock.move').create(cr, uid, {'name': stock_move_data.name,
                                                             'state': 'draft',
                                                             'product_id': stock_move_data.product_id.id,
                                                             'product_uom': stock_move_data.product_uom.id,
                                                             'prodlot_id': stock_move_data.prodlot_id.id,
                                                             'tracking_id': stock_move_data.tracking_id.id,
                                                             'picking_id': self.pool.get('acquisition.acquisition').browse(cr, uid, context.get('current_id'), context).picking_id.id,
                                                             'location_id': stock_move_data.location_dest_id.id,
                                                             'location_dest_id': destination_id,
                                                             })
        '''Call for a function who will display serial code list and product list in the pack layout'''                                                
        tracking_obj.get_products(cr, uid, ids, context=None)
        tracking_obj.get_serials(cr, uid, ids, context=None)
        return True
       

        
#    def create_inventory(self, cr, uid, ids, context=None):
#        '''init'''
#        if context == None:
#            context = {}
#        acquisition_obj = self.pool.get('acquisition.acquisition')
#        acquisition_data = acquisition_obj.browse(cr, uid, ids[0])
#        stock_inventory_obj = self.pool.get('stock.inventory')
#        '''variables'''
#        date = acquisition_data.inventory_date
#        ''''inventory creation'''
#        inventory_id = stock_inventory_obj.create(cr, uid, {'date_done': date})
#        '''End'''
#        return inventory_id
    

                
#            for line in inventory_data.inventory_line_id:                
#                if line.product_id.id == product_data.id:
#                    in_inventory = True
#                    inventory_line_obj.write(cr, uid, [line.id], {'product_qty': 1})                    
#                elif in_inventory == False:
#                    in_inventory = True
#                    vals = {
#                            'inventory_id': inventory_data.id,               
#                            'location_id': location_id,
#                            'product_id': product_data.id,
#                            'product_uom': product_data.uom_id.id,
#                            'product_qty': 1}        
#                    inventory_line_obj.create(cr, uid, vals)
            

    
acquisition_setting()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: