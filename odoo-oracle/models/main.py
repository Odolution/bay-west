from odoo import api, fields, models
from datetime import datetime
import requests,base64
import json
from odoo.exceptions import  UserError
import random
from requests.auth import HTTPBasicAuth
from logging import getLogger
_logger = getLogger(__name__)

class PartnerInherit(models.Model):
    _inherit = 'res.partner'

    tx_oracle_id = fields.Char(string='Oracle ID')
    tx_credit_days = fields.Integer(string='Credit Days')
    tx_profile_code = fields.Char("Profile Code")

class oracle(models.Model):
    _name = 'oracle.credentials'
    _description = 'Odoo to Oracle Integration'
    name = fields.Char(string='Name')
    url = fields.Char(string='Url')
    user_name = fields.Char(string='User Name')
    password = fields.Char(string='Password')
    job_execution_start=fields.Datetime(string='Job Execution Start')

    def sync(self):
        webservice_error=False
        job_execution_start= datetime.now()
        update_pram=self.env['ir.config_parameter'].search([('key','=','tx_customer_interface_timestamp')])
        self.job_execution_start=job_execution_start
        def randomPcode():
            characterlist=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            c1 = random.choice(characterlist)
            c2 = random.choice(characterlist)
            c3 = random.choice(characterlist)
            return c1+c2+c3
        def callApi(rpc,cc,name,sn,cd,add,phone,url_g,cdd,pid,c):
            url = c.url+"CUSTOMER/0"
            dict={
                "PROFILE_CODE": rpc,
                "COUNTRY_SHORT_NAME": cc,
                "CUSTOMER_NAME": name,
                "CUSTOMER_SHORT_NAME": sn,
                "JOINING_DATE": cd,
                "ADDRESS": add,
                "PHONE": phone,
                "URL": url_g,
                "CREDIT_DAYS": cdd,
                "ODOO_PARTNER_ID": pid
            }
            usrPass = c.user_name+":"+c.password
            encoded_u = base64.b64encode(usrPass.encode()).decode()
            payload = json.dumps(dict)
            headers = {
            'Authorization': 'Basic '+str(encoded_u),
            'Content-Type': 'application/json'
            }
            
            response = requests.request("POST", url, headers=headers, data=payload)
            return response.json()
        cred = self.env['oracle.credentials'].search([])
        

        if cred:
            for cc in cred:
                ResPartner=self.env['res.partner'].search([])
                
                
        
                if update_pram.value:
                    upadte_time=datetime.strptime(update_pram.value.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    ResPartner=self.env['res.partner'].search([('write_date','>=',upadte_time)])
                    update_pram.value=str(job_execution_start)

                for rp in ResPartner:
                    try:
                        if not rp.tx_oracle_id:
                            resp={"STATUSTEXT":"","STATUS":""}
                            rcode=False
                            checkw=True
                            while(checkw):
                                rcode=randomPcode()
                                resp=callApi(
                                    rcode,
                                    str(rp.country_id.code) if rp.country_id.code else "",
                                    str(rp.name),
                                    str(rp.name[0:2]),
                                    rp.create_date.strftime("%d-%b-%Y"),
                                    # str(rp.street if rp.street else "" + rp.street2 if rp.street2 else ""+ rp.city.name if rp.city else "" + rp.state_id if rp.state_id else ""+ rp.zip if rp.zip else ""),
                                    str(rp.contact_address),
                                    str(rp.phone),
                                    str(rp.website),
                                    str(rp.tx_credit_days),
                                    str(rp.id),
                                    cc
                                    )
                                if resp["STATUSTEXT"] != "profile code alreay exist in oracle":
                                    checkw=False
                            else:
                                if resp["STATUS"] == "1":
                                    rp.tx_oracle_id = resp["ID"]
                                    _logger.info(str(resp))
                                else:
                                    _logger.exception(str(resp))

                        else:
                            url = cc.url+"CUSTOMER/"+rp.tx_oracle_id
                            payload={}
                            usrPass = cc.user_name+":"+cc.password
                            encoded_u = base64.b64encode(usrPass.encode()).decode()
                            headers = {
                            'Authorization': 'Basic '+str(encoded_u)
                            }
                            update_dict={}
                            response_up = requests.request("GET", url, headers=headers, data=payload).json()["items"][0]
                            address=str(rp.street if rp.street else "" + rp.street2 if rp.street2 else ""+ rp.city if rp.city else "" + rp.state_id if rp.state_id else ""+ rp.zip if rp.zip else ""+ rp.country_id if rp.country_id else "")
                            if rp.name != response_up["name"]:
                                update_dict["name"]=rp.name
                                update_dict["short_name"]=rp.name[0:2]
                            if address != response_up["address"]:
                                update_dict["address"]=address
                            if rp.phone != response_up["phone"]:
                                update_dict["phone"]=rp.phone
                            if rp.website != response_up["url"]:
                                update_dict["url"]=rp.website
                            if str(rp.tx_credit_days) != response_up["credit_days"]:
                                update_dict["credit_days"]=str(rp.tx_credit_days)
                            if update_dict:
                                url = cc.url+"CUSTOMER/"+rp.tx_oracle_id

                                payload = json.dumps(update_dict)
                                headers = {
                                    'Authorization': 'Basic '+encoded_u,
                                    'Content-Type': 'application/json'
                                }

                                response = requests.request("PUT", url, headers=headers, data=payload)
                                
                                _logger.info(str(response.text))
                    except Exception as e:
                        webservice_error=True
                        _logger.exception(e)