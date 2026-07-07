# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools
from odoo.tools.pdf import OdooPdfFileReader, OdooPdfFileWriter
import io
import logging

_logger = logging.getLogger(__name__)


class AccountMoveSend(models.AbstractModel):
    _inherit = 'account.move.send'

    def _hook_invoice_document_after_pdf_report_render(self, invoice, invoice_data):
        if (
            'ubl_cii_xml_options' in invoice_data
            and invoice_data['ubl_cii_xml_options'].get('ubl_cii_format') not in ('facturx', 'blue_kira')
        ):
            self._postprocess_invoice_ubl_xml(invoice, invoice_data)
        if invoice_data.get('ubl_cii_xml_options', {}).get('ubl_cii_format') in ('facturx', 'blue_kira'):
            xml_facturx = invoice_data['ubl_cii_xml_attachment_values']['raw']
        else:
            xml_facturx = self.env['account.edi.xml.cii']._export_invoice(invoice)[0]
        if tools.config['test_enable']:
            self.env['ir.attachment'].sudo().create({
                'name': 'factur-x.xml',
                'raw': xml_facturx,
                'res_id': invoice.id,
                'res_model': 'account.move',
            })
            return
        pdf_values = (
            (not self.env.context.get('custom_template_facturx') and invoice.invoice_pdf_report_id)
            or invoice_data.get('pdf_attachment_values')
            or invoice_data['proforma_pdf_attachment_values']
        )
        reader_buffer = io.BytesIO(pdf_values['raw'])
        reader = OdooPdfFileReader(reader_buffer, strict=False)
        writer = OdooPdfFileWriter()
        writer.cloneReaderDocumentRoot(reader)
        writer.addAttachment('factur-x.xml', xml_facturx, subtype='text/xml')

        if invoice_data.get('ubl_cii_xml_options', {}).get('ubl_cii_format') in ('facturx', 'blue_kira') and not writer.is_pdfa:
            try:
                writer.convert_to_pdfa()
            except Exception:
                _logger.exception("Error while converting to PDF/A")
            content = self.env['ir.qweb']._render(
                'account_edi_ubl_cii.account_invoice_pdfa_3_facturx_metadata',
                {
                    'title': invoice.name,
                    'date': fields.Date.context_today(self),
                },
            )
            writer.add_file_metadata(content.encode())
        writer_buffer = io.BytesIO()
        writer.write(writer_buffer)
        pdf_values['raw'] = writer_buffer.getvalue()
        reader_buffer.close()
        writer_buffer.close()
