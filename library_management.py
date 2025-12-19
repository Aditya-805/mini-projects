import json
import os

# Book Class
class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self._title = title
        self._author = author
        self._isbn = isbn
        self._is_borrowed = False

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @property
    def isbn(self):
        return self._isbn

    @property
    def is_borrowed(self):
        return self._is_borrowed

    @is_borrowed.setter
    def is_borrowed(self, value):
        if isinstance(value, bool):
            self._is_borrowed = value
        else:
            raise ValueError("is_borrowed must be a boolean.")

    def borrow(self):
        if not self._is_borrowed:
            self._is_borrowed = True
            return True
        return False

    def return_book(self):
        if self._is_borrowed:
            self._is_borrowed = False
            return True
        return False

    def __str__(self):
        status = "Borrowed" if self._is_borrowed else "Available"
        return f"Title: {self._title}, Author: {self._author}, ISBN: {self._isbn}, Status: {status}"

    def to_dict(self):
        return {
            'title': self._title,
            'author': self._author,
            'isbn': self._isbn,
            'is_borrowed': self._is_borrowed
        }

# User Class
class User:
    def __init__(self, name: str, user_id: str):
        self._name = name
        self._user_id = user_id
        self._borrowed_books_isbns = []

    @property
    def name(self):
        return self._name

    @property
    def user_id(self):
        return self._user_id

    @property
    def borrowed_books_isbns(self):
        return list(self._borrowed_books_isbns)

    def add_borrowed_book_isbn(self, isbn: str):
        if isbn not in self._borrowed_books_isbns:
            self._borrowed_books_isbns.append(isbn)

    def remove_borrowed_book_isbn(self, isbn: str):
        if isbn in self._borrowed_books_isbns:
            self._borrowed_books_isbns.remove(isbn)

    def __str__(self):
        return f"User: {self._name} (ID: {self._user_id}), Borrowed Books: {len(self._borrowed_books_isbns)}"

    def to_dict(self):
        return {
            'name': self._name,
            'user_id': self._user_id,
            'borrowed_books_isbns': self._borrowed_books_isbns
        }

# Library Class
class Library:
    def __init__(self, book_file='books.json', user_file='users.json'):
        self._books = {}  # isbn: Book
        self._users = {}  # user_id: User
        self._data_file_books = book_file
        self._data_file_users = user_file
        self._load_data()

    def _load_data(self):
        # Load books
        try:
            with open(self._data_file_books, 'r') as f:
                books_data = json.load(f)
            for b in books_data:
                book = Book(b['title'], b['author'], b['isbn'])
                book.is_borrowed = b['is_borrowed']
                self._books[book.isbn] = book
        except FileNotFoundError:
            pass

        # Load users
        try:
            with open(self._data_file_users, 'r') as f:
                users_data = json.load(f)
            for u in users_data:
                user = User(u['name'], u['user_id'])
                user._borrowed_books_isbns = u['borrowed_books_isbns']
                self._users[user.user_id] = user
        except FileNotFoundError:
            pass

    def _save_data(self):
        # Save books
        with open(self._data_file_books, 'w') as f:
            json.dump([b.to_dict() for b in self._books.values()], f, indent=4)
        # Save users
        with open(self._data_file_users, 'w') as f:
            json.dump([u.to_dict() for u in self._users.values()], f, indent=4)

    def add_book(self, book: Book):
        if book.isbn in self._books:
            print(f"Book with ISBN {book.isbn} already exists.")
            return False
        self._books[book.isbn] = book
        self._save_data()
        return True

    def remove_book(self, isbn: str):
        book = self._books.get(isbn)
        if not book:
            print("Book not found.")
            return False
        if book.is_borrowed:
            print("Cannot remove a borrowed book.")
            return False
        del self._books[isbn]
        self._save_data()
        return True

    def register_user(self, user: User):
        if user.user_id in self._users:
            print(f"User ID {user.user_id} already exists.")
            return False
        self._users[user.user_id] = user
        self._save_data()
        return True

    def remove_user(self, user_id: str):
        user = self._users.get(user_id)
        if not user:
            print("User not found.")
            return False
        if user.borrowed_books_isbns:
            print("User has borrowed books. Cannot remove.")
            return False
        del self._users[user_id]
        self._save_data()
        return True

    def borrow_book(self, isbn: str, user_id: str):
        book = self._books.get(isbn)
        user = self._users.get(user_id)
        if not book:
            print("Book not found.")
            return False
        if not user:
            print("User not found.")
            return False
        if book.is_borrowed:
            print("Book is already borrowed.")
            return False
        if book.borrow():
            user.add_borrowed_book_isbn(isbn)
            self._save_data()
            return True
        return False

    def return_book(self, isbn: str, user_id: str):
        book = self._books.get(isbn)
        user = self._users.get(user_id)
        if not book:
            print("Book not found.")
            return False
        if not user:
            print("User not found.")
            return False
        if isbn not in user.borrowed_books_isbns:
            print("This user didn't borrow this book.")
            return False
        if book.return_book():
            user.remove_borrowed_book_isbn(isbn)
            self._save_data()
            return True
        return False

    def search_book(self, query: str):
        results = []
        query_lower = query.lower()
        for book in self._books.values():
            if (query_lower in book.title.lower() or
                query_lower in book.author.lower() or
                query_lower in book.isbn):
                results.append(book)
        return results

    def display_all_books(self, show_available_only=False):
        for book in self._books.values():
            if show_available_only and book.is_borrowed:
                continue
            print(book)

    def display_all_users(self):
        for user in self._users.values():
            print(user)

    def display_user_borrowed_books(self, user_id: str):
        user = self._users.get(user_id)
        if not user:
            print("User not found.")
            return
        if not user.borrowed_books_isbns:
            print("This user has not borrowed any books.")
            return
        print(f"Books borrowed by {user.name} (ID: {user.user_id}):")
        for isbn in user.borrowed_books_isbns:
            book = self._books.get(isbn)
            if book:
                print(book)

# Console Interface
def main():
    library = Library()

    while True:
        print("\n--- Library Management System ---")
        print("1. Add Book")
        print("2. Remove Book")
        print("3. Register User")
        print("4. Remove User")
        print("5. Borrow Book")
        print("6. Return Book")
        print("7. Search Books")
        print("8. Display All Books")
        print("9. Display All Users")
        print("10. Show User Borrowed Books")
        print("X. Exit")
        choice = input("Enter choice (1-10): ")

        if choice == '1':
            title = input("Enter book title: ")
            author = input("Enter author: ")
            isbn = input("Enter ISBN: ")
            book = Book(title, author, isbn)
            if library.add_book(book):
                print("Book added successfully.")
        elif choice == '2':
            isbn = input("Enter ISBN of the book to remove: ")
            if library.remove_book(isbn):
                print("Book removed.")
        elif choice == '3':
            name = input("Enter user name: ")
            user_id = input("Enter user ID: ")
            user = User(name, user_id)
            if library.register_user(user):
                print("User registered.")
        elif choice == '4':
            user_id = input("Enter user ID to remove: ")
            if library.remove_user(user_id):
                print("User removed.")
        elif choice == '5':
            isbn = input("Enter ISBN of the book to borrow: ")
            user_id = input("Enter user ID: ")
            if library.borrow_book(isbn, user_id):
                print("Book borrowed successfully.")
        elif choice == '6':
            isbn = input("Enter ISBN of the book to return: ")
            user_id = input("Enter user ID: ")
            if library.return_book(isbn, user_id):
                print("Book returned successfully.")
        elif choice == '7':
            query = input("Enter title, author, or ISBN to search: ")
            results = library.search_book(query)
            if results:
                print("Search Results:")
                for b in results:
                    print(b)
            else:
                print("No matching books found.")
        elif choice == '8':
            print("All Books:")
            library.display_all_books()
        elif choice == '9':
            print("All Users:")
            library.display_all_users()
        elif choice == '10':
            user_id = input("Enter user ID: ")
            library.display_user_borrowed_books(user_id)
        elif choice == 'X' or choice == 'x':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()