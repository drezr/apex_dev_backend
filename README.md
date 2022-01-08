# APEX backend developement project

 
## Linux installation

```
sudo apt update
```

```
sudo apt upgrade
```

```
sudo apt install python3-venv
```

```
sudo apt install python3-pip
```

```
cd /project/directory
```

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
pip3 install --upgrade pip
```

```
cd /project/directory/apex_dev_backend
```

```
pip install -r requirements.txt
```

```
mkdir /project/directory/media
```

```
sudo nano /project/directory/apex_dev_backend/backend/settings.py
```
Change the MEDIA_ROOT variable to the media directory previously created (/project/directory/media).

Change the EMAIL_* variables to your email service provider (not mandatory for developpement usage).


Instructions for production are inside the settings.py file.


```
python manage.py makemigrations
```

```
python manage.py migrate
```

```
python manage.py runserver
```

## License

[MIT License](https://opensource.org/licenses/MIT)
 
Copyright (c) 2021-present, Ronan Dumont
