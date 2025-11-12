from odoo import models, fields
from odoo.exceptions import UserError

class BibliotecaMulta(models.Model):
    _name = 'biblioteca.multa'
    _description = 'Multa de la biblioteca'

    codigo = fields.Char(string='Código de multa')
    usuario = fields.Many2one('biblioteca.usuario', string='Usuario')
    monto = fields.Float(string='Monto a pagar')
    
    motivo = fields.Selection([
        ('atraso', 'Atraso'),
        ('danio', 'Daño'),
        ('perdida', 'Pérdida')
    ], string='Causa de la multa')
    pago = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('saldada', 'Saldada')
    ], string='Pago de la multa', default='pendiente')
    prestamo_id = fields.Many2one('biblioteca.prestamo', string='Préstamo')
    
    def pagar_multa(self):
        for multa in self:
            if multa.pago == 'saldada':
                raise UserError("Esta multa ya ha sido saldada anteriormente.")
            
            # 1. Cambiar el estado de la multa a 'saldada'
            multa.write({'pago': 'saldada'})
            
            # 2. Actualizar el estado del préstamo relacionado a 'pg' (Pagado)
            if multa.prestamo_id:
                multa.prestamo_id.write({'estado': 'pg'})
            
       
    
        
