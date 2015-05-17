# simple-page-monitor  

Fetch Keywords in Page, and notify. 
 
(I use it to check Refurbished Mac.)


## Requirement

GNU/Linux  
Python 2.7  

**Optional**:  
[Mailgun](http://www.mailgun.com/) (Mail deliver)


## Install
```
$ git clone git@github.com:mapler/simple-page-monitor.git
$ cd simple-page-monitor
$ pip install -r requirements.txt
```

## Usage
Edit the config.ini.  
Set methods for senders.  
Set keywords and page url. All keywords will be check (logic OR)  
Set output format.

**simple-page-monitor/config.ini**

```
[Global]
SENDERS=Output
        File
```
```
[Page]
URL=http://website.which.you.want.to.monitor
KEYWORDS=Keyword1
         Keyword2
OUTPUT_FORMAT=<h3>Matched.</h3>
              <p>Keywords: {keywords}</p>
              <hr>
              {matched_messages}
              <hr>
              <a href="{url}">{url}</a>        
```

Supported Sender Methods:   

* File (Save to file)
* Output (Print out)
* Mail (Send by smtp)
* Mailgun (Send by [mailgun.com](http://www.mailgun.com/))

Run: 

```
$ cd simple-page-monitor
$ python ./main.py
```

## Licence

[MIT](https://github.com/mapler/simple-page-monitor/blob/master/LICENSE)

## Author

[mapler](https://github.com/mapler)