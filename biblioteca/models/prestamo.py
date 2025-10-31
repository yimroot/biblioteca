from odoo import models, fields, api
from odoo.exceptions import UserError

class BibliotecaPrestamos(models.Model):
    _name = 'biblioteca.prestamo'
    _description = 'Préstamo de libros'

    name = fields.Char(string="Código de préstamo")
    fecha_prestamo = fields.Datetime(string='Fecha de préstamo')
    libro = fields.Many2one('biblioteca.libro', string='Título de libro')
    usuario = fields.Many2one('biblioteca.usuario', string='Usuario')
    fecha_devolucion = fields.Datetime()
    fecha_max = fields.Datetime(string='Fecha máxima de devolución')
    multa_bol = fields.Boolean(default=False)
    multa = fields.Float()
    motivo_multa = fields.Selection([
        ('atraso', 'Atraso'),
        ('danio', 'Daño'),
        ('perdida', 'Pérdida')
    ], string="Motivo de Multa")
    estado = fields.Selection([
    ('b', 'Borrador'),
    ('p', 'Prestado'),
    ('m', 'Multa'),
    ('d', 'Devuelto'),
], string='Estado', default='b')
    personal = fields.Many2one('res.users', string='Persona que prestó el libro',
                               default=lambda self: self.env.uid)

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            seq = self.env.ref('biblioteca.sequence_codigo_prestamos').next_by_code('biblioteca.prestamo')
            vals['name'] = seq
        if not vals.get('fecha_prestamo'):
            vals['fecha_prestamo'] = fields.Datetime.now()
        return super().create(vals)

    def generar_prestamo(self):
        for rec in self:
            if rec.estado != 'b':
                raise UserError('Solo se puede prestar si está en borrador.')
            if not rec.name:
                seq = self.env.ref('biblioteca.sequence_codigo_prestamos').next_by_code('biblioteca.prestamo')
                rec.name = seq
            if not rec.fecha_prestamo:
                rec.fecha_prestamo = fields.Datetime.now()
            if not rec.fecha_max:
                raise UserError('Debe definir la fecha máxima de devolución antes de prestar.')
            rec.write({'estado': 'p'})

    def generar_multa(self):
        for rec in self:
            if rec.estado != 'p':
                raise UserError('Solo puede multar préstamos en estado "prestado".')
            if not rec.motivo_multa:
                raise UserError('Debe seleccionar un motivo de multa antes de generar la multa.')
            motivo = rec.motivo_multa
            if motivo == 'atraso':
                monto = 10.0
            elif motivo == 'danio':
                monto = 100.0
            elif motivo == 'perdida':
                monto = 50.0
            else:
                monto = 0.0

            seq_multa = self.env.ref('biblioteca.sequence_codigo_multa').next_by_code('biblioteca.multa')
            multa = self.env['biblioteca.multa'].create({
                'codigo': seq_multa,
                'usuario': rec.usuario.id,
                'monto': monto,
                'motivo': motivo,
                'pago': 'pendiente',
                'prestamo_id': rec.id
            })
            rec.write({
                'estado': 'm',
                'multa_bol': True,
                'multa': monto,
                'motivo_multa': motivo
            })

    def devolver_libro(self):
        for rec in self:
            if rec.estado == 'd':
                raise UserError('El libro ya fue devuelto.')
            rec.write({'estado': 'd'})

