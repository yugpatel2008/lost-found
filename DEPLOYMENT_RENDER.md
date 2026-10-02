# Render Deployment Guide for Indus Uni. Lost & Found

This Django application is pre-configured for seamless deployment on **Render.com**.

---

## Deployment Option 1: Automatic Blueprint (Recommended)

1. Push your repository to **GitHub** or **GitLab**.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** → **Blueprint**.
4. Connect your repository.
5. Render will automatically detect [`render.yaml`](file:///c:/Users/cyug1/Downloads/AIT-hackathon-shared-main/AIT-hackathon-shared-main/Lost_Found/render.yaml) and provision:
   - Web Service (Python 3.11 with Gunicorn & WhiteNoise)
   - Free PostgreSQL Database (`lost-found-db`)
6. Click **Apply**. Deployment will complete automatically.

---

## Deployment Option 2: Manual Web Service Setup

If you prefer to configure the Web Service manually on Render:

1. Create a **New Web Service** on Render and link your Git repository.
2. Configure the following fields:
   - **Environment**: `Python`
   - **Build Command**: `./build.sh` (or `bash build.sh`)
   - **Start Command**: `gunicorn Lost_Found.wsgi:application`
3. Add the following **Environment Variables** under *Environment*:

| Environment Variable | Recommended Value | Note |
|---|---|---|
| `SECRET_KEY` | *(Click Generate or paste a long random string)* | Required |
| `DEBUG` | `False` | Recommended for production |
| `DATABASE_URL` | `postgresql://...` | Copy from Render PostgreSQL connection string |
| `CLOUDINARY_URL` | `cloudinary://API_KEY:API_SECRET@CLOUD_NAME` | Optional (For uploaded media storage) |
| `EMAIL_HOST_USER` | `your-email@gmail.com` | Optional (For email notifications) |
| `EMAIL_HOST_PASSWORD` | `your-app-password` | Optional (Gmail App Password) |

---

## Pre-configured Production Setup Included

- **WSGI Server**: [Gunicorn](file:///c:/Users/cyug1/Downloads/AIT-hackathon-shared-main/AIT-hackathon-shared-main/Lost_Found/Procfile) (`web: gunicorn Lost_Found.wsgi:application`)
- **Static Files**: [WhiteNoise](file:///c:/Users/cyug1/Downloads/AIT-hackathon-shared-main/AIT-hackathon-shared-main/Lost_Found/Lost_Found/settings.py) (`whitenoise.middleware.WhiteNoiseMiddleware`)
- **Build Script**: [`build.sh`](file:///c:/Users/cyug1/Downloads/AIT-hackathon-shared-main/AIT-hackathon-shared-main/Lost_Found/build.sh) (Automates `pip install`, `collectstatic`, and `migrate`)
- **PostgreSQL Ready**: [`dj-database-url`](file:///c:/Users/cyug1/Downloads/AIT-hackathon-shared-main/AIT-hackathon-shared-main/Lost_Found/requirements.txt) & `psycopg2-binary` included
- **Render Host & CSRF**: Dynamic support for `RENDER_EXTERNAL_HOSTNAME` and `*.onrender.com`
