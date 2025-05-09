class OrderManagement:
    def __init__(self):
        self.orders_dict = {}

    def add_new_order(self, table_num, items, special_requests):
        order_id = len(self.orders_dict) + 1
        self.orders_dict[order_id] = {
            'table_num': table_num,
            'items': items,
            'special_requests': special_requests,
            'status': 'New'
        }
        return order_id

    def retrieve_current_orders(self):
        return self.orders_dict

    def update_order_progress(self, order_id, new_progress):
        if order_id in self.orders_dict:
            self.orders_dict[order_id]['status'] = new_progress

    def delete_order(self, order_id):
        if order_id in self.orders_dict:
            del self.orders_dict[order_id]



class OrdersController:
    def __init__(self, order_management):
        self.order_management = order_management
        self.current_orders_dict = {}

    def update_current_orders(self):
        self.current_orders_dict = self.order_management.retrieve_current_orders()

    def identify_ready_orders(self):
        ready_orders = {k: v for k, v in self.current_orders_dict.items() if v['status'] == 'Ready'}
        return ready_orders

    def retrieve_orders(self):
        self.update_current_orders()
        return self.current_orders_dict

    def retrieve_ready_orders(self):
        return self.identify_ready_orders()

    def add_new_order(self, table_num, items, special_requests):
        return self.order_management.add_new_order(table_num, items, special_requests)
