# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests

class BibliotecaLibro(models.Model):
    _name = 'biblioteca.libro'
    _description = 'Libro de la biblioteca'
    _rec_name = 'firstname'

    firstname = fields.Char(string='Nombre Libro')
    value = fields.Integer(string='Número de ejemplares')
    value2 = fields.Float(compute="_value_pc", store=True, string="Costo")
    autor = fields.Many2one('biblioteca.autor', string='Autor Libro')
    description = fields.Text(string='Resumen Libro')
    isbn = fields.Char(string='ISBN')

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

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
                authors = book_data.get('authors', [])
                if authors:
                    author_name = authors[0].get('name', '')
                    autor_obj = self.env['biblioteca.autor'].search([('firstname', '=', author_name)], limit=1)
                    if not autor_obj:
                        autor_obj = self.env['biblioteca.autor'].create({'firstname': author_name})
                    record.autor = autor_obj.id

                publish_date = book_data.get('publish_date', '')
                record.description = f"Publicado en: {publish_date}"
            else:
                raise ValidationError("ISBN no encontrado en OpenLibrary")
