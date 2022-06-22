# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError
import json


class ImprestApplication(models.Model):
    _name = 'imprest.application'
    _description = 'Imprest Application'
    _order = 'name desc'
    _inherit = 'mail.thread'

    def _active_budget(self):
        return self.env['crossovered.budget'].search([('state', 'in', ('confirm', 'validate'))], limit=1).id

    name = fields.Char(string='Imprest Application', copy=False, default=lambda self: ('New'), readonly=True)
    applicant_id = fields.Many2one('hr.employee', string='Applicant', required=True)
    # activity = fields.Many2one('account.analytic.account', required=True, string='Activity')

    #activity = fields.Many2one('account.analytic.account', string='Activity')

    imprest_application_project_line_ids = fields.One2many('imprest.application.project.lines', 'imprest_application_project', string='Project', track_visibility='onchange')

    #project_manager =  fields.Char(related=project_lines.)
    #budget_id = fields.Many2one('crossovered.budget', string='Budget', default=_active_budget)
    purpose = fields.Text(string='Purpose', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.today())
    #budget_balance = fields.Float('Budget Balance', compute='_compute_available_balance')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    imprest_application_line_ids = fields.One2many('imprest.application.lines', 'imprest_application_id')
    project_parcentage_total = fields.Float(compute='_compute_project_perctage_total', store=True, string='Total Parcentage')
    grand_total = fields.Float(compute='_compute_grand_total', store=True, string='Total')
    state = fields.Selection([
        ('draft', "Draft"),
        ('submitted', "Submitted"),
        ('authorized', "Authorized"),
        ('certified', "Certified"),
        ('approved', "Approved"),
        ('assign_project_codes', "PM's Verified"),
        ('verify', "Verify"),
        ('account1', "Accountant 1"),
        ('account2', "Accountant 2"),
        ('finance_lead', "Finance Lead"),
        ('finance_director', "Finance Director"),
        ('country_director', "Country Director"),
        ('post', "Post"),
        ('posted', "Paid"),
        ('retired', "Retirement Processed"),
        ('rejected', "Rejected")], default='draft', track_visibility='onchange')
    
    @api.onchange('imprest_application_line_ids')
    def _default_approve_limit(self):
        res = self.env['res.users']
        # user_id=-1
        # result = -1
        # for record in self:
        #     users_list = self.env['imprest.limit'].search([('initial_amount', '<', self.grand_total),('final_amount', '>', self.grand_total)]).user_id
        #     print(users_list,self.approver_id)
        #     for items in users_list:
        #         if items:
        #             user_id=items.id
        #             print("approve presents",user_id)
        #         break
        # if user_id!=-1:
        #     result = res.search([('id','=',user_id)])
        print("approve result presents",res)
        return res


    @api.model
    def default_get(self, fields):
        res = super(ImprestApplication, self).default_get(fields)
        res['applicant_id'] = self.env.user.employee_id.id
        res['verify_id'] = 736
        res['paid_id'] = 420
        res['post_id'] = 420


        # This is intended to return name DAVID FEO
        return res

    
    
    @api.onchange('imprest_application_line_ids')
    def _default_line_manager(self):
        rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)],limit=1)
        
        for user in rec:
            if user:
                self.authorizer_id = user.parent_id.id                
                print("records presents",user.parent_id.id)
            else:
                self.authorizer_id = false


    is_first_finacial_verify = fields.Boolean(string='first finacial verify', compute = '_is_first_finacial_verify', default = False)
    is_second_finacial_verify = fields.Boolean(string='second finacial verify', compute = '_is_second_finacial_verify', default = False)
    is_third_finacial_verify = fields.Boolean(string='third finacial verify', compute = '_is_third_finacial_verify', default = False)
    is_fourth_finacial_verify = fields.Boolean(string='fourth finacial verify', compute = '_is_fourth_finacial_verify', default = False)
    # project_parcentage_total = fields.Float(compute='compute project perctage', store=True, string='Total Parcentage')
    imprest_type=fields.Selection([('group', 'Group'), ('individual', 'Individual')],default='group')
    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id)
    authorizer_id = fields.Many2one('res.users', string='To Authorise',required = True ,store=True)
    authorizer_id_domain = fields.Char(string='Domain to Authorise',compute='_compute_authorizer_id_domain')
    certifier_id = fields.Many2one('res.users', string='To Certify (Select Project Lead)',required = True ,store=True)
    # certifier_id_domain = fields.Char(string='Domain to Certify',compute='_compute_certifier_id_domain')
    approver_id = fields.Many2one('res.users', string='To Approve',required = True ,store=True,)
    # approver_id_domain = fields.Char(string='Domain to Approve',compute='_compute_approver_id_domain')
    is_authorizer = fields.Boolean(string='Is Authorizer', compute='_is_authorizer', default = False)
    is_certifier = fields.Boolean(string='Is Certifier', compute = '_is_certifier', default = False)
    is_approver = fields.Boolean(string='Is Approver', compute = '_is_approver', default = False)
    authorized_by = fields.Many2one('hr.employee', string='Authorized By')
    certified_by = fields.Many2one('hr.employee', string='Certified By')
    approved_by = fields.Many2one('hr.employee', string='Approved By')
    date_authorized = fields.Datetime(string='Date Authorized')
    date_certified = fields.Datetime(string='Date Certified')
    date_approved = fields.Datetime(string='Date Approved')
    created_by_id = fields.Many2one('hr.employee', readonly=True, string='Created by',
                                    default=lambda self: self.env['hr.employee'].search(
                                        [('user_id', '=', self.env.uid)], limit=1))

    imprest_account_id = fields.Many2one('account.account', string='Imprest Account')
    bank_account_id = fields.Many2one('account.account', string='Bank Account')
    
    pm_approver_id = fields.Many2one('res.users',string='PM Approver',required=True)

    verify_id = fields.Many2one('res.users',string='Verify',readonly=True)

    account1_id = fields.Many2one(
        'res.users',
        string='Account1',
    )

    account2_id = fields.Many2one(
        'res.users',
        string='Account2',
    )

    finance_lead_id = fields.Many2one(
        'res.users',
        string='Finance Lead',
    )

    finance_director_id = fields.Many2one(
        'res.users',
        string='Finance Director',
    )

    country_dir_id = fields.Many2one(
        'res.users',
        string='Country Director',
    )

    post_id = fields.Many2one(
        'res.users',
        string='Post By',
    )

    paid_id = fields.Many2one(
        'res.users',
        string='Pay By',
    )

    retired_id = fields.Many2one(
        'res.users',
        string='Retired',
    )

    general_ids = fields.One2many(
        'general.advance',
        'imprest_id',
        string='General',
    )

    general_total = fields.Float(
        string='Total', compute='_compute_general_total'
    )

    url = fields.Char(
        string='URL', compute='compue_url'
    )

    def compue_url(self):
        url = ''
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for rec in self:
            base_url += '/web#id=%d&view_type=form&model=%s' % (
                rec.id, self._name)
            rec.url = base_url

    @api.depends('general_ids')
    def _compute_general_total(self):
        for items in self:
            total_amount = 0.0
            for line in items.general_ids:
                total_amount += line.sub_total
            items.general_total = total_amount
    

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
            vals['name'] = self.env['ir.sequence'].next_by_code('imprest.application') or ('New')
            return super(ImprestApplication, self).create(vals)

    @api.depends('imprest_application_line_ids')
    def _compute_grand_total(self):
        for items in self:
            total_amount = 0.0
            for line in items.imprest_application_line_ids:
                total_amount += line.line_total
            items.grand_total = total_amount

    @api.depends('imprest_application_project_line_ids')
    def _compute_project_perctage_total(self):
        for items in self:
            total_parcentage = 0.0
            for line in items.imprest_application_project_line_ids:
                total_parcentage += line.project_percentage
            items.project_parcentage_total = total_parcentage

    @api.depends('imprest_application_line_ids','applicant_id')
    def _compute_authorizer_id_domain(self):
        print("The domain result ",self.authorizer_id_domain)
        result = []

        for rec in self:
            users_list = self.env['imprest.limit'].search([('initial_amount', '<', rec.grand_total),('final_amount', '>', rec.grand_total)]).user_id
            manager_list = self.env['hr.employee'].search([('id', '=', rec.applicant_id.id)],limit=1).parent_id.user_id
            print("The domain result ",manager_list)
            rec.authorizer_id=manager_list

            for line in rec.imprest_application_project_line_ids:
                project_manager = line.project_manager
                #rec.certifier_id=project_manager
                #rec.approver_id=project_manager
                print("The domain project manager result ")

            for items in users_list:
                #rec.certifier_id=items
                rec.approver_id
                # domain = [("id", "=", items.id)]
                # result.append(("id", "=", "9"))
                # rec.authorizer_id_domain=json.dumps(domain)
                # rec.authorizer_id_domain=result
            print("The domain result ",rec.approver_id)

   

    @api.depends('imprest_application_line_ids')
    def _is_first_finacial_verify(self):
        for items in self:
            check = -1
            users_list = self.env['imprest.financial.limit'].search([('name','=',"1-5M"),('initial_amount', '<=', items.grand_total),('threashold_amount', '>', items.grand_total)]).user_id
            print("records first finacial",users_list)
            for record in users_list:
                if record.id == self.env.uid:
                    check=record.id
                print("Name of a person supposed to do action is ",record.id)
                print("NAME OF CURRENTLY LOGIN USER IS ",self.env.uid)
            if check !=-1:
                items.is_first_finacial_verify=True
            else:
                items.is_first_finacial_verify=False

    @api.depends('imprest_application_line_ids')
    def _is_second_finacial_verify(self):
        for items in self:
            check = -1
            users_list = self.env['imprest.financial.limit'].search([('name','=',"5-12M"),('initial_amount', '<=', items.grand_total),('threashold_amount', '>', items.grand_total)]).user_id
            print("records second finacial",users_list)
            for record in users_list:
                if record.id == self.env.uid:
                    check=record.id

                print("records second finacial",check)
            if check !=-1:
                items.is_second_finacial_verify=True
            else:
                items.is_second_finacial_verify=False

    @api.depends('imprest_application_line_ids')
    def _is_third_finacial_verify(self):
        for items in self:
            check = -1
            users_list = self.env['imprest.financial.limit'].search([('name','=',"12-25M"),('initial_amount', '<=', items.grand_total),('threashold_amount', '>', items.grand_total)]).user_id
            print("records third finacial",users_list)
            for record in users_list:
                if record.id == self.env.uid:
                    check=record.id
                print("records third finacial",check)
            if check !=-1:
                items.is_third_finacial_verify=True
            else:
                items.is_third_finacial_verify=False
    

    @api.depends('imprest_application_line_ids')
    def _is_fourth_finacial_verify(self):
        for items in self:
            check = -1
            users_list = self.env['imprest.financial.limit'].search([('name','=',"25M and above"),('initial_amount', '<=', items.grand_total),('threashold_amount', '>', items.grand_total)]).user_id
            print("records fourth finacial",users_list)
            for record in users_list:
                if record.id == self.env.uid:
                    check=record.id
                print("records fourth finacial",check)
            if check !=-1:
                items.is_fourth_finacial_verify=True
            else:
                items.is_fourth_finacial_verify=False

            

    # @api.depends('activity')
    # def _compute_available_balance(self):
    #     for imprest in self:
    #         amount = 0.0
    #         if imprest.activity:
    #             budget_line = self.env['crossovered.budget.lines']. \
    #                 search([
    #                 ('analytic_account_id', '=', imprest.activity.id), ('crossovered_budget_id', '=', imprest.budget_id.id)])
    #             for line in budget_line:
    #                 amount += (line.practical_amount - line.planned_amount)
    #         imprest.budget_balance = amount

    def view_imprest_posting(self):
        return {
            'name': 'Imprest Posting',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('ref', '=', self.name)]
        }

    def view_retirement(self):
        return {
            'name': 'Retirement',
            'view_mode': 'tree,form',
            'res_model': 'imprest.retirement',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('imprest_ref', '=', self.name)]
        }

    

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_pay_review(self):
        users_list = self.env['imprest.financial.limit'].search([('name','=',"1-5M"),('initial_amount', '<', self.grand_total),('threashold_amount', '>', self.grand_total)]).user_id
        print(users_list)
        if users_list:
            self.write({'state': 'account1'})
        else:
            self.write({'state': 'finance_lead'})

    # def action_pm_verify(self):
    #     self.write({'state': 'assign_project_codes'})


    def action_pm_verify(self):

        for rec in self.imprest_application_project_line_ids:
            if not rec.project_drl:
                raise UserError('You can not proceed the application without project DRL.')
            else:
                pass
        if self.env.user.id != self.pm_approver_id.id:
            raise UserError(
                'Only %s can Authorize or Reject this Application!' % self.pm_approver_id.name)
        self.write({'state': 'assign_project_codes'})
        template_id = self.env.ref(
            'tenmet_imprest.email_template_mst_imprest_global').id
        template = self.env['mail.template'].browse(template_id)
        template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
        template.email_to = self.verify_id.login
        template.send_mail(self.id, force_send=True)
        



    def action_fn_verify(self):
       
        if self.env.user.id != self.verify_id.id:
            raise UserError(
                'Only %s can Authorize or Reject this Application!' % self.verify_id.name)
        self.write({'state': 'verify'})
        template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
        template = self.env['mail.template'].browse(template_id)
        template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
        template.email_to = self.account1_id.login
        template.send_mail(self.id, force_send=True)

        
    # def action_fn_verify(self):
    #     self.write({'state': 'verify'})
        
    def action_first_finacial_review(self):
        if self.is_first_finacial_verify:
            self.write({'state':'account2'})
        else:
            raise UserError('Only User with Respective Limit Can Review this Advance')

    def action_second_finacial_review(self):
        if self.is_first_finacial_verify:
            self.write({'state':'post'})
        else:
            raise UserError('Only User with Respective Limit Can Review this Advance')


    def action_finance_lead_review(self):
        if self.is_second_finacial_verify:
            self.write({'state':'post'})
        elif self.is_third_finacial_verify:
            self.write({'state':'finance_director'})
        elif self.is_fourth_finacial_verify:
            self.write({'state':'finance_director'})
        else :
            raise UserError('Only Finance Lead with Respective Limit can  Verify this request')

    def action_finance_director_review(self):
        if self.is_third_finacial_verify:
            self.write({'state':'post'})
        elif self.is_fourth_finacial_verify:
            self.write({'state':'country_director'})
        else :
            raise UserError('Only Finance Director with Respective Limit can  Verify this request')

    def action_finance_lead_reject(self):
        if self.is_second_finacial_verify:
            self.write({'state':'rejected'})
        elif self.is_third_finacial_verify:
            self.write({'state':'rejected'})
        elif self.is_fourth_finacial_verify:
            self.write({'state':'rejected'})
        else :
            raise UserError('Only Financial Lead with Respective Limit can  Reject this request')



    def action_finance_director_reject(self):
        if self.is_third_finacial_verify:
            self.write({'state':'rejected'})
        elif self.is_fourth_finacial_verify:
            self.write({'state':'rejected'})
        else :
            raise UserError('Only Financial Director with Respective Limit can  Reject this request')
 

    def action_first_finacial_reject(self):
        if self.is_third_finacial_verify:
            self.write({'state':'rejected'})
        elif self.is_fourth_finacial_verify:
            self.write({'state':'rejected'})
        else :
            raise UserError('Only Candidate with Respective Limit can  Reject this request')

    def action_country_director_reject(self):
        if self.is_fourth_finacial_verify:
            self.write({'state':'rejected'})
        else :
            raise UserError('Only Country Director can Reject')


    def action_country_director_review(self):
        if self.is_fourth_finacial_verify:
            self.write({'state':'post'})
        else :
            raise UserError('Only Country Director with Respective Limit can  Reject this request')

    def action_post(self):
        self.write({'state':'posted'})
   
    # def _is_first_finacial_verify(self):
    #     print("current state is verify")
    #     print("current state is verify")
    #     print("current state is verify")
    #     if self.state=="verify":
    #         print("current state is verify")
    #         print("current state is verify")
    #         print("current state is verify")
    #         current_financial_user=self.env['imprest.financial.limit'].search([('user_id', '=', self.env.uid)],limit=1)
    #         if(current_financial_user):
    #             is_first_finacial_verify=True;
    #             print(is_first_finacial_verify)



    def action_submitted(self):
        
        for applications in self:
            # if self.grand_total > self.budget_balance:
            #     raise UserError('Budget balance for this Activity has been exceeded! '
            #                       'Please contact FGAM to review the Activity Budget or select a different Activity')
            if not applications.imprest_application_line_ids:
                raise UserError('Imprest details are missing. Please fill the details before submitting!')
            if not applications.authorizer_id:
                raise UserError('Include name of Person to authorize the Application')
            if not applications.certifier_id:
                raise UserError('Include name of Person to Certify the Application')
            if not applications.approver_id:
                raise UserError('Include name of Person to Approve the Application')
        self.write({'state': 'submitted'})
        template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id,force_send=True)

    def action_authorized(self):
        
        authorizer = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.env.user.id != self.authorizer_id.id:
            raise UserError('Only %s can Authorize or Reject this Application!' % self.authorizer_id.name)
        self.write({'state': 'authorized', 'authorized_by': authorizer})
        self.date_authorized = fields.Datetime.now()
        template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_authorized').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id,force_send=True)

    def action_certified(self):
         
        if not self.imprest_application_project_line_ids:
            raise UserError('Add at least One Project')

        certifier = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        if self.env.user.id != self.certifier_id.id:
            raise UserError('Only %s can Certify or Reject this Application!' % self.certifier_id.name)

        self.write({'state': 'certified', 'certified_by': certifier})
        self.date_certified = fields.Datetime.now()
        template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_approve').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id,force_send=True)
        
        
        

        

    def action_approved(self):
        

        approver = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.env.user.id != self.approver_id.id:
            raise UserError('Only %s can Approve or Reject this Application!' % self.approver_id.name)
        self.write({'state': 'approved', 'approved_by': approver})
        self.date_approved = fields.Datetime.now()
        # template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_pm').id
        # template = self.env['mail.template'].browse(template_id)
        # template.send_mail(self.id,force_send=True)

    # def action_posted(self):
    #     self.write({'state': 'posted'})
    #     journal_object = self.env['account.move']
    #     for record in self:
    #         if record.imprest_application_line_ids:
    #             debit_vals = {
    #                 'name': record.name,
    #                 'account_id': record.imprest_account_id.id or False,
    #                 'partner_id': record.applicant_id and record.applicant_id.id or False,
    #                 'analytic_account_id': record.activity and record.activity.id or False,
    #                 'analytic_tag_ids': record.project and record.project.ids or False,
    #                 'debit': record.grand_total,
    #                 'credit': 0.0,
    #             }

    #             credit_vals = {
    #                 'name': record.name,
    #                 'account_id': self.bank_account_id.id or False,
    #                 'debit': 0.0,
    #                 'credit': self.grand_total,
    #             }

    #             vals = {
    #                 'ref': record.name,
    #                 'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
    #             }
    #             journal = journal_object.create(vals)
    #             journal_view_id = self.env.ref('account.view_move_form')

    #             return {
    #                 'name': 'Journal',
    #                 'view_type': 'form',
    #                 'view_mode': 'form',
    #                 'res_model': 'account.move',
    #                 'view_id': journal_view_id.id,
    #                 'type': 'ir.actions.act_window',
    #                 'nodestroy': True,
    #                 'target': 'current',
    #                 'res_id': journal.id,
    #                 'context': {}
    #             }

    # def action_retired(self):
    #     self.write({'state': 'retired'})

    #     retirement_obj = self.env['imprest.retirement']
    #     for record in self:
    #         retirement_applicant_id = record.applicant_id
    #         if record.imprest_application_line_ids:
                

    #             for items in record.imprest_application_line_ids:
    #                 for x in items:
    #                     retirement_lines = []
    #                     retirement_lines.append((0, 0,{'name': x.name or False,'obligated_budget': x.line_total}))
    #                     vals = {
    #                     'retirement_applicant_id': x.employee_id.name,
                         
    #                     'retirement_purpose': record.purpose,
    #                     'imprest_ref': record.name,
    #                     'amount_advanced': x.line_total,
    #                     'imprest_retirement_line_ids': retirement_lines or False
    #                     }
    #                     retirement = retirement_obj.create(vals)
    #                     #retirement_view_id = self.env.ref('tenmet_imprest.imprest_retirement_form')



    def action_retired(self):
        self.write({'state': 'retired'})

        retirement_obj = self.env['imprest.retirement']
        for record in self:
            retirement_applicant_id = record.applicant_id
            if record.imprest_application_line_ids:
                

                for items in record.imprest_application_line_ids:
                    for x in items:
                        retirement_lines = []
                        retirement_lines.append((0, 0,{'name': x.name or False,'obligated_budget': x.line_total}))
                        vals = {
                        'retirement_applicant_id': x.employee_id.name,
                         
                        'retirement_purpose': record.purpose,
                        'imprest_ref': record.name,
                        'amount_advanced': x.line_total,
                        'imprest_retirement_line_ids': retirement_lines or False
                        }
                        retirement = retirement_obj.create(vals)
                        #retirement_view_id = self.env.ref('tenmet_imprest.imprest_retirement_form')




    def action_reset_to_posted(self):
        self.write({'state': 'posted'})

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

    def action_reject4(self):
        # if self.env.user.id != self.approver_id.id:
        #     raise UserError('Only %s can Approve or Reject this Application!' % self.approver_id.name)
        self.write({'state': 'rejected'})

    def action_reject5(self):

        # if self.env.user.id != self.approver_id.id:
        #     raise UserError('Only %s can Approve or Reject this Application!' % self.approver_id.name)
        self.write({'state': 'rejected'})

    def action_reject6(self):
        # if self.env.user.id != self.approver_id.id:
        #     raise UserError('Only %s can Approve or Reject this Application!' % self.approver_id.name)
        self.write({'state': 'rejected'})


        # Financial Review approver
    



class ImprestApplicationLines(models.Model):
    _name = 'imprest.application.lines'
    _description = 'Imprest Applcation Lines'

    name = fields.Char(string='Item Description')
    imprest_application_id = fields.Many2one('imprest.application', string='Imprest Application')
    employee_id=fields.Many2one('hr.employee', string='Emplyee Name')
    product_uom_id = fields.Many2one('uom.uom', string='Unit')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price', default=0.0)
    line_total = fields.Float(string='Line Total')

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")


    @api.onchange('quantity', 'unit_price')
    def _onchange_unit_price(self):
        for rec in self:
            rec.line_total = rec.quantity * rec.unit_price


class ImprestApplicationProjectLines(models.Model):
    _name = 'imprest.application.project.lines'
    _description = 'Imprest Applcation Project Lines'
    
    name = fields.Char(string='Item Description')
    project_codes_ids = fields.Many2one('imprest.application', string='Imprest Application')
    imprest_application_project = fields.Many2one('imprest.application', string='Imprest Application')
    project_ids = fields.Many2one('project.project', string='Project Name')
    project_manager = fields.Many2one( related='project_ids.user_id' , string='Project Manager')
    project_code = fields.Char(related='project_ids.pcode', string='Project Code')
    # project_line = fields.Many2one('imprest.project', string='Cost Lines')
    project_funder = fields.Char(related='project_ids.funder',readonly=True, string='Project Funder')
    project_drl = fields.Char('DRL')
    project_percentage = fields.Float(required=True, string='% Contribution', default=0.0)
    manager_confirmed = fields.Boolean(compute='compute_confirmed',  track_visibility='onchange')
    current_user = fields.Integer(string='Active User', track_visibility='onchange',
                              default=lambda self: self.env.user.id, compute='_compute_user_id')
    project_manager_id = fields.Integer(string='Active Project User', track_visibility='onchange',
                              default=lambda self: self.project_manager.id, compute='_compute_project_user_id')    

    def _compute_user_id(self):
        for rec in self:
            rec.current_user = self.env.user.id

    def _compute_project_user_id(self):
        for rec in self:
            rec.project_manager_id = rec.project_manager.id

    def compute_confirmed(self):
        for rec in self:
            rec.manager_confirmed = False            
            if rec.project_manager.id == self.env.uid:
                rec.manager_confirmed = True
            else:
                rec.manager_confirmed = False


    # @api.depends('project_percentage')
    # def _compute_project_perctage_total(self):
    #     for items in self:
    #         total_parcentage = 0.0
    #         for line in items.imprest_application_project_line_ids:
    #             total_parcentage += line.project_percentage
    #             if total_parcentage == 100.00:
    #                 self.check_percent=True
    #         items.project_parcentage_total = total_parcentage



class ProjectProject(models.Model):

    _inherit = 'project.project'

    funder=fields.Char('Project Funder')
    pcode=fields.Char('Project Code')
     
