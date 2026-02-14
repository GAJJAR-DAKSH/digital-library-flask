# 📚 Digital Library Management System

A modern **Flask-based Digital Library Web App** that allows users to manage books, borrow/return them, and share reviews — built with clean UI and integrated Data Structures (Queue, LinkedList) for advanced functionality.

---

## 🚀 Features

- ✅ Add and manage books
- ✅ Borrow & Return system with queue processing
- ✅ Book availability tracking
- ✅ Search by title and author
- ✅ ⭐ AJAX-based review system
- ✅ Borrow history tracking
- ✅ Clean responsive UI (Bulma + Custom CSS)
- ✅ Data Structures integrated:

* Queue → Borrow requests
* LinkedList → Book listing
* Dictionary Map → Fast lookup

---

## 🧠 Tech Stack

**Backend**

* Python
* Flask
* SQLite3

**Frontend**

* HTML5
* CSS3
* Bulma Framework
* Custom CSS

**Concepts Used**

* RESTful Routing
* SQL Aggregation Queries
* AJAX (Fetch API)
* Data Structures & Algorithms

---

## 📂 Project Structure

```
digital-library-flask/
│
├── app.py
├── templates/
│   ├── index.html
│   ├── add_book.html
│   ├── borrow.html
│   ├── return.html
│   ├── list_books.html
│   ├── review.html
│   └── search pages...
│
├── static/
│   └── custom.css
│
├── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```
git clone https://github.com/YOUR_USERNAME/digital-library-flask.git
cd digital-library-flask
```

### 2️⃣ Install Dependencies

```
pip install flask
```

### 3️⃣ Run Application

```
python app.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

## 📚 Main Routes

| Route      | Description        |
| ---------- | ------------------ |
| `/`        | Home dashboard     |
| `/add`     | Add new book       |
| `/books`   | View library       |
| `/borrow`  | Borrow book        |
| `/return`  | Return book        |
| `/reviews` | View & add reviews |
| `/borrows` | Borrow history     |

---

## ⭐ Highlights

* Uses SQL subqueries to calculate **remaining quantity** dynamically.
* Borrow system uses a **Queue data structure** for processing.
* Reviews are added asynchronously using **AJAX Fetch API**.
* Designed with reusable card-based UI components.

---


## 🔮 Future Improvements

* User authentication system (Login/Signup)
* Admin dashboard analytics
* Live search suggestions

---

## 👨‍💻 Author

**Daksh Gajjar**
Frontend & Python Developer

---

⭐ If you like this project, consider giving it a star!
