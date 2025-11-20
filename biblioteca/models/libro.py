from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests

class BibliotecaLibro(models.Model):
    _name = 'biblioteca.libro'
    _description = 'Libro de la biblioteca'
    _rec_name = 'firstname'

    firstname = fields.Char(string='Nombre Libro')
    value = fields.Integer(string='Número de ejemplares', default=2)
    reservado = fields.Integer(string='Ejemplares reservados', default=0)  # CAMBIO AÑADIDO
    ejemplares_str = fields.Char(string='Ejemplares', compute='_compute_ejemplares_str', store=True) # CAMBIO AÑADIDO
    description = fields.Text(string='Resumen Libro')
    isbn = fields.Char(string='ISBN')

    @api.depends('value', 'reservado')
    def _compute_ejemplares_str(self):
        for record in self:
            disponibles = record.value - record.reservado
            if disponibles > 0:
                record.ejemplares_str = f"{disponibles}/{record.value}"
            else:
                record.ejemplares_str = "Fuera de stock"

    def reservar_libro(self):
        for record in self:
            disponibles = record.value - record.reservado
            if disponibles <= 0:
                raise ValidationError("No hay ejemplares disponibles para reservar")
            record.reservado += 1
            record._compute_ejemplares_str()
            codigo = self.env['ir.sequence'].next_by_code('biblioteca.reserva') or "RESERVA001"
            self.env['biblioteca.reserva'].create({
                'libro_id': record.id,
                'codigo': codigo,
                'nombre_libro': record.firstname,
                'descripcion_libro': record.description,
                'isbn_libro': record.isbn,
                'cantidad': 1,
                'ejemplares_str': record.ejemplares_str,
            })

    def buscar_libro_por_isbn(self):
        for record in self:
            if not record.isbn:
                raise ValidationError("Debe ingresar un ISBN para buscar")
            url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{record.isbn}&format=json&jscmd=data'
            response = requests.get(url)
            if response.status_code != 200:
                raise ValidationError("Error al conectar con OpenLibrary")
            data = response.json()
            key = f'ISBN:{record.isbn}'
            if key in data:
                book_data = data[key]
                record.firstname = book_data.get('title', '')
                publish_date = book_data.get('publish_date', '')
                record.description = f"Publicado en: {publish_date}"
            else:
                raise ValidationError("ISBN no encontrado en OpenLibrary")
