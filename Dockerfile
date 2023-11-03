FROM odoo:16.0

USER root
WORKDIR /odoo

COPY requirements-portal.txt requirements-portal.txt
RUN pip3 install --no-cache-dir -r requirements-portal.txt
COPY portal-addons /mnt/extra-addons
