
# Red Hat Access Insights Client

   This is the container_mode branch of insights-client.  The instructions below don't explain
   how to use the container mode stuff (yet), but these instructions are only on the container_mode
   branch for now.

## Fetching

   When you clone this, make sure you get the container_mode branch:

   ```bash
   git clone --branch container_mode https://github.com/gavin-romig-koch/insights-client.git
   ```

## To get this running:

   I've only tested this on RHEL7

   1. make sure your machine has a reasonable unique hostname 'cause that's the only
         way to find it on the server.  It can be anything, just don't leave it 'localhost'. 

      sudo hostname myveryownhostname    # for example

   1. make sure the machine is subcribed and registered with Red Hat

      subscription-manager register --auto-attach
                     # it will ask for Red Hat Customer Portal username and password

   3. create a config file

      ```bash
      cd insights-client
      cp etc/redhat-access-insights.conf .
      ```

      Then edit redhat-access-insights.conf it to add

      ```bash
      auto_config=False
      no_schedule=True
      username=<YOUR RED HAT PORTAL USERNAME>
      password=<YOUR RED HAT PORTAL PASSWORD>
      upload_url=http://<IPADDR>:<PORT>/r/insights/uploads
      ```

      * IPADDR is the ip addr of the host where you are running the insights-engine
      * PORT is likely to be 8080 if you are running the insights-engine directly
                        to be something like 32XXXX if you are running insights-engine in a container

      If you are running insights-engin in a container, get the host port number liked to
      the container port 8080.  The following will tell you what PORT to use.
        
      ```bash
      sudo docker port CONTAINER_NAME 8080
      ```
        
   4. Install some prerequisites 

      ```bash
      sudo yum install -y python-setuptools python2-devel python-requests python-magic
      ```
        
   5. Run the 'install_and_run' script

      ```bash
      sudo ./install_and_run
       ```
        
      This will (re-)install the configuration (into /etc) and run insights-client from this directory
      so any changes to the config or code in this directory will have effect.

## Todo:
  
    * Figure out how to use config directly from this directory.
    * move the install_and_run scrip into the Makefile
