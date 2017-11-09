# Automate-IOS-upgrade

The 'upgrade info.csv' is the heart of this program.  
Column A just just for your info to make it more human readable

Column B is what the program looks for in "show ver" to figure out which row to use (So make sure the info correct and specific enough to not have false positives)

Column C is where the IOS will be copied to and where the boot statment says it should be (careful, some switches require flash:/ and some routers don't like that)

Column D is the IOS that will be copied to the device, these IOSs will need to be in the same folder as program you are running.

Column E is the output that the program will verify is in the output from the verify command.  This is exactly what will be there, so if it has the hash that should be there and the generated hash if you only put the correct hash in it could pass the check incorrectly.

Column F does nothing, it use to let you specify what server you would be useing, but we needed to upload directly from the PC

This program SSHs to the box and runs "show ver" on it.  

It then looks in the output for columb B in 'upgrade info.csv'.  

It will then enable SCP server on the router/switch and SCP over the IOS in the corosponding row.  

It will then run the verify command and verify that the exact output from Colum E is in there.

Next it will remove the 'ip scp server enable' command

Then it will remove the current boot statments

It will then run boot system "upgrade info.csv column C+column D"

Then write memory

Next check the boot statment to make sure the boot statment is in the startup config

PLEASE NOTE THIS DOESN'T DO ANY RESTARTS, THAT NEEDS TO BE DONE MANUALLY.
