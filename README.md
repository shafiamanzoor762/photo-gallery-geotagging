
# 📸 PhotoGallery Backend API

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-orange.svg)
![SQL Server](https://img.shields.io/badge/SQL--Server-database-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mobile-lightgrey.svg)

> **PhotoGallery Backend API** is a Flask-based application for managing and syncing photos with **geotagging**, **face detection**, **face recognition** (using `face_recognition` model), and **EXIF metadata extraction**. It leverages **SQL Server** and **Flask-SQLAlchemy** to store and serve data in JSON format, enabling seamless integration with both Mobile and Windows interfaces.

---

## 🚀 Features

- 🔍 **Face Detection & Recognition** using the `face_recognition` library  
- 🗺️ **Geotagging support** via EXIF metadata  
- 🧠 **EXIF Tag Parsing** for date, location, and device metadata  
- 🗂️ **Smart Photo Grouping** by person, location, and event  
- ⚙️ **API-Driven Architecture** with Flask  
- 🗃️ **SQL Server** for scalable and structured data storage  
- 🔁 **Photo Sync** between local systems and apps (Mobile/Desktop)

---

## 📁 Project Structure

```bash
photo-gallery-geotagging/
│
├── Model/
├── Controller/
├── stored-faces/
├── Database_Scripts/
├── config.py
├── request_methods.txt
├── router.py
├── directory.env
├── requirements.txt
├── haarcascade_frontalface_default.xml
└── README.md
````

---

## 🛠️ Getting Started

### ✅ Prerequisites

* Python 3.10+
* Flask
* SQL Server
* `face_recognition` library
* `Flask-SQLAlchemy`
* `Pillow`, `exifread`, and other dependencies

### 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/shafiamanzoor762/photo-gallery-geotagging.git
cd photo-gallery-geotagging
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure your SQL Server database URI in `config.py`.

---

## ▶️ Running the Application

```bash
python router.py
```

The API server will start on `http://127.0.0.1:5000` or `http://0.0.0.0:5000`.

---

## 📌 Example API Endpoints

* See requests_methods.txt for details about endpoints.

---

## 🧠 Technologies Used

* `Flask` — Python microframework
* `face_recognition` — Face detection & recognition
* `SQL Server` — Database management
* `Flask-SQLAlchemy` — ORM for SQL Server
* `EXIF` & `Pillow` — Metadata handling

---

## 🔐 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## 📚 Resources

* [face\_recognition GitHub](https://github.com/ageitgey/face_recognition)
* [Flask Documentation](https://flask.palletsprojects.com/)
* [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
* [Working with EXIF Tags](https://exiftool.org/)

---

## ✨ Acknowledgements

Thanks to the developers and open-source communities behind `face_recognition`, Flask, and EXIF tools that made this project possible.



## 👥 Team Info

### Members:
  * [Aimen](https://github.com/AIMEN-10)
  * [Shafia](https://github.com/shafiamanzoor762)
  * [Iqra](https://github.com/iqraraja1)
  * [Rafiya](https://github.com/RafiaTariq01)
##### Feel free to connect with us on GitHub or reach out for collaboration!
