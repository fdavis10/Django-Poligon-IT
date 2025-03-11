from locust import HttpUser, task, between
import random
import re

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    product_ids = [1, 2, 3]

    def get_csrf_token(self):
        """Получает CSRF-токен с главной страницы."""
        response = self.client.get("/")
        match = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', response.text)
        return match.group(1) if match else None

    @task
    def load_homepage(self):
        self.client.get("/")

    @task(2)
    def load_orders(self):
        self.client.get('/order/')

    @task(3)
    def load_cart(self):
        self.client.get("/cart/")

    @task(2)
    def add_to_cart(self):
        csrf_token = self.get_csrf_token()
        if not csrf_token:
            return  
        headers = {"X-CSRFToken": csrf_token}
        product_id = random.choice(self.product_ids)
        self.client.post(f"/cart/add/{product_id}/", data={"quantity": 1, "override": False}, headers=headers)

    @task(1)
    def remove_from_cart(self):
        csrf_token = self.get_csrf_token()
        if not csrf_token:
            return

        headers = {"X-CSRFToken": csrf_token}
        product_id = random.choice(self.product_ids)
        self.client.post(f"/cart/remove/{product_id}/", headers=headers)

    @task(1)
    def update_cart(self):
        csrf_token = self.get_csrf_token()
        if not csrf_token:
            return

        headers = {"X-CSRFToken": csrf_token}
        product_id = random.choice(self.product_ids)
        self.client.post(f"/cart/update/{product_id}/", data={"quantity": random.randint(1, 5)}, headers=headers)

    @task(1)
    def restore_cart(self):
        csrf_token = self.get_csrf_token()
        if not csrf_token:
            return

        headers = {"X-CSRFToken": csrf_token}
        product_id = random.choice(self.product_ids)
        self.client.post(f"/cart/restore/{product_id}/", headers=headers)

    @task
    def create_order(self):
        csrf_token = self.get_csrf_token()
        if not csrf_token:
            return

        headers = {"X-CSRFToken": csrf_token}
        self.client.post("/order/create/", data={
            "first_name": "Test",
            "email": "test_locust@test.com",
            "phone_number": "8436434"
        }, headers=headers)
