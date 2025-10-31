# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BibliotecaUsuario(models.Model):
    _name = 'biblioteca.usuario'
    _description = 'Usuario de la biblioteca'

    firstname = fields.Char()
    lastname = fields.Char()
    email = fields.Char()
    telefono = fields.Char()
    cedula = fields.Char(string="Cédula", size=10)

    @api.constrains('cedula')
    def _check_cedula(self):
        for record in self:
            if record.cedula:
                if len(record.cedula) != 10 or not record.cedula.isdigit():
                    raise ValidationError("La cédula debe tener exactamente 10 números.")
