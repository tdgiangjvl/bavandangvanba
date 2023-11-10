from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/?query=Vì+anh")
        self.client.get("/?query=là+anh+sao")