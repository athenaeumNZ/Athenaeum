from django.urls import path
from cart import views

urlpatterns = [
    #region cart
    path('cart/<int:library_id>&<int:member_id>', views.cart, name='cart'),
    path('cart_add_item/<int:library_id>&<int:release_id>&<str:previous_url>', views.cart_add_item, name='cart_add_item'),
    path('cart_remove_item/<int:library_id>&<int:release_id>', views.cart_remove_item, name='cart_remove_item'),
    path('cart_submission/<int:library_id>&<int:member_id>', views.cart_submission, name='cart_submission'),
    path('return_to_cart/<int:library_id>', views.return_to_cart, name='return_to_cart'),
    #endregion

    #region invoice ################
    # invoice
    path('member_order/<int:library_id>&<int:order_id>&<int:member_id>', views.member_order, name='member_order'),
    
    path('invoice_cashbook_entry_add_submission/<int:library_id>&<int:order_id>', views.invoice_cashbook_entry_add_submission, name='invoice_cashbook_entry_add_submission'),

    # invoice order ITEM submission
    path('invoice_order_item_submission/<int:library_id>&<int:order_id>&<int:order_item_id>', views.invoice_order_item_submission, name='invoice_order_item_submission'),
    
    # invoice order ITEM submission
    path('invoice_order_get_item_found_in_stock_submission/<int:library_id>&<int:order_id>&<int:order_item_id>', views.invoice_order_get_item_found_in_stock_submission, name='invoice_order_get_item_found_in_stock_submission'),

    # invoice order get item found in on order stock
    path('invoice_order_get_item_found_in_on_order_submission/<int:library_id>&<int:order_id>&<int:order_item_id>', views.invoice_order_get_item_found_in_on_order_submission, name='invoice_order_get_item_found_in_on_order_submission'),

    # invoice remove mark up submission
    path('invoice_remove_mark_up_submission/<int:library_id>&<int:order_id>', views.invoice_remove_mark_up_submission, name='invoice_remove_mark_up_submission'), 
    # invoice use credit submission
    path('invoice_use_credit_submission/<int:library_id>&<int:order_id>', views.invoice_use_credit_submission, name='invoice_use_credit_submission'), 
    # invoice item update
    path('invoice_item_update/<int:library_id>&<int:order_id>&<int:order_item_id>', views.invoice_item_update, name='invoice_item_update'),
    # invoice item update submission
    path('invoice_item_update_submission/<int:library_id>&<int:order_id>&<int:order_item_id>', views.invoice_item_update_submission, name='invoice_item_update_submission'),

    
    # invoice pay submission
    path('invoice_pay_submission/<int:library_id>&<int:order_id>', views.invoice_pay_submission, name='invoice_pay_submission'),
    # invoice order items submission
    path('invoice_order_items_submission/<int:library_id>&<int:order_id>', views.invoice_order_items_submission, name='invoice_order_items_submission'),
    # return to invoice
    path('return_to_member_order/<int:library_id>&<int:order_id>', views.return_to_member_order, name='return_to_member_order'),
    #endregion

    #region purchase order receipt
    path('purchase_order_receipt/<int:library_id>&<int:purchase_order_id>', views.purchase_order_receipt, name='purchase_order_receipt'),
    # cart purchase order submission
    path('cart_purchase_order_submission/<int:library_id>&<int:member_id>', views.cart_purchase_order_submission, name='cart_purchase_order_submission'),
    # purchase order order ITEM submission
    path('purchase_order_order_item_submission/<int:library_id>&<int:purchase_order_id>&<int:purchase_order_item_id>', views.purchase_order_order_item_submission, name='purchase_order_order_item_submission'),
    # purchase order order item update
    path('purchase_order_order_item_update/<int:library_id>&<int:purchase_order_id>&<int:purchase_order_item_id>', views.purchase_order_order_item_update, name='purchase_order_order_item_update'),
    # purchase order order item update submission
    path('purchase_order_order_item_update_submission/<int:library_id>&<int:purchase_order_id>&<int:purchase_order_item_id>', views.purchase_order_order_item_update_submission, name='purchase_order_order_item_update_submission'),
    # purchase order is restock submission
    path('purchase_order_is_restock_submission/<int:library_id>&<int:purchase_order_id>', views.purchase_order_is_restock_submission, name='purchase_order_is_restock_submission'), 
    # purchase order funded submission
    path('purchase_order_funded_submission/<int:library_id>&<int:purchase_order_id>', views.purchase_order_funded_submission, name='purchase_order_funded_submission'), 
    # purchase order order itemS submission
    path('purchase_order_cashbook_entry_add_submission/<int:library_id>&<int:purchase_order_id>', views.purchase_order_cashbook_entry_add_submission, name='purchase_order_cashbook_entry_add_submission'),
    # purchase order order itemS submission
    path('purchase_order_order_items_submission/<int:library_id>&<int:purchase_order_id>', views.purchase_order_order_items_submission, name='purchase_order_order_items_submission'),
    # return to purchase order reciept
    path('return_to_purchase_order_receipt/<int:library_id>&<int:purchase_order_id>', views.return_to_purchase_order_receipt, name='return_to_purchase_order_receipt'),
    #endregion
]