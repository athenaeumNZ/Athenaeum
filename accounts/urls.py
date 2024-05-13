from django.urls import path
from accounts import views

urlpatterns = [
    #region back orders
    path('distributors_back_orders/<int:library_id>', views.distributors_back_orders, name='distributors_back_orders'),
    path('distributors_priority_orders/<int:library_id>&<int:distributor_id>', views.distributors_priority_orders, name='distributors_priority_orders'),
    #endregion
    #region invoices
    path('invoice/<int:library_id>&<int:invoice_id>', views.invoice, name='invoice'),
    path('invoice_archive_submission/<int:library_id>&<int:invoice_id>', views.invoice_archive_submission, name='invoice_archive_submission'),
    path('invoice_payment_cleared_submission/<int:library_id>&<int:invoice_id>', views.invoice_payment_cleared_submission, name='invoice_payment_cleared_submission'),
    path('invoice_member_has_payed_submission/<int:library_id>&<int:invoice_id>', views.invoice_member_has_payed_submission, name='invoice_member_has_payed_submission'),
    path('invoice_member_has_received_all_plates_submission/<int:library_id>&<int:invoice_id>', views.invoice_member_has_received_all_plates_submission, name='invoice_member_has_received_all_plates_submission'),
    path('invoice_member_archive_submission/<int:library_id>&<int:invoice_id>', views.invoice_member_archive_submission, name='invoice_member_archive_submission'),
    path('invoice_create_submission/<int:library_id>&<int:member_id>', views.invoice_create_submission, name='invoice_create_submission'),
    path('invoice_use_credit_submission/<int:library_id>&<int:invoice_id>', views.invoice_use_credit_submission, name='invoice_use_credit_submission'),
    path('return_to_invoice/<int:library_id>&<int:invoice_id>', views.return_to_invoice, name='return_to_invoice'),
    #endregion
    #region order request items
    path('order_request_items_stockpile_submission/<int:library_id>', views.order_request_items_stockpile_submission, name='order_request_items_stockpile_submission'),
    path('order_request_item_split/<int:library_id>&<int:order_request_item_id>', views.order_request_item_split, name='order_request_item_split'),
    path('order_request_item_split_submission/<int:library_id>&<int:order_request_item_id>', views.order_request_item_split_submission, name='order_request_item_split_submission'),

    path('order_request_item_delete_submission/<int:library_id>&<int:order_request_item_id>', views.order_request_item_delete_submission, name='order_request_item_delete_submission'),
    path('order_request_item_order_submission/<int:library_id>&<int:order_request_item_id>', views.order_request_item_order_submission, name='order_request_item_order_submission'),
    path('order_request_item_stockpiled_submission/<int:library_id>&<int:order_request_id>&<int:order_request_item_id>&<str:previous_url>', views.order_request_item_stockpiled_submission, name='order_request_item_stockpiled_submission'),
    path('order_request_item_update_submission/<int:library_id>&<int:order_request_item_id>', views.order_request_item_update_submission, name='order_request_item_update_submission'),
    path('order_request_item_update/<int:library_id>&<int:order_request_item_id>', views.order_request_item_update, name='order_request_item_update'),
    path('return_to_dashboard/<int:library_id>', views.return_to_dashboard, name='return_to_dashboard'),
    #endregion
    #region dashboard
    path('dashboard/<int:library_id>', views.dashboard, name='dashboard'),
    path('dashboard_search/<int:library_id>', views.dashboard_search, name='dashboard_search'),
    #endregion
    #region purchase order request
    path('purchase_order_request_template/<int:library_id>', views.purchase_order_request_template, name='purchase_order_request_template'),
    path('purchase_order_request/<int:library_id>&<int:purchase_order_request_id>', views.purchase_order_request, name='purchase_order_request'),
    path('purchase_order_request_items_filled_submission/<int:library_id>&<int:purchase_order_request_id>', views.purchase_order_request_items_filled_submission, name='purchase_order_request_items_filled_submission'),
    path('purchase_order_request_item_filled_submission/<int:library_id>&<int:purchase_order_request_id>&<int:purchase_order_request_item_id>', views.purchase_order_request_item_filled_submission, name='purchase_order_request_item_filled_submission'),
    path('purchase_order_request_item_edit/<int:library_id>&<int:purchase_order_request_id>&<int:purchase_order_request_item_id>', views.purchase_order_request_item_edit, name='purchase_order_request_item_edit'),
    path('purchase_order_request_submission/<int:library_id>&<int:distributor_id>', views.purchase_order_request_submission, name='purchase_order_request_submission'),
    path('return_to_purchase_order_request/<int:library_id>&<int:purchase_order_request_id>', views.return_to_purchase_order_request, name='return_to_purchase_order_request'),
    #endregion
]


''' UNUSED Invoice
    path('invoice_template/<int:library_id>&<int:member_id>', views.invoice_template, name='invoice_template'),
    path('invoice_flatten_submission/<int:library_id>&<int:invoice_id>', views.invoice_flatten_submission, name='invoice_flatten_submission'),
    path('invoice_flatten_all_costs_to_zero_submission/<int:library_id>&<int:invoice_id>', views.invoice_flatten_all_costs_to_zero_submission, name='invoice_flatten_all_costs_to_zero_submission'),
    path('invoice_notes_add/<int:library_id>&<int:invoice_id>', views.invoice_notes_add, name='invoice_notes_add'),
    path('invoice_notes_add_submission/<int:library_id>&<int:invoice_id>', views.invoice_notes_add_submission, name='invoice_notes_add_submission'),
    path('invoice_paid_submission/<int:library_id>&<int:invoice_id>', views.invoice_paid_submission, name='invoice_paid_submission'),
    path('invoice_pseudo_edit/<int:library_id>&<int:invoice_id>', views.invoice_pseudo_edit, name='invoice_pseudo_edit'),
    path('invoice_pseudo_edit_submission/<int:library_id>&<int:invoice_id>', views.invoice_pseudo_edit_submission, name='invoice_pseudo_edit_submission'),
    path('invoice_stockpile_all_items_submission/<int:library_id>&<int:invoice_id>', views.invoice_stockpile_all_items_submission, name='invoice_stockpile_all_items_submission'),
'''
