# DoorLock
using raspbery PI, fingerprint and RFID.
use your own email and password.
I have changed the fingerprint's library because mine doesn't have some features.

In my final project, I have designed and implemented a House Door Security Lock System based
on IoT for smart homes using RFID reader, Fingerprint and Raspberry Pi3. This project has been written
in Python.
This system read users' tag or fingerprint and it will recognize whether it is valid or not. If it is valid the
entrance will be allowed. Otherwise, the system will alert the invalid entrance. After three invalid
entrance requests, the system will automatically send emails to admins to notify them and will be
suspended to providing security. This email is a simple message, yet a picture of the person who is tried
to enter the house can be attached. The RFID has been added due to the low quality of the fingerprint
sensor in some conditions such as wet weather. Moreover, this project has a "black box" which records
all the attempts to enter and exit the house. All these can be used when faced with a problem. Finally,
the system can be connected to the smart home's application to allow the admins to control the system.
