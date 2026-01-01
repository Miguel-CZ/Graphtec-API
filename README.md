# Graphtec-API
```
Graphtec-API
├─ graphtec
│  ├─ api
│  │  ├─ public.py
│  │  └─ __init__.py
│  ├─ config
│  │  └─ config_manager.py
│  ├─ connection
│  │  ├─ base.py
│  │  ├─ serial_connection.py
│  │  ├─ usb_connection.py
│  │  ├─ wlan_connection.py
│  │  └─ __init__.py
│  ├─ core
│  │  ├─ commands.py
│  │  ├─ device
│  │  │  ├─ alarm.py
│  │  │  ├─ amp.py
│  │  │  ├─ base.py
│  │  │  ├─ common.py
│  │  │  ├─ data.py
│  │  │  ├─ file.py
│  │  │  ├─ interface.py
│  │  │  ├─ logic.py
│  │  │  ├─ measure.py
│  │  │  ├─ option.py
│  │  │  ├─ status.py
│  │  │  ├─ transfer.py
│  │  │  ├─ trigger.py
│  │  │  └─ __init__.py
│  │  ├─ exceptions.py
│  │  └─ __init__.py
│  ├─ io
│  │  ├─ capture.py
│  │  ├─ decoder.py
│  │  ├─ realtime.py
│  │  └─ __init__.py
│  ├─ utils
│  │  ├─ logger.py
│  │  ├─ utils.py
│  │  └─ __init__.py
│  ├─ _version.py
│  └─ __init__.py
├─ LICENSE
├─ main.py
├─ pytest.ini
├─ README.md
├─ requirements-dev.txt
├─ requirements.txt
└─ tests
   ├─ conftest.py
   ├─ integration
   │  └─ test_public_api.py
   ├─ mocks
   │  ├─ mock_connection.py
   │  └─ responses.py
   └─ unit
      ├─ test_amp.py
      ├─ test_common.py
      ├─ test_data.py
      ├─ test_logic.py
      ├─ test_option.py
      ├─ test_status.py
      └─ test_trigger.py

```