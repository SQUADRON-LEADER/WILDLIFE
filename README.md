# 🐾 WildGuard - National Park Wildlife Conservation System

🌍 **WildGuard** is a powerful desktop application built with **Python + Tkinter**, designed to protect wildlife, empower donors, and support national park management.

> 🚨 Save Endangered Species • 🗺️ Track Habitats • 📊 Visualize Conservation Progress

---

## 🌟 Key Features

### 🏠 Dashboard (Home Screen)

* 📊 Real-time conservation statistics powered by **Matplotlib**
* 🦓 Wildlife counts, activity summaries, and module shortcuts

### 🐯 Species Directory

* 📁 Add, update, and delete species data effortlessly
* 📸 Store details like scientific name, habitat, threat level, and images
* 🗃️ Uses **SQLite3** for efficient data storage

### 🗺️ Habitat Map Viewer

* 🧭 Interactive maps created with **Folium** and **WebView**
* 🎯 Filter species by region or threat category

### 💬 Chatbot Assistant

* 🤖 Get instant assistance using a **rule-based** or **NLTK-powered** chatbot
* 📚 Supports help for species data, donors, and volunteers

### 🔐 Authentication System

* 🔑 Secure **Admin & User** login with role-based access
* 🧱 SQLite-backed authentication for reliability

### 💰 Donor Dashboard

* 💳 Record and manage donor contributions
* 📈 Track funding impact with progress bars and charts
* 📤 Export reports in **PDF** or **CSV** formats

### 💪 Volunteer Management

* 📝 Register, assign, and manage volunteer activities
* 📅 Role assignment with status tracking
* 📧 Send automated notifications using **smtplib**

### 🎨 Modern UI/UX Design

* ✨ Built with **Tkinter + ttk** for an intuitive interface
* 🎨 Image-based buttons, hover effects, and keyboard shortcuts
* 🧩 Accessible and visually appealing layout

---

## 🛠️ Tech Stack

| 🧪 Tool          | ⚙️ Purpose          |
| ---------------- | ------------------- |
| Python 3.x       | Core Programming    |
| Tkinter + ttk    | Graphical Interface |
| SQLite3          | Database Management |
| Matplotlib       | Data Visualization  |
| Folium + WebView | Interactive Mapping |
| smtplib          | Email Notifications |
| unittest         | Testing Framework   |

---

## 📁 Project Structure

```
wildguard/
├── assets/               # Images, icons, and map resources
├── database/             # SQLite database files
├── modules/              # Backend logic modules
│   ├── species.py
│   ├── donor.py
│   └── volunteer.py
├── gui/                  # User interface scripts
│   ├── dashboard.py
│   └── login.py
├── main.py               # Application entry point
└── requirements.txt      # Project dependencies
```

---

## 🚀 Getting Started

### 🧩 Installation

```bash
git clone https://github.com/your-username/wildguard-python
cd wildguard-python
pip install -r requirements.txt
python main.py
```

### ⚙️ Prerequisites

* Python 3.8 or above
* Pip package manager
* Internet connection for map loading

---

## 🧪 Testing & Validation

* ✅ GUI flow tested manually
* 🧪 Automated tests via `unittest`
* 📋 Edge case handling (duplicate donors, null values, invalid data)

---

## 🧬 ER Diagram Summary

* ✅ **15 Entities** including Species, Admin, Donor, and Volunteer
* 🔗 Includes primary and foreign keys
* ⚙️ Demonstrates participation and mapping constraints
* 🌳 Incorporates **specialization**, **generalization**, and **aggregation**

---

## 🖼️ Screenshots

![Dashboard](https://github.com/user-attachments/assets/24ca527a-854a-4346-a720-72d269f7c86e)
![Directory](https://github.com/user-attachments/assets/f8cd253a-b3d0-4730-8e5a-22ec3be9b3eb)
![Charts](https://github.com/user-attachments/assets/628deb2a-ce05-4ea6-bfb3-3b2ea4336d52)
![Login](https://github.com/user-attachments/assets/890a512a-5394-43af-85ec-dadff217a57c)
![Donor Panel](https://github.com/user-attachments/assets/3cb9379e-1d91-4339-86f5-5448bedd6ab5)
![Volunteer Management](https://github.com/user-attachments/assets/c225102b-8702-4919-8798-435506dcb115)
![Map Viewer](https://github.com/user-attachments/assets/1e82747d-2bc6-4c39-82e7-7088b57984fc)

---

## 🤝 Contributors

| Name       | Role           |
| ---------- | -------------- |
| **Aayush** | Lead Developer |
| **Ashmit** | Core Developer |

---

## 📬 Contact

📧 **Email:** [wildguard.team@gmail.com](mailto:wildguard.team@gmail.com)
🐛 **Report Issues:** [Open on GitHub](https://github.com/your-username/wildguard-python/issues)

---

## 📜 License

### MIT License

```
MIT License

Copyright (c) 2025 WildGuard Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

### 🐾 WildGuard – *Protecting Wildlife, Preserving the Future.* 🌿
