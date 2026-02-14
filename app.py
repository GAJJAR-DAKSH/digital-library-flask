from flask import Flask, render_template, request, redirect, url_for, flash, jsonify # type: ignore
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"

DB_PATH = "library.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_PATH):
        conn = get_conn()
        c = conn.cursor()


        c.execute("""
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL
            )
        """)

        c.execute("""
            CREATE TABLE borrows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                isbn TEXT NOT NULL,
                borrow_date TEXT NOT NULL,
                return_date TEXT
            )
        """)

       
        c.execute("""
            CREATE TABLE reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT NOT NULL,
                user_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at TEXT NOT NULL
            )
        """)

        sample_books = [
            ("The Alchemist", "Paulo Coelho", "0001AA", 3),
            ("Clean Code", "Robert Martin", "0002AA", 2),
            ("Algorithms", "Thomas Cormen", "0003AA", 1),
        ]

        for t, a, i, q in sample_books:
            c.execute("INSERT INTO books (title, author, isbn, quantity) VALUES (?,?,?,?)",
                      (t, a, i, q))

        conn.commit()
        conn.close()


init_db()

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result


class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def is_empty(self):
        return len(self.items) == 0

    def __len__(self):
        return len(self.items)


borrow_queue = Queue()
book_map = {}
active_borrows_vector = []



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"].strip()
        author = request.form["author"].strip()
        isbn = request.form["isbn"].strip()
        qty = int(request.form["quantity"])

        if len(isbn) != 6:
            flash(" ISBN must be exactly 6 characters.")
            return redirect(url_for("add_book"))

        conn = get_conn()
        try:
            conn.execute("INSERT INTO books (title, author, isbn, quantity) VALUES (?,?,?,?)",
                         (title, author, isbn, qty))
            conn.commit()
            flash(" Book added successfully!")
        except sqlite3.IntegrityError:
            flash(" ISBN already exists!")
        finally:
            conn.close()

        return redirect(url_for("list_books"))

    return render_template("add_book.html")


@app.route("/books")
def list_books():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT 
            b.*,
            (SELECT COUNT(*) FROM borrows WHERE isbn=b.isbn AND return_date IS NULL) AS borrowedCount,
            (b.quantity - (SELECT COUNT(*) FROM borrows WHERE isbn=b.isbn AND return_date IS NULL)) AS remainingQty,
            (SELECT GROUP_CONCAT(user_id, ', ') 
             FROM borrows 
             WHERE isbn=b.isbn AND return_date IS NULL) AS borrowedBy
        FROM books b
        ORDER BY b.title
    """)
    books = c.fetchall()
    conn.close()

    linked_books = LinkedList()
    global book_map
    book_map.clear()

    for b in books:
        data = {
            "title": b["title"],
            "author": b["author"],
            "isbn": b["isbn"],
            "quantity": b["quantity"],
            "remainingQty": b["remainingQty"],
            "borrowedBy": b["borrowedBy"] if b["borrowedBy"] else "—"
        }
        linked_books.append(data)
        book_map[b["isbn"]] = data

    return render_template("list_books.html", books=linked_books.to_list())


@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    if request.method == "POST":
        isbn = request.form["isbn"].strip()
        user_id = request.form["userId"].strip()

        borrow_queue.enqueue({"isbn": isbn, "user": user_id, "time": datetime.now()})
        flash(f" Borrow request added to queue! (Pending: {len(borrow_queue)})")
        return redirect(url_for("process_borrow"))

    return render_template("borrow.html")


@app.route("/process_borrow")
def process_borrow():
    if borrow_queue.is_empty():
        flash(" No pending borrow requests.")
        return redirect(url_for("list_books"))

    req = borrow_queue.dequeue()
    isbn, user_id = req["isbn"], req["user"]

    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE isbn=?", (isbn,))
    book = c.fetchone()

    if not book:
        flash(" Book not found.")
        conn.close()
        return redirect(url_for("list_books"))

    c.execute("SELECT COUNT(*) FROM borrows WHERE isbn=? AND return_date IS NULL", (isbn,))
    active = c.fetchone()[0]

    if active >= book["quantity"]:
        flash(f" No copies left for {book['title']}.")
    else:
        borrow_date = datetime.now().isoformat(timespec="seconds")
        c.execute("INSERT INTO borrows (user_id, isbn, borrow_date) VALUES (?,?,?)",
                  (user_id, isbn, borrow_date))
        conn.commit()

        active_borrows_vector.append({
            "isbn": isbn,
            "user": user_id,
            "borrow_date": borrow_date
        })

        flash(f" {user_id} successfully borrowed {book['title']}")
    conn.close()
    return redirect(url_for("list_books"))


@app.route("/return", methods=["GET", "POST"])
def return_book():
    if request.method == "POST":
        isbn = request.form["isbn"].strip()
        user_id = request.form["userId"].strip()

        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM borrows
            WHERE isbn=? AND user_id=? AND return_date IS NULL
        """, (isbn, user_id))
        record = c.fetchone()

        if not record:
            flash(" No active borrow found.")
            conn.close()
            return redirect(url_for("return_book"))

        return_date = datetime.now().isoformat(timespec="seconds")
        c.execute("UPDATE borrows SET return_date=? WHERE id=?", (return_date, record["id"]))
        conn.commit()
        conn.close()

        for b in active_borrows_vector:
            if b["isbn"] == isbn and b["user"] == user_id:
                active_borrows_vector.remove(b)
                break

        flash(" Book returned successfully!")
        return redirect(url_for("list_books"))

    return render_template("return.html")


@app.route("/reviews", methods=["GET"])
def reviews():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT r.*, b.title AS book_title
        FROM reviews r
        LEFT JOIN books b ON r.isbn = b.isbn
        ORDER BY r.created_at DESC
    """)
    data = c.fetchall()
    conn.close()
    return render_template("review.html", reviews=data)


@app.route("/add_review", methods=["POST"])
def add_review():
    isbn = request.form["isbn"]
    user_id = request.form["userId"]
    rating = int(request.form["rating"])
    comment = request.form["comment"]

    conn = get_conn()
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO reviews (isbn, user_id, rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (isbn, user_id, rating, comment, created_at))
    conn.commit()
    conn.close()

    return jsonify({
        "isbn": isbn,
        "user_id": user_id,
        "rating": rating,
        "comment": comment,
        "created_at": created_at
    })


@app.route("/borrows")
def borrows():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT br.*, b.title AS book_title
        FROM borrows br
        LEFT JOIN books b ON br.isbn = b.isbn
        ORDER BY br.borrow_date DESC
    """)
    data = c.fetchall()
    conn.close()
    return render_template("borrows.html", borrows=data)


@app.route("/debug")
def debug_info():
    return {
        "queue_length": len(borrow_queue),
        "book_map_keys": list(book_map.keys()),
        "active_borrows_vector": active_borrows_vector
    }

if __name__ == "__main__":
    app.run(debug=True)
