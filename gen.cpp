#include <windows.h>
#include <psapi.h>
#include <tchar.h>
#include <cstdio>
#include <TlHelp32.h>

typedef LONG(NTAPI *nt_suspend_process)(IN HANDLE process_handle);
typedef LONG(NTAPI *nt_resume_process)(IN HANDLE process_handle);

void suspend(DWORD process_id);
void resume(DWORD process_id);
bool is_driver_loaded();

int main()
{
    DWORD cb_needed;
    bool driver_found = false;

    while (!driver_found)
    {
        LPVOID drivers[1024];
        if (EnumDeviceDrivers(drivers, sizeof(drivers), &cb_needed) && cb_needed < sizeof(drivers))
        {
            const auto target_driver_name = TEXT("HoYoKProtect.sys");

            const int c_drivers = cb_needed / sizeof(drivers[0]);

            _tprintf(TEXT("Searching for driver: %s\n"), target_driver_name);

            for (int i = 0; i < c_drivers; i++)
            {
                TCHAR sz_driver[1024];
                if (GetDeviceDriverBaseName(drivers[i], sz_driver, sizeof(sz_driver) / sizeof(sz_driver[0])))
                {

                    // Check if the Genshin Impact Anticheat Driver is running
                    if (_tcsicmp(sz_driver, target_driver_name) == 0)
                    {
                        _tprintf(TEXT("Driver found at index %d: %s\n"), i + 1, sz_driver);

                        // Set the flag to exit the loop
                        driver_found = true;

                        // If the Anticheat Driver is running, immediately suspend / freeze the process "GenshinImpact.exe"
                        const HANDLE h_snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
                        PROCESSENTRY32 pe;
                        pe.dwSize = sizeof(PROCESSENTRY32);

                        if (Process32First(h_snapshot, &pe))
                        {
                            do
                            {
                                const auto target_process_name = TEXT("GenshinImpact.exe");
                                if (_tcsicmp(pe.szExeFile, target_process_name) == 0)
                                {
                                    suspend(pe.th32ProcessID);
                                    _tprintf(TEXT("Process %s (PID: %d) suspended.\n"), target_process_name, pe.th32ProcessID);

                                    // Check if the driver is still running
                                    while (is_driver_loaded())
                                    {
                                        // Sleep for a short time before checking again
                                        Sleep(100);
                                    }

                                    _tprintf(TEXT("Driver is not loaded. Resuming Genshin Impact.\n"));

                                    // If the Anticheat Driver stopped running, then resume the Genshin Impact process
                                    resume(pe.th32ProcessID);
                                    _tprintf(TEXT("Process %s (PID: %d) resumed.\n"), target_process_name, pe.th32ProcessID);
                                }
                            } while (Process32Next(h_snapshot, &pe));
                        }

                        CloseHandle(h_snapshot);
                    }
                }
            }
        }
        else
        {
            _tprintf(TEXT("EnumDeviceDrivers failed; array size needed is %llu\n"), cb_needed / sizeof(LPVOID));
            return 1;
        }

        // Sleep for a while before the next iteration
        Sleep(1);
    }

    system("pause");

    return 0;
}

void suspend(const DWORD process_id)
{
    const HANDLE process_handle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, process_id);
    if (process_handle != nullptr)
    {
        const auto pfn_nt_suspend_process = reinterpret_cast<nt_suspend_process>(GetProcAddress(
            GetModuleHandle(TEXT("ntdll")), "NtSuspendProcess"));

        if (pfn_nt_suspend_process != nullptr)
        {
            pfn_nt_suspend_process(process_handle);
            _tprintf(TEXT("Process suspended using NtSuspendProcess.\n"));
        }
        else
        {
            _tprintf(TEXT("Failed to get NtSuspendProcess function address.\n"));
        }

        CloseHandle(process_handle);
    }
}

void resume(const DWORD process_id)
{
    const HANDLE process_handle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, process_id);
    if (process_handle != nullptr)
    {
        const auto pfn_nt_resume_process = reinterpret_cast<nt_resume_process>(GetProcAddress(
            GetModuleHandle(TEXT("ntdll")), "NtResumeProcess"));

        if (pfn_nt_resume_process != nullptr)
        {
            pfn_nt_resume_process(process_handle);
            _tprintf(TEXT("Process resumed using NtResumeProcess.\n"));
        }
        else
        {
            _tprintf(TEXT("Failed to get NtResumeProcess function address.\n"));
        }

        CloseHandle(process_handle);
    }
}

bool is_driver_loaded()
{
    LPVOID drivers[1024];
    DWORD cb_needed;

    if (EnumDeviceDrivers(drivers, sizeof(drivers), &cb_needed) && cb_needed < sizeof(drivers))
    {
        const int c_drivers = cb_needed / sizeof(drivers[0]);

        for (int i = 0; i < c_drivers; i++)
        {
            TCHAR sz_driver[1024];
            if (GetDeviceDriverBaseName(drivers[i], sz_driver, sizeof(sz_driver) / sizeof(sz_driver[0])))
            {
                const auto target_driver_name = TEXT("HoYoKProtect.sys");
                if (_tcsicmp(sz_driver, target_driver_name) == 0)
                {
                    return true;
                }
            }
        }
    }

    return false;
}