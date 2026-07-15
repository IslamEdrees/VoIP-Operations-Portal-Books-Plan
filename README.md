# VoIP Operations Portal

## Features

- Accounts
- Operation Plans
- Check Items
- Change Requests
- Incident Management
- File Attachments
- Flask
- PostgreSQL
- Gunicorn
- Systemd

## Installation

```bash
git clone git@github.com:IslamEdrees/VoIP-Operations-Portal-Books-Plan.git
cd VoIP-Operations-Portal-Books-Plan

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

systemctl start voip-operations
```
