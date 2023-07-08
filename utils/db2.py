import socket

import google_auth_httplib2
import httplib2
import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest
import json
socket.setdefaulttimeout(15 * 60)

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1DM0oh1qpZZFqnYSWsrBCVnBkZvhDw4VrtOs2g-ycShI"
SHEET_NAME = "messages_chatbot"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
Json ={
  "type": "service_account",
  "project_id": "peppy-web-387119",
  "private_key_id": "f38d50c8821086e90eb8d2af90bb7b7308505cc8",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDBaDgVb2lltrBG\nvKr0ABpZA1bOAHKTfW3RfxEIhfGdiSge54ETT87qBONBo9wlt9oDkl5L+rus/wip\n3CTedSb8wTSn/jOoXRcdb0B3WQdBqFAXC1zbdxdytIuIuBBrAlR0jyuRL+CQCSBY\nn652xELm9/yYU5sr7SFEEkpu2+R3DYMdg3vBYEBPFMVQaRy8VXys4U3V4lYKTDmE\nkkTBu1LzfMFDHiPtEJcG2exs1gNDuMB/s3FX0Mdsgj53sUKH0ahcOM/NfLeWJS7+\n9dJNrip/dIHb5gqefs6lz9p9Aud0JWhVOMENIwUKvyG5AZLKyQakQddgzxcVLtR+\nqlmgWCHlAgMBAAECggEAYBArVx482/v3J1NbmBEbBR5e9bgMMMzKiJVT+QdKgKRY\n7KyxFE3+KIdf90DzvjpIy6BePN/fauhLvc6t815+DGnMhSqCLvx52DFjdEQgkhCP\nIzsOFqXa3Crn6XL/GJ+SIkjga187617VFZ/OkIgf8Me4y1IvjwxbiwuIs/J9UlHj\nPh4BsuX5EnpVnCzSJICnvNatA+3PftmBtcosS3WZnEcen8wq3BzUUt+lzpvD+nW2\ne0m3mejb3vhybst+v0IZAcClGO4PpbJSvTgLD1oulhYk5biRKJP9hbSJaqHFjQib\nhrGjSxeF2Ep453uf6JOjhp89gF9Vb/Dx8rclA9WF6wKBgQDh22clsDc3s5hM5JdH\n/6xiydHJkuDa1nNsC6iyBYb/ueow1aUgq14OEfO/edmDXKsuFgNFIcbqzUpdFITy\nRMUvy0xzU196H0uSZd/96H4gPLQDDBJ+vo3PalfLoIgnhNOXnNsZKuZ30hE4jyKj\nrBUQdXOKgp/J6H+6/HU2Tdd+dwKBgQDbOCL3pqeLpjrUOBFvrxeOOtswC1mxjnYQ\nWG3dUxnDKCOd94n0mVhnoyLwXP+qFPHPkyLhc1WeMfh2UJYE+DErGzTzjoBoClkm\ncihsSU5luu1MoDYUxzXehcCVSYLKKwR4yAXPU316KdEjW2OhyH4MyoYmljXktG7x\nNrtKxUStgwKBgC6X5J+RytJi6nhycAMaa6W1nOHIuzpqI0WW4iZXnZID+Jw6duZW\ndADTE0XdDVJcO7Q2NlZ8sVyfHUg2g3a3WTaS6iKggIHhEuYQvjTTUbG01C4Mv4QG\nK5suhQ4s/+mnLT+JzGlUwFbXr1XLsYmyZmYO1NcuO2ib3j3k9wlM5bfhAoGBAMM0\nq76HAi7SaRRMkQo4ies28bNIiCgZyXwoojwxIYGsnnqt0ISkgBpZJGWRCoBzghfq\n12aWgykJKkyA2fW25GGUKoSu4hzDCju379LtPAhOebx/9WhvM8Lgq2rEONi5kZPT\n2YiSuessjXTEjmWj2MqfFPILVBZBrYDR0dl07ADtAoGAIP0Hovq87hk0e66hxHzz\nrNCh2JOzZ7o01CP693EpBUYK3HWGI6IyHfshq0XfCr+TG/19LYt68F5bSLwVQer3\nF8dz7IsNnna9vk+zvS3Eoi86hO9VCRnGodhd8zVuj7tdXuLxmepH9PmE9c/7gJXg\nTCDXF9RI7r9hy5KaKpkqgec=\n-----END PRIVATE KEY-----\n",
  "client_email": "gcpgooglesheets@peppy-web-387119.iam.gserviceaccount.com",
  "client_id": "109513564103722430551",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gcpgooglesheets%40peppy-web-387119.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

@st.cache_resource()
def connect():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
    Json,
        scopes=[SCOPE],
    )

    # Create a new Http() object for every request
    def build_request(http, *args, **kwargs):
        new_http = google_auth_httplib2.AuthorizedHttp(
            credentials, http=httplib2.Http()
        )
        return HttpRequest(new_http, *args, **kwargs)

    authorized_http = google_auth_httplib2.AuthorizedHttp(
        credentials, http=httplib2.Http()
    )
    service = build(
        "sheets",
        "v4",
        requestBuilder=build_request,
        http=authorized_http,
    )
    gsheet_connector = service.spreadsheets()
    return gsheet_connector


def collect(gsheet_connector) -> pd.DataFrame:
    values = (
        gsheet_connector.values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range="!A:B",
        )
        .execute()
    )

    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]
    return df


def insert(gsheet_connector, row) -> None:
    values = (
        gsheet_connector.values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range="!A:B",
            body=dict(values=row),
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )
