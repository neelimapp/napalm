"""Test fixtures."""
import pytest
from napalm.base.test import conftest as parent_conftest

from napalm.base.test.double import BaseTestDouble

from napalm.iosxr_netconf import iosxr_netconf


@pytest.fixture(scope="class")
def set_device_parameters(request):
    """Set up the class."""
    def fin():
        request.cls.device.close()

    request.addfinalizer(fin)

    request.cls.driver = iosxr_netconf.IOSXRNETCONFDriver
    request.cls.patched_driver = PatchedIOSXRNETCONFDriver
    request.cls.vendor = "iosxr_netconf"
    parent_conftest.set_device_parameters(request)


def pytest_generate_tests(metafunc):
    """Generate test cases dynamically."""
    parent_conftest.pytest_generate_tests(metafunc, __file__)


class PatchedIOSXRNETCONFDriver(iosxr_netconf.IOSXRNETCONFDriver):
    """Patched IOSXR NETCONF Driver."""

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):

        super().__init__(hostname, username, password, timeout, optional_args)
        self.patched_attrs = ["device"]
        self.device = FakeIOSXRNETCONFDevice()

    def is_alive(self):
        return {"is_alive": True}  # In testing everything works..

    def open(self):
        pass


class FakeIOSXRNETCONFDevice(BaseTestDouble):
    """IOSXR NETCONF device test double."""

    def close_session(self):
        pass

    def find_mocked_data_file(self):
        """Find mocked XML file for the current testcase"""
        filename = "{}.xml".format(self.current_test[5:])
        full_path = self.find_file(filename)
        data = self.read_txt_file(full_path)
        return data

    def dispatch(self, rpc_command, source=None, filter=None):
        return FakeRPCReply(self.find_mocked_data_file())

    def get(self, filter=None):
        return FakeRPCReply(self.find_mocked_data_file())

    def get_config(self, source, filter=None):
        return FakeRPCReply(self.find_mocked_data_file())


class FakeRPCReply:
    """Fake RPC Reply"""
    def __init__(self, raw):
        self._raw = raw

    @property
    def xml(self):
        return self._raw
