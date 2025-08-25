from locust import HttpUser, between,task 
from random import randint


class WebsiteUser(HttpUser):
    wait_time = between(1, 2)
    # with @tasks we define the things this imaginary client would do and by giving them weights we define the possibility of accuring each function
    # example: if the imaginary client sends 8 requests here's how we define the weights ==> 3 of the requests are for view_products, 4 of them are for view_products_details and 1 of them is for add_to_cart
    @task(3)
    def view_products(self):
        print('view products')
        collection_id=randint(1,5)
        self.client.get(f'/store/products/?collection_id={collection_id}', name='store/products/')
    @task(4)
    def view_products_details(self):
        print('view products details')
        product_id=randint(2,10)
        self.client.get(f'/store/products/{product_id}/', name='store/products/:id')
    @task(1)
    def add_to_cart(self):
        print('adding 2 peoducts to a shopping cart')
        # here we select a product which id is between 1 to 5
        product_id1=randint(1,5)
        product_id2=randint(6,9)
        # here we want to put the product in the created cart(the cart we built at the begining)
        # /store/carts/{self.cart_id}/items => here we need an id for the shopping cart which you can see in the on_start function 
        self.client.post(f'/store/carts/{self.cart_id}/items/', name='store/carts/items', json={'product_id': product_id1, 'quantity': 1})#this for product1
        self.client.post(f'/store/carts/{self.cart_id}/items/', name='store/carts/items', json={'product_id': product_id2, 'quantity': 1})#this is for product2
        # json={'product_id':product_id , 'quantity':1 => so here we want to send the info to our db and for that we need json codes so by using json:{} we can write codes.
    # basically on_start function the first function that srats working. we want the imaginary user to make a cart and add a random product among product id 1 to 5
    def on_start(self):
        # here you send a request to the server(creating a cart) then you save it as "response"
        response=self.client.post('/store/carts/',json={'cart_id':''})
        # "response"'s result is a bunch of json codes so we turn it into python codes by adding .json and we save the python codes in a varianle called result which includes all the information of the new created cart such as id 
        result= response.json()
        # here we crreate an other variable called "self.cart_id" and we pull the id from the variable result and we put it in the assigned variable
        self.cart_id = result['id']
         
    def slow_API(self):
        self.client.get('/store/products/')

# locust -f locustfiles/brows_products.py