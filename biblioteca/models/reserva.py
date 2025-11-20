from odoo import models, fields

class BibliotecaReserva(models.Model):
    _name = 'biblioteca.reserva'
    _description = 'Reserva de Libros'

    codigo = fields.Char(string='Código Reserva')
    libro_id = fields.Many2one('biblioteca.libro', string='Libro')
    nombre_libro = fields.Char(string='Nombre del Libro')
    descripcion_libro = fields.Text(string='Resumen')
    isbn_libro = fields.Char(string='ISBN')
    cantidad = fields.Integer(string='Cantidad')
    ejemplares_str = fields.Char(string='Ejemplares') # CAMBIO AÑADIDO para mostrar el estado
