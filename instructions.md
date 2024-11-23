For the Windows Edition - A couple things may need to be done if the code fails.

  Install the following via command prompt
   
    Launch command prompt as administrator
    
    enter the following, and wait for it complete
    
    pip install pywin32

Once this is has been executed, the import win32evtlog (line 4) in the code should be able to fully function.


For the Linux Log In Script 

  Sudo password will be needed to execute this for the first time.

  The code is written with the intention of troubleshooting and debugging. If the email address changes, see line 8 (email_recipient="logs@turnanewleaf.com")
  


