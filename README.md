# VoIP Operations Portal

A production-ready VoIP Operations Management Portal built with Flask, PostgreSQL, Gunicorn and BookStack.

---

# Features

- User Authentication
- Accounts Management
- Operation Plans
- Check Items
- Change Requests
- Incident Management
- File Attachments
- PostgreSQL Database
- Gunicorn
- Systemd Service
- Automatic Installer
- Docker BookStack Knowledge Base

---

# Architecture

```
Ubuntu Server
│
├── PostgreSQL
├── Flask
├── Gunicorn
├── Systemd
├── Upload Storage
└── Docker
      ├── BookStack
      └── MariaDB
```

---

# Requirements

- Ubuntu 22.04 LTS
- Root privileges
- Internet connection

---

# Installation

Clone the repository:

```bash
git clone git@github.com:IslamEdrees/VoIP-Operations-Portal-Books-Plan.git
cd VoIP-Operations-Portal-Books-Plan
```

Run the installer:

```bash
sudo ./install.sh
```

The installer automatically installs:

- Python
- PostgreSQL
- Docker
- BookStack
- Flask dependencies
- Gunicorn
- Systemd Service
- Database Schema
- Administrator Account

---

# Services

Portal

```
http://SERVER_IP:6880
```

BookStack

```
http://SERVER_IP:6875
```

---

# Project Structure

```
app/
scripts/
scripts/installer/
docker/
systemd/
docs/
uploads/
backups/
migrations/
```

---

# Installer Modules

| Step | Description |
|------|-------------|
|01|System Validation|
|02|Python Environment|
|03|PostgreSQL|
|04|Docker Engine|
|05|BookStack|
|06|Portal|
|07|Systemd|
|08|Database|
|09|Administrator|
|10|Health Check|

---

# Backup

```bash
sudo ./backup.sh
```

---

# Restore

```bash
sudo ./restore.sh
```

---

# Upgrade

```bash
sudo ./upgrade.sh
```

---

# Uninstall

```bash
sudo ./uninstall.sh
```

---

# Technology Stack

- Python 3.10
- Flask
- SQLAlchemy
- PostgreSQL 14
- Gunicorn
- Docker
- BookStack
- MariaDB
- Systemd

---


<img width="1889" height="642" alt="image" src="https://github.com/user-attachments/assets/2c6d817f-1262-4860-bebb-a876a8ef2504" />


<img width="1907" height="903" alt="image" src="https://github.com/user-attachments/assets/bd11115c-7540-441d-9eb8-61c9c0b7ef4d" />

<img width="1900" height="893" alt="image" src="https://github.com/user-attachments/assets/a879c67c-b8a6-4c72-a9ba-4ff642dcb419" />

<img width="1886" height="903" alt="image" src="https://github.com/user-attachments/assets/4f69a7a3-1f91-4285-b156-f336217eafc3" />

---

# Author

Edrees Hassan

VoIP Engineer

GitHub

https://github.com/IslamEdrees
