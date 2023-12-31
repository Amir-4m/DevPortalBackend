import getpass

import boto3
from django.db.backends.mysql import base

from apps.django_iam_dbauth.utils import resolve_cname


class DatabaseWrapper(base.DatabaseWrapper):
    def get_connection_params(self):
        params = super().get_connection_params()
        enabled = params.pop('use_iam_auth', None)
        region = params.pop('region', None)
        if enabled:
            rds_client = boto3.client(
                service_name='rds',
                region_name=region
            )

            hostname = params.get('host')
            # hostname = resolve_cname(hostname) if hostname else "localhost"

            params["password"] = rds_client.generate_db_auth_token(
                DBHostname=hostname,
                Port=params.get("port", 3306),
                DBUsername=params.get("user"),
            )

        return params
