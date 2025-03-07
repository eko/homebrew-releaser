import subprocess
from typing import Tuple

import requests
import woodchips

from homebrew_releaser.constants import (
    GITHUB_OWNER,
    GITHUB_REPO,
    GITHUB_TOKEN,
    LOGGER_NAME,
    SUBPROCESS_TIMEOUT,
)
from homebrew_releaser.utils import Utils


class Checksum:
    @staticmethod
    def get_checksum(tar_filepath: str) -> Tuple[str, str]:
        """Gets the checksum of a file."""
        logger = woodchips.get(LOGGER_NAME)

        try:
            command = ['shasum', '-a', '256', tar_filepath]
            output = subprocess.check_output(
                command,
                stdin=None,
                stderr=None,
                timeout=SUBPROCESS_TIMEOUT,
            )
            checksum = output.decode().split()[0]
            checksum_file = output.decode().split()[1]
            logger.debug(f'Checksum generated successfully: {checksum}')
        except subprocess.TimeoutExpired as error:
            raise SystemExit(error)
        except subprocess.CalledProcessError as error:
            raise SystemExit(error)

        return checksum, checksum_file

    @staticmethod
    def upload_checksum_file():
        """Uploads a `checksum.txt` file to the latest release of the repo."""
        logger = woodchips.get(LOGGER_NAME)

        checksum_file = 'checksum.txt'  # This file was created elsewhere

        latest_release_url = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest'
        latest_release_response = Utils.make_get_request(latest_release_url)
        latest_release_id = latest_release_response.json()['id']

        with open('checksum.txt', 'rb') as filename:
            checksum_binary = filename.read()

        upload_url = f'https://uploads.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/{latest_release_id}/assets?name={checksum_file}'  # noqa
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'text/plain',
        }

        try:
            _ = requests.post(
                upload_url,
                headers=headers,
                data=checksum_binary,
            )
            logger.info(f'checksum.txt uploaded successfully to {GITHUB_REPO}.')
        except requests.exceptions.RequestException as error:
            raise SystemExit(error)
