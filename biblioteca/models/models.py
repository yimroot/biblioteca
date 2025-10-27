# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta 
import requests


class biblioteca(models.Model):
    _name = 'biblioteca.libro'
    _description = 'biblioteca.biblioteca'
    _rec_name = 'firstname'

    firstname = fields.Char(string='Nombre Libro')
    value = fields.Integer(string='Numero ejemplares')
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


class BiliotecaAutor(models.Model):
   _name = 'biblioteca.autor'
   _description = 'biblioteca.autor'

   firstname = fields.Char()
   lastname = fields.Char()
   libros_autor = fields.Many2one('biblioteca.libro',
                                 relation="Libro_autor_real",
                                 column1="autor_id", colum_2="libro_id", string='Libros autor ')

   @api.depends('firstname', 'lastname')
   def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.firstname} {record.lastname}"


class BibliotecaUsuario(models.Model):
    _name = 'biblioteca.usuario'
    _description = 'biblioteca.usuario'

    firstname = fields.Char()
    lastname = fields.Char()
    email = fields.Char()
    telefono = fields.Char()
    cedula = fields.Char(string="Cédula", size=10)

    @api.constrains('cedula')
    def _check_cedula(self):
        for record in self:
            if record.cedula:
                # Validar que sea solo dígitos y longitud 10
                if len(record.cedula) != 10 or not record.cedula.isdigit():
                    raise ValidationError("La cédula debe tener exactamente 10 números.")


class BibliotecaMulta(models.Model):
   _name = 'biblioteca.multa'
   _description = 'biblioteca.multa'
   codigo = fields.Char(string='Codigo de multa')
   usuario = fields.Many2one('biblioteca.usuario', string='Usuario')
   monto = fields.Float(string='Monto a pagar')
   motivo = fields.Selection(selection=[('retraso', 'Retraso'),
                                       ('daño', 'Daño'),
                                       ('perdida', 'Perdida')], string='Causa de la multa')
   pago = fields.Selection(selection=[('pendiente', 'Pendiente'),
                                     ('saldada', 'Saldada')], string='Pago de la multa')


class BibliotecaPrestamos(models.Model):
    _name = 'biblioteca.prestamo'
    _description = 'biblioteca.prestamo'
    _rec_name = 'fecha_max'

    name = fields.Char(required=True)
    fecha_prestamo = fields.Datetime(default=datetime.now(), string='Fecha de prestamo')
    libro = fields.Many2one('biblioteca.libro', string='Titulo de libro')
    usuario = fields.Many2one('biblioteca.usuario', string='Usuario')
    fecha_devolucion = fields.Datetime()
    multa_bol = fields.Boolean(default=False)
    multa = fields.Float()
    estado = fields.Selection([('b', 'Borrador'), ('p', 'Prestado'), ('m', 'Multa'), ('d', 'Devuelvo')],
                             string='Estado', default='b')
    personal = fields.Many2one('res.users', string='Persona que presto el libro',
                               default=lambda self: self.env.uid)
    fecha_max = fields.Datetime(compute='_compute_fecha_devo', string='Fecha Maxima de devolucion')

    def write(self, vals):
        seq = self.env.ref('biblioteca.sequence_codigo_prestamos').next_by_code('biblioteca.prestamo')
        vals['name'] = seq
        return super(BibliotecaPrestamos, self).write(vals)

    def generar_prestamo(self):
        print("Generando prestamo")
        self.write({'estado': 'p'})

    @api.depends('fecha_max', 'fecha_prestamo')
    def _compute_fecha_devo(self):
        for record in self:
            record.fecha_max = record.fecha_prestamo + timedelta(days=2)

   