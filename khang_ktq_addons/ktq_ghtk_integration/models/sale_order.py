# -*- coding: utf-8 -*-

import requests
import json
from odoo import models, fields
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # (Các trường GHTK của bạn)
    ktq_ghtk_tracking_code = fields.Char(
        string="Mã vận đơn GHTK",
        copy=False,
        readonly=True
    )
    ktq_ghtk_status = fields.Char(
        string="Trạng thái GHTK",
        copy=False,
        readonly=True
    )

    # === HÀM ĐỂ GỌI API ===
    def action_send_to_ghtk(self):
        config_params = self.env['ir.config_parameter'].sudo()
        api_token = config_params.get_param('ktq_ghtk_integration.api_token')

        if not api_token:
            raise UserError("Chưa cấu hình API Token GHTK! Vui lòng vào Cài đặt > Bán hàng > Giao Hàng Tiết Kiệm để thiết lập.")

        api_url = "https://services.giaohangtietkiem.vn/services/shipment/order"
        headers = {
            "Token": api_token,
            "Content-Type": "application/json"
        }

        for order in self:
            # === BẮT ĐẦU SỬA ĐỔI ===
            
            # 1. Kiểm tra Địa chỉ LẤY hàng (Kho/Công ty)
            company = order.company_id
            if not company.street or not company.street2 or not company.city or not company.state_id or not company.phone:
                raise UserError(
                    "Thông tin Công ty (Kho hàng) bị thiếu. "
                    "Vui lòng vào Cài đặt > Công ty để cập nhật (Dòng địa chỉ 1, Dòng địa chỉ 2 [Phường], Quận/Huyện [City], Tỉnh, SĐT)."
                )

            # 2. Kiểm tra Địa chỉ GIAO hàng (Khách hàng)
            shipping_partner = order.partner_shipping_id
            if not shipping_partner:
                raise UserError(f"Đơn hàng {order.name} thiếu Địa chỉ giao hàng!")
            if not shipping_partner.street or not shipping_partner.street2 or not shipping_partner.city or not shipping_partner.state_id or not shipping_partner.phone:
                raise UserError(
                    f"Địa chỉ Giao hàng của khách hàng '{shipping_partner.name}' bị thiếu. "
                    "Vui lòng cập nhật (Dòng địa chỉ 1, Dòng địa chỉ 2 [Phường], Quận/Huyện [City], Tỉnh, SĐT)."
                )

            # 3. Xây dựng danh sách sản phẩm
            product_list = []
            for line in order.order_line:
                if not line.product_id: continue
                product_weight = line.product_id.weight or 0.1 # Mặc định 0.1kg
                product_list.append({
                    "name": line.product_id.name,
                    "quantity": line.product_uom_qty,
                    "weight": product_weight
                })
            if not product_list:
                raise UserError("Đơn hàng không có sản phẩm để giao.")

            # 4. Xây dựng Payload (dữ liệu JSON) - ĐÃ SỬA MAPPING PHƯỜNG/XÃ
            payload = {
                "order": {
                    "id": order.name,
                    "pick_name": company.name,
                    "pick_address": company.street,            # Dòng 1: "52 Cô Bắc"
                    "pick_province": company.state_id.name,     # "TP Đà Nẵng (VN)"
                    "pick_district": company.city,              # "Quận Hải Châu"
                    "pick_ward": company.street2,               # Dòng 2: "phường Hải Châu"
                    "pick_tel": company.phone,
                    
                    "name": shipping_partner.name,
                    "address": shipping_partner.street,         # Dòng 1 (Khách)
                    "province": shipping_partner.state_id.name, # Tỉnh (Khách)
                    "district": shipping_partner.city,          # Quận (Khách)
                    "ward": shipping_partner.street2,           # Dòng 2 (Khách)
                    "hamlet": "Khác",
                    "tel": shipping_partner.phone,
                    "email": shipping_partner.email or "",
                    
                    "is_freeship": "0",
                    "pick_money": order.amount_total,
                    "note": order.note or "Giao hàng cẩn thận",
                    "value": order.amount_total,
                },
                "products": product_list
            }
            # === KẾT THÚC SỬA ĐỔI ===

            try:
                response = requests.post(api_url, data=json.dumps(payload), headers=headers, timeout=10)
                response.raise_for_status() 

                result = response.json()
                
                if result.get('success'):
                    ghtk_order = result.get('order', {})
                    tracking_code = ghtk_order.get('label')
                    status = ghtk_order.get('status_id')
                    order.write({
                        'ktq_ghtk_tracking_code': tracking_code,
                        'ktq_ghtk_status': f"GHTK Status ID: {status}"
                    })
                else:
                    raise UserError(f"GHTK báo lỗi (nghiệp vụ): {result.get('message', 'Lỗi không xác định')}")

            except requests.exceptions.Timeout:
                raise UserError("Lỗi: Không kết nối được tới server GHTK (Timeout).")
            except requests.exceptions.RequestException as e:
                if e.response is not None:
                    try:
                        error_data = e.response.json()
                        message = error_data.get('message', 'Lỗi không rõ từ GHTK')
                        raise UserError(f"GHTK báo lỗi (dữ liệu sai): {message}")
                    except json.JSONDecodeError:
                        raise UserError(f"Lỗi kết nối API: {e.response.status_code} - {e.response.text}")
                else:
                    raise UserError(f"Lỗi kết nối API: {e}")
            except Exception as e:
                raise UserError(f"Lỗi không xác định: {e}")
            
        return True