import json

class Product:
    def __init__(self, product_id: str, name: str, price: float, quantity_available: int):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_available = quantity_available

    @property
    def product_id(self):
        return self._product_id

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @property
    def quantity_available(self):
        return self._quantity_available

    @quantity_available.setter
    def quantity_available(self, value):
        if value >= 0:
            self._quantity_available = value
        else:
            raise ValueError("Quantity cannot be negative.")

    def decrease_quantity(self, amount: int) -> bool:
        if amount <= 0:
            return False
        if self._quantity_available >= amount:
            self._quantity_available -= amount
            return True
        return False

    def increase_quantity(self, amount: int) -> None:
        if amount > 0:
            self._quantity_available += amount

    def display_details(self) -> str:
        return (f"ID: {self._product_id} | Name: {self._name} | "
                f"Price: ${self._price:.2f} | Available: {self._quantity_available}")

    def to_dict(self) -> dict:
        return {
            'product_id': self._product_id,
            'name': self._name,
            'price': self._price,
            'quantity_available': self._quantity_available,
            'type': 'product'  # base type
        }

    def __str__(self):
        return self.display_details()
class PhysicalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float, quantity_available: int, weight: float):
        super().__init__(product_id, name, price, quantity_available)
        self._weight = weight

    @property
    def weight(self):
        return self._weight

    def display_details(self) -> str:
        base_details = super().display_details()
        return f"{base_details} | Weight: {self._weight} kg"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'weight': self._weight,
            'type': 'physical'
        })
        return data
class DigitalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float, quantity_available: int, download_link: str):
        super().__init__(product_id, name, price, quantity_available)
        self._download_link = download_link

    @property
    def download_link(self):
        return self._download_link

    def display_details(self) -> str:
        return (f"ID: {self._product_id} | Name: {self._name} | "
                f"Price: ${self._price:.2f} | Download Link: {self._download_link}")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'download_link': self._download_link,
            'type': 'digital'
        })
        return data
class CartItem:
    def __init__(self, product: Product, quantity: int):
        self._product = product
        self._quantity = quantity

    @property
    def product(self):
        return self._product

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if value >= 0:
            self._quantity = value
        else:
            raise ValueError("Quantity cannot be negative.")

    def calculate_subtotal(self) -> float:
        return self._product.price * self._quantity

    def __str__(self) -> str:
        return (f"Item: {self._product.name}, Quantity: {self._quantity}, "
                f"Price: ${self._product.price:.2f}, Subtotal: ${self.calculate_subtotal():.2f}")

    def to_dict(self) -> dict:
        return {
            'product_id': self._product.product_id,
            'quantity': self._quantity
        }
class ShoppingCart:
    def __init__(self, product_catalog_file='products.json', cart_state_file='cart.json'):
        self._items = {}  # key: product_id, value: CartItem
        self._product_catalog_file = product_catalog_file
        self._cart_state_file = cart_state_file
        self._catalog = self._load_catalog()
        self._load_cart_state()

    def _load_catalog(self) -> dict:
        catalog = {}
        try:
            with open(self._product_catalog_file, 'r') as f:
                data_list = json.load(f)
                for data in data_list:
                    p_type = data.get('type', 'product')
                    if p_type == 'physical':
                        product = PhysicalProduct(
                            data['product_id'], data['name'], data['price'],
                            data['quantity_available'], data['weight']
                        )
                    elif p_type == 'digital':
                        product = DigitalProduct(
                            data['product_id'], data['name'], data['price'],
                            data['quantity_available'], data['download_link']
                        )
                    else:
                        product = Product(
                            data['product_id'], data['name'], data['price'],
                            data['quantity_available']
                        )
                    catalog[product.product_id] = product
        except FileNotFoundError:
            print("Product catalog file not found. Starting with empty catalog.")
        return catalog

    def _load_cart_state(self):
        try:
            with open(self._cart_state_file, 'r') as f:
                data_list = json.load(f)
                for data in data_list:
                    product_id = data['product_id']
                    quantity = data['quantity']
                    product = self._catalog.get(product_id)
                    if product:
                        # Reduce stock based on cart
                        if product.decrease_quantity(quantity):
                            self._items[product_id] = CartItem(product, quantity)
        except FileNotFoundError:
            pass

    def _save_catalog(self):
        data_list = [product.to_dict() for product in self._catalog.values()]
        with open(self._product_catalog_file, 'w') as f:
            json.dump(data_list, f, indent=2)

    def _save_cart_state(self):
        data_list = [item.to_dict() for item in self._items.values()]
        with open(self._cart_state_file, 'w') as f:
            json.dump(data_list, f, indent=2)

    def add_item(self, product_id: str, quantity: int) -> bool:
        product = self._catalog.get(product_id)
        if product and quantity > 0:
            if product.decrease_quantity(quantity):
                if product_id in self._items:
                    self._items[product_id].quantity += quantity
                else:
                    self._items[product_id] = CartItem(product, quantity)
                self._save_cart_state()
                self._save_catalog()
                return True
        return False

    def remove_item(self, product_id: str) -> bool:
        if product_id in self._items:
            cart_item = self._items.pop(product_id)
            # Return stock
            cart_item.product.increase_quantity(cart_item.quantity)
            self._save_cart_state()
            self._save_catalog()
            return True
        return False

    def update_quantity(self, product_id: str, new_quantity: int) -> bool:
        if product_id in self._items and new_quantity >=0:
            cart_item = self._items[product_id]
            current_quantity = cart_item.quantity
            delta = new_quantity - current_quantity
            if delta > 0:
                # Need more stock
                if cart_item.product.decrease_quantity(delta):
                    cart_item.quantity = new_quantity
                else:
                    return False
            elif delta < 0:
                # Return stock
                cart_item.product.increase_quantity(-delta)
                cart_item.quantity = new_quantity
            else:
                return True  # No change
            self._save_cart_state()
            self._save_catalog()
            return True
        return False

    def get_total(self) -> float:
        total = sum(item.calculate_subtotal() for item in self._items.values())
        return total

    def display_cart(self) -> None:
        if not self._items:
            print("Your cart is empty.")
            return
        print("\nCurrent Shopping Cart:")
        print("-" * 50)
        for item in self._items.values():
            print(str(item))
        print("-" * 50)
        print(f"Grand Total: ${self.get_total():.2f}\n")

    def display_products(self) -> None:
        if not self._catalog:
            print("No products available.")
            return
        print("\nAvailable Products:")
        print("-" * 50)
        for product in self._catalog.values():
            print(product.display_details())
        print("-" * 50)
def main():
    cart = ShoppingCart()

    def show_menu():
        print("\n======= Online Shopping Cart =======")
        print("1. View Products")
        print("2. Add Item to Cart")
        print("3. View Cart")
        print("4. Update Quantity")
        print("5. Remove Item")
        print("6. Exit")
        print("=====================================")

    while True:
        show_menu()
        choice = input("Enter your choice (1-6): ").strip()
        if choice == '1':
            cart.display_products()
        elif choice == '2':
            product_id = input("Enter Product ID to add: ").strip()
            try:
                quantity = int(input("Enter quantity: "))
                if quantity <= 0:
                    print("Quantity must be positive.")
                    continue
            except ValueError:
                print("Invalid quantity.")
                continue
            if cart.add_item(product_id, quantity):
                print("Item added to cart.")
            else:
                print("Failed to add item. Check product ID and stock.")
        elif choice == '3':
            cart.display_cart()
        elif choice == '4':
            product_id = input("Enter Product ID to update: ").strip()
            try:
                quantity = int(input("Enter new quantity: "))
                if quantity < 0:
                    print("Quantity cannot be negative.")
                    continue
            except ValueError:
                print("Invalid quantity.")
                continue
            if cart.update_quantity(product_id, quantity):
                print("Cart updated.")
            else:
                print("Failed to update. Check product ID and stock.")
        elif choice == '5':
            product_id = input("Enter Product ID to remove: ").strip()
            if cart.remove_item(product_id):
                print("Item removed from cart.")
            else:
                print("Product not found in cart.")
        elif choice == '6':
            print("Exiting. Saving data...")
            break
        else:
            print("Invalid choice. Please select from 1-6.")

if __name__ == "__main__":
    main()
