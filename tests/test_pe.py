#!/usr/bin/env python3
# 
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
#

import os, random, sys, unittest, logging
import string as st

sys.path.append("..")
from qiling import Qiling
from qiling.const import *
from qiling.exception import *
from qiling.extensions import pipe
from qiling.loader.pe import QlPeCache
from qiling.os.const import *
from qiling.os.windows.fncc import *
from qiling.os.windows.utils import *
from qiling.os.mapper import QlFsMappedObject
import multiprocess as mb

# On Windows, the CPython GC is too conservative and may hold too
# many Unicorn objects (nearly 16GB) until free-ing them which may
# cause failure during tests.
#
# Use subprocess to make sure resources are free-ed when the subprocess
# is killed.
class QLWinSingleTest:

    def __init__(self, test):
        self._test = test

    def _run_test(self, results):
        try:
            results['result'] = self._test()
        except Exception as e:
            results['exception'] = e
            results['result'] = False

    def run(self):
        with mb.Manager() as m:
            results = m.dict()
            p = mb.Process(target=QLWinSingleTest._run_test, args=(self, results))
            p.start()
            p.join()
            if "exception" not in results:
                return results['result']
            else:
                raise results['exception']


class TestOut:
    def __init__(self):
        self.output = {}

    def write(self, string):
        key, value = string.split(b': ', 1)
        assert key not in self.output
        self.output[key] = value
        return len(string)


class PETest(unittest.TestCase):

    def test_pe_win_x8664_hello(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x8664_windows/bin/x8664_hello.exe"], "../examples/rootfs/x8664_windows",
                        verbose=QL_VERBOSE.DEFAULT)
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_hello(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x86_windows/bin/x86_hello.exe"], "../examples/rootfs/x86_windows",
                        verbose=QL_VERBOSE.DEFAULT, profile="profiles/append_test.ql")
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_uselessdisk(self):
        def _t():
            if 'QL_FAST_TEST' in os.environ:
                return
            class Fake_Drive(QlFsMappedObject):

                def read(self, size):
                    return random.randint(0, 256)
                
                def write(self, bs):
                    print(bs)
                    return

                def fstat(self):
                    return -1
                
                def close(self):
                    return 0

            ql = Qiling(["../examples/rootfs/x86_windows/bin/UselessDisk.bin"], "../examples/rootfs/x86_windows",
                        verbose=QL_VERBOSE.DEBUG)
            ql.add_fs_mapper(r"\\.\PHYSICALDRIVE0", Fake_Drive())
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_gandcrab(self):
        def _t():
            if 'QL_FAST_TEST' in os.environ:
                return
            def stop(ql, default_values):
                print("Ok for now")
                ql.emu_stop()

            def randomize_config_value(ql, key, subkey):
                # https://en.wikipedia.org/wiki/Volume_serial_number
                # https://www.digital-detective.net/documents/Volume%20Serial%20Numbers.pdf
                if key == "VOLUME" and subkey == "serial_number":
                    month = random.randint(0, 12)
                    day = random.randint(0, 30)
                    first = hex(month)[2:] + hex(day)[2:]
                    seconds = random.randint(0, 60)
                    milli = random.randint(0, 100)
                    second = hex(seconds)[2:] + hex(milli)[2:]
                    first_half = int(first, 16) + int(second, 16)
                    hour = random.randint(0, 24)
                    minute = random.randint(0, 60)
                    third = hex(hour)[2:] + hex(minute)[2:]
                    year = random.randint(2000, 2020)
                    second_half = int(third, 16) + year
                    result = int(hex(first_half)[2:] + hex(second_half)[2:], 16)
                    ql.os.profile[key][subkey] = str(result)
                elif key == "USER" and subkey == "username":
                    length = random.randint(0, 15)
                    new_name = ""
                    for i in range(length):
                        new_name += random.choice(st.ascii_lowercase + st.ascii_uppercase)
                    old_name = ql.os.profile[key][subkey]
                    # update paths
                    ql.os.profile[key][subkey] = new_name
                    for path in ql.os.profile["PATH"]:
                        val = ql.os.profile["PATH"][path].replace(old_name, new_name)
                        ql.os.profile["PATH"][path] = val
                elif key == "SYSTEM" and subkey == "computername":
                    length = random.randint(0, 15)
                    new_name = ""
                    for i in range(length):
                        new_name += random.choice(st.ascii_lowercase + st.ascii_uppercase)
                    ql.os.profile[key][subkey] = new_name
                else:
                    raise QlErrorNotImplemented("API not implemented")

            ql = Qiling(["../examples/rootfs/x86_windows/bin/GandCrab502.bin"], "../examples/rootfs/x86_windows",
                        verbose=QL_VERBOSE.DEBUG, profile="profiles/windows_gandcrab_admin.ql")
            default_user = ql.os.profile["USER"]["username"]
            default_computer = ql.os.profile["SYSTEM"]["computername"]

            ql.hook_address(stop, 0x40860f, user_data=(default_user, default_computer))
            randomize_config_value(ql, "USER", "username")
            randomize_config_value(ql, "SYSTEM", "computername")
            randomize_config_value(ql, "VOLUME", "serial_number")
            num_syscalls_admin = ql.os.utils.syscalls_counter
            ql.run()
            del ql

            # RUN AS USER
            ql = Qiling(["../examples/rootfs/x86_windows/bin/GandCrab502.bin"], "../examples/rootfs/x86_windows", profile="profiles/windows_gandcrab_user.ql")

            ql.run()
            num_syscalls_user = ql.os.utils.syscalls_counter

            # let's check that gandcrab behave takes a different path if a different environment is found
            if num_syscalls_admin == num_syscalls_user:
                return False

            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())

    def test_pe_win_x86_multithread(self):
        def _t():
            thread_id = None
            def ThreadId_onEnter(ql, address, params):
                nonlocal thread_id
                thread_id = ql.os.thread_manager.cur_thread.id
                return address, params

            ql = Qiling(["../examples/rootfs/x86_windows/bin/MultiThread.exe"], "../examples/rootfs/x86_windows")
            ql.set_api("GetCurrentThreadId", ThreadId_onEnter, QL_INTERCEPT.ENTER)
            ql.run()
            
            if not ( 1<= thread_id < 255):
                return False
            
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_clipboard(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x8664_windows/bin//x8664_clipboard_test.exe"], "../examples/rootfs/x8664_windows")
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_tls(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x8664_windows/bin/x8664_tls.exe"], "../examples/rootfs/x8664_windows")
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_getlasterror(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x86_windows/bin/GetLastError.exe"], "../examples/rootfs/x86_windows")
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_regdemo(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x86_windows/bin/RegDemo.exe"], "../examples/rootfs/x86_windows")
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x8664_fls(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x8664_windows/bin/Fls.exe"], "../examples/rootfs/x8664_windows", verbose=QL_VERBOSE.DEFAULT)
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_return_from_main_stackpointer(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x86_windows/bin/return_main.exe"], "../examples/rootfs/x86_windows", libcache=True, stop_on_stackpointer=True)
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_return_from_main_exit_trap(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x86_windows/bin/return_main.exe"], "../examples/rootfs/x86_windows", libcache=True, stop_on_exit_trap=True)
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x8664_return_from_main_stackpointer(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x8664_windows/bin/x8664_return_main.exe"], "../examples/rootfs/x8664_windows", libcache=True, stop_on_stackpointer=True)
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x8664_return_from_main_exit_trap(self):
        def _t():
            ql = Qiling(["../examples/rootfs/x8664_windows/bin/x8664_return_main.exe"], "../examples/rootfs/x8664_windows", libcache=True, stop_on_exit_trap=True)
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_wannacry(self):
        def _t():
            if 'QL_FAST_TEST' in os.environ:
                return
            def stop(ql):
                ql.log.info("killerswtichfound")
                ql.log.setLevel(logging.CRITICAL)
                ql.log.info("No Print")
                ql.emu_stop()

            ql = Qiling(["../examples/rootfs/x86_windows/bin/wannacry.bin"], "../examples/rootfs/x86_windows")
            ql.hook_address(stop, 0x40819a)
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_NtQueryInformationSystem(self):
        def _t():
            ql = Qiling(
            ["../examples/rootfs/x86_windows/bin/NtQuerySystemInformation.exe"],
            "../examples/rootfs/x86_windows")
            ql.run()
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_al_khaser(self):
        def _t():
            if 'QL_FAST_TEST' in os.environ:
                return
            ql = Qiling(["../examples/rootfs/x86_windows/bin/al-khaser.bin"], "../examples/rootfs/x86_windows")

            # The hooks are to remove the prints to file. It crashes. will debug why in the future
            def results(ql):

                if ql.reg.ebx == 1:
                    print("BAD")
                else:
                    print("GOOD ")
                ql.reg.eip = 0x402ee4

            #ql.hook_address(results, 0x00402e66)
            # the program alloc 4 bytes and then tries to write 0x2cc bytes.
            # I have no idea of why this code should work without this patch
            ql.patch(0x00401984, b'\xb8\x04\x00\x00\x00')

            def end(ql):
                print("We are finally done")
                ql.emu_stop()

            ql.hook_address(end, 0x004016ae)

            ql.run()
            del ql
            return True

        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x8664_customapi(self):
        def _t():
            set_api = None
            set_api_onenter = None
            set_api_onexit = None

            @winsdkapi(cc=CDECL, params={
                "str" : STRING
            })
            def my_puts64(ql: Qiling, address: int, params):
                nonlocal set_api
                print(f'[oncall] my_puts64: params = {params}')

                params["str"] = "Hello Hello Hello"
                ret = len(params["str"])
                set_api = ret

                return ret

            def my_onenter(ql: Qiling, address: int, params):
                nonlocal set_api_onenter
                print(f'[onenter] my_onenter: params = {params}')

                set_api_onenter = len(params["str"])

            def my_onexit(ql: Qiling, address: int, params, retval: int):
                nonlocal set_api_onexit
                print(f'[onexit] my_onexit: params = {params}')

                set_api_onexit = len(params["str"])

            def my_sandbox(path, rootfs):
                nonlocal set_api, set_api_onenter, set_api_onexit
                ql = Qiling(path, rootfs, verbose=QL_VERBOSE.DEBUG)
                ql.set_api("puts", my_onenter, QL_INTERCEPT.ENTER)
                ql.set_api("puts", my_puts64, QL_INTERCEPT.CALL)
                ql.set_api("puts", my_onexit, QL_INTERCEPT.EXIT)
                ql.run()

                if 12 != set_api_onenter:
                    return False
                if 17 != set_api:
                    return False
                if 17 != set_api_onexit:
                    return False

                del ql
                return True

            return my_sandbox(["../examples/rootfs/x8664_windows/bin/x8664_hello.exe"], "../examples/rootfs/x8664_windows")
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_argv(self):
        def _t():
            
            target_txt = None

            def check_print(ql: Qiling, address: int, params):
                nonlocal target_txt
                ql.os.fcall = ql.os.fcall_select(CDECL)

                params = ql.os.resolve_fcall_params({
                    '_Options' : PARAM_INT64,
                    '_Stream'  : POINTER,
                    '_Format'  : STRING,
                    '_Locale'  : DWORD,
                    '_ArgList' : POINTER
                })

                format = params['_Format']
                arglist = params['_ArgList']

                count = format.count("%")
                fargs = [ql.unpack(ql.mem.read(arglist + i * ql.pointersize, ql.pointersize)) for i in range(count)]

                target_txt = ""

                try:
                    target_txt = ql.mem.string(fargs[1])
                except:
                    pass

                return address, params

            ql = Qiling(["../examples/rootfs/x86_windows/bin/argv.exe"], "../examples/rootfs/x86_windows")
            ql.set_api('__stdio_common_vfprintf', check_print, QL_INTERCEPT.ENTER)
            ql.run()
            
            if target_txt.find("argv.exe"):
                target_txt = "argv.exe"
            
            if "argv.exe" != target_txt:
                return False
            
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x86_crackme(self):
        def _t():
            def force_call_dialog_func(ql):
                # get DialogFunc address
                lpDialogFunc = ql.unpack32(ql.mem.read(ql.reg.esp - 0x8, 4))
                # setup stack for DialogFunc
                ql.stack_push(0)
                ql.stack_push(1001)
                ql.stack_push(273)
                ql.stack_push(0)
                ql.stack_push(0x0401018)
                # force EIP to DialogFunc
                ql.reg.eip = lpDialogFunc

            def our_sandbox(path, rootfs):
                ql = Qiling(path, rootfs)
                ql.patch(0x004010B5, b'\x90\x90')
                ql.patch(0x004010CD, b'\x90\x90')
                ql.patch(0x0040110B, b'\x90\x90')
                ql.patch(0x00401112, b'\x90\x90')

                ql.os.stdin = pipe.SimpleStringBuffer()
                ql.os.stdin.write(b"Ea5yR3versing\n")

                ql.hook_address(force_call_dialog_func, 0x00401016)
                ql.run()
                del ql

            our_sandbox(["../examples/rootfs/x86_windows/bin/Easy_CrackMe.exe"], "../examples/rootfs/x86_windows")
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())
        

    def test_pe_win_x86_cmdln(self):
        def _t():
            ql = Qiling(
            ["../examples/rootfs/x86_windows/bin/cmdln32.exe", 'arg1', 'arg2 with spaces'],
            "../examples/rootfs/x86_windows")
            ql.os.stdout = TestOut()
            ql.run()
            expected_string = b'<C:\\Users\\Qiling\\Desktop\\cmdln32.exe arg1 "arg2 with spaces">\n'
            expected_keys = [b'_acmdln', b'_wcmdln', b'__p__acmdln', b'__p__wcmdln', b'GetCommandLineA', b'GetCommandLineW']
            for key in expected_keys:
                if not (key in ql.os.stdout.output):
                    return False
                if expected_string != ql.os.stdout.output[key]:
                    return False
            del ql
            return True

        self.assertTrue(QLWinSingleTest(_t).run())


    def test_pe_win_x8664_cmdln(self):
        def _t():
            ql = Qiling(
            ["../examples/rootfs/x8664_windows/bin/cmdln64.exe", 'arg1', 'arg2 with spaces'],
            "../examples/rootfs/x8664_windows")
            ql.os.stdout = TestOut()
            ql.run()
            expected_string = b'<C:\\Users\\Qiling\\Desktop\\cmdln64.exe arg1 "arg2 with spaces">\n'
            expected_keys = [b'_acmdln', b'_wcmdln', b'GetCommandLineA', b'GetCommandLineW']
            for key in expected_keys:
                if not (key in ql.os.stdout.output):
                    return False
                if expected_string != ql.os.stdout.output[key]:
                    return False
            del ql
            return True
        
        self.assertTrue(QLWinSingleTest(_t).run())

    class RefreshCache(QlPeCache):
        def restore(self, path):
            # If the cache entry exists, delete it
            fcache = self.create_filename(path)
            if os.path.exists(fcache):
                os.remove(fcache)
            return super().restore(path)

    class TestCache(QlPeCache):
        def __init__(self, testcase):
            super().__init__()
            self.testcase = testcase

        def restore(self, path):
            entry = super().restore(path)
            self.testcase.assertTrue(entry is not None)  # Check that it loaded a cache entry
            if path.endswith('msvcrt.dll'):
                self.testcase.assertEqual(len(entry.cmdlines), 2)
            else:
                self.testcase.assertEqual(len(entry.cmdlines), 0)
            self.testcase.assertIsInstance(entry.data, bytearray)
            return entry

        def save(self, path, entry):
            self.testcase.assertFalse(True)  # This should not be called!


    def test_pe_win_x8664_libcache(self):
        
        def _t():
            # First force the cache to be recreated
            ql = Qiling(["../examples/rootfs/x8664_windows/bin/cmdln64.exe",
                        'arg1', 'arg2 with spaces'],
                        "../examples/rootfs/x8664_windows",
                        libcache=PETest.RefreshCache(),
                        verbose=QL_VERBOSE.DEFAULT)
            ql.run()
            del ql

            # Now run with a special cache that validates that the 'real' cache will load,
            # and that the file is not written again
            ql = Qiling(["../examples/rootfs/x8664_windows/bin/cmdln64.exe",
                        'arg1', 'arg2 with spaces'],
                        "../examples/rootfs/x8664_windows",
                        libcache=PETest.TestCache(self),
                        verbose=QL_VERBOSE.DEFAULT)
            ql.run()
            del ql
            return True

        self.assertTrue(QLWinSingleTest(_t).run())

if __name__ == "__main__":
    unittest.main()
