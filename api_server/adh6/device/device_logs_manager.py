import typing as t
import logging
import re

from adh6.entity import DeviceFilter, Member, MemberStatus
from adh6.decorator import log_call
from adh6.exceptions import LogFetchError

if t.TYPE_CHECKING:
    from adh6.member import MemberManager

from .interfaces import DeviceRepository, LogsRepository

class DeviceLogsManager:
    def __init__(self, device_repository: DeviceRepository, logs_repository: LogsRepository, member_manager: 'MemberManager') -> None:
        self.logs_repository = logs_repository
        self.device_repository = device_repository
        self.member_manager = member_manager
    
    @log_call
    def get(self, member: Member, dhcp: bool = False) -> t.List[t.Any]:
        devices, _ = self.device_repository.search_by(limit=20, offset=0, device_filter=DeviceFilter(member=member.id))
        try:
            logs = self.logs_repository.get(member=member, devices=devices, dhcp=dhcp)
        except LogFetchError:
            logging.warning("log_fetch_failed")
            logs = []
        return logs

    @log_call
    def get_logs(self, login: str, dhcp=False) -> t.List[str]:
        # Check that the user exists in the system.
        member = self.member_manager.get_by_login(login)
        logs = self.get(member=member, dhcp=dhcp)

        return list(map(
            lambda x: "{} {}".format(x[0], x[1]),
            logs
        ))


    @log_call
    def get_statuses(self, login: str) -> t.List[MemberStatus]:
        # Check that the user exists in the system.
        member = self.member_manager.get_by_login(login)

        logs = self.get(member=member, dhcp=False)
        device_to_statuses = {}
        last_ok_login_mac = {}

        def add_to_statuses(status, timestamp, mac):
            if mac not in device_to_statuses:
                device_to_statuses[mac] = {}
            if status not in device_to_statuses[mac] or device_to_statuses[mac][
                status].last_timestamp < timestamp:
                device_to_statuses[mac][status] = MemberStatus(status=status, last_timestamp=timestamp,
                                                                comment=mac)

        prev_log = ["", ""]
        for log in logs:
            if "Login OK" in log[1]:
                match = re.search(r'.*?Login OK:\s*\[(.*?)\].*?cli ([a-f0-9|-]+)\).*', log[1])
                if match is not None:
                    login, mac = match.group(1), match.group(2).upper()
                    if mac not in last_ok_login_mac or last_ok_login_mac[mac] < log[0]:
                        last_ok_login_mac[mac] = log[0]
            if "EAP sub-module failed" in prev_log[1] \
                    and "mschap: MS-CHAP2-Response is incorrect" in log[1] \
                    and (prev_log[0] - log[0]).total_seconds() < 1:
                match = re.search(r'.*?EAP sub-module failed\):\s*\[(.*?)\].*?cli ([a-f0-9\-]+)\).*',
                                    prev_log[1])
                if match:
                    login, mac = match.group(1), match.group(2).upper()
                    if login != member.username:
                        add_to_statuses("LOGIN_INCORRECT_WRONG_USER", log[0], mac)
                    else:
                        add_to_statuses("LOGIN_INCORRECT_WRONG_PASSWORD", log[0], mac)
            if 'rlm_python' in log[1]:
                match = re.search(r'.*?rlm_python: Fail (.*?) ([a-f0-9A-F\-]+) with (.+)', log[1])
                if match is not None:
                    login, mac, reason = match.group(1), match.group(2).upper(), match.group(3)
                    if 'MAC not found and not association period' in reason:
                        add_to_statuses("LOGIN_INCORRECT_WRONG_MAC", log[0], mac)
                    if 'Adherent not found' in reason:
                        add_to_statuses("LOGIN_INCORRECT_WRONG_USER", log[0], mac)
            if "TLS Alert" in log[1]:  # @TODO Difference between TLS Alert read and TLS Alert write ??
                # @TODO a read access denied means the user is validating the certificate
                # @TODO a read/write protocol version is ???
                # @TODO a write unknown CA means the user is validating the certificate
                # @TODO a write decryption failed is ???
                # @TODO a read internal error is most likely not user-related
                # @TODO a write unexpected_message is ???
                match = re.search(
                    r'.*?TLS Alert .*?\):\s*\[(.*?)\].*?cli ([a-f0-9\-]+)\).*',
                    log[1])
                if match is not None:
                    login, mac = match.group(1), match.group(2).upper()
                    add_to_statuses("LOGIN_INCORRECT_SSL_ERROR", log[0], mac)
            prev_log = log

        all_statuses = []
        for mac, statuses in device_to_statuses.items():
            for _, object in statuses.items():
                if mac in last_ok_login_mac and object.last_timestamp < last_ok_login_mac[mac]:
                    continue
                all_statuses.append(object)
        return all_statuses
