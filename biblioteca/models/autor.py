# -*- coding: utf-8 -*-
from odoo import models, fields, api

class BibliotecaAutor(models.Model):
    _name = 'biblioteca.autor'
    _description = 'Autor de libros'

    firstname = fields.Char()
    lastname = fields.Char()
    libros_autor = fields.Many2one('biblioteca.libro',
                                   relation="Libro_autor_real",
                                   column1="autor_id", column2="libro_id", string='Libros autor')

    @api.depends('firstname', 'lastname')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.firstname} {record.lastname}"
