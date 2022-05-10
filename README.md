# SMA-OSINT-Reconnaissance
This projects aims to show an autamated process to perform reconnaissance on a given target.
We will use OSINT and Social Media Analyitics techniques to gather and analyze the data.

### Installation
- Download this tool by typing `git clone "https://github.com/lprotopapa/SMA-OSINT-Reconnaissance.git"` and `cd SMA-OSINT-Reconnaissance` into it,
- Install the requirements with `pip install -r requirements.txt`,
- Install Pytorch (used with the BERT model for Sentiment Analysis) with the custom installation process explained on their website https://pytorch.org/ (it changes based on your system).

To install Pytorch on my Kali setup I used `pip3 install torch==1.10.1+cpu torchvision==0.11.2+cpu torchaudio==0.10.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
`

### Configuration
Create a configuration file by using the default one as template (you can also overwite it). The tool is modular and allows you to run only certain sections of the code if you want (and have the correct input data), setting them to 'false' prevents those sections from running. You will need to complete the fields as follows:
- **linkedin_scrape_mode** and **linkedin_find_users** must be set to 'true' if you wish to use an .har file as input for the targets identification and company hierarchy definition.
- **linkedin_har_file** must contain a path to the .har file you wish to use as input.
- **twitter_key1** and **twitter_key1** must contain the paths to the .json file which has the Twitter API data regarding your authentication. If you wish to use only 1 key, you can only write the path inside the first field and make sure that the field **multi_key** is set to 'false'.
- **manual_target_mode** and **manual_targets_file** are used to skip the linkedin scraping section and launch the rest of the tool using a manually inserted dataset composed of a list of twitter handles. Right now the tool can only run in manual mode due to Twitter API constraints.
- The field **twitter_target** must contain the Twitter handle of the main target (e.g. '@target')
- **visual_output** must be set to 'true' if you wish to have a visual output of the analyzed data. (Careful! You will need to manually close the visual popups to proceed with the tool execution, on large projects the executions might require several hours so be careful with this setting)
- The remaining fields **twitter_\*** are associated with their related section of code inside the tool. You can set some of them to 'false' to avoid their execution.

### Twitter APIs
To allow the tool to access Twitter, you will need to provide a .json file containing your autheintication key data. You can create a new file by following the structure of the default one you can find inside the 'keys' directory (you can also overwrite it). Remember to add two separate file and insert their path in the configuration file, along with setting the 'multi_key' field to 'true' if you want a faster execution.

### Execution
Once you have completed the configuration, you can run the tool by simply typing `./main.py -c <configFile>` where <configFile> is the path of your configuration file. You can also run it directly with Python by using `Python main.py -c <configFile>`. You can open the help page by adding the `-h` flag (or `--help`).

