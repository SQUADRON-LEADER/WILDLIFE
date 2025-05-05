# 🐾 WildGuard - National Park Wildlife Conservation System (Python Tkinter)

🌍 **WildGuard** is a feature-rich desktop application developed using **Python + Tkinter**, designed to protect wildlife, empower donors, and support national park management.

> 🚨 Save Endangered Species • 🗺️ Track Habitats • 📊 Visualize Progress

---

## 🌟 Features

### 🏠 Dashboard (Home Screen)

📊 Track conservation stats in real-time with Matplotlib
🦓 Wildlife counts, activity overview, and module shortcuts

### 🐯 Species Directory

📁 Add, update, delete & manage species info
📸 Include scientific names, habitat, threat level & images
🗃️ SQLite-powered data storage

### 🗺️ Habitat Map Viewer

🧭 View habitat locations using embedded maps (Folium + WebView)
🎯 Filter species by region or threat level

### 💬 Chatbot Assistant

🤖 Ask questions and get guided help
📚 Built using rule-based logic or `nltk`

### 🔐 Authentication System

🔑 Admin & User role-based access
🔐 Secure SQLite login system

### 💰 Donor Dashboard

💳 Record contributions, show progress bars
📈 View impact charts
📤 Export donor reports to PDF/CSV

### 💪 Volunteer Panel

📝 Register & manage volunteers
📅 Assign conservation roles
📧 Email notifications via `smtplib`

### 🎨 Modern UI/UX

✨ Tkinter + ttk widgets for clean design
🎨 Image-based buttons and hover effects
🧩 Keyboard accessibility

---

## 🛠️ Tech Stack

| 🧪 Tool          | ⚙️ Usage             |
| ---------------- | -------------------- |
| Python 3.x       | Programming Language |
| Tkinter + ttk    | GUI Development      |
| SQLite3          | Lightweight Database |
| Matplotlib       | Graphs and Charts    |
| Folium + WebView | Habitat Mapping      |
| smtplib          | Email Notifications  |
| `unittest`       | Module Testing       |

---

## 📁 Project Structure

```
wildguard/
├── assets/               # Images, icons, maps
├── database/             # SQLite DB files
├── modules/              # Core backend modules
│   ├── species.py
│   ├── donor.py
│   └── volunteer.py
├── gui/                  # UI logic
│   ├── dashboard.py
│   └── login.py
├── main.py               # Main driver script
└── requirements.txt      # Dependencies
```

---

## 🚀 Getting Started

🔧 **Installation Steps**

```bash
git clone https://github.com/your-username/wildguard-python
cd wildguard-python
pip install -r requirements.txt
python main.py
```

---

## 🧪 Testing & Validation

* ✅ Manual testing for GUI flow
* 🧪 Unit testing using `unittest`
* 📋 Check edge cases (null entries, duplicate donors, etc.)

---

## 🧬 ER Diagram Overview

* ✅ 15 Entities: Species, Admin, Donor, Volunteer, etc.
* 📌 Key Features: Primary keys, foreign keys, partial/total participation
* 🌳 Advanced: Specialization, generalization, aggregation

---

## 🖼️ Screenshots

![Screenshot 2025-05-05 093832](https://github.com/user-attachments/assets/24ca527a-854a-4346-a720-72d269f7c86e)
![Screenshot 2025-05-05 093853](https://github.com/user-attachments/assets/f8cd253a-b3d0-4730-8e5a-22ec3be9b3eb)
![Screenshot 2025-05-05 093912](https://github.com/user-attachments/assets/628deb2a-ce05-4ea6-bfb3-3b2ea4336d52)
![Screenshot 2025-05-05 093921](https://github.com/user-attachments/assets/890a512a-5394-43af-85ec-dadff217a57c)
![Screenshot 2025-05-05 093931](https://github.com/user-attachments/assets/3cb9379e-1d91-4339-86f5-5448bedd6ab5)
![Screenshot 2025-05-05 093946](https://github.com/user-attachments/assets/c225102b-8702-4919-8798-435506dcb115)
![Screenshot 2025-05-05 093954](https://github.com/user-attachments/assets/1e82747d-2bc6-4c39-82e7-7088b57984fc)
![Screenshot 2025-05-05 094014](https://github.com/user-attachments/assets/e246edaa-9b54-4d60-a302-8b5deba3fb02)
![Screenshot 2025-05-05 094041](https://github.com/user-attachments/assets/e67df49b-bf24-4537-b8c9-193d84b35bcf)
![Screenshot 2025-05-05 094053](https://github.com/user-attachments/assets/b61d37d7-804e-42e8-be45-acb1338d22e8)



> 🖼️ Add your screenshots to the `assets/` folder for display.

---

## 🤝 Contributors

* 👨‍💻 **Aayush** – Lead Developer
* 👥 **Ashmit** - Core Developer

---

## 📬 Contact Us

📧 [wildguard.team@gmail.com](mailto:wildguard.team@gmail.com)
🐛 Found a bug? [Open an Issue](https://github.com/your-username/wildguard-python/issues)

---

## 📜 License

MIT License – Free for personal and academic use.

---

### 🐾 WildGuard – *Protecting Wildlife. Preserving the Future.* 🌿
