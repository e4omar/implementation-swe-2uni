import socket
import threading
import json

class OrderManagement:
    def __init__(self):
        self.orders_dict = {}
        # id system need to be improved

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


class OrdersDashboard:
    def __init__(self, orders_controller):
        self.orders_controller = orders_controller

    def display_orders(self):
        orders = self.orders_controller.retrieve_orders()
        for order_id, details in orders.items():
            print(f"Order ID: {order_id}, Table: {details['table_num']}, Items: {details['items']}, Status: {details['status']}")

    def notify_ready_order(self):
        ready_orders = self.orders_controller.retrieve_ready_orders()
        for order_id, details in ready_orders.items():
            print(f"Order ID: {order_id} is ready!")

    def delete_ready_order(self, order_id):
        self.orders_controller.order_management.delete_order(order_id)


class OrdersDashboardKitchen(OrdersDashboard):
    def update_order_progress(self, order_id, new_progress):
        self.orders_controller.order_management.update_order_progress(order_id, new_progress)

class OrdersDashboardWaitstaff(OrdersDashboard):
    def add_new_order(self, table_num, items, special_requests):
        return self.orders_controller.add_new_order(table_num, items, special_requests)


class OrderManagementServer:
    def __init__(self, host='localhost', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        print(f"Server started on {host}:{port}")

        self.order_management = OrderManagement()
        self.orders_controller = OrdersController(self.order_management)
        self.orders_dashboard_kitchen = OrdersDashboardKitchen(self.orders_controller)
        self.orders_dashboard_waitstaff = OrdersDashboardWaitstaff(self.orders_controller)

    def handle_client(self, client_socket):
        while True:
            try:
                request = client_socket.recv(1024).decode('utf-8')
                if not request:
                    break
                print(f"Received: {request}")
                response = self.process_request(request)
                client_socket.send(response.encode('utf-8'))
            except ConnectionResetError:
                break
        client_socket.close()

    def process_request(self, request):
        try:
            data = json.loads(request)
            action = data.get('action')
            if action == 'ADD_ORDER':
                table_num = data['table_num']
                items = data['items']
                special_requests = data['special_requests']
                order_id = self.orders_dashboard_waitstaff.add_new_order(table_num, items, special_requests)
                return json.dumps({'status': 'success', 'order_id': order_id})
            elif action == 'GET_ORDERS':
                orders = self.orders_controller.retrieve_orders()
                return json.dumps({'status': 'success', 'orders': orders})
            elif action == 'UPDATE_ORDER':
                order_id = data['order_id']
                new_status = data['status']
                self.orders_dashboard_kitchen.update_order_progress(order_id, new_status)
                return json.dumps({'status': 'success'})
            else:
                return json.dumps({'status': 'error', 'message': 'Invalid action'})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})

    def start(self):
        while True:
            client_socket, addr = self.server.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    server = OrderManagementServer()
    server.start()
