# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class ImprestRetirement(models.Model):
    _name = 'imprest.retirement'
    _description = 'Imprest Retirement'
    _order = 'name desc'
    _inherit = 'mail.thread'

    name = fields.Char(string='Payment Requisition', copy=False, default=lambda self: ('New'), readonly=True)
    imprest_ref = fields.Char(string='Imprest Application #')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    retirement_applicant_id = fields.Char(string='Applicant', required=True)
    retirement_activity = fields.Char(string='Activity')
    retirement_project = fields.Char(string='Project')
    retirement_purpose = fields.Text(string='Purpose')
    date = fields.Date(string='Date', default=datetime.today())
    imprest_amount = fields.Float(string='Imprest Amount')
    imprest_retirement_line_ids = fields.One2many('imprest.retirement.lines', 'imprest_retirement_id',
                                                  string='Imprest Lines')
    amount_advanced = fields.Float(string='Amount Advanced')
    total_amount_spent = fields.Float(string='Amount Spent', compute='_compute_amount_spent')
    retirement_balance = fields.Float(string='Balance', compute='_compute_balance')
    comment = fields.Text(string='Comment')


    #it4business_dms_file_id = fields.Many2one('it4business_dms.file', string="Document", store=True, default=lambda self: self.env['it4business_dms.file'].search([('user_id', '=', self.env.uid)]))
    state = fields.Selection([
        ('draft', "Draft"),
        ('submitted', "Submitted"),
        ('authorized', "Authorized"),
        ('certified', "Certified"),
        ('approved', "Approved"),
        ('rejected', "Rejected")], default='draft', track_visibility='onchange')
    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id)
    authorizer_id = fields.Many2one('res.users', string='To Authorise')
    certifier_id = fields.Many2one('res.users', string='To Certify')
    approver_id = fields.Many2one('res.users', string='To Approve')
    is_authorizer = fields.Boolean(string='Is Authorizer', compute='_is_authorizer', default=False)
    is_certifier = fields.Boolean(string='Is Certifier', compute='_is_certifier', default=False)
    is_approver = fields.Boolean(string='Is Approver', compute='_is_approver', default=False)
    authorized_by = fields.Many2one('hr.employee', string='Authorized By')
    certified_by = fields.Many2one('hr.employee', string='Certified By')
    approved_by = fields.Many2one('hr.employee', string='Approved By')
    date_authorized = fields.Datetime(string='Date Authorized')
    date_certified = fields.Datetime(string='Date Certified')
    date_approved = fields.Datetime(string='Date Approved')
    created_by_id = fields.Many2one('hr.employee', readonly=True, string='Created by',
                                    default=lambda self: self.env['hr.employee'].search(
                                        [('user_id', '=', self.env.uid)], limit=1))

    # Determine if logged-in user is the one to authorize
    @api.depends('current_user')
    def _is_authorizer(self):
        if self.env.user.id == self.authorizer_id.id:
            self.is_authorizer = True
        else:
            self.is_authorizer = False

    # Determine if logged in user is the one to certify
    @api.depends('current_user')
    def _is_certifier(self):
        if self.env.user.id == self.certifier_id.id:
            self.is_certifier = True
        else:
            self.is_certifier = False

    # Determine if logged in user is the one to approve
    @api.depends('current_user')
    def _is_approver(self):
        if self.env.user.id == self.approver_id.id:
            self.is_approver = True
        else:
            self.is_approver = False

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('imprest.retirement') or ('New')
            return super(ImprestRetirement, self).create(vals)

    @api.depends('imprest_retirement_line_ids')
    def _compute_amount_spent(self):
        for retirement in self:
            total = 0.0
            for line in retirement.imprest_retirement_line_ids:
                total += line.amount_spent
            retirement.total_amount_spent = total

    @api.depends('imprest_retirement_line_ids')
    def _compute_balance(self):
        for retirement in self:
            total = 0.0
            for line in retirement.imprest_retirement_line_ids:
                total += line.balance
            retirement.retirement_balance = total
    


    # def get_file(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'it4business_dms_file_id',
    #         'view_mode': 'tree',
    #         'res_model': 'it4business_dms.file',
    #         'domain': [('id', '=', self.it4business_dms_file_id.id)],
    #         'context': "{'create': True}"
    #     }
        
    def action_draft(self):
        self.write({'state': 'draft'})

    def action_submitted(self):
        self.write({'state': 'submitted'})
        for retirements in self:
            if not retirements.imprest_retirement_line_ids:
                raise UserError('Retirement details are missing. Please fill the details before submitting!')
            if not retirements.authorizer_id:
                raise UserError('Include name of Person to authorize the Retirement')
            if not retirements.certifier_id:
                raise UserError('Include name of Person to Certify the Retirement')
            if not retirements.approver_id:
                raise UserError('Include name of Person to Approve the Retirement')

    def action_authorized(self):
        authorizer = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.env.user.id != self.authorizer_id.id:
            raise UserError('Only %s can Authorize or Reject this Application!' % self.authorizer_id.name)
        self.write({'state': 'authorized', 'authorized_by': authorizer})
        self.date_authorized = fields.Datetime.now()

    def action_certified(self):
        certifier = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.env.user.id != self.certifier_id.id:
            raise UserError('Only %s can Certify or Reject this Application!' % self.certifier_id.name)
        self.write({'state': 'certified', 'certified_by': certifier})
        self.date_certified = fields.Datetime.now()

    def action_approved(self):
        approver = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.env.user.id != self.approver_id.id:
            raise UserError('Only %s can Approve or Reject this Application!' % self.approver_id.name)
        self.write({'state': 'approved', 'approved_by': approver})
        self.date_approved = fields.Datetime.now()

    # def action_rejected(self):
    #     self.write({'state': 'rejected'})

    def action_reject1(self):
        if self.env.user.id != self.authorizer_id.id:
            raise UserError('Only %s can Authorize or Reject this Application!' % self.authorizer_id.name)
        self.write({'state': 'rejected'})

    def action_reject2(self):
        if self.env.user.id != self.certifier_id.id:
            raise UserError('Only %s can Certify or Reject this Application!' % self.certifier_id.name)
        self.write({'state': 'rejected'})

    def action_reject3(self):
        if self.env.user.id != self.approver_id.id:
            raise UserError('Only %s can Approve or Reject this Application!' % self.approver_id.name)
        self.write({'state': 'rejected'})


class ImprestRetirementLines(models.Model):
    _name = 'imprest.retirement.lines'
    _description = 'Imprest Retirement Lines'

    name = fields.Char(string='Item Description')
    imprest_retirement_id = fields.Many2one('imprest.retirement', string='Imprest Retirement')
    date = fields.Date(string='Date')
    payee_name = fields.Char(string='Payee Name')
    obligated_budget = fields.Float(string='Obligated Budget')
    amount_spent = fields.Float(string='Amount Spent')
    balance = fields.Float(string='Balance', compute='_compute_amount')
    doc_ref_number = fields.Char(string='Doc. Ref #')

    state = fields.Selection(related='imprest_retirement_id.state', store=True)

    # @api.onchange('obligated_budget', 'amount_spent')
    # def _onchange_amount_spent(self):
    #     for rec in self:
    #         rec.balance = rec.obligated_budget - rec.amount_spent

    @api.depends('obligated_budget', 'amount_spent')
    def _compute_amount(self):
        for rec in self:
            rec.balance = rec.obligated_budget - rec.amount_spent

    # @api.onchange('price_unit', 'quantity')
    #    def _onchange_price_unit(self):
    #        for rec in self:
    #            rec.price_subtotal = rec.price_unit * rec.quantity



