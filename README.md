# Aayu Language 🚀

**Aayu** is a brand new, highly readable, intent-driven programming language designed to bridge the gap between human thought and executable code.

## 🧠 How it Works

Aayu follows a clean, modern compilation pipeline:
**Human Intent** → **Aayu Code** → **AST (Abstract Syntax Tree)** → **Execution**

The language features a custom lexer, parser, and interpreter, enabling features like structured records, variable declarations, loops, error handling, and tasks (functions) in a natural syntax.

---

## 📂 Projects

### 1. Library Management System (Pure Aayu)
This repository contains a fully functional **Library Management System** built entirely in **Pure Aayu** to demonstrate the language's capabilities.

**Features Implemented:**
- `Student` and `Book` entity records.
- Modularized code using Aayu's `use` keyword.
- Custom tasks for borrowing and returning books.

#### Example: `student.aayu`
```aayu
record Student.
name
age
student_id
end.
```

#### Example: `main.aayu`
```aayu
use student.
use book.
use borrow.
use return.

Book b1 is.
  title "The Alchemist"
  author "Paulo Coelho"
  book_id 101
  available 1
end.

Student s1 is.
  name "Ayush"
  age 20
  student_id 1
end.

run borrow_book with b1 and s1.
run return_book with b1 and s1.
```

---

## 🚀 Running the Project

Ensure you have Python installed to run the interpreter.

```bash
python run.py projects/library_management/main.aayu
```

**Expected Output:**
```text
Student Added
Book Added
Book Borrowed
Book Returned
```

---

## 🛠️ Future Roadmap (Phase 2)

Aayu is rapidly evolving! The next steps for the language include:
1. **Building more Real-World Projects:**
   - Student Management System
   - Task Manager
   - Mini Web Backend
2. **Aayu Specification v1.0:** Freezing the syntax and features.
3. **VS Code Extension:** Adding official syntax highlighting and IntelliSense for `.aayu` files.
4. **GitHub Linguist PR:** Registering Aayu as an official GitHub language!