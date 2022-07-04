# -*- coding: utf-8 -*-

{
    'name': 'Odoo-Oracle Integration',
    'version': '1.0.0',
    'category': 'Integration',
    'summary': 'Odoo-Oracle Integration',
    'description': """Odoo-Oracle Integration""",
    'sequence': -100,
    'depends': ['contacts'],
    'data': [
        'security/ir.model.access.csv',
        'Data/add_data.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}
