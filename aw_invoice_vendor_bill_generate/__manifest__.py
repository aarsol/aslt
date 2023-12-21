{
    "name": "Customer Vendor Bill Generator",
    "description": "This module allows for the generation of vendor bills through invoices, linking invoices to vendor bills, and applying a 2.5% donation surcharge to the vendor bills.",
    "summary": "Generate vendor bills from invoices with a 2.5% donation surcharge.",
    "author": "Ansa Saeed",
    "depends": ["base", "product", "account", "purchase"],
    "data": [
        "views/product_template.xml",
        "views/res_partner.xml"
    ],
    "installable": True
}
