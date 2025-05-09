class OrderManagement:
    def __init__(self):
        self.orders_dict = {}

    def add_new_order(self, table_num, items, special_requests):
        order_id = len(self.orders_dict) + 1
        self.orders_dict[order_id] = {
            'table_num': table_num,
            'items': items,
            'special_requests': special_requests,
            'status': 'Pending'
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


class OrdersDashboard:
    def __init__(self, orders_controller):
        self.orders_controller = orders_controller

    def display_orders(self):
        orders = self.orders_controller.retrieve_orders()
        for order_id, details in orders.items():
            print(f"Order ID: {order_id}, Details: {details}")

    def notify_ready_order(self):
        ready_orders = self.orders_controller.retrieve_ready_orders()
        for order_id, details in ready_orders.items():
            print(f"Ready Order ID: {order_id}, Details: {details}")

    def delete_ready_order(self, order_id):
        self.orders_controller.order_management.delete_order(order_id)


class OrdersDashboardKitchen(OrdersDashboard):
    def update_order_progress(self, order_id, new_progress):
        self.orders_controller.order_management.update_order_progress(order_id, new_progress)


class OrdersDashboardWaitstaff(OrdersDashboard):
    def add_new_order(self, table_num, items, special_requests):
        return self.orders_controller.add_new_order(table_num, items, special_requests)


# Example usage
order_management = OrderManagement()
orders_controller = OrdersController(order_management)
dashboard_kitchen = OrdersDashboardKitchen(orders_controller)
dashboard_waitstaff = OrdersDashboardWaitstaff(orders_controller)

# Adding new orders
dashboard_waitstaff.add_new_order(1, {'Burger': 2, 'Fries': 1}, 'No onions')
dashboard_waitstaff.add_new_order(2, {'Pizza': 1}, 'Extra cheese')

# Displaying orders
dashboard_waitstaff.display_orders()

# Updating order progress
dashboard_kitchen.update_order_progress(1, 'Ready')

# Notifying ready orders
dashboard_waitstaff.notify_ready_order()

# Deleting ready orders
dashboard_waitstaff.delete_ready_order(1)
